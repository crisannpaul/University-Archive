"""Canonical rename + filesystem mtime sync.

Spec references: "Pipeline order → Rename (step 6)", "Filesystem metadata sync".

After hash:
  - Any non-canonical clip → renamed to `{date}_{shortid}.MP4`
  - Already canonical with the same shortid → no action (slug preserved)
  - Already canonical but shortid mismatch (file content changed) → renamed

After rename:
  - mtime ← capture_datetime_utc (so file browsers sort chronologically)
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

import l1_filename as fn
import l1_identity as identity


def canonical_target_name(
    capture_dt: datetime,
    clip_id: str,
    *,
    preserve_slug_from: str | None = None,
) -> str:
    """Build the desired canonical filename for a clip.

    If `preserve_slug_from` is an already-canonical filename whose shortid
    matches `clip_id`, its `_{desc-slug}` tail is carried into the new name.
    Otherwise the slug is dropped (the existing slug came from a stale caption).
    """
    date_str, time_str = fn.canonical_parts_from_datetime(capture_dt)
    short = identity.shortid(clip_id)
    slug: str | None = None
    if preserve_slug_from:
        parsed = fn.parse(preserve_slug_from)
        if (
            parsed.shape == fn.SHAPE_CANONICAL
            and parsed.canonical_shortid == short
            and parsed.canonical_slug
        ):
            slug = parsed.canonical_slug
    return fn.build_canonical(date_str, time_str, short, slug)


def maybe_rename(path: Path, capture_dt: datetime, clip_id: str) -> tuple[Path, bool]:
    """Rename to canonical if needed. Returns (final_path, did_rename).

    Idempotent: if the current filename already matches the target, returns
    (path, False) without touching the filesystem.
    """
    path = Path(path)
    target = canonical_target_name(capture_dt, clip_id, preserve_slug_from=path.name)
    if path.name == target:
        return path, False
    new_path = path.with_name(target)
    # If a clip with this exact target already exists in the same folder
    # (e.g. a duplicate copy), refuse to clobber. Caller logs + writes error.
    if new_path.exists():
        raise FileExistsError(f"rename target already exists: {new_path}")
    os.rename(path, new_path)
    return new_path, True


def sync_mtime(path: Path, capture_dt: datetime) -> None:
    """Set the file's atime + mtime to `capture_dt`. ctime is left alone."""
    if capture_dt.tzinfo is None:
        capture_dt = capture_dt.replace(tzinfo=timezone.utc)
    ts = capture_dt.timestamp()
    os.utime(path, (ts, ts))
