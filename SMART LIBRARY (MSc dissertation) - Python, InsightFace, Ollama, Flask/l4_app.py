"""Flask UI — v2 window-row primary surface.

Window-row primitive shifts the UI from clip-tiles to window-tiles. Cluster
sidebar surfaces the HDBSCAN pool (§1h) so the user can browse by scene
family. Range playback drives `<video>` seek + stop on the client.

MVP scope (task 8): hidden / favorite / tags stay clip-level. The
`_window_user_state` seam in `l4_sync` returns clip-level state uniformly
for every window of the same clip, so a favorite toggle on any window of
clip X favorites every window of clip X. Per-window overlay (§1g) is the
follow-up that locks the sidecar schema.

Endpoints:
  - GET  /                       SPA shell (templates/index.html)
  - POST /api/library/check      validate path + report library marker
  - POST /api/library/init       drop a .smart-library marker
  - POST /api/op                 kick a pipeline op (single-slot worker)
  - GET  /api/job                poll current op status
  - GET  /api/logs?since=N       tail in-memory log ring buffer
  - GET  /api/windows            window-row list (filterable by cluster, hidden)
  - GET  /api/clusters           cluster distribution + representative window
  - GET  /api/query?q=…          top-k window hits (basic; task 9 adds merge)
  - GET  /api/stats              clip / face / caption / window / cluster counts
  - GET  /api/people             reference names from People/
  - GET  /api/tags               union of clip-level tags
  - GET  /api/errors             open .error.json list
  - GET  /api/clip/<clip_id>     sidecar dump for one clip (windows in caption)
  - POST /api/clip/<clip_id>/user  partial-update clip-level user state
  - GET  /api/thumb              cached per-clip poster JPG
  - GET  /api/window_thumb       cached per-window mid-frame JPG
  - GET  /api/video              stream a clip's bytes (range playback client-side)
"""

from __future__ import annotations

import argparse
import logging
import threading
from collections import deque
from pathlib import Path
from typing import Any

from flask import Flask, abort, jsonify, render_template, request, send_file

import l1_config as config
import l1_marker as marker
import l1_sidecar as sidecar
import l2_thumbnail as thumbnail
import l4_pipeline as pipeline
import l4_sync as sync
import l4_user as user
from l1_logger import get_logger

log = get_logger("app")


# ── In-memory log ring buffer + custom handler ────────────────────────────────

class _LogBuffer:
    def __init__(self, capacity: int = 2000):
        self._buf: deque[tuple[int, str, str]] = deque(maxlen=capacity)
        self._lock = threading.Lock()
        self._next = 1

    def add(self, level: str, line: str) -> None:
        with self._lock:
            self._buf.append((self._next, level, line))
            self._next += 1

    def since(self, seq: int) -> list[dict[str, Any]]:
        with self._lock:
            return [
                {"seq": s, "level": lvl, "line": ln}
                for s, lvl, ln in self._buf if s > seq
            ]

    def latest_seq(self) -> int:
        with self._lock:
            return self._next - 1


class _BufferingHandler(logging.Handler):
    def __init__(self, buf: _LogBuffer):
        super().__init__()
        self._buf = buf
        self.setFormatter(logging.Formatter("%(asctime)s %(message)s", datefmt="%H:%M:%S"))

    def emit(self, record: logging.LogRecord) -> None:
        try:
            self._buf.add(record.levelname, self.format(record))
        except Exception:
            self.handleError(record)


# ── Job runner (single-slot worker thread) ────────────────────────────────────

class _JobRunner:
    def __init__(self):
        self._lock = threading.Lock()
        self._thread: threading.Thread | None = None
        self._state: dict[str, Any] = {"status": "idle", "op": None, "result": None, "error": None}

    def status(self) -> dict[str, Any]:
        with self._lock:
            return dict(self._state)

    def busy(self) -> bool:
        with self._lock:
            return self._state["status"] == "running"

    def start(self, op: str, library_root: Path, *,
              target: Path | None, force: bool, dry_run: bool, retry_errors: bool) -> bool:
        with self._lock:
            if self._state["status"] == "running":
                return False
            self._state = {"status": "running", "op": op, "result": None, "error": None}
            self._thread = threading.Thread(
                target=self._run,
                args=(op, library_root, target, force, dry_run, retry_errors),
                daemon=True,
            )
            self._thread.start()
            return True

    def _run(self, op, library_root, target, force, dry_run, retry_errors):
        try:
            result = pipeline.run(
                op, library_root,
                target=target, force=force, dry_run=dry_run, retry_errors=retry_errors,
            )
            with self._lock:
                self._state = {
                    "status": "done",
                    "op": op,
                    "result": {
                        "op": result.op,
                        "scope_path": result.scope_path,
                        "succeeded": result.succeeded,
                        "skipped": result.skipped,
                        "errored": result.errored,
                        "notes": result.notes,
                    },
                    "error": None,
                }
        except Exception as e:  # noqa: BLE001
            log.exception("pipeline op failed")
            with self._lock:
                self._state = {"status": "error", "op": op, "result": None, "error": str(e)}


# ── Row → JSON helpers ────────────────────────────────────────────────────────

def _csv_to_list(s) -> list[str]:
    if not s:
        return []
    return [t for t in str(s).split(",") if t]


def _window_row_to_json(window_id: str, meta: dict) -> dict:
    meta = meta or {}
    return {
        "window_id":            window_id,
        "clip_id":              meta.get("clip_id", window_id.split(":", 1)[0]),
        "window_start_s":       float(meta.get("window_start_s") or 0.0),
        "window_end_s":         float(meta.get("window_end_s") or 0.0),
        "clip_filename":        meta.get("clip_filename", ""),
        "relative_path":        meta.get("relative_path", ""),
        "location":             meta.get("location", ""),
        "event_path":           meta.get("event_path", ""),
        "capture_datetime_utc": meta.get("capture_datetime_utc", ""),
        "duration_s":           meta.get("duration_s", 0),
        "is_cut":               meta.get("is_cut"),
        "source_clip_id":       meta.get("source_clip_id", ""),
        "source_clip_name":     meta.get("source_clip_name", ""),
        "people":               _csv_to_list(meta.get("people")),
        "description_subjects_action": meta.get("description_subjects_action", ""),
        "description_framing":         meta.get("description_framing", ""),
        "scene":                meta.get("scene", ""),
        "vibe":                 meta.get("vibe", ""),
        "mood":                 meta.get("mood", ""),
        "energy_level":         meta.get("energy_level", ""),
        "scene_type":           meta.get("scene_type", ""),
        "aesthetic_score":      meta.get("aesthetic_score"),
        "low_quality_samples":  bool(meta.get("low_quality_samples", False)),
        "cluster_id":           meta.get("cluster_id"),
        "hidden":               bool(meta.get("hidden", False)),
        "favorite":             bool(meta.get("favorite", False)),
        "tags":                 _csv_to_list(meta.get("tags")),
    }


# ── App factory ───────────────────────────────────────────────────────────────

def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder=str(Path(__file__).parent / "templates"),
        static_folder=str(Path(__file__).parent / "static"),
    )

    log_buf = _LogBuffer(capacity=4000)
    handler = _BufferingHandler(log_buf)
    handler.setLevel(logging.DEBUG)
    logging.getLogger("smart_library").addHandler(handler)

    runner = _JobRunner()

    # ── Page ──────────────────────────────────────────────────────────────────

    @app.route("/")
    def index():
        return render_template("index.html")

    # ── Library lifecycle ─────────────────────────────────────────────────────

    @app.route("/api/library/check", methods=["POST"])
    def library_check():
        path_str = (request.json or {}).get("path", "")
        if not path_str:
            return jsonify({"ok": False, "reason": "no path provided"}), 400
        p = Path(path_str)
        if not p.exists() or not p.is_dir():
            return jsonify({"ok": False, "reason": "path is not a directory", "path": str(p)})
        return jsonify({
            "ok": True,
            "path": str(p.resolve()),
            "is_library": marker.is_library(p),
            "marker": marker.read_marker(p),
        })

    @app.route("/api/library/init", methods=["POST"])
    def library_init():
        path_str = (request.json or {}).get("path", "")
        if not path_str:
            return jsonify({"ok": False, "reason": "no path provided"}), 400
        p = Path(path_str)
        try:
            payload = marker.init_library(p)
        except OSError as e:
            return jsonify({"ok": False, "reason": str(e)}), 400
        return jsonify({"ok": True, "path": str(p.resolve()), "marker": payload})

    # ── Op runner ─────────────────────────────────────────────────────────────

    @app.route("/api/op", methods=["POST"])
    def op_run():
        body = request.json or {}
        op = body.get("op", "")
        library_path = body.get("library", "")
        target = body.get("target") or None
        force = bool(body.get("force"))
        dry_run = bool(body.get("dry_run"))
        retry_errors = bool(body.get("retry_errors"))

        if op not in pipeline.OPS:
            return jsonify({"ok": False, "reason": f"unknown op {op!r}"}), 400
        if not library_path:
            return jsonify({"ok": False, "reason": "no library path"}), 400

        library_root = Path(library_path)
        if not marker.is_library(library_root):
            return jsonify({"ok": False, "reason": "not a Smart Library root"}), 400

        target_path: Path | None = None
        if target:
            target_path = Path(target)
            if not target_path.is_absolute():
                target_path = library_root / target_path

        if not runner.start(
            op, library_root,
            target=target_path, force=force, dry_run=dry_run, retry_errors=retry_errors,
        ):
            return jsonify({"ok": False, "reason": "another op is running"}), 409
        return jsonify({"ok": True, "op": op})

    @app.route("/api/job", methods=["GET"])
    def job_status():
        return jsonify(runner.status())

    @app.route("/api/logs", methods=["GET"])
    def logs():
        try:
            since = int(request.args.get("since", "0"))
        except ValueError:
            since = 0
        return jsonify({"latest": log_buf.latest_seq(), "lines": log_buf.since(since)})

    # ── Window browser ────────────────────────────────────────────────────────

    @app.route("/api/windows", methods=["GET"])
    def windows_list():
        """All window rows, filterable by hidden + cluster_id.

        Default sort: chronological by `capture_datetime_utc`, then
        `window_start_s` within a clip — matches §1a cluster-retrieval UX rule.
        """
        library_path = request.args.get("library", "")
        if not library_path:
            abort(400)
        library_root = Path(library_path)
        if not marker.is_library(library_root):
            abort(400)

        show_hidden = request.args.get("show_hidden", "0") == "1"
        cluster_arg = request.args.get("cluster")
        cluster_filter: int | None = None
        if cluster_arg not in (None, ""):
            try:
                cluster_filter = int(cluster_arg)
            except ValueError:
                abort(400)

        try:
            collection = sync.get_collection(library_root)
            get_kwargs: dict[str, Any] = {"include": ["metadatas"]}
            where: dict[str, Any] = {}
            if not show_hidden:
                where["hidden"] = False
            if cluster_filter is not None:
                where["cluster_id"] = cluster_filter
            if where:
                if len(where) == 1:
                    get_kwargs["where"] = where
                else:
                    get_kwargs["where"] = {"$and": [{k: v} for k, v in where.items()]}
            data = collection.get(**get_kwargs)
        except Exception:
            data = {"ids": [], "metadatas": []}

        ids = data.get("ids") or []
        metas = data.get("metadatas") or []
        rows = [_window_row_to_json(wid, m) for wid, m in zip(ids, metas)]
        rows.sort(key=lambda r: (
            r["capture_datetime_utc"] or "",
            r["clip_id"],
            r["window_start_s"],
        ))
        return jsonify({"windows": rows})

    @app.route("/api/clusters", methods=["GET"])
    def clusters_list():
        """Cluster distribution + a representative window per cluster.

        Representative = highest `aesthetic_score` in the cluster (matches the
        §1e display-name picking strategy). Noise (cluster_id=-1) is included
        as a bucket so the UI can offer "Browse noise". Rows without a
        `cluster_id` (pre-cluster) are aggregated as `unclustered_count`.
        """
        library_path = request.args.get("library", "")
        if not library_path:
            abort(400)
        library_root = Path(library_path)
        if not marker.is_library(library_root):
            abort(400)

        try:
            collection = sync.get_collection(library_root)
            data = collection.get(include=["metadatas"])
        except Exception:
            return jsonify({"clusters": [], "unclustered_count": 0})

        ids = data.get("ids") or []
        metas = data.get("metadatas") or []

        by_cluster: dict[int, list[tuple[str, dict]]] = {}
        unclustered = 0
        for wid, m in zip(ids, metas):
            m = m or {}
            cid = m.get("cluster_id")
            if cid is None:
                unclustered += 1
                continue
            try:
                cid = int(cid)
            except (TypeError, ValueError):
                continue
            by_cluster.setdefault(cid, []).append((wid, m))

        clusters = []
        for cid, members in sorted(by_cluster.items(), key=lambda kv: (kv[0] == -1, kv[0])):
            # Representative = highest aesthetic_score; ties broken by window_id.
            def _score(item):
                _, meta = item
                v = meta.get("aesthetic_score")
                try:
                    return float(v) if v is not None else -1.0
                except (TypeError, ValueError):
                    return -1.0
            rep_wid, rep_meta = max(members, key=_score)

            # Top mood / scene_type among members for quick legibility.
            mood_counts: dict[str, int] = {}
            scene_counts: dict[str, int] = {}
            for _, m in members:
                mo = m.get("mood")
                st = m.get("scene_type")
                if mo:
                    mood_counts[mo] = mood_counts.get(mo, 0) + 1
                if st:
                    scene_counts[st] = scene_counts.get(st, 0) + 1
            top_mood = max(mood_counts.items(), key=lambda kv: kv[1])[0] if mood_counts else ""
            top_scene = max(scene_counts.items(), key=lambda kv: kv[1])[0] if scene_counts else ""

            clusters.append({
                "cluster_id": cid,
                "count": len(members),
                "representative_window_id": rep_wid,
                "representative_clip_id": rep_meta.get("clip_id", ""),
                "representative_relative_path": rep_meta.get("relative_path", ""),
                "representative_window_start_s": float(rep_meta.get("window_start_s") or 0.0),
                "representative_window_end_s":   float(rep_meta.get("window_end_s") or 0.0),
                "representative_vibe": rep_meta.get("vibe", ""),
                "top_mood": top_mood,
                "top_scene_type": top_scene,
            })

        return jsonify({"clusters": clusters, "unclustered_count": unclustered})

    @app.route("/api/query", methods=["GET"])
    def query():
        """Top-K window ranges per §1c (adjacent-merge T=0.78).

        Each range has `start_s/end_s` spanning the merged consecutive
        windows, `best_window_id` as the representative (for thumb +
        snippet display), and `constituent_ids` for traceability.
        `?merge=0` disables merging for debugging.
        """
        library_path = request.args.get("library", "")
        q = request.args.get("q", "")
        try:
            top_k = int(request.args.get("k", "20"))
        except ValueError:
            top_k = 20
        show_hidden = request.args.get("show_hidden", "0") == "1"
        merge = request.args.get("merge", "1") != "0"
        if not library_path or not q:
            return jsonify({"hits": []})
        library_root = Path(library_path)
        if not marker.is_library(library_root):
            abort(400)

        if merge:
            ranges = sync.query_with_merge(
                library_root, q, top_k=top_k, include_hidden=show_hidden,
            )
            return jsonify({"hits": ranges, "merged": True})
        hits = sync.query(
            library_root, q, top_k=top_k, include_hidden=show_hidden,
        )
        return jsonify({"hits": hits, "merged": False})

    @app.route("/api/stats", methods=["GET"])
    def stats():
        library_path = request.args.get("library", "")
        if not library_path:
            return jsonify({})
        library_root = Path(library_path)
        if not marker.is_library(library_root):
            return jsonify({})

        def _count(suffix: str) -> int:
            return sum(1 for _ in sidecar.iter_sidecars(library_root, suffix))

        normalized = _count(config.SIDECAR_NORMALIZE)
        faced = _count(config.SIDECAR_FACES)
        captioned = _count(config.SIDECAR_CAPTION)
        errors = _count(config.SIDECAR_ERROR)

        windows_count = 0
        cluster_count = 0
        try:
            collection = sync.get_collection(library_root)
            data = collection.get(include=["metadatas"])
            metas = data.get("metadatas") or []
            windows_count = len(metas)
            cluster_ids = set()
            for m in metas:
                cid = (m or {}).get("cluster_id")
                if cid is not None:
                    try:
                        cid = int(cid)
                    except (TypeError, ValueError):
                        continue
                    if cid >= 0:
                        cluster_ids.add(cid)
            cluster_count = len(cluster_ids)
        except Exception:
            pass

        return jsonify({
            "total_clips":     normalized,
            "faced":           faced,
            "captioned":       captioned,
            "errors":          errors,
            "pct_faced":       (faced / normalized * 100) if normalized else 0.0,
            "pct_captioned":   (captioned / normalized * 100) if normalized else 0.0,
            "total_windows":   windows_count,
            "total_clusters":  cluster_count,
        })

    @app.route("/api/tags", methods=["GET"])
    def tags_list():
        library_path = request.args.get("library", "")
        if not library_path:
            return jsonify({"tags": []})
        library_root = Path(library_path)
        if not marker.is_library(library_root):
            return jsonify({"tags": []})
        seen: set[str] = set()
        for clip_id, _ in sidecar.iter_sidecars(library_root, config.SIDECAR_USER):
            u = sidecar.read_user(library_root, clip_id) or {}
            for t in (u.get("tags") or []):
                if isinstance(t, str) and t:
                    seen.add(t)
        return jsonify({"tags": sorted(seen)})

    @app.route("/api/people", methods=["GET"])
    def people_list():
        library_path = request.args.get("library", "")
        if not library_path:
            return jsonify({"people": []})
        library_root = Path(library_path)
        if not marker.is_library(library_root):
            return jsonify({"people": []})
        people_dir = library_root / config.PEOPLE_DIR
        if not people_dir.is_dir():
            return jsonify({"people": []})
        names = sorted(
            (p.name for p in people_dir.iterdir()
             if p.is_dir() and not p.name.startswith(".")),
            key=str.lower,
        )
        return jsonify({"people": names})

    @app.route("/api/errors", methods=["GET"])
    def errors():
        library_path = request.args.get("library", "")
        if not library_path:
            return jsonify({"errors": []})
        library_root = Path(library_path)
        if not marker.is_library(library_root):
            return jsonify({"errors": []})
        out = []
        for clip_id, _ in sidecar.iter_sidecars(library_root, config.SIDECAR_ERROR):
            err = sidecar.read_error(library_root, clip_id)
            if err:
                out.append({"clip_id": clip_id, **err})
        return jsonify({"errors": out})

    @app.route("/api/clip/<clip_id>/user", methods=["POST"])
    def clip_user_state(clip_id: str):
        """Partial-update a clip's user overlay (clip-level for MVP).

        Per the `_window_user_state` seam, this state applies uniformly to
        every window of the clip. After writing the sidecar, every window
        row in Chroma is refreshed (no embed) so queries reflect the change.
        """
        body = request.json or {}
        library_path = (body.get("library") or request.args.get("library") or "")
        if not library_path:
            return jsonify({"ok": False, "reason": "no library path"}), 400
        library_root = Path(library_path)
        if not marker.is_library(library_root):
            return jsonify({"ok": False, "reason": "not a Smart Library root"}), 400

        partial = {k: v for k, v in body.items() if k != "library"}
        try:
            new_state = user.set_user_state(library_root, clip_id, **partial)
        except (TypeError, ValueError) as e:
            return jsonify({"ok": False, "reason": str(e)}), 400

        try:
            sync.update_one_metadata(library_root, clip_id)
        except Exception as e:  # noqa: BLE001
            log.warning("update_one_metadata failed for %s: %s", clip_id, e)

        return jsonify({"ok": True, "clip_id": clip_id, "state": new_state})

    @app.route("/api/clip/<clip_id>", methods=["GET"])
    def clip_detail(clip_id: str):
        library_path = request.args.get("library", "")
        if not library_path:
            abort(400)
        library_root = Path(library_path)
        if not marker.is_library(library_root):
            abort(400)
        return jsonify({
            "clip_id": clip_id,
            "normalize": sidecar.read_normalize(library_root, clip_id),
            "faces": sidecar.read_faces(library_root, clip_id),
            "caption": sidecar.read_caption(library_root, clip_id),
            "error": sidecar.read_error(library_root, clip_id),
            "user": user.get_user_state(library_root, clip_id),
        })

    # ── Thumbnails + video ────────────────────────────────────────────────────

    def _safe_hex(s: str) -> str:
        return "".join(ch for ch in s if ch in "0123456789abcdefABCDEF")

    def _safe_window_id(window_id: str) -> str:
        """Sanitize `<clip_id>:<int>` for filesystem use."""
        if ":" not in window_id:
            return ""
        clip_hex, ts = window_id.split(":", 1)
        clip_hex = _safe_hex(clip_hex)
        try:
            ts_i = int(ts)
        except ValueError:
            return ""
        if not clip_hex:
            return ""
        return f"{clip_hex}_{ts_i}"

    @app.route("/api/thumb", methods=["GET"])
    def thumb():
        """Clip-level poster JPG cached under `.cache/thumbnails/{clip_id}.jpg`."""
        library_path = request.args.get("library", "")
        clip_id = request.args.get("clip_id", "")
        rel = request.args.get("rel", "")
        try:
            duration_s = float(request.args.get("duration", "0") or 0)
        except ValueError:
            duration_s = 0.0
        if not library_path or not clip_id or not rel:
            abort(400)
        library_root = Path(library_path).resolve()
        if not marker.is_library(library_root):
            abort(400)
        safe_id = _safe_hex(clip_id)
        if not safe_id:
            abort(400)
        cache_dir = library_root / config.CACHE_DIR / "thumbnails"
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache_path = cache_dir / f"{safe_id}.jpg"
        if not cache_path.is_file():
            target = (library_root / rel).resolve()
            try:
                target.relative_to(library_root)
            except ValueError:
                abort(403)
            if not target.is_file():
                abort(404)
            at_s = max(0.0, duration_s * config.THUMBNAIL_AT_PCT) if duration_s > 0 else 1.0
            try:
                thumbnail._extract_poster(target, at_s, cache_path)
            except Exception:
                log.exception("thumb extract failed for %s", target)
                abort(500)
        return send_file(cache_path, mimetype="image/jpeg", conditional=True)

    @app.route("/api/window_thumb", methods=["GET"])
    def window_thumb():
        """Per-window JPG extracted at the window's mid-point and cached under
        `.cache/window_thumbnails/{clip_hex}_{start_ms}.jpg`.

        We use the mid-point rather than `caption.windows[i].frames_sampled_t_s[0]`
        for simplicity (no sidecar read needed at thumb time, no dependency on
        a captioned state). Visually equivalent for a 5s window thumbnail.
        """
        library_path = request.args.get("library", "")
        window_id = request.args.get("window_id", "")
        rel = request.args.get("rel", "")
        try:
            start_s = float(request.args.get("start", "0") or 0)
            end_s = float(request.args.get("end", "0") or 0)
        except ValueError:
            abort(400)
        if not library_path or not window_id or not rel:
            abort(400)
        if end_s <= start_s:
            abort(400)
        library_root = Path(library_path).resolve()
        if not marker.is_library(library_root):
            abort(400)
        safe = _safe_window_id(window_id)
        if not safe:
            abort(400)

        cache_dir = library_root / config.CACHE_DIR / "window_thumbnails"
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache_path = cache_dir / f"{safe}.jpg"
        if not cache_path.is_file():
            target = (library_root / rel).resolve()
            try:
                target.relative_to(library_root)
            except ValueError:
                abort(403)
            if not target.is_file():
                abort(404)
            at_s = (start_s + end_s) / 2.0
            try:
                thumbnail._extract_poster(target, at_s, cache_path)
            except Exception:
                log.exception("window thumb extract failed for %s @ %.2fs", target, at_s)
                abort(500)
        return send_file(cache_path, mimetype="image/jpeg", conditional=True)

    @app.route("/api/video", methods=["GET"])
    def video():
        """Stream a clip; client drives range playback via seek + timeupdate."""
        library_path = request.args.get("library", "")
        rel = request.args.get("rel", "")
        if not library_path or not rel:
            abort(400)
        library_root = Path(library_path).resolve()
        if not marker.is_library(library_root):
            abort(400)
        target = (library_root / rel).resolve()
        try:
            target.relative_to(library_root)
        except ValueError:
            abort(403)
        if not target.is_file():
            abort(404)
        return send_file(target, mimetype="video/mp4", conditional=True)

    return app


# ── CLI entrypoint ────────────────────────────────────────────────────────────

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m smart_library_v2.l4_app")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args(argv)
    app = create_app()
    app.run(host=args.host, port=args.port, debug=args.debug, threaded=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
