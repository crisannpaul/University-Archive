"""Apply display names — append `_{desc-slug}` to canonical filenames.

Spec references: Operations table → "Apply display names", Canonical naming
contract → Slug rules, "Apply display names" rules ("Idempotent: clips
already carrying a slug are checked against the current `display_name` and
updated only if different").

Per spec, the leading 18 characters (`{date}_{shortid}`) are immutable —
this op only touches the optional `_{desc-slug}` tail. mtime is preserved
explicitly across the rename so chronological filesystem ordering survives.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

import l1_config as config
import l1_filename as fn
import l1_identity as identity
import l1_sidecar as sidecar
import l4_sync as sync
from l1_logger import get_logger, step, step_error

log = get_logger("apply_names")

OP_NAME = "apply_names"


@dataclass
class ApplyResult:
    clip_id: str
    old_name: str | None = None
    new_name: str | None = None
    skipped_reason: str | None = None
    error: str | None = None


def _derive_target_name(current_name: str, display_name: str) -> str | None:
    """Build the canonical filename with `_{slug}` appended from display_name.

    Returns None if the current filename is not canonical (apply_names refuses
    to rename a non-normalized clip — run normalize first). Returns the
    current name unchanged when the existing slug already matches.
    """
    parsed = fn.parse(current_name)
    if parsed.shape != fn.SHAPE_CANONICAL:
        return None
    slug = identity.slugify(display_name or "", config.SLUG_MAX_LEN)
    return fn.build_canonical(
        parsed.canonical_date,
        parsed.canonical_time,
        parsed.canonical_shortid,
        slug or None,
    )


def apply_clip(
    library_root: Path,
    clip_id: str,
    *,
    fs_index: dict[str, Path] | None = None,
    dry_run: bool = False,
) -> ApplyResult:
    """Apply (or refresh) the slug on a single clip's filename.

    Skips silently when the caption sidecar is missing or carries no
    `display_name`. Idempotent: a clip that already has the correct slug is
    a no-op.
    """
    library_root = Path(library_root)
    result = ApplyResult(clip_id=clip_id)

    caption = sidecar.read_caption(library_root, clip_id)
    if caption is None:
        result.skipped_reason = "no_caption"
        return result

    fields = caption.get("fields") or {}
    display_name = (fields.get("display_name") or "").strip()
    if not display_name:
        result.skipped_reason = "empty_display_name"
        return result

    # Resolve the current path on disk.
    if fs_index is None:
        fs_index = sync.build_filesystem_index(library_root)
    try:
        short = identity.shortid(clip_id)
    except ValueError:
        result.skipped_reason = "bad_clip_id"
        return result
    current_path = fs_index.get(short)
    if current_path is None:
        result.skipped_reason = "not_on_disk"
        return result

    result.old_name = current_path.name

    target = _derive_target_name(current_path.name, display_name)
    if target is None:
        result.skipped_reason = "not_canonical"
        log.warning("[%s] %s: skip (filename not canonical — run normalize first)",
                    OP_NAME, current_path.name)
        return result

    if target == current_path.name:
        result.skipped_reason = "slug_already_current"
        step(log, OP_NAME, current_path.name, "skip (slug already current)")
        return result

    new_path = current_path.with_name(target)

    if dry_run:
        step(log, OP_NAME, current_path.name, f"→ {target} (dry-run)")
        result.new_name = target
        return result

    if new_path.exists():
        msg = f"target already exists: {target}"
        step_error(log, OP_NAME, current_path.name, msg)
        result.error = msg
        return result

    try:
        # Preserve mtime explicitly (os.rename keeps it on most platforms but
        # we re-apply to be safe across SMB / CIFS / network shares).
        st = current_path.stat()
        os.rename(current_path, new_path)
        os.utime(new_path, (st.st_atime, st.st_mtime))
    except OSError as e:
        msg = f"rename failed: {e}"
        step_error(log, OP_NAME, current_path.name, msg)
        result.error = msg
        return result

    # Refresh the index so subsequent calls in the same batch find this clip.
    fs_index[short] = new_path
    result.new_name = target
    step(log, OP_NAME, result.old_name, f"→ {target}")
    return result


# ── Library-scope driver ──────────────────────────────────────────────────────

@dataclass
class ApplySummary:
    total: int = 0
    renamed: int = 0
    unchanged: int = 0
    skipped: int = 0
    errored: int = 0
    actions: list[tuple[str, str]] = field(default_factory=list)  # (old, new)


def apply_library(
    library_root: Path,
    *,
    dry_run: bool = False,
    clip_ids: list[str] | None = None,
) -> ApplySummary:
    """Apply slugs across the whole library (or a specific list of clip_ids).

    Walks every `*.caption.json` sidecar in `.cache/` (or the supplied list)
    and renames each clip whose filename's slug differs from its caption's
    `display_name`-derived slug.
    """
    library_root = Path(library_root).resolve()
    summary = ApplySummary()

    fs_index = sync.build_filesystem_index(library_root)

    if clip_ids is None:
        candidates: list[str] = [
            cid for cid, _ in sidecar.iter_sidecars(library_root, config.SIDECAR_CAPTION)
        ]
    else:
        candidates = list(clip_ids)

    for clip_id in candidates:
        summary.total += 1
        res = apply_clip(library_root, clip_id, fs_index=fs_index, dry_run=dry_run)
        if res.error is not None:
            summary.errored += 1
        elif res.skipped_reason == "slug_already_current":
            summary.unchanged += 1
        elif res.new_name and res.old_name and res.new_name != res.old_name:
            summary.renamed += 1
            summary.actions.append((res.old_name, res.new_name))
        else:
            summary.skipped += 1

    log.info(
        "apply_names summary: total=%d renamed=%d unchanged=%d skipped=%d errored=%d",
        summary.total, summary.renamed, summary.unchanged,
        summary.skipped, summary.errored,
    )
    return summary
