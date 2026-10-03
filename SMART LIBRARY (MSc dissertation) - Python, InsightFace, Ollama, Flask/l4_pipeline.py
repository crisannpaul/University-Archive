"""Pipeline orchestration — per-scope, per-op runner (v2 window-level).

Operations exposed:
  - normalize     (Layer 2 walk: discover → sanitize → thumbnail → hash → rename)
  - face          (l3_scan_faces.scan_clip per clip — local insightface)
  - rematch       (l3_rematch_faces.rematch_clip per clip — cosine-only)
  - caption       (l3_scan_caption.scan_clip — Ollama VLM, dual-host §1k)
  - sync          (l4_sync.sync_library — window-row Chroma upserts, §1j)
  - cluster       (l4_cluster.cluster_pool — HDBSCAN, §1h, standalone per §1i)
  - apply-names   (l4_apply_names.apply_library)
  - run-all       (per clip: normalize → face → caption dual-host, then sync → cluster)

Scope levels: library (default), folder, single clip.

Resume / Force / Dry-run / Retry-errors:
  - Default: skip a clip if the relevant sidecar already exists.
  - `force=True`: ignore resume-skip and regenerate.
  - `dry_run=True`: walk + log, write nothing.
  - `retry_errors=True`: only run clips that have a `.error.json` for the op.

Concurrency (§1k locked 2026-05-20):
  - Face scan is local (insightface on CPU/iGPU) → serial on the driver host.
  - Caption is dispatched across `OLLAMA_HOSTS`. Startup probes each host
    (`GET /api/tags`); primary failure is fatal, secondary failures drop
    the host and continue single-host. Per-host 3-retry-with-backoff;
    cross-host failover on exhaustion; 3 consecutive errors trigger a
    re-probe and demote on failure.
  - Sync, cluster, normalize, apply-names — driver-local.
"""

from __future__ import annotations

import argparse
import sys
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from queue import Empty, Queue
from urllib.parse import urlparse

import requests

import l1_config as config
import l1_filename as fn
import l1_marker as marker
import l1_sidecar as sidecar
import l2_discover as discover
import l3_rematch_faces as rematch_faces
import l3_scan_caption as scan_caption
import l3_scan_faces as scan_faces
import l4_apply_names as apply_names
import l4_cluster as cluster
import l4_sync as sync
from l1_logger import get_logger, set_verbose, step, step_error

log = get_logger("pipeline")


OPS = ("normalize", "face", "rematch", "caption", "sync", "cluster",
       "apply-names", "run-all")


# ── Result envelope ───────────────────────────────────────────────────────────

@dataclass
class PipelineResult:
    op: str
    scope_path: str
    succeeded: int = 0
    skipped: int = 0
    errored: int = 0
    notes: list[str] = field(default_factory=list)
    sub_summaries: dict = field(default_factory=dict)


# ── Scope resolution ──────────────────────────────────────────────────────────

@dataclass
class Scope:
    library_root: Path
    walk_root: Path           # where to enumerate clips from
    single_clip: Path | None  # set iff scope is a single clip
    label: str                # "library" / "folder" / "clip"


def resolve_scope(library_root: Path, target: Path | None) -> Scope:
    library_root = Path(library_root).resolve()
    if target is None:
        return Scope(library_root, library_root, None, "library")
    target = Path(target).resolve()
    if target.is_file():
        return Scope(library_root, target.parent, target, "clip")
    if target.is_dir():
        if target == library_root:
            return Scope(library_root, library_root, None, "library")
        return Scope(library_root, target, None, "folder")
    raise FileNotFoundError(f"scope target does not exist: {target}")


# ── Helpers (clip enumeration / normalize tracking) ───────────────────────────

def _iter_scope_clips(scope: Scope):
    if scope.single_clip is not None:
        yield scope.single_clip
        return
    yield from discover.iter_clips(scope.walk_root)


def _shortid_from_canonical(name: str) -> str | None:
    parsed = fn.parse(name)
    if parsed.shape == fn.SHAPE_CANONICAL:
        return parsed.canonical_shortid.lower()
    return None


def _load_normalize_index(library_root: Path) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for clip_id, _ in sidecar.iter_sidecars(library_root, config.SIDECAR_NORMALIZE):
        n = sidecar.read_normalize(library_root, clip_id)
        if n:
            out[clip_id] = n
    return out


def _retry_error_ids(library_root: Path, op: str) -> list[str]:
    out: list[str] = []
    for clip_id, _ in sidecar.iter_sidecars(library_root, config.SIDECAR_ERROR):
        err = sidecar.read_error(library_root, clip_id)
        if err and err.get("operation") == op:
            out.append(clip_id)
    return out


def _ensure_normalized(scope: Scope, log_op: str) -> dict[str, Path]:
    """Make sure every clip in scope has a normalize sidecar; return
    `{clip_id: clip_path}` for enrichment.
    """
    normalize_index = _load_normalize_index(scope.library_root)

    pending: list[tuple[Path, str | None]] = []
    for clip_path in _iter_scope_clips(scope):
        short = _shortid_from_canonical(clip_path.name)
        clip_id = None
        if short:
            for cid in normalize_index.keys():
                if cid.startswith(short):
                    clip_id = cid
                    break
        pending.append((clip_path, clip_id))

    out: dict[str, Path] = {}
    for clip_path, clip_id in pending:
        if clip_id is not None and fn.parse(clip_path.name).shape == fn.SHAPE_CANONICAL:
            out[clip_id] = clip_path
            continue
        nr = discover.normalize_clip(scope.library_root, clip_path)
        if nr.error is not None or nr.clip_id is None:
            log.warning("[%s] %s: cannot enrich (normalize failed/skipped)",
                        log_op, clip_path.name)
            continue
        out[nr.clip_id] = nr.path
    return out


# ── Ollama host probing + labelling ───────────────────────────────────────────

def _host_label(host_url: str) -> str:
    label = config.OLLAMA_HOST_LABELS.get(host_url)
    if label:
        return label
    try:
        h = urlparse(host_url).hostname
        return h or host_url
    except Exception:
        return host_url


def _probe_host(host_url: str, *, timeout: float | None = None) -> tuple[bool, str]:
    """Returns `(ok, reason)`. `ok=True` iff host responds to `/api/tags` AND
    has both VLM_MODEL and EMBED_MODEL pulled.
    """
    if timeout is None:
        timeout = float(config.OLLAMA_PROBE_TIMEOUT_S)
    url = host_url.rstrip("/") + "/api/tags"
    try:
        resp = requests.get(url, timeout=timeout)
        resp.raise_for_status()
    except requests.RequestException as e:
        return False, f"unreachable: {e}"
    try:
        data = resp.json()
    except ValueError as e:
        return False, f"invalid /api/tags response: {e}"
    models = {(m or {}).get("name", "") for m in (data.get("models") or [])}
    required = {config.VLM_MODEL, config.EMBED_MODEL}
    missing = required - models
    if missing:
        return False, f"missing models: {sorted(missing)}"
    return True, "ok"


def probe_hosts() -> list[str]:
    """Probe every host in `OLLAMA_HOSTS`. Returns the list of alive hosts.

    Primary (`OLLAMA_HOSTS[0]`) failure raises — there's no fallback for it.
    Secondary failures are logged and dropped; the pipeline continues
    single-host. Empty active list raises.
    """
    if not config.OLLAMA_HOSTS:
        raise RuntimeError("OLLAMA_HOSTS is empty in l1_config.py")

    alive: list[str] = []
    for i, host in enumerate(config.OLLAMA_HOSTS):
        label = _host_label(host)
        ok, reason = _probe_host(host)
        if ok:
            log.info("[probe] %s (%s) → ok", label, host)
            alive.append(host)
        elif i == 0:
            raise RuntimeError(
                f"primary host {label!r} ({host}) failed startup probe: {reason}. "
                f"start Ollama and `ollama pull {config.VLM_MODEL}` + "
                f"`ollama pull {config.EMBED_MODEL}`, then retry."
            )
        else:
            log.warning("[probe] %s (%s) → drop: %s", label, host, reason)

    if not alive:
        raise RuntimeError("no Ollama hosts available")
    log.info("[probe] active hosts: %s", [_host_label(h) for h in alive])
    return alive


# ── Dual-host caption dispatcher (§1k) ────────────────────────────────────────

@dataclass
class _DispatcherState:
    alive_hosts: set[str]
    exhausted_by_clip: dict[str, set[str]]
    consecutive_errors: dict[str, int]
    in_flight: int
    lock: threading.Lock


def _backoff_seconds(attempt_idx: int) -> float:
    """`attempt_idx` is 0-based — the index of the FAILED attempt whose backoff
    precedes the next retry. List in config is reused; last value covers
    attempt indices past list length.
    """
    table = config.DUAL_HOST_BACKOFF_S
    if not table:
        return 2.0
    if attempt_idx >= len(table):
        return float(table[-1])
    return float(table[attempt_idx])


def _dispatch_caption(
    library_root: Path,
    clip_map: dict[str, Path],
    alive_hosts: list[str],
    *,
    force: bool,
) -> dict[str, scan_caption.CaptionResult]:
    """Drive per-clip captioning across `alive_hosts` via work-stealing.

    Single-host short-circuits the threading layer. Returns
    `{clip_id: CaptionResult}` for every clip in `clip_map` — clips that
    were stranded by host demotions are written to `.error.json` and
    surfaced in the result map as errored.
    """
    work_queue: Queue = Queue()
    for clip_id, clip_path in clip_map.items():
        work_queue.put((clip_id, clip_path))

    state = _DispatcherState(
        alive_hosts=set(alive_hosts),
        exhausted_by_clip={},
        consecutive_errors={h: 0 for h in alive_hosts},
        in_flight=0,
        lock=threading.Lock(),
    )

    results: dict[str, scan_caption.CaptionResult] = {}
    results_lock = threading.Lock()

    total = len(clip_map)
    per_host_done: dict[str, int] = {h: 0 for h in alive_hosts}
    per_host_lock = threading.Lock()

    def _try_clip(clip_id: str, clip_path: Path, host: str) -> scan_caption.CaptionResult | None:
        """Attempt this clip up to DUAL_HOST_RETRY_MAX times on `host`.
        Returns the result on success / terminal failure that should not
        retry, or None on host-exhaustion (caller decides cross-host failover).
        """
        label = _host_label(host)
        attempts = max(1, int(config.DUAL_HOST_RETRY_MAX))
        for attempt in range(attempts):
            try:
                r = scan_caption.scan_clip(
                    library_root, clip_path, clip_id,
                    force=force, host_url=host,
                )
            except Exception as e:  # noqa: BLE001
                # scan_clip swallows its own; an exception here is unexpected.
                log.error("[%s] %s: scan_clip raised: %s", label, clip_path.name, e)
                r = scan_caption.CaptionResult(clip_id=clip_id, error=str(e))

            if r.error is None:
                with state.lock:
                    state.consecutive_errors[host] = 0
                with per_host_lock:
                    per_host_done[host] += 1
                    n = per_host_done[host]
                tag = "skip" if r.skipped_reason else "ok"
                step(log, "caption",
                     f"[{label} {n}/{total}] {clip_path.name}",
                     tag)
                return r

            log.warning(
                "[%s] %s attempt %d/%d failed: %s",
                label, clip_path.name, attempt + 1, attempts, r.error,
            )

            with state.lock:
                state.consecutive_errors[host] += 1
                trip_reprobe = (
                    state.consecutive_errors[host]
                    >= int(config.DUAL_HOST_REPROBE_AFTER)
                )

            if trip_reprobe:
                ok, reason = _probe_host(host)
                if not ok:
                    log.error(
                        "[%s] re-probe failed after %d consecutive errors → "
                        "demoting host (%s)",
                        label, config.DUAL_HOST_REPROBE_AFTER, reason,
                    )
                    with state.lock:
                        state.alive_hosts.discard(host)
                    return None  # caller handles failover
                # Probe passed: this clip is poison, not the host.
                with state.lock:
                    state.consecutive_errors[host] = 0

            if attempt + 1 < attempts:
                time.sleep(_backoff_seconds(attempt))

        return None  # exhausted retries on this host

    def _worker(host: str) -> None:
        label = _host_label(host)
        while True:
            with state.lock:
                if host not in state.alive_hosts:
                    log.info("[%s] worker exiting (demoted)", label)
                    return

            try:
                clip_id, clip_path = work_queue.get(timeout=1.0)
            except Empty:
                with state.lock:
                    if state.in_flight == 0 and work_queue.empty():
                        return
                continue

            # Am I exhausted on this clip? Hand off if so.
            with state.lock:
                ex = state.exhausted_by_clip.get(clip_id, set())
                if host in ex:
                    can_others = any(
                        h in state.alive_hosts and h not in ex
                        for h in state.alive_hosts
                    )
                    if can_others:
                        work_queue.put((clip_id, clip_path))
                    # else: no one can help. Result already recorded when this
                    # host exhausted; just drop. (Shouldn't normally reach here.)
                if host in ex:
                    if can_others:
                        time.sleep(0.5)  # avoid spin if others are mid-clip
                    continue
                state.in_flight += 1

            try:
                result = _try_clip(clip_id, clip_path, host)
                if result is not None:
                    with results_lock:
                        results[clip_id] = result
                    continue

                # Exhausted on this host → cross-host failover
                with state.lock:
                    state.exhausted_by_clip.setdefault(clip_id, set()).add(host)
                    ex = state.exhausted_by_clip[clip_id]
                    can_others = any(
                        h in state.alive_hosts and h not in ex
                        for h in state.alive_hosts
                    )
                if can_others:
                    log.info(
                        "[%s] %s: failing over to another host",
                        label, clip_path.name,
                    )
                    work_queue.put((clip_id, clip_path))
                else:
                    msg = "all hosts exhausted"
                    step_error(log, "caption", clip_path.name, msg)
                    try:
                        sidecar.write_error(
                            library_root, clip_id,
                            clip_filename=clip_path.name,
                            operation="caption",
                            error=msg,
                        )
                    except OSError:
                        pass
                    with results_lock:
                        results[clip_id] = scan_caption.CaptionResult(
                            clip_id=clip_id, error=msg,
                        )
            finally:
                with state.lock:
                    state.in_flight -= 1

    # Single-host short-circuit
    if len(alive_hosts) == 1:
        host = alive_hosts[0]
        log.info("[caption] single-host mode → %s (%d clip(s))",
                 _host_label(host), total)
        _worker(host)
    else:
        log.info(
            "[caption] dual-host mode → %s (%d clip(s))",
            [_host_label(h) for h in alive_hosts], total,
        )
        threads = [
            threading.Thread(
                target=_worker, args=(host,),
                name=f"caption-{_host_label(host)}",
                daemon=False,
            )
            for host in alive_hosts
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

    # Drain stranded queue items — single-host run that lost its only host
    # leaves clips here with no result, and no future worker to consume them.
    while True:
        try:
            clip_id, clip_path = work_queue.get_nowait()
        except Empty:
            break
        if clip_id in results:
            continue
        msg = "no active host (all demoted before processing)"
        step_error(log, "caption", clip_path.name, msg)
        try:
            sidecar.write_error(
                library_root, clip_id,
                clip_filename=clip_path.name,
                operation="caption",
                error=msg,
            )
        except OSError:
            pass
        results[clip_id] = scan_caption.CaptionResult(clip_id=clip_id, error=msg)

    return results


# ── Per-op runners ────────────────────────────────────────────────────────────

def run_normalize(scope: Scope, *, force: bool = False, dry_run: bool = False, **_) -> PipelineResult:
    res = PipelineResult(op="normalize", scope_path=str(scope.walk_root))
    if dry_run:
        n = sum(1 for _ in _iter_scope_clips(scope))
        res.notes.append(f"dry-run: would normalize {n} clip(s)")
        return res
    if scope.single_clip is not None:
        nr = discover.normalize_clip(scope.library_root, scope.single_clip)
        if nr.error is not None:
            res.errored += 1
        elif nr.skipped_reason is not None:
            res.skipped += 1
        else:
            res.succeeded += 1
        res.sub_summaries["normalize"] = vars(nr)
        return res
    summary = discover.normalize_library(scope.library_root, scope=scope.walk_root)
    res.succeeded = summary.succeeded
    res.skipped = summary.skipped
    res.errored = summary.errored
    res.sub_summaries["normalize"] = vars(summary)
    return res


def run_face(
    scope: Scope,
    *,
    force: bool = False,
    dry_run: bool = False,
    retry_errors: bool = False,
) -> PipelineResult:
    res = PipelineResult(op="face", scope_path=str(scope.walk_root))
    library_root = scope.library_root

    clip_map = _ensure_normalized(scope, "face")
    if retry_errors:
        retry_ids = set(_retry_error_ids(library_root, "face"))
        clip_map = {k: v for k, v in clip_map.items() if k in retry_ids}

    if not clip_map:
        res.notes.append("no clips in scope")
        return res

    if dry_run:
        for clip_id, clip_path in clip_map.items():
            has = sidecar.has_sidecar(library_root, clip_id, config.SIDECAR_FACES)
            action = "skip (faces.json exists)" if has and not force else "scan"
            step(log, "face", clip_path.name, f"{action} (dry-run)")
            if has and not force:
                res.skipped += 1
            else:
                res.succeeded += 1
        return res

    app = scan_faces.get_face_analyzer()
    refs = scan_faces.load_references(library_root, app=app)

    for clip_id, clip_path in clip_map.items():
        sr = scan_faces.scan_clip(
            library_root, clip_path, clip_id,
            force=force, refs=refs, app=app,
        )
        if sr.error is not None:
            res.errored += 1
        elif sr.skipped_reason is not None:
            res.skipped += 1
        else:
            res.succeeded += 1
    return res


def run_rematch(
    scope: Scope,
    *,
    force: bool = False,
    dry_run: bool = False,
    retry_errors: bool = False,
) -> PipelineResult:
    res = PipelineResult(op="rematch", scope_path=str(scope.walk_root))
    library_root = scope.library_root

    cached_ids = {cid for cid, _ in sidecar.iter_sidecars(library_root, config.SIDECAR_FACES)}
    if scope.label != "library":
        scope_ids = set(_ensure_normalized(scope, "rematch").keys())
        ids = sorted(cached_ids & scope_ids)
    else:
        ids = sorted(cached_ids)

    if retry_errors:
        retry_ids = set(_retry_error_ids(library_root, "rematch"))
        ids = [i for i in ids if i in retry_ids]

    if not ids:
        res.notes.append("no faces.json in scope to rematch")
        return res

    if dry_run:
        for clip_id in ids:
            step(log, "rematch", clip_id, "rematch (dry-run)")
            res.succeeded += 1
        return res

    app = scan_faces.get_face_analyzer()
    refs = scan_faces.load_references(library_root, app=app)

    for clip_id in ids:
        rr = rematch_faces.rematch_clip(library_root, clip_id, refs=refs, app=app)
        if rr.error is not None:
            res.errored += 1
        elif rr.skipped_reason is not None:
            res.skipped += 1
        else:
            res.succeeded += 1
    return res


def run_caption(
    scope: Scope,
    *,
    force: bool = False,
    dry_run: bool = False,
    retry_errors: bool = False,
) -> PipelineResult:
    res = PipelineResult(op="caption", scope_path=str(scope.walk_root))
    library_root = scope.library_root

    clip_map = _ensure_normalized(scope, "caption")
    if retry_errors:
        retry_ids = set(_retry_error_ids(library_root, "caption"))
        clip_map = {k: v for k, v in clip_map.items() if k in retry_ids}

    if not clip_map:
        res.notes.append("no clips in scope")
        return res

    if dry_run:
        for clip_id, clip_path in clip_map.items():
            has = sidecar.has_sidecar(library_root, clip_id, config.SIDECAR_CAPTION)
            action = "skip (caption.json exists)" if has and not force else "caption"
            step(log, "caption", clip_path.name, f"{action} (dry-run)")
            if has and not force:
                res.skipped += 1
            else:
                res.succeeded += 1
        return res

    alive_hosts = probe_hosts()
    results = _dispatch_caption(
        library_root, clip_map, alive_hosts, force=force,
    )

    for r in results.values():
        if r.error is not None:
            res.errored += 1
        elif r.skipped_reason is not None:
            res.skipped += 1
        else:
            res.succeeded += 1

    missing = set(clip_map) - set(results)
    if missing:
        log.warning("[caption] %d clip(s) missing from results — counting as errored",
                    len(missing))
        res.errored += len(missing)

    return res


def run_sync(scope: Scope, *, dry_run: bool = False, **_) -> PipelineResult:
    """Sync reconciles the entire Chroma collection against filesystem state,
    so it's library-wide regardless of scope. v2 fans clips out to window rows.
    """
    res = PipelineResult(op="sync", scope_path=str(scope.library_root))
    summary = sync.sync_library(scope.library_root, dry_run=dry_run)
    res.succeeded = summary.rows_upserted
    res.skipped = summary.skipped
    res.errored = summary.errored
    res.notes.append(
        f"clips_seen={summary.clips_seen} captioned={summary.clips_with_caption} "
        f"rows_upserted={summary.rows_upserted} rows_deleted={summary.rows_deleted} "
        f"clips_deleted={summary.clips_deleted}"
    )
    res.sub_summaries["sync"] = vars(summary)
    return res


def run_cluster(scope: Scope, *, dry_run: bool = False, **_) -> PipelineResult:
    """Pool-scope HDBSCAN over every Chroma window row; writes `cluster_id`
    back per row. Scope is ignored — clustering is always library-wide (§1h).
    """
    res = PipelineResult(op="cluster", scope_path=str(scope.library_root))
    summary = cluster.cluster_pool(scope.library_root, dry_run=dry_run)
    if summary.skipped_reason and summary.rows_updated == 0:
        res.skipped = 1
        res.notes.append(f"skipped: {summary.skipped_reason}")
    else:
        res.succeeded = summary.rows_updated
        sil = (f"{summary.silhouette:.3f}"
               if summary.silhouette is not None else "n/a")
        res.notes.append(
            f"rows_scanned={summary.rows_scanned} "
            f"clustered={summary.rows_clustered} noise={summary.rows_noise} "
            f"n_clusters={summary.n_clusters} silhouette={sil}"
        )
    res.sub_summaries["cluster"] = vars(summary)
    return res


def run_apply_names(
    scope: Scope,
    *,
    force: bool = False,
    dry_run: bool = False,
    retry_errors: bool = False,
) -> PipelineResult:
    res = PipelineResult(op="apply-names", scope_path=str(scope.walk_root))
    library_root = scope.library_root

    if scope.label == "library":
        clip_ids = None
    else:
        clip_ids = list(_ensure_normalized(scope, "apply-names").keys())

    if retry_errors:
        retry_ids = set(_retry_error_ids(library_root, "apply_names"))
        if clip_ids is None:
            clip_ids = list(retry_ids)
        else:
            clip_ids = [c for c in clip_ids if c in retry_ids]

    summary = apply_names.apply_library(library_root, dry_run=dry_run, clip_ids=clip_ids)
    res.succeeded = summary.renamed
    res.skipped = summary.skipped + summary.unchanged
    res.errored = summary.errored
    res.notes.append(f"renamed={summary.renamed} unchanged={summary.unchanged}")
    res.sub_summaries["apply_names"] = vars(summary)
    return res


def run_all(
    scope: Scope,
    *,
    force: bool = False,
    dry_run: bool = False,
    retry_errors: bool = False,
) -> PipelineResult:
    """v2 chain: normalize → face (serial) → caption (dual-host §1k) → sync → cluster.

    Per-clip failures isolate. Sync + cluster run regardless of upstream
    errors so deletions reconcile and downstream rows update.
    """
    res = PipelineResult(op="run-all", scope_path=str(scope.walk_root))
    library_root = scope.library_root

    clip_map = _ensure_normalized(scope, "run-all")

    if retry_errors:
        retry_ids = (
            set(_retry_error_ids(library_root, "face")) |
            set(_retry_error_ids(library_root, "caption"))
        )
        clip_map = {k: v for k, v in clip_map.items() if k in retry_ids}

    if not clip_map:
        res.notes.append("no clips in scope")
        if not dry_run:
            sync_res = run_sync(scope, dry_run=False)
            res.sub_summaries["sync"] = sync_res.sub_summaries.get("sync")
            res.notes.extend(sync_res.notes)
            cluster_res = run_cluster(scope, dry_run=False)
            res.sub_summaries["cluster"] = cluster_res.sub_summaries.get("cluster")
            res.notes.extend(cluster_res.notes)
        return res

    if dry_run:
        for clip_id, clip_path in clip_map.items():
            step(log, "run-all", clip_path.name, "would run face → caption (dry-run)")
            res.succeeded += 1
        res.notes.append("dry-run: sync + cluster skipped")
        return res

    # Step 1 — face scan (serial, local insightface).
    app = scan_faces.get_face_analyzer()
    refs = scan_faces.load_references(library_root, app=app)
    for clip_id, clip_path in clip_map.items():
        scan_faces.scan_clip(
            library_root, clip_path, clip_id,
            force=force, refs=refs, app=app,
        )

    # Step 2 — caption (dual-host work-stealing).
    alive_hosts = probe_hosts()
    caption_results = _dispatch_caption(
        library_root, clip_map, alive_hosts, force=force,
    )
    for r in caption_results.values():
        if r.error is not None:
            res.errored += 1
        elif r.skipped_reason is not None:
            res.skipped += 1
        else:
            res.succeeded += 1

    # Step 3 — sync.
    sync_summary = sync.sync_library(library_root, dry_run=False)
    res.sub_summaries["sync"] = vars(sync_summary)
    res.notes.append(
        f"sync: rows_upserted={sync_summary.rows_upserted} "
        f"rows_deleted={sync_summary.rows_deleted} "
        f"clips_deleted={sync_summary.clips_deleted}"
    )

    # Step 4 — cluster (pool-scope, per §1i auto post-sync).
    cluster_summary = cluster.cluster_pool(library_root, dry_run=False)
    res.sub_summaries["cluster"] = vars(cluster_summary)
    if cluster_summary.skipped_reason and cluster_summary.rows_updated == 0:
        res.notes.append(f"cluster: skipped ({cluster_summary.skipped_reason})")
    else:
        sil = (f"{cluster_summary.silhouette:.3f}"
               if cluster_summary.silhouette is not None else "n/a")
        res.notes.append(
            f"cluster: n_clusters={cluster_summary.n_clusters} "
            f"noise={cluster_summary.rows_noise} silhouette={sil}"
        )
    return res


# ── Top-level dispatch ────────────────────────────────────────────────────────

_DISPATCH = {
    "normalize":    run_normalize,
    "face":         run_face,
    "rematch":      run_rematch,
    "caption":      run_caption,
    "sync":         run_sync,
    "cluster":      run_cluster,
    "apply-names":  run_apply_names,
    "run-all":      run_all,
}


def run(
    op: str,
    library_root: Path,
    *,
    target: Path | None = None,
    force: bool = False,
    dry_run: bool = False,
    retry_errors: bool = False,
) -> PipelineResult:
    """Public entry point used by the Flask UI and the CLI smoke harness."""
    op = op.lower()
    if op not in _DISPATCH:
        raise ValueError(f"unknown op: {op!r}; expected one of {sorted(_DISPATCH)}")

    library_root = Path(library_root).resolve()
    if not marker.is_library(library_root):
        raise RuntimeError(
            f"not a Smart Library root (no {config.MARKER_FILENAME} marker): {library_root}"
        )

    scope = resolve_scope(library_root, target)
    fn_runner = _DISPATCH[op]

    log.info("starting op=%s scope=%s force=%s dry_run=%s retry_errors=%s",
             op, scope.label, force, dry_run, retry_errors)
    return fn_runner(scope, force=force, dry_run=dry_run, retry_errors=retry_errors)


# ── CLI entrypoint ────────────────────────────────────────────────────────────

def _build_argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="python -m smart_library_v2.l4_pipeline",
        description="Smart Library v2 pipeline orchestrator (window-level).",
    )
    p.add_argument("op", choices=OPS, help="operation to run")
    p.add_argument("library_root", type=Path, help="Smart Library root directory")
    p.add_argument("--target", type=Path, default=None,
                   help="folder or single .MP4 to scope to (default: whole library)")
    p.add_argument("--force", action="store_true", help="bypass resume-skip")
    p.add_argument("--dry-run", action="store_true", help="walk + log only")
    p.add_argument("--retry-errors", action="store_true",
                   help="re-run only clips with a matching .error.json")
    p.add_argument("--verbose", action="store_true", help="DEBUG logging")
    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_argparser().parse_args(argv)
    if args.verbose:
        set_verbose(True)
    try:
        result = run(
            args.op,
            args.library_root,
            target=args.target,
            force=args.force,
            dry_run=args.dry_run,
            retry_errors=args.retry_errors,
        )
    except Exception as e:  # noqa: BLE001
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    print(
        f"[{result.op}] succeeded={result.succeeded} "
        f"skipped={result.skipped} errored={result.errored}"
    )
    for note in result.notes:
        print(f"  - {note}")
    return 0 if result.errored == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
