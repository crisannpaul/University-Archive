"""Rematch faces — cosine-only re-match against fresh `People/` centroids.

Spec reference: "Rematch faces op detail [v0]".

When the user adds, removes, or replaces a reference photo in `People/`,
running a full Face scan is wasteful — the slow part (RetinaFace +
ArcFace inference per frame) doesn't need to repeat. Rematch loads each
clip's existing `<clip_id>.faces.json`, re-cosines every detection's
stored 512-d embedding against newly-computed `People/` centroids, and
updates `matched_name` / `score` / `people` / `rematched_at` in place.

Cost: cosine-only, no GPU inference. Typical clip → milliseconds.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

import l1_config as config
import l1_sidecar as sidecar
import l3_scan_faces as scan_faces
from l1_logger import get_logger, step, step_error

log = get_logger("rematch_faces")

OP_NAME = "rematch"


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass
class RematchResult:
    clip_id: str
    skipped_reason: str | None = None
    error: str | None = None
    people: list[str] = field(default_factory=list)


def rematch_clip(
    library_root: Path,
    clip_id: str,
    *,
    refs: dict[str, np.ndarray] | None = None,
    app=None,
) -> RematchResult:
    """Re-tag a single clip's faces.json against fresh `People/` centroids.

    Detection bboxes, frame timestamps, and stored embeddings are NOT touched —
    only `matched_name`, `score`, `people`, and `rematched_at`.

    Skips (no error, no sidecar update) when the clip has no faces.json yet.
    """
    library_root = Path(library_root)
    result = RematchResult(clip_id=clip_id)

    faces = sidecar.read_faces(library_root, clip_id)
    if faces is None:
        result.skipped_reason = "no_faces_json"
        log.info("[%s] %s: skip (no faces.json)", OP_NAME, clip_id)
        return result

    fname = faces.get("clip_filename", clip_id)

    try:
        if refs is None:
            if app is None:
                app = scan_faces.get_face_analyzer()
            refs = scan_faces.load_references(library_root, app=app)

        t0 = time.monotonic()
        detections = faces.get("detections") or []
        rematched_n = 0
        for d in detections:
            emb = d.get("embedding")
            if emb is None:
                # Older sidecar shape without stored embeddings — leave alone.
                continue
            arr = np.asarray(emb, dtype=np.float32)
            matched, score = scan_faces._match(arr, refs)
            d["matched_name"] = matched
            d["score"] = round(score, 4)
            rematched_n += 1

        people = scan_faces._vote_people(detections)
        faces["detections"] = detections
        faces["people"] = people
        faces["rematched_at"] = _now_iso()

        sidecar.write_faces(library_root, clip_id, faces)
        sidecar.clear_error_if_op(library_root, clip_id, OP_NAME)
        elapsed = time.monotonic() - t0

        result.people = people
        step(
            log, OP_NAME, fname,
            f"{rematched_n}/{len(detections)} detections re-matched, people={people or '∅'}",
            elapsed,
        )
        return result

    except Exception as e:  # noqa: BLE001
        msg = f"{type(e).__name__}: {e}"
        step_error(log, OP_NAME, fname, msg)
        try:
            sidecar.write_error(
                library_root, clip_id,
                clip_filename=fname,
                operation=OP_NAME,
                error=msg,
            )
        except OSError:
            pass
        result.error = msg
        return result


# ── Library-scope driver ──────────────────────────────────────────────────────

@dataclass
class RematchSummary:
    total: int = 0
    succeeded: int = 0
    skipped: int = 0
    errored: int = 0


def rematch_library(library_root: Path) -> RematchSummary:
    """Re-embed `People/` once, then walk every faces.json sidecar in `.cache/`.

    The InsightFace model is loaded only to embed the (small) set of
    reference photos — no per-clip detection. Runtime scales with
    `len(detections)` summed across the library, not with the number of
    video frames.
    """
    library_root = Path(library_root).resolve()
    app = scan_faces.get_face_analyzer()
    refs = scan_faces.load_references(library_root, app=app)

    summary = RematchSummary()
    for clip_id, _ in sidecar.iter_sidecars(library_root, config.SIDECAR_FACES):
        summary.total += 1
        res = rematch_clip(library_root, clip_id, refs=refs, app=app)
        if res.error is not None:
            summary.errored += 1
        elif res.skipped_reason is not None:
            summary.skipped += 1
        else:
            summary.succeeded += 1

    log.info(
        "rematch summary: total=%d ok=%d skipped=%d errored=%d",
        summary.total, summary.succeeded, summary.skipped, summary.errored,
    )
    return summary
