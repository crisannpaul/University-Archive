"""Smart Library engine — the v0 video library pipeline.

Layered module structure (see Documentation/smart-library-build-order.md):
  Layer 1 — Foundations:    config, identity, filename, marker, sidecar, logger
  Layer 2 — Discovery:      discover, sanitize, thumbnail, rename
  Layer 3 — Enrichment:     scan_faces, rematch_faces, annotate, scan_caption
  Layer 4 — Persistence:    sync, apply_names, pipeline, app
"""
