"""User overlay — per-clip curation state authored by the UI.

Spec reference: "User overlay (`.user.json`)".

Schema is `{hidden: bool, favorite: bool, tags: [str]}`. Absence of a sidecar
means default state for every field. Reset-to-default deletes the sidecar
instead of writing an all-defaults stub — keeps `.cache/` clean and preserves
the "absence = default" invariant the sync layer relies on.

Forward-compat: unknown fields read from disk are preserved when the sidecar
is re-written, so a future schema bump doesn't get erased by an older client.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import l1_identity as identity
import l1_sidecar as sidecar
from l1_logger import get_logger

log = get_logger("user")


# Canonical defaults. The sync layer applies the same defaults when no sidecar
# exists; both code paths must agree, so this dict is the single source.
DEFAULTS: dict = {
    "hidden": False,
    "favorite": False,
    "tags": [],
}

KNOWN_KEYS = frozenset(DEFAULTS.keys())


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def normalize_tags(tags) -> list[str]:
    """Canonicalize a list of user-supplied tag strings.

    Each tag is slugified (lowercase + ASCII alphanumeric + hyphens) using the
    same rules as filename slugs, deduped while preserving first-seen order,
    and empty results are dropped. Keeps the library's tag vocabulary tight —
    `"Golden Hour"`, `"golden-hour"`, and `"Golden  Hour "` all collapse to
    `"golden-hour"`.
    """
    if not tags:
        return []
    out: list[str] = []
    seen: set[str] = set()
    for t in tags:
        if not isinstance(t, str):
            continue
        slug = identity.slugify(t)
        if not slug or slug in seen:
            continue
        seen.add(slug)
        out.append(slug)
    return out


def _normalize_state(merged: dict) -> dict:
    """Coerce a raw sidecar dict into the typed user-state shape."""
    return {
        "hidden": bool(merged.get("hidden", DEFAULTS["hidden"])),
        "favorite": bool(merged.get("favorite", DEFAULTS["favorite"])),
        "tags": normalize_tags(merged.get("tags") or []),
    }


def get_user_state(library_root: Path, clip_id: str) -> dict:
    """Return the merged user state for a clip, applying defaults for any
    missing field. Always returns a dict — absence of the sidecar yields
    a fresh `DEFAULTS` copy.
    """
    sc = sidecar.read_user(library_root, clip_id) or {}
    return _normalize_state(sc)


def _validate_partial(partial: dict) -> None:
    bad = set(partial) - KNOWN_KEYS
    if bad:
        raise ValueError(f"unknown user-state keys: {sorted(bad)}")
    if "hidden" in partial and not isinstance(partial["hidden"], bool):
        raise ValueError("hidden must be a bool")
    if "favorite" in partial and not isinstance(partial["favorite"], bool):
        raise ValueError("favorite must be a bool")
    if "tags" in partial:
        tags = partial["tags"]
        if not isinstance(tags, list) or not all(isinstance(t, str) for t in tags):
            raise ValueError("tags must be a list of strings")


def set_user_state(
    library_root: Path,
    clip_id: str,
    *,
    clip_filename: str | None = None,
    **partial,
) -> dict:
    """Apply a partial update to a clip's user state.

    Any subset of `{hidden, favorite, tags}` may be passed. Fields not in the
    partial keep their existing values. Unknown future fields already on disk
    are preserved verbatim. If the resulting state equals every default, the
    sidecar is deleted instead of being written.

    Returns the merged user-state dict (typed, defaults applied).
    """
    _validate_partial(partial)

    existing = sidecar.read_user(library_root, clip_id) or {}
    merged = dict(existing)
    merged.update(partial)

    state = _normalize_state(merged)

    if state == DEFAULTS:
        if existing:
            sidecar.delete_user(library_root, clip_id)
            log.info("[user] %s: reset to default (sidecar deleted)", clip_id)
        return state

    if clip_filename is None:
        clip_filename = existing.get("clip_filename")
        if not clip_filename:
            n = sidecar.read_normalize(library_root, clip_id)
            clip_filename = (n or {}).get("clip_filename") or clip_id

    payload = dict(merged)  # preserves unknown future fields
    payload["clip_id"] = clip_id
    payload["clip_filename"] = clip_filename
    payload["updated_at"] = _now_iso()
    payload["hidden"] = state["hidden"]
    payload["favorite"] = state["favorite"]
    payload["tags"] = state["tags"]

    sidecar.write_user(library_root, clip_id, payload)
    log.info(
        "[user] %s: hidden=%s favorite=%s tags=%s",
        clip_id, state["hidden"], state["favorite"], state["tags"] or "∅",
    )
    return state
