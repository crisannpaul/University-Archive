"""`.smart-library` marker file: read, write, init.

Spec reference: "Marker file `.smart-library`".
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import l1_config as config


def marker_path(library_root: Path) -> Path:
    return Path(library_root) / config.MARKER_FILENAME


def is_library(library_root: Path) -> bool:
    """True iff the marker file exists at the given root."""
    return marker_path(library_root).is_file()


def read_marker(library_root: Path) -> dict | None:
    """Return the parsed marker dict, or None if no marker is present."""
    p = marker_path(library_root)
    if not p.is_file():
        return None
    try:
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def write_marker(library_root: Path, root_name: str | None = None) -> dict:
    """Write a fresh marker file at `library_root`. Returns the written dict."""
    library_root = Path(library_root)
    library_root.mkdir(parents=True, exist_ok=True)
    payload = {
        "smart_library_version": config.SMART_LIBRARY_VERSION,
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "root_name": root_name or library_root.name,
    }
    with open(marker_path(library_root), "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    return payload


def init_library(library_root: Path) -> dict:
    """Initialize a library root: create marker if missing, ensure People/.

    Idempotent — re-running on an already-initialized library is a no-op for
    the marker (existing marker is preserved) but still ensures People/ exists.
    Returns the (existing or newly created) marker dict.
    """
    library_root = Path(library_root)
    library_root.mkdir(parents=True, exist_ok=True)
    (library_root / config.PEOPLE_DIR).mkdir(exist_ok=True)
    existing = read_marker(library_root)
    if existing is not None:
        return existing
    return write_marker(library_root)
