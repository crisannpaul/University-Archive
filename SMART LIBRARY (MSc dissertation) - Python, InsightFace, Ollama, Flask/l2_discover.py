"""Walk a Smart Library, classify clips, drive per-clip normalize.

Spec reference: "Pipeline order" steps 1–7 + the Capture-datetime priority.

The discover op walks the library root, skipping hidden directories (.cache,
.chroma_db, anything else dotted) and the global `People/` folder. Each
candidate clip (`.MP4` / `.mov`) is then normalized:

    1. ffprobe
    2. resolve capture_datetime_utc  (container → DJI filename → mtime)
    3. sanitize (LC-native phantom remux, idempotent)
    4. thumbnail (embed attached_pic poster, idempotent)
    5. hash → clip_id
    6. rename → {date}_{shortid}.MP4 (idempotent, slug preserved if matching)
    7. sync mtime ← capture_datetime_utc
    8. write .normalize.json sidecar (Layer 2 extension — see build-order)

Failures during any step write `.error.json` keyed by clip_id (or by a
filename-stable fallback id when hashing itself failed) and the loop continues.
"""

from __future__ import annotations

import json
import os
import subprocess
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path

import l1_config as config
import l1_filename as fn
import l1_identity as identity
import l1_sidecar as sidecar
import l2_rename as rename_mod
import l2_sanitize as sanitize
import l2_thumbnail as thumbnail
from l1_logger import get_logger, step, step_error

log = get_logger("discover")

VIDEO_EXTS = (".mp4", ".mov")
OP_NAME = "normalize"


# ── ffprobe wrapper ───────────────────────────────────────────────────────────

def ffprobe(path: Path) -> dict:
    """Return parsed `ffprobe -show_format -show_streams` JSON.

    Raises subprocess.CalledProcessError on ffprobe failure or
    json.JSONDecodeError on parse failure (caller catches both).
    """
    result = subprocess.run(
        [
            "ffprobe",
            "-v", "error",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


# ── Capture datetime resolution ───────────────────────────────────────────────

def _parse_iso_utc(s: str) -> datetime | None:
    """Parse an ffprobe ISO-8601 string into a UTC-aware datetime, or None."""
    if not s:
        return None
    s = s.strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _container_creation_time(probe: dict) -> datetime | None:
    """Pull `creation_time` from format tags first, then any stream's tags."""
    fmt_tags = (probe.get("format") or {}).get("tags") or {}
    dt = _parse_iso_utc(fmt_tags.get("creation_time"))
    if dt is not None:
        return dt
    for s in probe.get("streams") or []:
        tags = s.get("tags") or {}
        dt = _parse_iso_utc(tags.get("creation_time"))
        if dt is not None:
            return dt
    return None


@dataclass
class CaptureDatetime:
    utc: datetime
    source: str           # "container" / "filename" / "mtime"
    confidence: str       # "high" / "low"
    local_filename: datetime | None = None


def resolve_capture_datetime(path: Path, parsed: fn.ParsedFilename, probe: dict) -> CaptureDatetime | None:
    """Walk the spec's source-priority chain. Returns None if nothing usable."""
    # 1. Container creation_time — the authoritative source.
    ct = _container_creation_time(probe)
    if ct is not None:
        local_dji = fn.dji_filename_local_datetime(parsed.original_filename)
        return CaptureDatetime(utc=ct, source="container", confidence="high", local_filename=local_dji)

    # 2. DJI raw filename embedded YYYYMMDDHHMMSS — local time, low confidence.
    local_dji = fn.dji_filename_local_datetime(parsed.original_filename)
    if local_dji is not None:
        offset = config.LIBRARY_TIMEZONE_OFFSET
        if offset is None:
            # No offset configured: treat camera-local as UTC. Low confidence.
            utc = local_dji.replace(tzinfo=timezone.utc)
        else:
            tz = timezone(timedelta(hours=offset))
            utc = local_dji.replace(tzinfo=tz).astimezone(timezone.utc)
        return CaptureDatetime(utc=utc, source="filename", confidence="low", local_filename=local_dji)

    # 3. mtime — last resort, low confidence.
    try:
        mt = path.stat().st_mtime
    except OSError:
        return None
    utc = datetime.fromtimestamp(mt, tz=timezone.utc)
    return CaptureDatetime(utc=utc, source="mtime", confidence="low")


# ── Walker ────────────────────────────────────────────────────────────────────

def _should_skip_dir(name: str, parent: Path, library_root: Path) -> bool:
    if name.startswith("."):
        return True
    # `People/` is global at the library root only.
    if name == config.PEOPLE_DIR and Path(parent).resolve() == Path(library_root).resolve():
        return True
    return False


def iter_clips(library_root: Path):
    """Yield candidate clip paths under `library_root`.

    Skips hidden directories (anything starting with `.`), the top-level
    `People/` folder, and any file whose name starts with `.` (in-flight
    normalize temp files use that prefix).
    """
    library_root = Path(library_root)
    for dirpath, dirnames, filenames in os.walk(library_root):
        dirnames[:] = [
            d for d in dirnames
            if not _should_skip_dir(d, Path(dirpath), library_root)
        ]
        for f in filenames:
            if f.startswith("."):
                continue
            if not f.lower().endswith(VIDEO_EXTS):
                continue
            yield Path(dirpath) / f


# ── Per-clip normalize ────────────────────────────────────────────────────────

@dataclass
class NormalizeResult:
    path: Path                    # final path after rename
    clip_id: str | None = None
    shape: str | None = None
    capture: CaptureDatetime | None = None
    actions: list[str] = field(default_factory=list)
    skipped_reason: str | None = None
    error: str | None = None


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _build_normalize_sidecar(
    *,
    clip_id: str,
    final_path: Path,
    library_root: Path,
    parsed: fn.ParsedFilename,
    capture: CaptureDatetime,
    duration_s: float | None,
    actions: list[str],
) -> dict:
    rel = final_path.resolve().relative_to(Path(library_root).resolve()).as_posix()
    payload = {
        "clip_id": clip_id,
        "clip_filename": final_path.name,
        "original_path": rel,
        "original_filename": parsed.original_filename,
        "shape": parsed.shape,
        "is_cut": parsed.is_cut,
        "camera_brand": parsed.camera_brand,
        "camera_seq": parsed.camera_seq,
        "source_clip_name": parsed.source_clip_name,
        "capture_datetime_utc": capture.utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "capture_datetime_source": capture.source,
        "capture_datetime_confidence": capture.confidence,
        "duration_s": duration_s,
        "normalized_at": _now_iso(),
        "operations_applied": actions,
    }
    if capture.local_filename is not None:
        payload["capture_datetime_local_filename"] = capture.local_filename.strftime("%Y-%m-%dT%H:%M:%S")
    return payload


def normalize_clip(library_root: Path, clip_path: Path) -> NormalizeResult:
    """Run the discovery + normalize phase on a single clip.

    Idempotent. Catches all per-clip exceptions, writes `.error.json`, and
    returns a NormalizeResult with `error` set on failure.
    """
    library_root = Path(library_root)
    clip_path = Path(clip_path)
    result = NormalizeResult(path=clip_path)
    op = OP_NAME
    fname = clip_path.name
    # Capture the fallback id derived from the *input* filename so success
    # can clear any orphan .error.json from a prior failed run that died
    # before clip_id was known (e.g. failed at thumbnail step). Without this,
    # the orphan would persist forever — clear_error(library_root, clip_id)
    # only matches the real clip_id, which the prior failure never wrote.
    input_fallback_eid = _filename_fallback_id(fname)

    try:
        # 2. Classify.
        parsed = fn.parse(fname)
        result.shape = parsed.shape
        step(log, op, fname, f"classified as {parsed.shape}")

        # 1. (already done — we have the path) + ffprobe.
        try:
            probe = ffprobe(clip_path)
        except subprocess.CalledProcessError as e:
            err = (e.stderr or "").strip().splitlines()[-1] if e.stderr else "ffprobe failed"
            raise RuntimeError(f"ffprobe failed: {err}") from e
        except json.JSONDecodeError as e:
            raise RuntimeError(f"ffprobe returned invalid JSON: {e}") from e

        # 2b. Resolve capture datetime.
        capture = resolve_capture_datetime(clip_path, parsed, probe)
        if capture is None:
            step(log, op, fname, "skip — no parseable capture_datetime")
            result.skipped_reason = "no_capture_datetime"
            return result
        result.capture = capture

        # 3. Sanitize.
        if sanitize.needs_sanitize(parsed, probe):
            t0 = time.monotonic()
            sanitize.remux_in_place(clip_path)
            step(log, "sanitize", fname, "remuxed (phantom LC cut)", time.monotonic() - t0)
            result.actions.append("sanitize")
            probe = ffprobe(clip_path)
        else:
            step(log, "sanitize", fname, "skip (clean)")

        # 4. Thumbnail.
        if thumbnail.needs_thumbnail(probe):
            t0 = time.monotonic()
            duration = sanitize.format_duration_s(probe)
            thumbnail.attach_in_place(clip_path, duration_s=duration if duration is not None else 0.0)
            step(log, "thumbnail", fname, "attached_pic embedded", time.monotonic() - t0)
            result.actions.append("thumbnail")
            probe = ffprobe(clip_path)
        else:
            step(log, "thumbnail", fname, "skip (already attached)")

        duration_s = sanitize.format_duration_s(probe)

        # 5. Hash.
        t0 = time.monotonic()
        clip_id = identity.compute_clip_id(clip_path)
        step(log, "hash", fname, f"clip_id={clip_id}", time.monotonic() - t0)
        result.clip_id = clip_id

        # 6. Rename.
        try:
            new_path, did_rename = rename_mod.maybe_rename(clip_path, capture.utc, clip_id)
        except FileExistsError as e:
            raise RuntimeError(str(e)) from e
        if did_rename:
            step(log, "rename", fname, f"→ {new_path.name}")
            result.actions.append("rename")
            fname = new_path.name
        else:
            step(log, "rename", fname, "skip (already canonical)")
        result.path = new_path

        # 7. mtime sync.
        rename_mod.sync_mtime(new_path, capture.utc)
        step(log, "mtime", fname, f"synced ← {capture.utc.isoformat()}")
        result.actions.append("mtime_sync")

        # 8. Write normalize sidecar.
        payload = _build_normalize_sidecar(
            clip_id=clip_id,
            final_path=new_path,
            library_root=library_root,
            parsed=parsed,
            capture=capture,
            duration_s=duration_s,
            actions=result.actions,
        )
        sidecar.write_normalize(library_root, clip_id, payload)
        # Clear only normalize's own .error.json — never stomp another op's
        # failure record (e.g. a prior face/caption error on the same clip).
        sidecar.clear_error_if_op(library_root, clip_id, OP_NAME)
        # Also clear an orphan keyed by the input filename's fallback id, in
        # case the previous run died before clip_id was computed.
        if input_fallback_eid != clip_id:
            sidecar.clear_error_if_op(library_root, input_fallback_eid, OP_NAME)
        return result

    except Exception as e:  # noqa: BLE001 — catch-all is intentional per spec
        msg = f"{type(e).__name__}: {e}"
        step_error(log, op, fname, msg)
        # Use clip_id when known; fall back to a filename-derived stable id so
        # the .error.json doesn't collide across runs.
        eid = result.clip_id or _filename_fallback_id(fname)
        try:
            sidecar.write_error(
                library_root,
                eid,
                clip_filename=fname,
                operation=op,
                error=msg,
            )
        except OSError:
            pass
        result.error = msg
        return result


def _filename_fallback_id(name: str) -> str:
    """Stable id derived from a filename — used when hashing fails before clip_id."""
    import hashlib
    return "fnerr_" + hashlib.sha1(name.encode("utf-8")).hexdigest()[:12]


# ── Library-scope driver ──────────────────────────────────────────────────────

@dataclass
class NormalizeSummary:
    total: int = 0
    succeeded: int = 0
    skipped: int = 0
    errored: int = 0
    actions_total: dict = field(default_factory=dict)


def normalize_library(library_root: Path, scope: Path | None = None) -> NormalizeSummary:
    """Walk the library (or `scope` subpath) and normalize every clip serially.

    Returns a `NormalizeSummary`. Per-clip failures are isolated — a single
    bad clip never aborts the run.
    """
    library_root = Path(library_root).resolve()
    walk_root = Path(scope).resolve() if scope is not None else library_root

    summary = NormalizeSummary()
    for clip_path in iter_clips(walk_root):
        summary.total += 1
        res = normalize_clip(library_root, clip_path)
        if res.error is not None:
            summary.errored += 1
        elif res.skipped_reason is not None:
            summary.skipped += 1
        else:
            summary.succeeded += 1
        for a in res.actions:
            summary.actions_total[a] = summary.actions_total.get(a, 0) + 1

    log.info(
        "normalize summary: total=%d ok=%d skipped=%d errored=%d actions=%s",
        summary.total, summary.succeeded, summary.skipped, summary.errored,
        summary.actions_total,
    )
    return summary
