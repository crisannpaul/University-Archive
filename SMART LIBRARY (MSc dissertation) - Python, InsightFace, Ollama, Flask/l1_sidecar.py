"""Sidecar JSON I/O — atomic writes, hash-keyed flat cache.

Layout (per spec → "Sidecar storage — hash-keyed flat cache"):
    <library_root>/.cache/<clip_id>.faces.json
    <library_root>/.cache/<clip_id>.caption.json
    <library_root>/.cache/<clip_id>.error.json

Atomicity: every write goes to `<file>.tmp` first, then `os.replace()`. A
partial write never leaves a corrupt sidecar in place — sync and the UI both
read these and a half-written file would crash both.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

import l1_config as config


# ── JSON encoder tolerant of numpy + paths ────────────────────────────────────

class _SidecarEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, np.bool_):
            return bool(obj)
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, Path):
            return str(obj)
        return super().default(obj)


# ── Cache directory resolution ────────────────────────────────────────────────

def cache_dir(library_root: Path) -> Path:
    """Return the .cache/ path under the library root, creating it if needed."""
    p = Path(library_root) / config.CACHE_DIR
    p.mkdir(parents=True, exist_ok=True)
    return p


def sidecar_path(library_root: Path, clip_id: str, suffix: str) -> Path:
    """Build the full path for a sidecar.

    `suffix` is one of `config.SIDECAR_FACES` / `SIDECAR_CAPTION` / `SIDECAR_ERROR`.
    """
    return cache_dir(library_root) / f"{clip_id}.{suffix}"


# ── Atomic JSON write ─────────────────────────────────────────────────────────

def atomic_write_json(data: dict, path: Path) -> None:
    """Write JSON to `path` atomically: write `<path>.tmp`, then os.replace()."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, cls=_SidecarEncoder)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


# ── Generic sidecar read/write/delete ─────────────────────────────────────────

def read_sidecar(library_root: Path, clip_id: str, suffix: str) -> dict | None:
    """Return the parsed sidecar, or None if missing / unparseable."""
    p = sidecar_path(library_root, clip_id, suffix)
    if not p.is_file():
        return None
    try:
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def write_sidecar(library_root: Path, clip_id: str, suffix: str, data: dict) -> Path:
    """Atomically write a sidecar. Returns the final path."""
    p = sidecar_path(library_root, clip_id, suffix)
    atomic_write_json(data, p)
    return p


def delete_sidecar(library_root: Path, clip_id: str, suffix: str) -> bool:
    """Remove a sidecar if present. Returns True iff a file was deleted."""
    p = sidecar_path(library_root, clip_id, suffix)
    try:
        p.unlink()
        return True
    except FileNotFoundError:
        return False


def has_sidecar(library_root: Path, clip_id: str, suffix: str) -> bool:
    return sidecar_path(library_root, clip_id, suffix).is_file()


# ── Convenience wrappers per sidecar type ─────────────────────────────────────

def read_faces(library_root: Path, clip_id: str) -> dict | None:
    return read_sidecar(library_root, clip_id, config.SIDECAR_FACES)


def write_faces(library_root: Path, clip_id: str, data: dict) -> Path:
    return write_sidecar(library_root, clip_id, config.SIDECAR_FACES, data)


def read_caption(library_root: Path, clip_id: str) -> dict | None:
    return read_sidecar(library_root, clip_id, config.SIDECAR_CAPTION)


def write_caption(library_root: Path, clip_id: str, data: dict) -> Path:
    return write_sidecar(library_root, clip_id, config.SIDECAR_CAPTION, data)


def read_normalize(library_root: Path, clip_id: str) -> dict | None:
    return read_sidecar(library_root, clip_id, config.SIDECAR_NORMALIZE)


def write_normalize(library_root: Path, clip_id: str, data: dict) -> Path:
    return write_sidecar(library_root, clip_id, config.SIDECAR_NORMALIZE, data)


def read_user(library_root: Path, clip_id: str) -> dict | None:
    return read_sidecar(library_root, clip_id, config.SIDECAR_USER)


def write_user(library_root: Path, clip_id: str, data: dict) -> Path:
    return write_sidecar(library_root, clip_id, config.SIDECAR_USER, data)


def delete_user(library_root: Path, clip_id: str) -> bool:
    return delete_sidecar(library_root, clip_id, config.SIDECAR_USER)


def write_error(
    library_root: Path,
    clip_id: str,
    *,
    clip_filename: str,
    operation: str,
    error: str,
) -> Path:
    """Write an `.error.json` sidecar. Schema per spec → `.error.json`."""
    payload = {
        "clip_id": clip_id,
        "clip_filename": clip_filename,
        "operation": operation,
        "failed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "error": error,
    }
    return write_sidecar(library_root, clip_id, config.SIDECAR_ERROR, payload)


def read_error(library_root: Path, clip_id: str) -> dict | None:
    return read_sidecar(library_root, clip_id, config.SIDECAR_ERROR)


def clear_error(library_root: Path, clip_id: str) -> bool:
    """Remove `.error.json` after a successful retry. Returns True iff deleted."""
    return delete_sidecar(library_root, clip_id, config.SIDECAR_ERROR)


def clear_error_if_op(library_root: Path, clip_id: str, op: str) -> bool:
    """Remove `.error.json` only if its `operation` field matches `op`.

    Prevents cross-op clearing — e.g. face-failed → caption-succeeded must
    not erase the face failure record. Returns True iff a sidecar was deleted.
    """
    err = read_error(library_root, clip_id)
    if err is None:
        return False
    if err.get("operation") != op:
        return False
    return delete_sidecar(library_root, clip_id, config.SIDECAR_ERROR)


# ── Cache enumeration ─────────────────────────────────────────────────────────

def iter_sidecars(library_root: Path, suffix: str):
    """Yield (clip_id, path) for every sidecar of the given suffix in the cache."""
    cache = cache_dir(library_root)
    needle = f".{suffix}"
    for p in cache.iterdir():
        if not p.is_file():
            continue
        name = p.name
        if not name.endswith(needle):
            continue
        clip_id = name[: -len(needle)]
        yield clip_id, p
