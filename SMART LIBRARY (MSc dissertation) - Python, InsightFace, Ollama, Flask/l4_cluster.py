"""HDBSCAN clustering over window-row embeddings — pool-scope, post-Sync.

Spec references:
  - §1h (LOCKED 2026-05-20, iter05 atmospheric composition) — algorithm +
        thesis finding that atmospheric+categorical fields cluster by scene
        family while narrative fields surface clip-fingerprint
  - §1i (LOCKED 2026-05-21) — runs after Sync; exposed as standalone button
  - §1j — `cluster_id int/null` row field (-1 = noise; null = pre-cluster)

Hard invariants:
  - Cluster never calls Ollama and never reads caption sidecars. Embeddings
    come from Chroma (written by Sync from `caption.windows[i].embedding`).
    By construction those vectors were composed from `EMBED_FIELDS` only —
    no `subjects_action` / `framing` contamination.
  - Cluster never writes sidecars. Cluster IDs are not stable across passes
    (§1h) and live only in Chroma.
  - Each pass overwrites every row's `cluster_id`: clustered → int, noise → -1.
  - Stale cluster_ids on rows from a prior pool that's since shrunk below
    skip-threshold are left alone — harmless when pool is too small to browse,
    reassigned on the next successful pass.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

import l1_config as config
import l4_sync as sync
from l1_logger import get_logger, step, step_error

log = get_logger("cluster")

OP_NAME = "cluster"


# ── Result ────────────────────────────────────────────────────────────────────

@dataclass
class ClusterSummary:
    rows_scanned: int = 0
    rows_clustered: int = 0
    rows_noise: int = 0
    n_clusters: int = 0
    silhouette: float | None = None
    rows_updated: int = 0
    skipped_reason: str | None = None
    notes: list[str] = field(default_factory=list)


# ── Pool read ─────────────────────────────────────────────────────────────────

def _read_pool(collection) -> tuple[list[str], np.ndarray, list[dict]]:
    """Return (ids, embeddings, metadatas) for the entire `clips` collection.

    Embeddings are L2-normalized so euclidean distance == cosine distance
    inside HDBSCAN (phase7's proven path; avoids hdbscan version drift on
    the native `metric="cosine"` option).
    """
    res = collection.get(include=["embeddings", "metadatas"])
    ids = list(res.get("ids") or [])
    # `embeddings` is an ndarray in chromadb >=0.5; `or []` triggers numpy's
    # ambiguous-truth-value error. Check None explicitly instead.
    embs_raw = res.get("embeddings")
    if embs_raw is None:
        embs_raw = []
    metas = list(res.get("metadatas") or [])
    if not ids:
        return [], np.zeros((0, 0), dtype=np.float32), []

    emb = np.asarray(embs_raw, dtype=np.float32)
    if emb.ndim != 2 or emb.shape[0] != len(ids):
        raise RuntimeError(
            f"chroma returned malformed embeddings: shape={emb.shape}, ids={len(ids)}"
        )
    norms = np.linalg.norm(emb, axis=1, keepdims=True) + 1e-12
    emb = emb / norms
    return ids, emb, metas


# ── HDBSCAN ───────────────────────────────────────────────────────────────────

def _run_hdbscan(emb: np.ndarray) -> np.ndarray:
    import hdbscan
    model = hdbscan.HDBSCAN(
        min_cluster_size=int(config.CLUSTER_MIN_CLUSTER_SIZE),
        min_samples=int(config.CLUSTER_MIN_SAMPLES) if config.CLUSTER_MIN_SAMPLES else None,
        metric="euclidean",  # vectors are L2-normalized → equivalent to cosine
        cluster_selection_method=config.CLUSTER_SELECTION_METHOD,
    )
    return model.fit_predict(emb)


def _silhouette_safe(emb: np.ndarray, labels: np.ndarray) -> float | None:
    """Silhouette over clustered subset only. None if <2 clusters or <2 rows."""
    mask = labels >= 0
    clustered_labels = labels[mask]
    if clustered_labels.size < 2:
        return None
    if len(set(clustered_labels.tolist())) < 2:
        return None
    try:
        from sklearn.metrics import silhouette_score
        return float(silhouette_score(emb[mask], clustered_labels, metric="euclidean"))
    except Exception as e:  # noqa: BLE001
        log.warning("silhouette computation failed: %s", e)
        return None


# ── Write-back ────────────────────────────────────────────────────────────────

def _build_updated_metas(metas: list[dict], labels: np.ndarray) -> list[dict]:
    """Overlay `cluster_id` onto a copy of each existing metadata dict.

    Chroma's `update()` replaces the metadata document, not field-by-field —
    so we must carry every existing key forward and overlay cluster_id on
    top, otherwise we'd wipe the rest of the row.
    """
    out: list[dict] = []
    for meta, lbl in zip(metas, labels):
        new = dict(meta or {})
        new["cluster_id"] = int(lbl)  # -1 stays explicit per §1j
        out.append(new)
    return out


# ── Driver ────────────────────────────────────────────────────────────────────

def cluster_pool(library_root: Path, *, dry_run: bool = False) -> ClusterSummary:
    """Run HDBSCAN over every window row in Chroma; write cluster_id back.

    Returns a summary; never raises on degenerate input (empty pool, too few
    rows, HDBSCAN failure) — those land in `skipped_reason` so the pipeline
    can continue.
    """
    library_root = Path(library_root).resolve()
    summary = ClusterSummary()

    try:
        collection = sync.get_collection(library_root)
    except Exception as e:  # noqa: BLE001
        step_error(log, OP_NAME, str(library_root), f"chromadb init failed: {e}")
        summary.skipped_reason = f"chroma init failed: {e}"
        return summary

    try:
        ids, emb, metas = _read_pool(collection)
    except Exception as e:  # noqa: BLE001
        step_error(log, OP_NAME, str(library_root), f"pool read failed: {e}")
        summary.skipped_reason = f"pool read failed: {e}"
        return summary

    summary.rows_scanned = len(ids)

    if not ids:
        log.info("[%s] pool is empty — nothing to cluster", OP_NAME)
        summary.skipped_reason = "empty pool"
        return summary

    # HDBSCAN needs at least min_cluster_size points to even attempt a cluster;
    # require 2× that before bothering — a 6-row pool with mcs=3 produces at
    # most one cluster, not meaningful for the UI sidebar.
    min_pool = 2 * int(config.CLUSTER_MIN_CLUSTER_SIZE)
    if len(ids) < min_pool:
        msg = f"pool too small ({len(ids)} < {min_pool}); skipping (stale cluster_ids preserved)"
        log.info("[%s] %s", OP_NAME, msg)
        summary.skipped_reason = msg
        return summary

    log.info(
        "[%s] HDBSCAN over %d rows  (mcs=%d, ms=%s, sel=%s)",
        OP_NAME, len(ids),
        config.CLUSTER_MIN_CLUSTER_SIZE,
        config.CLUSTER_MIN_SAMPLES,
        config.CLUSTER_SELECTION_METHOD,
    )

    try:
        labels = _run_hdbscan(emb)
    except Exception as e:  # noqa: BLE001
        step_error(log, OP_NAME, str(library_root), f"HDBSCAN failed: {e}")
        summary.skipped_reason = f"hdbscan failed: {e}"
        return summary

    n_noise = int((labels == -1).sum())
    cluster_label_set = sorted({int(l) for l in labels.tolist() if l >= 0})
    summary.rows_noise = n_noise
    summary.rows_clustered = len(ids) - n_noise
    summary.n_clusters = len(cluster_label_set)
    summary.silhouette = _silhouette_safe(emb, labels)

    log.info(
        "[%s] clustered=%d  noise=%d  n_clusters=%d  silhouette=%s",
        OP_NAME,
        summary.rows_clustered, summary.rows_noise, summary.n_clusters,
        f"{summary.silhouette:.3f}" if summary.silhouette is not None else "n/a",
    )

    if dry_run:
        step(log, OP_NAME, str(library_root),
             f"DRY-RUN: would update {len(ids)} rows")
        return summary

    new_metas = _build_updated_metas(metas, labels)

    try:
        collection.update(ids=ids, metadatas=new_metas)
        summary.rows_updated = len(ids)
    except Exception as e:  # noqa: BLE001
        step_error(log, OP_NAME, str(library_root),
                   f"chroma update failed: {e}")
        summary.skipped_reason = f"chroma update failed: {e}"
        return summary

    step(log, OP_NAME, str(library_root),
         f"wrote cluster_id to {summary.rows_updated} rows")
    return summary
