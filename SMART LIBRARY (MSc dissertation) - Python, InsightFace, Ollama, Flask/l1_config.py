"""Locked configuration knobs for the Smart Library engine.

All values match Documentation/smart-library-spec.md → "Configuration".
Paths under the library root are stored as relative names; resolve against the
runtime-selected library root before use.
"""

# ── Models ────────────────────────────────────────────────────────────────────
VLM_MODEL = "gemma3:4b"
EMBED_MODEL = "nomic-embed-text:latest"
EMBED_BATCH_SIZE = 64  # texts per /api/embed call during sync

# ── Ollama hosts (dual-host captioning, §1k) ──────────────────────────────────
# Single host = single-host run. Multiple hosts = work-stealing dual-host run.
# Each host must have VLM_MODEL and EMBED_MODEL pulled. Each entry runs the
# full per-clip pipeline end-to-end (caption + embed).
OLLAMA_HOSTS = [
    "http://localhost:11434",   # ROG (Strix Halo + ROCm baseline) — PRIMARY
    "http://192.168.1.200:11434",  # Mac M4 on LAN — SECONDARY
]
# Human-readable labels for log prefixes — `[rog]` / `[mac]` per §1k.
# Unknown hosts fall back to their hostname.
OLLAMA_HOST_LABELS = {
    "http://localhost:11434":     "rog",
    "http://192.168.1.200:11434": "mac",
}
OLLAMA_PROBE_TIMEOUT_S = 5
OLLAMA_TIMEOUT_S = 600
VLM_TEMPERATURE = 0.2
VLM_NUM_CTX = 16384
DUAL_HOST_RETRY_MAX = 3  # per (clip, host); on exhaustion → re-queue to other host
# Backoff seconds between attempts on the same host. List length should be
# >= DUAL_HOST_RETRY_MAX - 1; last value reused if attempts exceed list.
DUAL_HOST_BACKOFF_S = (2, 5, 10)
# Consecutive errors on a host that trigger a health re-probe per §1k.
# If the re-probe fails, the host is demoted for the rest of the run.
DUAL_HOST_REPROBE_AFTER = 3

# ── Face scan / rematch ───────────────────────────────────────────────────────
FACE_DETECTOR = "buffalo_l"
FACE_MATCH_THRESHOLD = 0.45
FACE_SAMPLE_FPS = 1.0
FACE_FRAMES_MAX = 30
FACE_VOTE_MIN = 1  # §1f revised 2026-05-21: window-local voting → 1 (was 2)

# ── Windowing (§1a locked) ────────────────────────────────────────────────────
# 5s non-overlapping windows. Clips shorter than the cut threshold get a single
# window covering the whole duration. Threshold = 2 × WINDOW_SIZE − 3 = 7s.
WINDOW_SIZE_S = 5.0
WINDOW_CUT_THRESHOLD_S = 7.0
SAMPLES_PER_WINDOW = 3

# ── Smart frame picker (§1b locked — calibration 2026-05-19) ──────────────────
# Each of the 3 samples is bounded to its own third of the window. Inside its
# band, candidates are decoded at CANDIDATE_FPS, hard-rejected against the
# catastrophe net, then ranked by laplacian × edge_density.
CANDIDATE_FPS = 5
LAPLACIAN_MIN = 30
BRIGHTNESS_MIN = 25
BRIGHTNESS_MAX = 230
BRIGHTNESS_STD_MIN = 15
PICKER_ANALYSIS_WIDTH = 480  # downscale for metric compute

# ── Frames sent to VLM ────────────────────────────────────────────────────────
CAPTION_FRAME_LONG_SIDE = 1280
CAPTION_FRAME_JPEG_QUALITY = 90
CAPTION_PATCH_MULTIPLE = 28  # safe across Gemma 3 / Qwen2.5-VL
CAPTION_ANNOTATE_FRAMES = True
CAPTION_ANNOTATE_BOX_COLOR = (0, 255, 0)  # BGR
CAPTION_ANNOTATE_LABEL_FONT_SCALE = 0.6

# ── Embedding composition (§1h locked) ────────────────────────────────────────
# Atmospheric fields only. Order is convention; nomic is order-tolerant.
# Joined as " | ".join(non-empty fields).
EMBED_FIELDS = ("vibe", "scene", "scene_type", "mood")

# ── Adjacent-window merge (§1c locked) ────────────────────────────────────────
# Query-time only — windows remain the storage primitive. Adjacent intra-clip
# hits with cosine ≥ T collapse into a single served range.
ADJACENT_MERGE_THRESHOLD = 0.78
QUERY_INTERNAL_K_MULTIPLIER = 3  # fetch K × this, merge, return top K

# ── Clustering (§1h locked — iter05 values 2026-05-20) ───────────────────────
# Values from `code/phase7/03_clustering/results_iter05_n133_eom_mcs3_ms2_atmospheric/`.
# Cosine metric is the conceptual intent; HDBSCAN runs euclidean on L2-normalized
# vectors (equivalent on unit vectors, more stable across hdbscan versions).
CLUSTER_MIN_CLUSTER_SIZE = 3
CLUSTER_MIN_SAMPLES = 2
CLUSTER_SELECTION_METHOD = "eom"  # 'eom' (fewer/larger) or 'leaf' (fine-grained)
CLUSTER_METRIC = "cosine"  # documentation only — implementation uses L2+euclidean

# ── Thumbnail (poster frame) ──────────────────────────────────────────────────
THUMBNAIL_AT_PCT = 0.25
THUMBNAIL_LONG_SIDE = 320
THUMBNAIL_JPEG_QUALITY = 2  # ffmpeg -q:v scale, 2 = high quality

# ── Identity / naming ─────────────────────────────────────────────────────────
CLIP_ID_LEN = 16          # hex chars of SHA-256 kept as clip_id
SHORTID_LEN = 6           # hex chars of clip_id used in canonical filename
SLUG_MAX_LEN = 30

# ── Library layout (relative to library root) ─────────────────────────────────
MARKER_FILENAME = ".smart-library"
CACHE_DIR = ".cache"
CHROMA_DIR = ".chroma_db"
PEOPLE_DIR = "People"

# ── ChromaDB ──────────────────────────────────────────────────────────────────
CHROMA_COLLECTION = "clips"

# ── Datetime fallback ─────────────────────────────────────────────────────────
# When DJI filename is the only datetime source, this offset converts the
# camera-local time to UTC. None = treat as UTC and flag low-confidence.
LIBRARY_TIMEZONE_OFFSET = None

# ── Marker file ───────────────────────────────────────────────────────────────
SMART_LIBRARY_VERSION = 1

# ── Sidecar suffixes ──────────────────────────────────────────────────────────
SIDECAR_FACES = "faces.json"
SIDECAR_CAPTION = "caption.json"
SIDECAR_ERROR = "error.json"
# User overlay sidecar — UI-authored curation state (hidden / favorite / tags).
# Absent sidecar = default state (`hidden=false, favorite=false, tags=[]`).
SIDECAR_USER = "user.json"
# Layer 2 normalize sidecar — records original_filename, capture datetime,
# parsed cut metadata, and per-clip ingest history. Required by sync (Layer 4)
# because the canonical rename discards the original filename.
SIDECAR_NORMALIZE = "normalize.json"

# ── Sanitize / thumbnail tuning ───────────────────────────────────────────────
# Stream-vs-format duration delta that triggers LosslessCut phantom remux.
SANITIZE_DURATION_DELTA_S = 0.5
