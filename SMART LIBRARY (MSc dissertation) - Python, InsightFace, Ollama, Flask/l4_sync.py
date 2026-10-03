"""ChromaDB sync — read sidecars + filesystem state → upsert one row per
window. Reconciles the `clips` collection against the library; never invokes
face / caption / cluster, never calls Ollama for embeddings.

Spec references:
  - §1j (LOCKED 2026-05-21) — per-window row schema, read/write boundary
  - §1f (LOCKED 2026-05-21, FACE_VOTE_MIN revised to 1 same day) —
        window-local face voting
  - §1g (OPEN) — per-window user overlay; stub applies clip-level state
        uniformly via `_window_user_state()`; task 8 plugs per-window overrides
  - §1h — cluster_id is owned by the cluster op; sync preserves existing
        ids across re-runs (carry-forward) so standalone sync doesn't wipe them

Window-row invariants:
  - Caption sidecar absent → zero rows for that clip. No partial inserts.
  - Embeddings come from `caption.windows[i].embedding` (computed at caption
    time, Option A1 sidecar-is-truth). Wipe Chroma → rebuild from sidecars
    with zero VLM/nomic re-compute.
  - Row id = `{clip_id}:{int(window_start_s * 1000)}`. Stale ids (window
    count shrank, caption sidecar gone, clip file gone) are removed by the
    end-of-sync stale scan keyed on `clip_id`-prefix membership.

Move semantics:
  - Same `clip_id` discovered at a different `relative_path` → all of that
    clip's window rows are re-upserted with refreshed path / location /
    event_path; enrichment carries forward via the caption sidecar.
  - `clip_id` no longer present on disk → every row whose id starts with
    `clip_id:` is deleted and every sidecar for the clip is swept.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import requests

import l1_config as config
import l1_filename as fn
import l1_identity as identity
import l1_sidecar as sidecar
import l2_discover as discover
import l4_user as user
from l1_logger import get_logger, step, step_error

log = get_logger("sync")

OP_NAME = "sync"


# ── Ollama embedding (query path only — sync NEVER embeds) ────────────────────

def embed_text(text: str, *, timeout_s: int = 120) -> list[float]:
    """Embed a single query string via Ollama `/api/embeddings` on OLLAMA_HOSTS[0].

    Used by the query path only. The sync path reads vectors directly from
    `caption.windows[i].embedding` and never touches Ollama.
    """
    host = config.OLLAMA_HOSTS[0].rstrip("/")
    resp = requests.post(
        host + "/api/embeddings",
        json={"model": config.EMBED_MODEL, "prompt": text or ""},
        timeout=timeout_s,
    )
    resp.raise_for_status()
    vec = resp.json().get("embedding")
    if not vec:
        raise RuntimeError(f"empty embedding from {config.EMBED_MODEL}")
    return vec


# ── ChromaDB client ───────────────────────────────────────────────────────────

def _chroma_path(library_root: Path) -> Path:
    return Path(library_root) / config.CHROMA_DIR


def get_collection(library_root: Path):
    """Return the `clips` collection (one row per window). User-provided
    embeddings; no Chroma embedding function.
    """
    import chromadb
    client = chromadb.PersistentClient(path=str(_chroma_path(library_root)))
    return client.get_or_create_collection(
        name=config.CHROMA_COLLECTION,
        metadata={"hnsw:space": "cosine"},
    )


# ── Filesystem index (shortid → current_path) ─────────────────────────────────

def build_filesystem_index(library_root: Path) -> dict[str, Path]:
    """Walk the library, parse canonical filenames, return `{shortid: path}`.

    Non-canonical clips are skipped — they can't be matched to a clip_id
    without re-hashing every sync. Collisions (essentially impossible at
    thesis scale) resolve to the lexicographically earliest path with a
    warning.
    """
    library_root = Path(library_root)
    index: dict[str, Path] = {}
    collisions: dict[str, list[Path]] = {}
    for clip_path in discover.iter_clips(library_root):
        parsed = fn.parse(clip_path.name)
        if parsed.shape != fn.SHAPE_CANONICAL or not parsed.canonical_shortid:
            continue
        sid = parsed.canonical_shortid.lower()
        prior = index.get(sid)
        if prior is None:
            index[sid] = clip_path
        else:
            collisions.setdefault(sid, [prior]).append(clip_path)
            if str(clip_path) < str(prior):
                index[sid] = clip_path
    for sid, paths in collisions.items():
        log.warning("shortid collision %s — keeping %s, ignoring %s",
                    sid, index[sid], [p for p in paths if p != index[sid]])
    return index


# ── Path utilities ────────────────────────────────────────────────────────────

def _split_path_parts(library_root: Path, current_path: Path) -> tuple[str, str, str]:
    """(relative_path, location, event_path) for a clip under the root."""
    rel = Path(current_path).resolve().relative_to(Path(library_root).resolve())
    parts = rel.parts
    if len(parts) <= 1:
        return rel.as_posix(), "", ""
    location = parts[0]
    event_path = " / ".join(parts[1:-1])
    return rel.as_posix(), location, event_path


def _scrub(meta: dict) -> dict:
    """Drop None values — Chroma metadata accepts only str/int/float/bool.
    Absence at storage time == null at filter time.
    """
    out: dict = {}
    for k, v in meta.items():
        if v is None:
            continue
        if isinstance(v, (str, int, float, bool)):
            out[k] = v
        else:
            out[k] = str(v)
    return out


# ── Source-clip resolution (cuts → source_clip_id) ────────────────────────────

def _resolve_source_clip_ids(normalize_index: dict[str, dict]) -> dict[str, str]:
    """Map each cut's normalize sidecar → source_clip_id when the source clip
    is also in the library. Returns `{clip_id: source_clip_id}` for cuts only.
    """
    by_original_filename: dict[str, str] = {}
    for clip_id, n in normalize_index.items():
        ofn = (n.get("original_filename") or "").strip()
        if ofn:
            by_original_filename[ofn] = clip_id
    out: dict[str, str] = {}
    for clip_id, n in normalize_index.items():
        if not n.get("is_cut"):
            continue
        src_name = (n.get("source_clip_name") or "").strip()
        if not src_name:
            continue
        src_id = by_original_filename.get(src_name)
        if src_id:
            out[clip_id] = src_id
    return out


# ── Window-local face attribution (§1f) ───────────────────────────────────────

def _window_people(
    faces_json: dict | None,
    ws: float,
    we: float,
    *,
    vote_min: int,
) -> str:
    """Names whose detections fall inside [ws, we) and clear `vote_min`.

    Returns CSV (sorted) for Chroma metadata. With FACE_VOTE_MIN=1 every
    named detection in the window counts; tail-window under-tag accepted
    by §1f trade-off.
    """
    if not faces_json:
        return ""
    counts: dict[str, int] = {}
    for d in faces_json.get("detections") or []:
        try:
            t = float(d.get("frame_t_s", -1.0))
        except (TypeError, ValueError):
            continue
        if not (ws <= t < we):
            continue
        name = d.get("matched_name")
        if not name:
            continue
        counts[name] = counts.get(name, 0) + 1
    return ",".join(sorted(n for n, c in counts.items() if c >= vote_min))


# ── User overlay scope (§1g stub) ─────────────────────────────────────────────

def _window_user_state(clip_user_state: dict, window_start_s: float) -> dict:
    """Resolve user-overlay state for one window.

    v2-task-5 stub: clip-level state applies uniformly to every window of the
    clip. Task 8 will plug per-window overrides keyed on `window_start_s`
    (per §1g sketch). Signature stays stable across that change.
    """
    return clip_user_state


# ── Window-row construction ───────────────────────────────────────────────────

def _window_id(clip_id: str, window_start_s: float) -> str:
    return f"{clip_id}:{int(round(window_start_s * 1000))}"


def build_window_rows(
    *,
    library_root: Path,
    current_path: Path,
    normalize: dict,
    faces: dict | None,
    caption: dict,
    user_state: dict,
    existing_cluster_by_id: dict[str, int] | None = None,
) -> list[dict]:
    """Fan one captioned clip out to one row per window.

    Each row is `{"id", "embedding", "document", "metadata"}` — the four
    things `collection.upsert` needs. Embeddings come from the caption
    sidecar (sync never re-embeds). `cluster_id` is carried forward from
    `existing_cluster_by_id` when set; otherwise omitted (= null), to be
    written by the cluster op.
    """
    rel, location, event_path = _split_path_parts(library_root, current_path)
    existing_cluster_by_id = existing_cluster_by_id or {}

    rows: list[dict] = []
    for w in caption.get("windows") or []:
        try:
            ws = float(w["window_start_s"])
            we = float(w["window_end_s"])
        except (KeyError, TypeError, ValueError):
            log.warning("malformed window in %s — skipping", normalize.get("clip_id"))
            continue

        fields = w.get("fields") or {}
        desc = fields.get("description") or {}
        emb = w.get("embedding")
        if not emb:
            log.warning(
                "window %s @ %.3fs has no embedding — skipping",
                normalize.get("clip_id"), ws,
            )
            continue

        wid = _window_id(normalize["clip_id"], ws)
        us = _window_user_state(user_state, ws)
        people = _window_people(faces, ws, we, vote_min=config.FACE_VOTE_MIN)

        meta = {
            # Identity + grouping
            "window_id":           wid,
            "clip_id":             normalize["clip_id"],
            "window_start_s":      round(ws, 3),
            "window_end_s":        round(we, 3),
            # Path / display
            "clip_filename":       current_path.name,
            "relative_path":       rel,
            "location":            location,
            "event_path":          event_path,
            # Clip-level normalize carry-through
            "is_cut":              bool(normalize["is_cut"]) if normalize.get("is_cut") is not None else None,
            "source_clip_id":      normalize.get("source_clip_id") or None,
            "source_clip_name":    normalize.get("source_clip_name") or None,
            "capture_datetime_utc": normalize.get("capture_datetime_utc") or "",
            "duration_s":          normalize.get("duration_s"),
            # Window-scoped people
            "people":              people,
            # Caption fields (snippet display + filters)
            "description_subjects_action": desc.get("subjects_action") or "",
            "description_framing":         desc.get("framing") or "",
            "scene":                       fields.get("scene") or "",
            "vibe":                        fields.get("vibe") or "",
            "mood":                        fields.get("mood") or "",
            "energy_level":                fields.get("energy_level") or "",
            "scene_type":                  fields.get("scene_type") or "",
            "aesthetic_score":             fields.get("aesthetic_score"),
            "low_quality_samples":         bool(w.get("low_quality_samples", False)),
            # Cluster (carry forward; cluster op writes new ids)
            "cluster_id":          existing_cluster_by_id.get(wid),
            # User overlay
            "hidden":              bool(us.get("hidden", False)),
            "favorite":            bool(us.get("favorite", False)),
            "tags":                ",".join(us.get("tags") or []),
        }

        rows.append({
            "id":        wid,
            "embedding": list(emb),
            "document":  w.get("embed_text") or "",
            "metadata":  _scrub(meta),
        })

    return rows


# ── Sync driver ───────────────────────────────────────────────────────────────

@dataclass
class SyncSummary:
    clips_seen: int = 0
    clips_with_caption: int = 0
    rows_upserted: int = 0
    rows_deleted: int = 0
    clips_deleted: int = 0
    errored: int = 0
    skipped: int = 0
    notes: list[str] = field(default_factory=list)


def _load_existing_cluster_ids(collection) -> dict[str, int]:
    """Snapshot current `cluster_id` per window_id so re-upsert preserves it
    between cluster runs.
    """
    try:
        existing = collection.get(include=["metadatas"])
    except Exception as e:  # noqa: BLE001
        log.warning("could not read existing cluster ids: %s", e)
        return {}
    out: dict[str, int] = {}
    ids = existing.get("ids") or []
    metas = existing.get("metadatas") or []
    for wid, meta in zip(ids, metas):
        if not meta:
            continue
        cid = meta.get("cluster_id")
        if isinstance(cid, int):
            out[wid] = cid
    return out


def _existing_ids_for_clip(collection, clip_id: str) -> set[str]:
    """All window_ids currently in Chroma for one clip_id."""
    try:
        res = collection.get(where={"clip_id": clip_id}, include=[])
    except Exception as e:  # noqa: BLE001
        log.warning("could not enumerate rows for clip_id=%s: %s", clip_id, e)
        return set()
    return set(res.get("ids") or [])


def sync_library(library_root: Path, *, dry_run: bool = False) -> SyncSummary:
    """Reconcile ChromaDB against current library state.

    Reads normalize / faces / caption / user sidecars, walks the filesystem
    to locate each clip, fans every captioned clip out to one row per
    window, upserts. Deletes rows for clips whose files are gone or whose
    caption sidecar disappeared. End-of-sync stale scan drops any window_id
    not emitted in this run.
    """
    library_root = Path(library_root).resolve()
    summary = SyncSummary()

    # 1. Authoritative clip list = every normalize sidecar.
    normalize_index: dict[str, dict] = {}
    for clip_id, _ in sidecar.iter_sidecars(library_root, config.SIDECAR_NORMALIZE):
        n = sidecar.read_normalize(library_root, clip_id)
        if n is None:
            continue
        normalize_index[clip_id] = n

    # 2. Filesystem index by shortid (catches moves / slug-renames).
    fs_index = build_filesystem_index(library_root)

    # 3. Resolve cut → source_clip_id linkages once.
    src_resolution = _resolve_source_clip_ids(normalize_index)

    collection = None
    existing_cluster_by_id: dict[str, int] = {}
    if not dry_run:
        try:
            collection = get_collection(library_root)
            existing_cluster_by_id = _load_existing_cluster_ids(collection)
        except Exception as e:  # noqa: BLE001
            step_error(log, OP_NAME, str(library_root), f"chromadb init failed: {e}")
            raise

    # 4. Plan pass — assemble per-clip upserts + deletes without touching Chroma.
    seen_window_ids: set[str] = set()
    seen_clip_ids: set[str] = set()
    to_upsert_rows: list[dict] = []           # flat list of rows across all clips
    to_drop_stale_per_clip: list[tuple[str, set[str]]] = []  # (clip_id, stale_ids)
    to_delete_clips: list[tuple[str, str]] = []  # (clip_id, clip_filename)

    for clip_id, normalize in normalize_index.items():
        summary.clips_seen += 1
        seen_clip_ids.add(clip_id)

        try:
            short = identity.shortid(clip_id)
        except ValueError:
            log.warning("normalize sidecar has unexpected clip_id %s — skipping", clip_id)
            summary.skipped += 1
            continue

        current_path = fs_index.get(short)
        clip_filename = normalize.get("clip_filename") or clip_id

        if current_path is None:
            to_delete_clips.append((clip_id, clip_filename))
            continue

        caption = sidecar.read_caption(library_root, clip_id)
        if caption is None:
            # No partial rows in v2. If the clip already had window rows from
            # a prior captioned state but the sidecar is gone, drop them.
            if collection is not None:
                stale = _existing_ids_for_clip(collection, clip_id)
                if stale:
                    to_drop_stale_per_clip.append((clip_id, stale))
            continue

        summary.clips_with_caption += 1

        faces = sidecar.read_faces(library_root, clip_id)
        user_state = user.get_user_state(library_root, clip_id)

        if src_resolution.get(clip_id):
            normalize = dict(normalize)
            normalize["source_clip_id"] = src_resolution[clip_id]

        try:
            rows = build_window_rows(
                library_root=library_root,
                current_path=current_path,
                normalize=normalize,
                faces=faces,
                caption=caption,
                user_state=user_state,
                existing_cluster_by_id=existing_cluster_by_id,
            )
        except Exception as e:  # noqa: BLE001
            step_error(log, OP_NAME, clip_filename, f"row build failed: {e}")
            summary.errored += 1
            continue

        if not rows:
            log.warning("[%s] %s: caption sidecar produced 0 window rows", OP_NAME, clip_filename)
            continue

        new_ids = {r["id"] for r in rows}
        seen_window_ids.update(new_ids)
        to_upsert_rows.extend(rows)

        # Per-clip stale: window count may have shrunk on re-caption.
        if collection is not None:
            current_ids = _existing_ids_for_clip(collection, clip_id)
            stale = current_ids - new_ids
            if stale:
                to_drop_stale_per_clip.append((clip_id, stale))

    # Dry-run: log the plan and stop.
    if dry_run:
        for row in to_upsert_rows:
            step(log, OP_NAME, row["metadata"]["clip_filename"],
                 f"upsert {row['id']}")
            summary.rows_upserted += 1
        for clip_id, _ in to_delete_clips:
            step(log, OP_NAME, clip_id, "delete (not on disk)")
            summary.clips_deleted += 1
        for _, stale in to_drop_stale_per_clip:
            summary.rows_deleted += len(stale)
        log.info(
            "sync DRY-RUN: clips_seen=%d captioned=%d rows_upsert=%d "
            "rows_drop=%d clips_drop=%d errored=%d skipped=%d",
            summary.clips_seen, summary.clips_with_caption,
            summary.rows_upserted, summary.rows_deleted,
            summary.clips_deleted, summary.errored, summary.skipped,
        )
        return summary

    # 5. Delete clips whose files are gone (Chroma rows + every sidecar).
    for clip_id, clip_filename in to_delete_clips:
        step(log, OP_NAME, clip_filename, "delete (not on disk)")
        try:
            collection.delete(where={"clip_id": clip_id})
            summary.clips_deleted += 1
        except Exception as e:  # noqa: BLE001
            step_error(log, OP_NAME, clip_filename, f"chroma delete failed: {e}")
            summary.errored += 1
        for suffix in (
            config.SIDECAR_NORMALIZE,
            config.SIDECAR_FACES,
            config.SIDECAR_CAPTION,
            config.SIDECAR_ERROR,
            config.SIDECAR_USER,
        ):
            sidecar.delete_sidecar(library_root, clip_id, suffix)

    # 6. Drop stale window rows (caption gone, or window count shrank).
    for clip_id, stale in to_drop_stale_per_clip:
        try:
            collection.delete(ids=list(stale))
            summary.rows_deleted += len(stale)
            log.info("[%s] %s: removed %d stale window rows", OP_NAME, clip_id, len(stale))
        except Exception as e:  # noqa: BLE001
            step_error(log, OP_NAME, clip_id, f"chroma stale-window delete failed: {e}")
            summary.errored += 1

    # 7. Upsert in one batched call per clip group (Chroma handles batching
    #    internally; one call per clip keeps logs readable).
    by_clip: dict[str, list[dict]] = {}
    for row in to_upsert_rows:
        by_clip.setdefault(row["metadata"]["clip_id"], []).append(row)
    for clip_id, rows in by_clip.items():
        fname = rows[0]["metadata"]["clip_filename"]
        try:
            collection.upsert(
                ids=[r["id"] for r in rows],
                embeddings=[r["embedding"] for r in rows],
                documents=[r["document"] for r in rows],
                metadatas=[r["metadata"] for r in rows],
            )
            summary.rows_upserted += len(rows)
            step(log, OP_NAME, fname, f"upsert {len(rows)} window rows")
        except Exception as e:  # noqa: BLE001
            step_error(log, OP_NAME, fname, f"chroma upsert failed: {e}")
            summary.errored += 1

    # 8. End-of-sync stale scan — drop any window_id we didn't emit and
    #    didn't already drop above. Handles edge cases like orphan rows
    #    whose clip_id has no normalize sidecar anymore.
    try:
        existing = collection.get(include=[])
        existing_ids = set(existing.get("ids") or [])
    except Exception as e:  # noqa: BLE001
        step_error(log, OP_NAME, str(library_root), f"chroma scan failed: {e}")
        existing_ids = set()
    orphan = existing_ids - seen_window_ids
    # Already-deleted-this-run ids may overlap; collection.delete is idempotent.
    if orphan:
        try:
            collection.delete(ids=list(orphan))
            summary.rows_deleted += len(orphan)
            log.info("[%s] removed %d orphan window rows", OP_NAME, len(orphan))
        except Exception as e:  # noqa: BLE001
            step_error(log, OP_NAME, str(library_root),
                       f"orphan delete failed: {e}")
            summary.errored += 1

    log.info(
        "sync summary: clips_seen=%d captioned=%d rows_upsert=%d "
        "rows_drop=%d clips_drop=%d errored=%d skipped=%d",
        summary.clips_seen, summary.clips_with_caption,
        summary.rows_upserted, summary.rows_deleted,
        summary.clips_deleted, summary.errored, summary.skipped,
    )
    return summary


# ── Query helpers ─────────────────────────────────────────────────────────────

def _cosine_similarity(a, b) -> float:
    """Cosine similarity between two raw vectors."""
    import numpy as np
    av = np.asarray(a, dtype=np.float32)
    bv = np.asarray(b, dtype=np.float32)
    na = float(np.linalg.norm(av))
    nb = float(np.linalg.norm(bv))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return float(np.dot(av, bv) / (na * nb))


def query(
    library_root: Path,
    text: str,
    *,
    top_k: int = 10,
    include_hidden: bool = False,
    where: dict | None = None,
) -> list[dict]:
    """Embed `text` and return raw top-k window hits.

    Each hit is `{window_id, clip_id, distance, metadata, document}`. Used
    internally by `query_with_merge`; UI callers should prefer that wrapper
    so adjacent windows collapse per §1c.
    """
    if not text or not text.strip():
        return []
    collection = get_collection(library_root)
    try:
        emb = embed_text(text)
    except Exception as e:  # noqa: BLE001
        log.error("query embed failed: %s", e)
        return []
    kwargs: dict = {
        "query_embeddings": [emb],
        "n_results": top_k,
        "include": ["metadatas", "documents", "distances"],
    }
    merged_where: dict = {}
    if not include_hidden:
        merged_where["hidden"] = False
    if where:
        merged_where.update(where)
    if merged_where:
        kwargs["where"] = merged_where
    try:
        res = collection.query(**kwargs)
    except Exception as e:  # noqa: BLE001
        log.error("chroma query failed: %s", e)
        return []
    ids = (res.get("ids") or [[]])[0]
    distances = (res.get("distances") or [[]])[0]
    metadatas = (res.get("metadatas") or [[]])[0]
    documents = (res.get("documents") or [[]])[0]
    out = []
    for wid, dist, meta, doc in zip(ids, distances, metadatas, documents):
        meta = meta or {}
        out.append({
            "window_id": wid,
            "clip_id":   meta.get("clip_id", wid.split(":", 1)[0]),
            "distance":  dist,
            "metadata":  meta,
            "document":  doc or "",
        })
    return out


# ── Adjacent-merge query (§1c locked T=0.78) ──────────────────────────────────

def _merge_adjacent_hits(
    hits: list[dict],
    embeddings_by_id: dict[str, list],
    threshold: float,
) -> list[dict]:
    """Collapse temporally-adjacent hits in the same clip whose pairwise
    cosine similarity ≥ `threshold` into single ranges. §1c locked algorithm.

    Adjacency = `window_start_s` of hit B equals `window_end_s` of hit A
    (within 0.01s). Hits that skip a window in the underlying clip do NOT
    merge across the gap — keeps "merged range" semantically equivalent to
    "continuous block of matching consecutive windows."
    """
    by_clip: dict[str, list[dict]] = {}
    for h in hits:
        by_clip.setdefault(h["clip_id"], []).append(h)

    ranges: list[dict] = []
    for _, clip_hits in by_clip.items():
        clip_hits.sort(key=lambda h: float((h["metadata"] or {}).get("window_start_s") or 0.0))

        current: dict | None = None

        def _start(h: dict) -> dict:
            meta = h["metadata"] or {}
            return {
                "clip_id":           h["clip_id"],
                "start_s":           float(meta.get("window_start_s") or 0.0),
                "end_s":             float(meta.get("window_end_s") or 0.0),
                "best_distance":     float(h["distance"]) if h.get("distance") is not None else 1.0,
                "best_window_id":    h["window_id"],
                "best_metadata":     meta,
                "best_document":     h.get("document") or "",
                "constituent_ids":   [h["window_id"]],
                "constituent_metas": [meta],
                "_last_window_id":   h["window_id"],
            }

        def _extend(rng: dict, h: dict) -> None:
            meta = h["metadata"] or {}
            rng["end_s"] = float(meta.get("window_end_s") or rng["end_s"])
            rng["constituent_ids"].append(h["window_id"])
            rng["constituent_metas"].append(meta)
            dist = float(h["distance"]) if h.get("distance") is not None else 1.0
            if dist < rng["best_distance"]:
                rng["best_distance"] = dist
                rng["best_window_id"] = h["window_id"]
                rng["best_metadata"] = meta
                rng["best_document"] = h.get("document") or ""
            rng["_last_window_id"] = h["window_id"]

        for h in clip_hits:
            if current is None:
                current = _start(h)
                continue

            this_start = float((h["metadata"] or {}).get("window_start_s") or 0.0)
            is_adjacent = abs(this_start - current["end_s"]) < 0.01

            merge = False
            if is_adjacent:
                emb_prev = embeddings_by_id.get(current["_last_window_id"])
                emb_this = embeddings_by_id.get(h["window_id"])
                if emb_prev is not None and emb_this is not None:
                    sim = _cosine_similarity(emb_prev, emb_this)
                    if sim >= threshold:
                        merge = True

            if merge:
                _extend(current, h)
            else:
                ranges.append(current)
                current = _start(h)

        if current is not None:
            ranges.append(current)

    for r in ranges:
        r.pop("_last_window_id", None)
    return ranges


def query_with_merge(
    library_root: Path,
    text: str,
    *,
    top_k: int = 10,
    include_hidden: bool = False,
    where: dict | None = None,
) -> list[dict]:
    """Embed `text`, fetch K × multiplier raw hits, collapse adjacent
    intra-clip hits per §1c (T=0.78), return the top-K merged ranges.

    Each range is:
        {
          "clip_id", "start_s", "end_s",
          "best_distance",      # lowest distance among constituents
          "best_window_id",     # representative for thumbnail / metadata
          "best_metadata",      # snippet display fields
          "best_document",      # embed_text of the representative
          "constituent_ids":   [window_id, …],
          "constituent_metas": [meta, …],
          "n_windows": int,
        }

    On embedding-fetch failure (transient Chroma error) the function
    degrades to singleton ranges — no merge attempted, behavior collapses
    to basic top-K. UI contract stays intact either way.
    """
    if not text or not text.strip():
        return []
    multiplier = int(getattr(config, "QUERY_INTERNAL_K_MULTIPLIER", 3))
    internal_k = max(top_k, top_k * multiplier)
    hits = query(
        library_root, text,
        top_k=internal_k, include_hidden=include_hidden, where=where,
    )
    if not hits:
        return []

    embeddings_by_id: dict[str, list] = {}
    try:
        collection = get_collection(library_root)
        hit_ids = [h["window_id"] for h in hits]
        data = collection.get(ids=hit_ids, include=["embeddings"])
        # `embeddings` is an ndarray in chromadb >=0.5 → don't `or []` it.
        emb_ids = data.get("ids") or []
        emb_vecs = data.get("embeddings")
        if emb_vecs is None:
            emb_vecs = []
        for wid, vec in zip(emb_ids, emb_vecs):
            if vec is not None:
                embeddings_by_id[wid] = vec
    except Exception as e:  # noqa: BLE001
        log.warning("query merge: embedding fetch failed (%s) — returning raw top-K", e)
        ranges = []
        for h in hits:
            meta = h["metadata"] or {}
            ranges.append({
                "clip_id":           h["clip_id"],
                "start_s":           float(meta.get("window_start_s") or 0.0),
                "end_s":             float(meta.get("window_end_s") or 0.0),
                "best_distance":     float(h["distance"]) if h.get("distance") is not None else 1.0,
                "best_window_id":    h["window_id"],
                "best_metadata":     meta,
                "best_document":     h.get("document") or "",
                "constituent_ids":   [h["window_id"]],
                "constituent_metas": [meta],
                "n_windows":         1,
            })
        return ranges[:top_k]

    ranges = _merge_adjacent_hits(
        hits, embeddings_by_id,
        threshold=float(config.ADJACENT_MERGE_THRESHOLD),
    )
    for r in ranges:
        r["n_windows"] = len(r["constituent_ids"])
    ranges.sort(key=lambda r: r["best_distance"])
    return ranges[:top_k]


# ── Single-clip metadata refresh (no re-embed) ────────────────────────────────

def update_one_metadata(library_root: Path, clip_id: str) -> bool:
    """Refresh every window row for one clip from current sidecars + filesystem.

    Used by user-state edits — embeddings don't change, so `collection.update`
    rewrites metadata only. Returns True iff the rows were updated.
    """
    library_root = Path(library_root).resolve()
    normalize = sidecar.read_normalize(library_root, clip_id)
    if normalize is None:
        return False

    fs_index = build_filesystem_index(library_root)
    try:
        short = identity.shortid(clip_id)
    except ValueError:
        return False
    current_path = fs_index.get(short)
    if current_path is None:
        return False

    caption = sidecar.read_caption(library_root, clip_id)
    if caption is None:
        return False  # no rows to update

    faces = sidecar.read_faces(library_root, clip_id)
    user_state = user.get_user_state(library_root, clip_id)

    src_resolution = _resolve_source_clip_ids({clip_id: normalize})
    if src_resolution.get(clip_id):
        normalize = dict(normalize)
        normalize["source_clip_id"] = src_resolution[clip_id]

    collection = get_collection(library_root)
    existing_cluster_by_id = _load_existing_cluster_ids(collection)

    rows = build_window_rows(
        library_root=library_root,
        current_path=current_path,
        normalize=normalize,
        faces=faces,
        caption=caption,
        user_state=user_state,
        existing_cluster_by_id=existing_cluster_by_id,
    )
    if not rows:
        return False

    try:
        collection.update(
            ids=[r["id"] for r in rows],
            metadatas=[r["metadata"] for r in rows],
        )
    except Exception as e:  # noqa: BLE001
        log.warning("update_one_metadata fallback for %s: %s — full upsert", clip_id, e)
        try:
            collection.upsert(
                ids=[r["id"] for r in rows],
                embeddings=[r["embedding"] for r in rows],
                documents=[r["document"] for r in rows],
                metadatas=[r["metadata"] for r in rows],
            )
        except Exception as e2:  # noqa: BLE001
            log.error("update_one_metadata upsert fallback also failed: %s", e2)
            return False
    return True


def collection_stats(library_root: Path) -> dict:
    """Small summary stats for the UI status strip."""
    try:
        collection = get_collection(library_root)
        n = collection.count()
    except Exception:
        n = 0
    return {"total_rows": n}
