# Smart Library: local video library engine (MSc dissertation)

The code for my master's dissertation. It turns a folder of personal video clips into a searchable library, entirely on local hardware:

1. scans the folder and normalises filenames
2. detects and matches faces (InsightFace `buffalo_l`)
3. cuts clips into 5-second windows, picks sharp frames and captions them with a local vision-language model through Ollama
4. embeds the captions and clusters them with HDBSCAN
5. serves a Flask single-page UI with semantic search, person filters, cluster browsing and range playback

State is kept in per-clip sidecar files. The modules are layered by filename prefix: `l1_*` foundations, `l2_*` discovery, `l3_*` enrichment, `l4_*` persistence, pipeline and the web app (`l4_app.py`, `static/`, `templates/`).

Requires a running Ollama instance with a vision model and `nomic-embed-text`; hosts are set in `l1_config.py`.
