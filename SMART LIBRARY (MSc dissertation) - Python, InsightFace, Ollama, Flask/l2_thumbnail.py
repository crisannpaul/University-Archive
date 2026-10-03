"""Embed an `attached_pic` poster frame into the MP4 container.

Spec reference: "Pipeline order → Thumbnail (step 4)".

DJI app exports and many drone files ship without an embedded poster frame, so
file pickers fall back to a generic icon. We extract a JPG at 25% duration and
remux it into the MP4 as an `attached_pic` stream — universal, no re-encode of
the video itself, ~50 KB extra per clip.

Detection: probe streams for one with `disposition.attached_pic == 1`.
Idempotent + deterministic: same input always produces the same poster bytes,
so re-running on a clip that lost its thumbnail rebuilds the same hash.
"""

from __future__ import annotations

import os
import subprocess
import uuid

from pathlib import Path

import l1_config as config

# ── Detection ─────────────────────────────────────────────────────────────────

def has_attached_pic(probe: dict) -> bool:
    """True iff the probe shows any stream with disposition.attached_pic == 1."""
    for s in probe.get("streams") or []:
        if (s.get("disposition") or {}).get("attached_pic") == 1:
            return True
    return False


def needs_thumbnail(probe: dict) -> bool:
    return not has_attached_pic(probe)


# ── Attach in place ───────────────────────────────────────────────────────────

def _extract_poster(src: Path, at_s: float, jpg_out: Path) -> None:
    long_side = config.THUMBNAIL_LONG_SIDE
    # ffmpeg `scale=W:-1` keeps aspect ratio. Long-side selection without
    # knowing input orientation: use `force_original_aspect_ratio=decrease`
    # against a long_side x long_side bounding box.
    vf = f"scale='if(gt(iw,ih),{long_side},-1)':'if(gt(iw,ih),-1,{long_side})'"
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-loglevel", "error",
            "-ss", f"{at_s:.3f}",
            "-i", str(src),
            "-frames:v", "1",
            "-q:v", str(config.THUMBNAIL_JPEG_QUALITY),
            "-vf", vf,
            str(jpg_out),
        ],
        check=True,
        capture_output=True,
        text=True,
    )


def _remux_with_poster(src: Path, jpg: Path, dst: Path) -> None:
    """Remux source + JPG into a new MP4 with the JPG flagged as attached_pic.

    Stream selection: first video stream + all audio. Data streams (e.g. DJI's
    proprietary `djmd` telemetry and `dbgi` debug streams, whose codec ids map
    to "none" and can't be written back to MP4) and subtitles are dropped so
    this works uniformly across every camera in the library. Telemetry loss is
    acceptable — the pipeline doesn't consume it.
    """
    try:
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-loglevel", "error",
                "-i", str(src),
                "-i", str(jpg),
                "-map", "0:v:0",
                "-map", "0:a?",
                "-map", "1:v:0",
                "-c", "copy",
                "-map_metadata", "0",
                "-disposition:v:1", "attached_pic",
                str(dst),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        stderr = (e.stderr or "").strip() or "(no stderr)"
        raise RuntimeError(f"ffmpeg remux failed: {stderr}") from e


def attach_in_place(path: Path, duration_s: float) -> None:
    """Extract poster at 25% duration and remux as attached_pic, atomic in-place."""
    path = Path(path)
    if duration_s is None or duration_s <= 0:
        # Fall back to a small offset — clips with unknown duration are rare
        # enough that this won't be load-bearing.
        at_s = 1.0
    else:
        at_s = max(0.0, duration_s * config.THUMBNAIL_AT_PCT)

    suffix = uuid.uuid4().hex[:8]
    jpg_tmp = path.with_name(f".sl-thumb-{suffix}.jpg")
    mp4_tmp = path.with_name(f".sl-thumb-{suffix}-{path.name}")

    try:
        _extract_poster(path, at_s, jpg_tmp)
        _remux_with_poster(path, jpg_tmp, mp4_tmp)
        os.replace(mp4_tmp, path)
    finally:
        for tmp in (jpg_tmp, mp4_tmp):
            if tmp.exists():
                try:
                    tmp.unlink()
                except OSError:
                    pass
