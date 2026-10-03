"""Window-level caption op — windowing + smart frame picker + VLM + embed.

Spec reference: open-questions §1a (windowing), §1b (smart frame picker, locked
2026-05-19), §1d (window-scope schema + embed text formula + conditional face
paragraph), §1h (atmospheric embed composition), §1k (dual-host kwargs).

Per-clip pipeline:
    1. Probe duration → define 5s non-overlapping windows. Clips <7s get one
       window covering the whole duration.
    2. Per window:
         a. Smart picker: 3 samples, each bounded to its own third of the
            window, decoded at CANDIDATE_FPS, hard-rejected against the
            catastrophe net (laplacian / brightness / std), ranked by
            laplacian × edge_density. `low_quality_samples=True` if any third
            falls back to the least-bad rejected frame.
         b. Annotate frames with bbox + name labels for face detections
            whose `frame_t_s` falls inside the window AND have a matched_name
            (skipped entirely when faces.json missing or window has no named
            detections — runtime branch per §1d).
         c. Downscale + JPEG-encode → POST to <host>/api/generate.
         d. Validate window-scope JSON schema. One automatic retry on
            parse/validation failure.
         e. Compose embed_text from EMBED_FIELDS, POST to <host>/api/embeddings.
    3. Build windows array fully in memory; atomic-write the sidecar once
       at the end. Any window failure (after retry) aborts the clip → no
       sidecar written → next run re-does the whole clip from scratch.
       Invariant: a caption.json exists ⟺ every window for that clip is
       fully captioned + embedded.

Host URLs are kwargs (default localhost). The orchestrator in l4_pipeline
binds each ThreadPoolExecutor worker to one host URL for dual-host runs (§1k).
"""

from __future__ import annotations

import base64
import json
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import cv2
import numpy as np
import requests

import l1_config as config
import l1_sidecar as sidecar
import l2_discover as discover
import l2_sanitize as sanitize
import l3_annotate as annotate
from l1_logger import get_logger, step, step_error

log = get_logger("scan_caption")

OP_NAME = "caption"


# ── Locked window-scope schema ────────────────────────────────────────────────

REQUIRED_FIELDS = (
    "description",
    "scene",
    "vibe",
    "mood",
    "energy_level",
    "scene_type",
    "aesthetic_score",
    "notes",
)
DESCRIPTION_FIELDS = ("subjects_action", "framing")


# ── Locked window-scope system prompt (§1d) ───────────────────────────────────

_PEOPLE_BLOCK_NAMED = """NAMED PEOPLE
Frames are annotated with bounding boxes and name labels around identified faces. When the action involves a labeled person, refer to them by their label name (e.g. "Paul laughing with friends"). Unlabeled people stay generic ("a man", "a group"). Do not guess names.

"""

_PEOPLE_BLOCK_GENERIC = """PEOPLE NAMING
Refer to people generically ('a man', 'a group'). There is no name grounding in this window — do not invent names.

"""

SYSTEM_PROMPT_TEMPLATE = """You are a senior video editor reviewing raw footage for an AI-driven editing pipeline.

CONTEXT
You are analyzing one short window ({window_s:.1f}s) sampled from a longer raw clip of travel / lifestyle / action footage. A downstream "director" LLM will consume your analysis to build a highlight reel synced to a music track. Your output should give the director observable facts about WHAT and WHO, plus a textured read on the WORLD the shot lives in.

ANTI-HALLUCINATION (READ FIRST)
If you cannot CLEARLY see a person, subject, object, or detail in the frames, do NOT include it. Saying "no people in frame; drone tracks over rocks and sea" is BETTER than inventing subjects to fill the description. Inventing details is worse than admitting absence. When uncertain about a field, prefer the most generic enum value or an empty string over a guess.

PEAK MOMENT RULE
If a specific action or interaction occurs in the window — a kiss, hug, jump, drop, toast, peak gesture, sudden expression change — describe it EXPLICITLY in subjects_action. Do not average across frames; describe what HAPPENS, not what's most common across frames. If the window is monotonic, do not invent or exaggerate actions to fit this criterion.

EDITING MINDSET
Think like an editor reviewing dailies. Useful = grounded, specific, and where it matters, atmospherically textured. Useless = padded, alt-text-flavoured, or stenographic shot-list prose.

{people_block}FIELD TONE GUIDANCE
- subjects_action stays GROUNDED and CONCRETE. Describe what subjects do in flowing natural language. Stick to what you can see. Do not invent emotions you cannot read off the frame. If there are no people, say so directly ("no people in frame; ...") — do NOT invent subjects.
- framing stays MECHANICAL: subject placement, light direction, foreground/background separation. If subjects was WHO?, this is WHERE?, describe the setting, include perspective.
- scene is ALLOWED TO BREATHE. 1-2 sentences describing the world the shot lives in: location feel, light quality, environmental texture. Be evocative WHEN THE WORLD MATTERS — a bike on a seafront promenade, a late-night kitchen, a drone over a cliff, a crowd lit by neon. Use EMPTY STRING for tight close-ups or featureless interiors (a plain wall, an out-of-context torso). Do not invent context that is not there.
- vibe is ONE compressed 4-10 word phrase capturing the texture/feel. NOT a mood-enum repeat. Examples: "boozy late-night chaos", "sunlit kitchen morning", "tender candlelit closeness", "wind-in-hair drone freedom", "gritty handheld realism".

INSTRUCTIONS
Analyze the {n_frames} frames sampled from a {window_s:.1f}-second window. Return ONLY a valid JSON object with EXACTLY these keys. No markdown fences, no explanation.

{{
  "description": {{
    "subjects_action": "Who/what does what — flowing, observable.",
    "framing":         "Shot size (wide / medium / close), subject placement, light direction, foreground/background separation."
  }},

  "scene": "1-2 sentences on the world the shot lives in: location feel, light quality, environmental texture. Allowed to be evocative when the setting is part of the shot's value. EMPTY STRING for tight close-ups or featureless interiors — do not invent.",

  "vibe": "4-10 word evocative phrase capturing the texture/feel of the shot. NOT a mood-enum repeat.",

  "mood": "ONE of [cinematic, energetic, calm, somber, playful, intimate, tense, celebratory, mundane]",

  "energy_level": "ONE of [very_low, low, medium, high, very_high]",

  "scene_type": "ONE of [interior_home, interior_venue, exterior_urban, exterior_nature, exterior_party, drone_aerial, vehicle, mixed]",

  "aesthetic_score": 6.0,

  "notes": "Quality flags or oddities (blur, audio-only-good, lens-wipe, etc). Empty string if nothing notable."
}}

AESTHETIC SCORING RUBRIC
  1-2  Unusable — out of focus, badly exposed, obstructed, no clear subject
  3-4  Weak — usable as filler only
  5    Average — acceptable, nothing special
  6-7  Good — solid composition, clear subject, good light
  8-9  Excellent — strong visual impact, cinematic quality
  10   Exceptional — portfolio-worthy

Most raw footage lands 4-6. Be critical and consistent across windows."""


def _build_prompt(n_frames: int, window_s: float, has_named: bool) -> str:
    block = _PEOPLE_BLOCK_NAMED if has_named else _PEOPLE_BLOCK_GENERIC
    return SYSTEM_PROMPT_TEMPLATE.format(
        n_frames=n_frames, window_s=window_s, people_block=block,
    )


# ── Windowing (§1a) ───────────────────────────────────────────────────────────

def define_windows(duration_s: float) -> list[tuple[float, float]]:
    """5s non-overlapping windows. Clips < 7s collapse to a single window."""
    if duration_s <= 0:
        return []
    if duration_s < config.WINDOW_CUT_THRESHOLD_S:
        return [(0.0, round(duration_s, 3))]
    windows: list[tuple[float, float]] = []
    t = 0.0
    while t < duration_s - 1e-3:
        end = min(t + config.WINDOW_SIZE_S, duration_s)
        windows.append((round(t, 3), round(end, 3)))
        t = end
    return windows


# ── Smart frame picker (§1b) ──────────────────────────────────────────────────

def _downscale_for_analysis(frame: np.ndarray) -> np.ndarray:
    h, w = frame.shape[:2]
    target = config.PICKER_ANALYSIS_WIDTH
    if w <= target:
        return frame
    new_h = int(h * target / w)
    return cv2.resize(frame, (target, new_h), interpolation=cv2.INTER_AREA)


def _compute_metrics(frame_bgr: np.ndarray) -> dict:
    gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
    return {
        "laplacian":      float(cv2.Laplacian(gray, cv2.CV_64F).var()),
        "edge_density":   float(cv2.Canny(gray, 100, 200).mean()),
        "brightness":     float(gray.mean()),
        "brightness_std": float(gray.std()),
    }


def _hard_rejects(m: dict) -> list[str]:
    fired: list[str] = []
    if m["brightness"] < config.BRIGHTNESS_MIN:           fired.append("too_dark")
    if m["brightness"] > config.BRIGHTNESS_MAX:           fired.append("too_bright")
    if m["brightness_std"] < config.BRIGHTNESS_STD_MIN:   fired.append("flat")
    if m["laplacian"] < config.LAPLACIAN_MIN:             fired.append("very_blurry")
    return fired


def _rank_score(m: dict) -> float:
    return m["laplacian"] * m["edge_density"]


def pick_frames_for_window(
    cap: cv2.VideoCapture,
    win_start: float,
    win_end: float,
) -> dict:
    """Return picks + discards + low_quality flag for one window.

    Each of the SAMPLES_PER_WINDOW samples is bounded to its own equal third
    of the window. Inside its third, candidates are decoded at CANDIDATE_FPS,
    hard-rejected against the catastrophe net, then ranked. If a third has
    no surviving candidate, the highest-ranked rejected frame is taken and
    `low_quality_samples` is set True.
    """
    n = config.SAMPLES_PER_WINDOW
    window_dur = win_end - win_start
    third = window_dur / n

    picks: list[dict] = []
    discarded: list[dict] = []
    low_quality = False

    step_s = 1.0 / config.CANDIDATE_FPS

    for k in range(n):
        third_start = win_start + k * third
        third_end = win_start + (k + 1) * third

        scored: list[dict] = []
        t = third_start
        while t < third_end:
            cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
            ok, frame = cap.read()
            if ok and frame is not None:
                metrics = _compute_metrics(_downscale_for_analysis(frame))
                scored.append({
                    "t": round(t, 3),
                    "metrics": metrics,
                    "rejected_by": _hard_rejects(metrics),
                })
            t += step_s

        if not scored:
            low_quality = True
            continue

        survivors = [s for s in scored if not s["rejected_by"]]
        pool, from_rejected = (survivors, False) if survivors else (scored, True)
        if from_rejected:
            low_quality = True

        best = max(pool, key=lambda s: _rank_score(s["metrics"]))
        picks.append({
            "third_idx":   k,
            "third_start": round(third_start, 3),
            "third_end":   round(third_end, 3),
            "picked_t":    best["t"],
            "metrics":     best["metrics"],
            "rank":        round(_rank_score(best["metrics"]), 1),
            "picked_from_rejected": from_rejected,
        })
        for s in scored:
            if s["rejected_by"]:
                discarded.append({
                    "t": s["t"],
                    "metrics": s["metrics"],
                    "rejected_by": s["rejected_by"],
                })

    return {
        "picks": picks,
        "discarded": discarded,
        "low_quality_samples": low_quality,
    }


# ── Frame extraction + downscale for VLM ──────────────────────────────────────

def _downscale_for_vlm(frame: np.ndarray) -> np.ndarray:
    h, w = frame.shape[:2]
    long = max(h, w)
    target = config.CAPTION_FRAME_LONG_SIDE
    patch = config.CAPTION_PATCH_MULTIPLE
    if long > target:
        scale = target / long
        new_w, new_h = int(round(w * scale)), int(round(h * scale))
    else:
        new_w, new_h = w, h
    new_w = max(patch, (new_w // patch) * patch)
    new_h = max(patch, (new_h // patch) * patch)
    if (new_w, new_h) == (w, h):
        return frame
    return cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_AREA)


def _encode_jpeg(frame: np.ndarray) -> bytes:
    ok, buf = cv2.imencode(
        ".jpg", frame,
        [cv2.IMWRITE_JPEG_QUALITY, int(config.CAPTION_FRAME_JPEG_QUALITY)],
    )
    if not ok:
        raise RuntimeError("cv2 JPEG encode failed")
    return buf.tobytes()


def _nearest_detections(
    dets_by_time: dict[float, list[dict]],
    target_t: float,
    tol: float,
) -> list[dict]:
    if not dets_by_time:
        return []
    best_t = min(dets_by_time.keys(), key=lambda t: abs(t - target_t))
    if abs(best_t - target_t) > tol:
        return []
    return dets_by_time[best_t]


def extract_window_frames(
    cap: cv2.VideoCapture,
    picks: list[dict],
    window_detections: list[dict],
) -> list[np.ndarray]:
    """Read picked frames, optionally annotate, and downscale for VLM."""
    dets_by_time: dict[float, list[dict]] = {}
    for d in window_detections:
        try:
            t = round(float(d.get("frame_t_s", 0.0)), 3)
        except (TypeError, ValueError):
            continue
        dets_by_time.setdefault(t, []).append(d)

    frames: list[np.ndarray] = []
    for p in picks:
        cap.set(cv2.CAP_PROP_POS_MSEC, p["picked_t"] * 1000)
        ok, frame = cap.read()
        if not ok or frame is None:
            continue
        # Picked timestamps almost never align to face-scan timestamps (faces
        # sampled at 1 fps, picker at CANDIDATE_FPS). Use the nearest face-scan
        # detection within ±0.5s so annotations follow the picked frame.
        nearest = _nearest_detections(dets_by_time, p["picked_t"], tol=0.5)
        if config.CAPTION_ANNOTATE_FRAMES and nearest:
            frame = annotate.draw_named_detections(frame, nearest)
        frame = _downscale_for_vlm(frame)
        frames.append(frame)
    return frames


def _filter_window_detections(
    faces_json: dict | None,
    win_start: float,
    win_end: float,
) -> list[dict]:
    """Detections whose frame_t_s lies inside [win_start, win_end)."""
    if not faces_json:
        return []
    out: list[dict] = []
    for d in faces_json.get("detections") or []:
        try:
            t = float(d.get("frame_t_s", -1.0))
        except (TypeError, ValueError):
            continue
        if win_start <= t < win_end:
            out.append(d)
    return out


# ── Ollama calls ──────────────────────────────────────────────────────────────

def _call_vlm(
    prompt: str,
    frames: list[np.ndarray],
    generate_url: str,
) -> tuple[dict, float]:
    """POST frames + prompt to Ollama /api/generate. Returns (parsed, elapsed_s).

    Raises RuntimeError on transport, HTTP, or JSON-parse failure.
    """
    images_b64 = [base64.b64encode(_encode_jpeg(f)).decode("ascii") for f in frames]
    payload = {
        "model": config.VLM_MODEL,
        "prompt": prompt,
        "images": images_b64,
        "stream": False,
        "format": "json",
        "options": {
            "temperature": config.VLM_TEMPERATURE,
            "num_ctx": config.VLM_NUM_CTX,
        },
    }
    t0 = time.monotonic()
    resp = requests.post(generate_url, json=payload, timeout=config.OLLAMA_TIMEOUT_S)
    elapsed = time.monotonic() - t0
    resp.raise_for_status()
    data = resp.json()
    raw = data.get("response", "")
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as e:
        raise RuntimeError(
            f"VLM returned non-JSON response: {e}; raw[:200]={raw[:200]!r}"
        ) from e
    return parsed, elapsed


def _call_embed(text: str, embed_url: str) -> list[float]:
    """POST text to Ollama /api/embeddings. Returns the embedding vector."""
    payload = {"model": config.EMBED_MODEL, "prompt": text}
    resp = requests.post(embed_url, json=payload, timeout=config.OLLAMA_TIMEOUT_S)
    resp.raise_for_status()
    data = resp.json()
    emb = data.get("embedding")
    if not isinstance(emb, list) or not emb:
        raise RuntimeError("embed call returned no vector")
    return emb


def build_embed_text(parsed: dict) -> str:
    """Atmospheric composition per §1h: vibe | scene | scene_type | mood.

    Field list controlled by config.EMBED_FIELDS. Missing/empty fields skipped.
    `description.subjects_action` etc. live in caption.json for snippet display
    and are intentionally NOT embedded — they pull the vector toward concrete
    action and away from scene-family clustering.
    """
    parts: list[str] = []
    for name in config.EMBED_FIELDS:
        val = parsed.get(name)
        if isinstance(val, str):
            s = val.strip()
            if s:
                parts.append(s)
    return " | ".join(parts)


# ── Validation ────────────────────────────────────────────────────────────────

def _validate(parsed) -> None:
    if not isinstance(parsed, dict):
        raise ValueError(f"caption JSON not an object (got {type(parsed).__name__})")
    missing = [k for k in REQUIRED_FIELDS if k not in parsed]
    if missing:
        raise ValueError(f"caption JSON missing required fields: {missing}")
    desc = parsed.get("description")
    if not isinstance(desc, dict):
        raise ValueError("description must be an object")
    desc_missing = [k for k in DESCRIPTION_FIELDS if k not in desc]
    if desc_missing:
        raise ValueError(f"description missing fields: {desc_missing}")


# ── Helpers ───────────────────────────────────────────────────────────────────

def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _relpath(clip_path: Path, library_root: Path) -> str:
    try:
        return clip_path.resolve().relative_to(Path(library_root).resolve()).as_posix()
    except ValueError:
        return str(clip_path)


# ── Per-clip op ───────────────────────────────────────────────────────────────

@dataclass
class CaptionResult:
    clip_id: str
    sidecar_path: Path | None = None
    skipped_reason: str | None = None
    error: str | None = None
    degraded: bool = False
    n_windows: int = 0
    low_quality_windows: int = 0
    vlm_elapsed_s: float = 0.0
    failed_window: int | None = None


def scan_clip(
    library_root: Path,
    clip_path: Path,
    clip_id: str,
    *,
    force: bool = False,
    host_url: str | None = None,
) -> CaptionResult:
    """Run the window-level caption op on one clip.

    Idempotent unless force=True: the existence of a caption sidecar is the
    "fully captioned" signal (per the locked invariant — no partial sidecars).

    host_url is the Ollama base URL for both VLM and embedding calls. Defaults
    to the first entry of config.OLLAMA_HOSTS. The orchestrator in l4_pipeline
    binds each worker to one host for dual-host runs.
    """
    library_root = Path(library_root)
    clip_path = Path(clip_path)
    fname = clip_path.name
    result = CaptionResult(clip_id=clip_id)

    if host_url is None:
        host_url = config.OLLAMA_HOSTS[0]
    generate_url = host_url.rstrip("/") + "/api/generate"
    embed_url = host_url.rstrip("/") + "/api/embeddings"

    if not force and sidecar.has_sidecar(library_root, clip_id, config.SIDECAR_CAPTION):
        step(log, OP_NAME, fname, "skip (caption.json exists)")
        result.skipped_reason = "exists"
        return result

    try:
        try:
            probe = discover.ffprobe(clip_path)
        except Exception as e:
            raise RuntimeError(f"ffprobe failed: {e}") from e
        duration_s = sanitize.format_duration_s(probe)
        if duration_s is None or duration_s <= 0:
            raise RuntimeError("clip has no readable duration")

        win_bounds = define_windows(duration_s)
        if not win_bounds:
            raise RuntimeError("no windows could be computed")

        faces_json = sidecar.read_faces(library_root, clip_id)
        if faces_json is None:
            log.warning(
                "[%s] %s: faces.json missing — degraded mode (no name grounding)",
                OP_NAME, fname,
            )
            result.degraded = True

        cap = cv2.VideoCapture(str(clip_path))
        if not cap.isOpened():
            raise RuntimeError("cv2 cannot open clip")

        windows_payload: list[dict] = []
        total_vlm_s = 0.0
        low_quality_count = 0

        try:
            for w_idx, (ws, we) in enumerate(win_bounds):
                window_dets = _filter_window_detections(faces_json, ws, we)
                has_named = any(d.get("matched_name") for d in window_dets)

                picker = pick_frames_for_window(cap, ws, we)
                if not picker["picks"]:
                    raise RuntimeError(
                        f"window {w_idx} [{ws:.2f}-{we:.2f}s]: picker returned no frames"
                    )
                if picker["low_quality_samples"]:
                    low_quality_count += 1

                frames = extract_window_frames(cap, picker["picks"], window_dets)
                if not frames:
                    raise RuntimeError(
                        f"window {w_idx} [{ws:.2f}-{we:.2f}s]: frame extraction failed"
                    )

                prompt = _build_prompt(
                    n_frames=len(frames),
                    window_s=we - ws,
                    has_named=has_named,
                )

                # One automatic retry on parse/validation failure — covers
                # sporadic Ollama JSON glitches (empty objects, wrapper objects,
                # malformed JSON). Same prompt, same frames.
                attempt = 0
                parsed = None
                vlm_elapsed = 0.0
                while True:
                    attempt += 1
                    try:
                        parsed, vlm_elapsed = _call_vlm(prompt, frames, generate_url)
                        _validate(parsed)
                        break
                    except (ValueError, RuntimeError) as e:
                        if attempt >= 2:
                            result.failed_window = w_idx
                            raise RuntimeError(
                                f"window {w_idx} [{ws:.2f}-{we:.2f}s]: "
                                f"VLM failed twice — {e}"
                            ) from e
                        log.warning(
                            "[%s] %s W%02d: VLM attempt %d failed (%s), retrying",
                            OP_NAME, fname, w_idx, attempt, e,
                        )

                total_vlm_s += vlm_elapsed

                embed_text = build_embed_text(parsed)
                embedding = _call_embed(embed_text, embed_url) if embed_text else []

                picked_times = [p["picked_t"] for p in picker["picks"]]
                windows_payload.append({
                    "window_index":        w_idx,
                    "window_start_s":      ws,
                    "window_end_s":        we,
                    "frames_sampled_t_s":  picked_times,
                    "low_quality_samples": bool(picker["low_quality_samples"]),
                    "fields":              parsed,
                    "embed_text":          embed_text,
                    "embedding":           embedding,
                })

                log.debug(
                    "[%s] %s W%02d %.1f-%.1fs: VLM %.2fs%s",
                    OP_NAME, fname, w_idx, ws, we, vlm_elapsed,
                    " [low_quality]" if picker["low_quality_samples"] else "",
                )
        finally:
            cap.release()

        payload = {
            "clip_id":       clip_id,
            "clip_filename": fname,
            "original_path": _relpath(clip_path, library_root),
            "scanned_at":    _now_iso(),
            "model":         config.VLM_MODEL,
            "embed_model":   config.EMBED_MODEL,
            "duration_s":    round(float(duration_s), 3),
            "windows":       windows_payload,
        }
        path = sidecar.write_caption(library_root, clip_id, payload)
        sidecar.clear_error_if_op(library_root, clip_id, OP_NAME)
        result.sidecar_path = path
        result.n_windows = len(windows_payload)
        result.low_quality_windows = low_quality_count
        result.vlm_elapsed_s = total_vlm_s

        suffix_parts = [f"windows={result.n_windows}"]
        if low_quality_count:
            suffix_parts.append(f"low_q={low_quality_count}")
        if result.degraded:
            suffix_parts.append("degraded")
        step(
            log, OP_NAME, fname,
            f"caption written ({', '.join(suffix_parts)})",
            total_vlm_s,
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
