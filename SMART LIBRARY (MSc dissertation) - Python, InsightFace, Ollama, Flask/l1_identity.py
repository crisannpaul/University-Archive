"""Clip identity primitives: content hash, shortid, slug.

Spec references: "Clip identity", "Canonical naming contract → Slug rules".
"""

import hashlib
import re
import unicodedata
from pathlib import Path

import l1_config as config

_HASH_CHUNK = 1024 * 1024  # 1 MiB


def compute_clip_id(path: Path) -> str:
    """SHA-256 over the file bytes, truncated to `CLIP_ID_LEN` hex chars."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(_HASH_CHUNK)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()[: config.CLIP_ID_LEN]


def shortid(clip_id: str) -> str:
    """First `SHORTID_LEN` hex chars of a clip_id."""
    if len(clip_id) < config.SHORTID_LEN:
        raise ValueError(f"clip_id too short: {clip_id!r}")
    return clip_id[: config.SHORTID_LEN]


_SLUG_STRIP_RE = re.compile(r"[^a-z0-9]+")
_SLUG_COLLAPSE_RE = re.compile(r"-+")


def slugify(text: str, max_len: int = config.SLUG_MAX_LEN) -> str:
    """Lowercased, ascii-alphanumeric + hyphens, max_len chars (truncated at
    word boundary if possible). Returns "" if input is empty / un-sluggable."""
    if not text:
        return ""
    # Normalize unicode → ascii
    normalized = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    lowered = normalized.lower()
    hyphenated = _SLUG_STRIP_RE.sub("-", lowered)
    collapsed = _SLUG_COLLAPSE_RE.sub("-", hyphenated).strip("-")
    if not collapsed:
        return ""
    if len(collapsed) <= max_len:
        return collapsed
    truncated = collapsed[:max_len]
    # Prefer to break at a word boundary if one is reasonably close.
    last_hyphen = truncated.rfind("-")
    if last_hyphen >= max_len - 10 and last_hyphen > 0:
        truncated = truncated[:last_hyphen]
    return truncated.rstrip("-")
