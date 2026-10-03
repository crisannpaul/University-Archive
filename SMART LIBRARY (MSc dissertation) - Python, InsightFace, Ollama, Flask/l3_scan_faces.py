"""Face scan op — InsightFace detection + ArcFace embedding + reference matching.

Spec reference: "Face scan op detail — reference embeddings", `.faces.json`
schema, "Reference photos (`People/<name>/`)".

Reference embeddings are recomputed on every run (no cache, no stale-embedding
bugs — adding/removing a photo in `People/` always takes effect on the next
run). Per-detection 512-d ArcFace embeddings are stored inline in
`<clip_id>.faces.json` so the cheap `l3_rematch_faces` op can re-tag clips
when `People/` changes without re-running detection.

Detector + embedder: InsightFace `buffalo_l` (RetinaFace + ArcFace), CPU only.
Heavy import + model load (~5-10s) is hidden behind a process-wide lazy
singleton — multiple per-clip calls in the same library scope reuse it.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import cv2
import numpy as np

import l1_config as config
import l1_sidecar as sidecar
from l1_logger import get_logger, step, step_error

log = get_logger("scan_faces")

OP_NAME = "face"
IMAGE_EXTS = {".jpg", ".jpeg", ".png"}
DET_SIZE = (640, 640)
EMBEDDING_DIM = 512  # buffalo_l / ArcFace output dimensionality.


# ── InsightFace lazy singleton ────────────────────────────────────────────────

_app_singleton = None


def get_face_analyzer():
    """Return a process-wide InsightFace `FaceAnalysis` configured for CPU.

    Lazy: first call downloads + loads buffalo_l (~5-10s on Strix Halo CPU),
    subsequent calls return the same analyzer. `ctx_id=-1` selects CPU.
    """
    global _app_singleton
    if _app_singleton is None:
        from insightface.app import FaceAnalysis
        log.info("loading InsightFace %s on CPU…", config.FACE_DETECTOR)
        t0 = time.monotonic()
        app = FaceAnalysis(name=config.FACE_DETECTOR)
        app.prepare(ctx_id=-1, det_size=DET_SIZE)
        log.info("InsightFace ready (%.1fs)", time.monotonic() - t0)
        _app_singleton = app
    return _app_singleton


# ── Reference embedding ───────────────────────────────────────────────────────

def _largest_face(faces):
    return max(
        faces,
        key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1]),
    )


def load_references(library_root: Path, app=None) -> dict[str, np.ndarray]:
    """Walk `People/` and return `{name: L2-normalized identity centroid}`.

    Folder layout: `People/<name>/*.{jpg,jpeg,png}`. The folder name is the
    person's display name; image filenames inside don't matter. Per spec, the
    centroid is the L2-normalized mean of every valid photo's largest-face
    embedding. Photos with no detected face are skipped with a warning, and a
    person with no usable photos is dropped (the run does not fail).
    """
    if app is None:
        app = get_face_analyzer()

    people_dir = Path(library_root) / config.PEOPLE_DIR
    if not people_dir.is_dir():
        log.info("People/ not found under %s — no reference identities", library_root)
        return {}

    refs: dict[str, np.ndarray] = {}
    for sub in sorted(people_dir.iterdir()):
        if not sub.is_dir() or sub.name.startswith("."):
            continue
        name = sub.name
        embeddings: list[np.ndarray] = []
        for img_path in sorted(sub.iterdir()):
            if img_path.suffix.lower() not in IMAGE_EXTS:
                continue
            img = cv2.imread(str(img_path))
            if img is None:
                log.warning("ref skip — unreadable image: %s", img_path)
                continue
            faces = app.get(img)
            if not faces:
                log.warning("ref skip — no face detected: %s", img_path)
                continue
            face = _largest_face(faces)
            embeddings.append(np.asarray(face.normed_embedding, dtype=np.float32))
        if not embeddings:
            log.warning("ref skip — no usable photos for %s", name)
            continue
        mean = np.mean(np.stack(embeddings), axis=0)
        norm = float(np.linalg.norm(mean))
        if norm == 0.0:
            log.warning("ref skip — zero centroid for %s", name)
            continue
        refs[name] = (mean / norm).astype(np.float32)
        log.info(
            "ref loaded — %s (%d photo%s)",
            name, len(embeddings), "" if len(embeddings) == 1 else "s",
        )
    return refs


# ── Helpers ───────────────────────────────────────────────────────────────────

def _cosine(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity assuming both vectors are L2-normalized."""
    return float(np.dot(a, b))


def _sample_times(duration_s: float) -> list[float]:
    """Evenly-spaced sample timestamps at FACE_SAMPLE_FPS, capped to FACE_FRAMES_MAX."""
    if duration_s <= 0:
        return []
    n = int(duration_s * config.FACE_SAMPLE_FPS)
    n = min(max(n, 1), config.FACE_FRAMES_MAX)
    if duration_s <= 1.0 or n == 1:
        return [round(float(duration_s / 2), 3)]
    pad = min(0.2, duration_s * 0.1)
    return [round(float(t), 3)
            for t in np.linspace(pad, max(pad, duration_s - pad), n)]


def _match(emb: np.ndarray, refs: dict[str, np.ndarray]) -> tuple[str | None, float]:
    """Return `(matched_name_or_None, best_cosine_score)` against ref centroids."""
    if not refs:
        return None, -1.0
    best_name, best_score = None, -1.0
    for name, ref in refs.items():
        s = _cosine(emb, ref)
        if s > best_score:
            best_name, best_score = name, s
    matched = best_name if best_score >= config.FACE_MATCH_THRESHOLD else None
    return matched, best_score


def _vote_people(detections: list[dict]) -> list[str]:
    """Per spec: a person joins `people` only if ≥ FACE_VOTE_MIN frames matched."""
    votes: dict[str, int] = {}
    for d in detections:
        n = d.get("matched_name")
        if not n:
            continue
        votes[n] = votes.get(n, 0) + 1
    return sorted(n for n, c in votes.items() if c >= config.FACE_VOTE_MIN)


def _read_clip_duration(cap) -> float:
    fps = cap.get(cv2.CAP_PROP_FPS) or 0.0
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    return total / fps if fps > 0 else 0.0


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _relpath(clip_path: Path, library_root: Path) -> str:
    try:
        return clip_path.resolve().relative_to(Path(library_root).resolve()).as_posix()
    except ValueError:
        return str(clip_path)


# ── Per-clip scan ─────────────────────────────────────────────────────────────

@dataclass
class FaceScanResult:
    clip_id: str
    sidecar_path: Path | None = None
    skipped_reason: str | None = None
    error: str | None = None
    detections: int = 0
    people: list[str] = field(default_factory=list)


def scan_clip(
    library_root: Path,
    clip_path: Path,
    clip_id: str,
    *,
    force: bool = False,
    refs: dict[str, np.ndarray] | None = None,
    app=None,
) -> FaceScanResult:
    """Run face detection + matching on a single clip.

    Idempotent: if `<clip_id>.faces.json` already exists and `force=False`,
    skips. Per-clip exceptions are caught, written to `.error.json`, and
    surfaced as `result.error` so the library-scope driver can keep going.

    `refs` and `app` may be passed in by the orchestrator to avoid re-loading
    the heavy InsightFace model and re-embedding `People/` per clip.
    """
    library_root = Path(library_root)
    clip_path = Path(clip_path)
    fname = clip_path.name
    result = FaceScanResult(clip_id=clip_id)

    if not force and sidecar.has_sidecar(library_root, clip_id, config.SIDECAR_FACES):
        step(log, OP_NAME, fname, "skip (faces.json exists)")
        result.skipped_reason = "exists"
        return result

    try:
        if app is None:
            app = get_face_analyzer()
        if refs is None:
            refs = load_references(library_root, app=app)

        cap = cv2.VideoCapture(str(clip_path))
        if not cap.isOpened():
            raise RuntimeError("cv2 cannot open clip")
        try:
            duration_s = _read_clip_duration(cap)
            times = _sample_times(duration_s)

            t0 = time.monotonic()
            detections: list[dict] = []
            for t in times:
                cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
                ok, frame = cap.read()
                if not ok or frame is None:
                    continue
                faces = app.get(frame)
                if not faces:
                    continue
                for face in faces:
                    matched, score = _match(face.normed_embedding, refs)
                    x1, y1, x2, y2 = [float(v) for v in face.bbox]
                    detections.append({
                        "frame_t_s": round(float(t), 3),
                        "bbox": [x1, y1, x2 - x1, y2 - y1],
                        "embedding": np.asarray(
                            face.normed_embedding, dtype=np.float32
                        ).tolist(),
                        "matched_name": matched,
                        "score": round(score, 4),
                    })
            elapsed = time.monotonic() - t0
        finally:
            cap.release()

        people = _vote_people(detections)
        payload = {
            "clip_id": clip_id,
            "clip_filename": fname,
            "original_path": _relpath(clip_path, library_root),
            "scanned_at": _now_iso(),
            "frames_sampled_t_s": times,
            "detections": detections,
            "people": people,
        }
        sidecar_path = sidecar.write_faces(library_root, clip_id, payload)
        sidecar.clear_error_if_op(library_root, clip_id, OP_NAME)

        result.sidecar_path = sidecar_path
        result.detections = len(detections)
        result.people = people
        step(
            log, OP_NAME, fname,
            f"{len(detections)} detections, people={people or '∅'}",
            elapsed,
        )
        return result

    except Exception as e:  # noqa: BLE001 — per-clip catch-all is intentional
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
