"""LosslessCut phantom-cut detection + ffmpeg remux.

Spec reference: "Pipeline order → Sanitize (step 3)".

LosslessCut produces "lossless" cuts using MP4 `elst` (edit list) atoms. The
underlying `mdat` still holds the full source data — players honor the edit
list, but other tools may see the full source duration, sample phantom frames,
or transcribe phantom audio. `ffmpeg -c copy` honors the edit list and remuxes
only the playable window into a fresh container — no re-encode, ~seconds.

Detection: the file's filename shape is LosslessCut-native AND its stream
duration exceeds its format duration by more than `SANITIZE_DURATION_DELTA_S`
(format duration honors `elst`; stream duration does not). DJI raws never have
an `elst`, so they never trip this check — but we also short-circuit on shape.

Behaviour: in-place replacement (sanitized file overwrites the phantom).
`creation_time` and other tags are preserved via `-map_metadata 0`.

Idempotent: a clip already-clean is left untouched.
"""

from __future__ import annotations

import os
import subprocess
import uuid
from pathlib import Path

import l1_config as config
from l1_filename import ParsedFilename, SHAPE_LC_HHMMSS, SHAPE_LC_SEGN


# ── Probe helpers ─────────────────────────────────────────────────────────────

def format_duration_s(probe: dict) -> float | None:
    """Return the container's reported duration in seconds, or None."""
    fmt = probe.get("format") or {}
    dur = fmt.get("duration")
    if dur is None:
        return None
    try:
        return float(dur)
    except (TypeError, ValueError):
        return None


def video_stream_duration_s(probe: dict) -> float | None:
    """Return the longest video stream's raw duration in seconds, or None.

    Falls back to `tags.DURATION` when the stream has no top-level duration
    field (some MP4s, especially DJI exports, only report it as a tag).
    """
    longest: float | None = None
    for s in probe.get("streams") or []:
        if s.get("codec_type") != "video":
            continue
        # An attached_pic stream is a still poster — ignore it for duration.
        if (s.get("disposition") or {}).get("attached_pic") == 1:
            continue
        candidate: float | None = None
        if s.get("duration") is not None:
            try:
                candidate = float(s["duration"])
            except (TypeError, ValueError):
                pass
        if candidate is None:
            tags = s.get("tags") or {}
            d = tags.get("DURATION") or tags.get("duration")
            if d:
                candidate = _parse_hhmmss_duration(d)
        if candidate is None:
            continue
        if longest is None or candidate > longest:
            longest = candidate
    return longest


def _parse_hhmmss_duration(s: str) -> float | None:
    """Parse `HH:MM:SS.mmm` (and degenerate forms) → seconds."""
    s = s.strip()
    parts = s.split(":")
    try:
        if len(parts) == 3:
            h, m, sec = parts
            return int(h) * 3600 + int(m) * 60 + float(sec)
        if len(parts) == 2:
            m, sec = parts
            return int(m) * 60 + float(sec)
        if len(parts) == 1:
            return float(parts[0])
    except ValueError:
        return None
    return None


# ── Detection ─────────────────────────────────────────────────────────────────

def needs_sanitize(parsed: ParsedFilename, probe: dict) -> bool:
    """Return True iff this clip is a LosslessCut phantom that needs remux."""
    if parsed.shape not in (SHAPE_LC_HHMMSS, SHAPE_LC_SEGN):
        return False
    fmt_dur = format_duration_s(probe)
    stream_dur = video_stream_duration_s(probe)
    if fmt_dur is None or stream_dur is None:
        return False
    return (stream_dur - fmt_dur) > config.SANITIZE_DURATION_DELTA_S


# ── Remux in place ────────────────────────────────────────────────────────────

def remux_in_place(path: Path) -> None:
    """Run `ffmpeg -c copy` on the file and atomically replace it.

    Raises subprocess.CalledProcessError on ffmpeg failure (caller writes
    .error.json and continues to the next clip).
    """
    path = Path(path)
    tmp = path.with_name(f".sl-sanitize-{uuid.uuid4().hex[:8]}-{path.name}")
    try:
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-loglevel", "error",
                "-i", str(path),
                "-c", "copy",
                "-map_metadata", "0",
                "-movflags", "+faststart",
                str(tmp),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        os.replace(tmp, path)
    finally:
        # Best-effort cleanup if ffmpeg wrote a partial file before failing.
        if tmp.exists():
            try:
                tmp.unlink()
            except OSError:
                pass
