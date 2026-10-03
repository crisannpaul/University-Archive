// Smart Library v2 — window-row UI.
//
// MVP scope (task 8): hidden/favorite/tags stay clip-level. Toggling a
// favorite on any window of clip X marks every window of clip X. Per-window
// overlay (§1g) is the follow-up. Range playback is seek + stop (no loop,
// no auto-advance).

const STATE = {
  library: null,
  logSeq: 0,
  pollTimer: null,
  jobBusy: false,
  windows: [],                 // last fetched windows (browse mode)
  clusters: [],                // last fetched clusters
  unclusteredCount: 0,
  lastQueryHits: null,         // when set, grid shows hits instead of `windows`
  selectedCluster: null,       // active cluster_id filter (or null)
  selectedPeople: new Set(),
  selectedTags: new Set(),
  showHidden: false,
  favoritesOnly: false,
  groupByClip: false,
  tagVocab: [],
  detailWindowId: null,        // window currently shown in detail pane
  rightTab: "clusters",        // "clusters" | "detail"
};

// Inline SVG icons.
const ICON_EYE = `<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>`;
const ICON_EYE_OFF = `<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>`;
const ICON_STAR = `<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>`;
const ICON_STAR_FILLED = `<svg viewBox="0 0 24 24" width="16" height="16" fill="#f5c542" stroke="#f5c542" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>`;

const LS_KEY = "smart_library_root";

// ── DOM helpers ──────────────────────────────────────────────────────────────

function $(id) { return document.getElementById(id); }
function esc(s) {
  if (s === null || s === undefined) return "";
  return String(s)
    .replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;").replaceAll("'", "&#39;");
}
async function api(path, opts = {}) {
  const resp = await fetch(path, opts);
  return resp.json();
}

// ── Setup flow ───────────────────────────────────────────────────────────────

async function tryOpenPath(path) {
  const result = await api("/api/library/check", {
    method: "POST", headers: {"Content-Type": "application/json"},
    body: JSON.stringify({path}),
  });
  const status = $("setup-status");
  $("init-prompt").classList.add("hidden");
  if (!result.ok) {
    status.className = "status-line err";
    status.textContent = result.reason;
    return;
  }
  if (!result.is_library) {
    status.className = "status-line";
    status.textContent = `${result.path} — no marker file present.`;
    $("init-prompt").classList.remove("hidden");
    $("init-prompt").dataset.path = result.path;
    return;
  }
  status.className = "status-line ok";
  status.textContent = `Opened: ${result.path}`;
  STATE.library = result.path;
  localStorage.setItem(LS_KEY, result.path);
  showMain();
}

async function initLibrary(path) {
  const result = await api("/api/library/init", {
    method: "POST", headers: {"Content-Type": "application/json"},
    body: JSON.stringify({path}),
  });
  if (!result.ok) {
    const status = $("setup-status");
    status.className = "status-line err";
    status.textContent = result.reason;
    return;
  }
  await tryOpenPath(result.path);
}

function showMain() {
  $("setup-panel").classList.add("hidden");
  $("main").classList.remove("hidden");
  refreshAll();
  if (STATE.pollTimer) clearInterval(STATE.pollTimer);
  STATE.pollTimer = setInterval(pollTick, 800);
}

function showSetup() {
  if (STATE.pollTimer) { clearInterval(STATE.pollTimer); STATE.pollTimer = null; }
  $("main").classList.add("hidden");
  $("setup-panel").classList.remove("hidden");
  $("init-prompt").classList.add("hidden");
  $("setup-status").textContent = "";
  $("setup-status").className = "status-line";
  $("path-input").focus();
  $("path-input").select();
}

// ── Polling: logs + job + stats ──────────────────────────────────────────────

async function pollTick() {
  if (!STATE.library) return;
  const logs = await api(`/api/logs?since=${STATE.logSeq}`);
  if (logs.lines && logs.lines.length) {
    appendLogs(logs.lines);
    STATE.logSeq = logs.latest;
  }
  const job = await api("/api/job");
  const wasBusy = STATE.jobBusy;
  STATE.jobBusy = job.status === "running";
  setOpButtonsEnabled(!STATE.jobBusy);
  if (wasBusy && !STATE.jobBusy) {
    // Job just finished — refresh views.
    refreshStats();
    refreshWindows();
    refreshClusters();
  }
  if (!STATE.jobBusy && Math.random() < 0.05) {
    refreshStats();
  }
}

function appendLogs(lines) {
  const el = $("log");
  for (const l of lines) {
    const div = document.createElement("div");
    if (l.level === "ERROR") div.className = "err";
    div.textContent = l.line;
    el.appendChild(div);
  }
  el.scrollTop = el.scrollHeight;
}

async function refreshStats() {
  const s = await api(`/api/stats?library=${encodeURIComponent(STATE.library)}`);
  $("status-total").textContent      = `${s.total_clips || 0} clips`;
  $("status-windows").textContent    = `${s.total_windows || 0} windows`;
  $("status-clusters").textContent   = `${s.total_clusters || 0} clusters`;
  $("status-faced").textContent      = `${(s.pct_faced     || 0).toFixed(0)}% faced`;
  $("status-captioned").textContent  = `${(s.pct_captioned || 0).toFixed(0)}% captioned`;
  $("status-errors").textContent     = `${s.errors || 0} errors`;
}

async function refreshAll() {
  await refreshStats();
  await loadPeople();
  await loadTags();
  await refreshWindows();
  await refreshClusters();
}

// ── Person filter ────────────────────────────────────────────────────────────

async function loadPeople() {
  const r = await api(`/api/people?library=${encodeURIComponent(STATE.library)}`);
  const names = r.people || [];
  const wrap = $("people-filter");
  const chips = $("people-chips");
  chips.innerHTML = "";
  if (!names.length) {
    wrap.classList.add("hidden");
    return;
  }
  wrap.classList.remove("hidden");
  const known = new Set(names.map(n => n.toLowerCase()));
  for (const sel of [...STATE.selectedPeople]) {
    if (!known.has(sel)) STATE.selectedPeople.delete(sel);
  }
  for (const name of names) {
    const chip = document.createElement("button");
    chip.className = "person-chip";
    chip.type = "button";
    chip.textContent = name;
    chip.dataset.name = name.toLowerCase();
    if (STATE.selectedPeople.has(chip.dataset.name)) chip.classList.add("selected");
    chip.addEventListener("click", () => {
      const key = chip.dataset.name;
      if (STATE.selectedPeople.has(key)) {
        STATE.selectedPeople.delete(key);
        chip.classList.remove("selected");
      } else {
        STATE.selectedPeople.add(key);
        chip.classList.add("selected");
      }
      refreshWindows();
    });
    chips.appendChild(chip);
  }
}

function applyPeopleFilter(windows) {
  if (STATE.selectedPeople.size === 0) return windows;
  const sel = [...STATE.selectedPeople];
  return windows.filter(w => {
    const have = (w.people || []).map(s => String(s).toLowerCase());
    return sel.every(s => have.includes(s));
  });
}

// ── Tag filter ───────────────────────────────────────────────────────────────

async function loadTags() {
  const r = await api(`/api/tags?library=${encodeURIComponent(STATE.library)}`);
  const tags = r.tags || [];
  STATE.tagVocab = tags;
  const dl = $("tag-vocab");
  if (dl) dl.innerHTML = tags.map(t => `<option value="${esc(t)}"></option>`).join("");
  const wrap = $("tag-filter");
  const chips = $("tag-chips");
  chips.innerHTML = "";
  if (!tags.length) {
    wrap.classList.add("hidden");
    return;
  }
  wrap.classList.remove("hidden");
  const known = new Set(tags);
  for (const sel of [...STATE.selectedTags]) {
    if (!known.has(sel)) STATE.selectedTags.delete(sel);
  }
  for (const tag of tags) {
    const chip = document.createElement("button");
    chip.className = "tag-chip";
    chip.type = "button";
    chip.textContent = tag;
    chip.dataset.tag = tag;
    if (STATE.selectedTags.has(tag)) chip.classList.add("selected");
    chip.addEventListener("click", () => {
      if (STATE.selectedTags.has(tag)) {
        STATE.selectedTags.delete(tag);
        chip.classList.remove("selected");
      } else {
        STATE.selectedTags.add(tag);
        chip.classList.add("selected");
      }
      refreshWindows();
    });
    chips.appendChild(chip);
  }
}

function applyTagFilter(windows) {
  if (STATE.selectedTags.size === 0) return windows;
  const sel = [...STATE.selectedTags];
  return windows.filter(w => {
    const have = new Set((w.tags || []).filter(Boolean));
    return sel.every(t => have.has(t));
  });
}

function applyFavoritesFilter(windows) {
  if (!STATE.favoritesOnly) return windows;
  return windows.filter(w => !!w.favorite);
}

function applyAllFilters(windows) {
  return applyFavoritesFilter(applyTagFilter(applyPeopleFilter(windows)));
}

// ── Window browser ───────────────────────────────────────────────────────────

async function refreshWindows() {
  let list;
  if (STATE.lastQueryHits !== null) {
    list = STATE.lastQueryHits;
  } else {
    const params = new URLSearchParams({
      library: STATE.library,
      show_hidden: STATE.showHidden ? "1" : "0",
    });
    if (STATE.selectedCluster !== null) {
      params.set("cluster", String(STATE.selectedCluster));
    }
    const result = await api(`/api/windows?${params.toString()}`);
    STATE.windows = result.windows || [];
    list = STATE.windows;
  }
  renderWindowList(applyAllFilters(list), STATE.lastQueryHits !== null);
  updateActiveClusterChip();
}

function updateActiveClusterChip() {
  const wrap = $("active-cluster");
  if (STATE.selectedCluster === null) {
    wrap.classList.add("hidden");
    return;
  }
  wrap.classList.remove("hidden");
  const cid = STATE.selectedCluster;
  const label = cid === -1 ? "Noise" : `Cluster ${cid}`;
  $("active-cluster-name").textContent = label;
}

function renderWindowList(windows, isQuery) {
  const grid = $("clip-grid");
  grid.innerHTML = "";
  $("result-count").textContent = `${windows.length} window${windows.length === 1 ? "" : "s"}`;

  if (STATE.groupByClip) {
    // Group windows by clip_id; render one clip-header + horizontal strip.
    const buckets = new Map();
    for (const w of windows) {
      if (!buckets.has(w.clip_id)) buckets.set(w.clip_id, []);
      buckets.get(w.clip_id).push(w);
    }
    // Sort: chronological by first window's capture date.
    const groups = [...buckets.entries()].sort((a, b) => {
      const ca = a[1][0].capture_datetime_utc || "";
      const cb = b[1][0].capture_datetime_utc || "";
      return ca < cb ? -1 : ca > cb ? 1 : 0;
    });
    let lastDay = null;
    for (const [, ws] of groups) {
      ws.sort((a, b) => a.window_start_s - b.window_start_s);
      const day = (ws[0].capture_datetime_utc || "").slice(0, 10) || "(undated)";
      if (day !== lastDay) {
        const h = document.createElement("div");
        h.className = "date-header";
        h.textContent = day;
        grid.appendChild(h);
        lastDay = day;
      }
      grid.appendChild(makeClipGroup(ws));
    }
    return;
  }

  const viewMode = $("view-mode").value;
  if (viewMode === "tree") {
    const buckets = new Map();
    for (const w of windows) {
      const key = w.location || "(root)";
      if (!buckets.has(key)) buckets.set(key, []);
      buckets.get(key).push(w);
    }
    for (const [key, list] of [...buckets.entries()].sort()) {
      const h = document.createElement("div");
      h.className = "date-header";
      h.textContent = `${key} — ${list.length}`;
      grid.appendChild(h);
      list.forEach(w => grid.appendChild(makeWindowCard(w)));
    }
    return;
  }

  // Chronological default — group by day.
  let lastDay = null;
  for (const w of windows) {
    const day = (w.capture_datetime_utc || "").slice(0, 10) || "(undated)";
    if (day !== lastDay) {
      const h = document.createElement("div");
      h.className = "date-header";
      h.textContent = day;
      grid.appendChild(h);
      lastDay = day;
    }
    grid.appendChild(makeWindowCard(w));
  }
}

// ── Card rendering ───────────────────────────────────────────────────────────

const MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];

function humanDateTime(iso) {
  if (!iso) return "";
  const d = new Date(iso);
  if (isNaN(d)) return "";
  const HH = String(d.getHours()).padStart(2, "0");
  const MM = String(d.getMinutes()).padStart(2, "0");
  return `${MONTHS[d.getMonth()]} ${d.getDate()} · ${HH}:${MM}`;
}

function windowIndex(w) {
  // Approximate window index from start_s / 5s window. Display only.
  return Math.round((w.window_start_s || 0) / 5);
}

function windowThumbUrl(w) {
  return `/api/window_thumb?library=${encodeURIComponent(STATE.library)}`
    + `&window_id=${encodeURIComponent(w.window_id)}`
    + `&rel=${encodeURIComponent(w.relative_path)}`
    + `&start=${encodeURIComponent(w.window_start_s)}`
    + `&end=${encodeURIComponent(w.window_end_s)}`;
}

function clipThumbUrl(w) {
  return `/api/thumb?library=${encodeURIComponent(STATE.library)}`
    + `&clip_id=${encodeURIComponent(w.clip_id)}`
    + `&rel=${encodeURIComponent(w.relative_path)}`
    + `&duration=${encodeURIComponent(w.duration_s || 0)}`;
}

function makeWindowCard(w) {
  const card = document.createElement("div");
  card.className = "clip-card";
  if (w.hidden) card.classList.add("is-hidden");
  if (STATE.detailWindowId === w.window_id) card.classList.add("selected");
  card.dataset.windowId = w.window_id;
  card.dataset.clipId = w.clip_id;
  card.title = `${w.clip_filename} · W${windowIndex(w)}`;

  // Title: vibe → display fallback to filename + W##.
  let title = w.vibe || "";
  if (!title) {
    if (w.location) {
      title = w.event_path ? `${w.location} · ${w.event_path}` : w.location;
    } else {
      title = `${w.clip_filename} · W${windowIndex(w)}`;
    }
  }

  const dateLine = humanDateTime(w.capture_datetime_utc);
  const range = `${w.window_start_s.toFixed(1)}–${w.window_end_s.toFixed(1)}s`;

  let badges = "";
  if (w.mood) badges += `<span class="badge mood">${esc(w.mood)}</span>`;
  if (w.scene_type) badges += `<span class="badge">${esc(w.scene_type)}</span>`;
  if (w.aesthetic_score !== null && w.aesthetic_score !== undefined) {
    badges += `<span class="badge">aes ${(+w.aesthetic_score).toFixed(1)}</span>`;
  }
  if (w.distance !== undefined && w.distance !== null) {
    badges += `<span class="badge dist">d=${(+w.distance).toFixed(3)}</span>`;
  }

  const hideIcon = w.hidden ? ICON_EYE_OFF : ICON_EYE;
  const hideLabel = w.hidden ? "Unhide clip" : "Hide clip (all windows)";
  const favIcon = w.favorite ? ICON_STAR_FILLED : ICON_STAR;
  const favLabel = w.favorite ? "Remove favorite" : "Favorite clip (all windows)";

  const clusterBadge = (w.cluster_id !== null && w.cluster_id !== undefined)
    ? `<button type="button" class="cluster-badge" data-cluster="${w.cluster_id}">${w.cluster_id === -1 ? "noise" : "c" + w.cluster_id}</button>`
    : "";
  const lqBadge = w.low_quality_samples ? `<span class="lq-badge" title="low-quality frame samples">LQ</span>` : "";
  const mergedBadge = (w.n_windows && w.n_windows > 1)
    ? `<span class="merged-badge" title="${w.n_windows} adjacent windows merged">↔ ${w.n_windows}</span>`
    : "";
  const windowLabel = (w.n_windows && w.n_windows > 1)
    ? `W${windowIndex(w)}+`
    : `W${windowIndex(w)}`;

  card.innerHTML = `
    <div class="thumb">
      <img loading="lazy" src="${esc(windowThumbUrl(w))}" alt="" />
      <span class="window-badge">${windowLabel}</span>
      ${mergedBadge}
      ${lqBadge}
      <span class="range-pill">${esc(range)}</span>
      ${clusterBadge}
      <div class="card-overlay">
        <button type="button" class="fav-toggle${w.favorite ? " on" : ""}" title="${esc(favLabel)}" aria-label="${esc(favLabel)}">${favIcon}</button>
        <button type="button" class="hide-toggle" title="${esc(hideLabel)}" aria-label="${esc(hideLabel)}">${hideIcon}</button>
      </div>
    </div>
    <div class="card-body">
      <div class="name">${esc(title)}</div>
      ${dateLine ? `<div class="meta">${esc(dateLine)}</div>` : ""}
      ${w.description_subjects_action ? `<div class="meta vibe">${esc(w.description_subjects_action)}</div>` : ""}
      <div class="filename">${esc(w.clip_filename)}</div>
      <div class="badges">${badges}</div>
    </div>
  `;

  card.addEventListener("click", (ev) => {
    if (ev.target.closest(".hide-toggle")) return;
    if (ev.target.closest(".fav-toggle")) return;
    if (ev.target.closest(".cluster-badge")) {
      const cid = parseInt(ev.target.closest(".cluster-badge").dataset.cluster, 10);
      setClusterFilter(cid);
      return;
    }
    showWindowDetail(w);
  });
  card.querySelector(".hide-toggle").addEventListener("click", (ev) => {
    ev.stopPropagation();
    toggleHidden(w);
  });
  card.querySelector(".fav-toggle").addEventListener("click", (ev) => {
    ev.stopPropagation();
    toggleFavorite(w);
  });
  return card;
}

function makeClipGroup(windows) {
  // Header + horizontal strip of window thumbs for one clip.
  const w0 = windows[0];
  const group = document.createElement("div");
  group.className = "clip-group";

  const title = (w0.location ? (w0.event_path ? `${w0.location} · ${w0.event_path}` : w0.location)
                              : w0.clip_filename);
  const dateLine = humanDateTime(w0.capture_datetime_utc);
  const dur = w0.duration_s ? `${(+w0.duration_s).toFixed(1)}s` : "";
  const sub = [dateLine, dur, `${windows.length} window${windows.length === 1 ? "" : "s"}`]
    .filter(Boolean).join(" · ");

  group.innerHTML = `
    <div class="group-head">
      <div class="group-title">${esc(title)}</div>
      <div class="group-sub">${esc(sub)} · ${esc(w0.clip_filename)}</div>
    </div>
    <div class="window-strip"></div>
  `;
  const strip = group.querySelector(".window-strip");
  for (const w of windows) {
    const tile = document.createElement("div");
    tile.className = "strip-tile";
    if (STATE.detailWindowId === w.window_id) tile.classList.add("selected");
    tile.title = `W${windowIndex(w)} · ${w.window_start_s.toFixed(1)}–${w.window_end_s.toFixed(1)}s · ${w.vibe || ""}`;
    tile.innerHTML = `
      <img loading="lazy" src="${esc(windowThumbUrl(w))}" alt="" />
      <span class="strip-label">W${windowIndex(w)}</span>
    `;
    tile.addEventListener("click", () => showWindowDetail(w));
    strip.appendChild(tile);
  }
  return group;
}

// ── Toggles (clip-level for MVP) ─────────────────────────────────────────────

async function postClipUser(clipId, partial) {
  const r = await api(`/api/clip/${encodeURIComponent(clipId)}/user`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({library: STATE.library, ...partial}),
  });
  if (!r || !r.ok) {
    appendLogs([{level: "ERROR", line: `clip user update failed: ${r && r.reason || "unknown"}`}]);
    return null;
  }
  return r.state;
}

function applyClipUserToWindows(clipId, state) {
  // Update STATE.windows and STATE.lastQueryHits in place.
  const apply = (rows) => {
    for (const w of rows) {
      if (w.clip_id !== clipId) continue;
      w.hidden = !!state.hidden;
      w.favorite = !!state.favorite;
      w.tags = Array.isArray(state.tags) ? state.tags.slice() : (w.tags || []);
    }
  };
  apply(STATE.windows);
  if (STATE.lastQueryHits) apply(STATE.lastQueryHits);
}

async function toggleFavorite(w) {
  const newFav = !w.favorite;
  const state = await postClipUser(w.clip_id, {favorite: newFav});
  if (!state) return;
  applyClipUserToWindows(w.clip_id, state);
  refreshWindows();
}

async function toggleHidden(w) {
  const newHidden = !w.hidden;
  const state = await postClipUser(w.clip_id, {hidden: newHidden});
  if (!state) return;
  applyClipUserToWindows(w.clip_id, state);
  // Re-fetch because show_hidden=false filters the dataset server-side.
  if (STATE.lastQueryHits !== null) runQuery();
  else refreshWindows();
}

// ── Cluster sidebar ──────────────────────────────────────────────────────────

async function refreshClusters() {
  const r = await api(`/api/clusters?library=${encodeURIComponent(STATE.library)}`);
  STATE.clusters = r.clusters || [];
  STATE.unclusteredCount = r.unclustered_count || 0;
  renderClusterList();
}

function renderClusterList() {
  const wrap = $("cluster-list");
  wrap.classList.remove("muted");
  wrap.innerHTML = "";

  if (!STATE.clusters.length && !STATE.unclusteredCount) {
    wrap.classList.add("muted");
    wrap.textContent = "Run Cluster (or Run all) to populate.";
    return;
  }

  if (STATE.selectedCluster !== null) {
    const showAll = document.createElement("button");
    showAll.className = "link-btn";
    showAll.textContent = "← Show all windows";
    showAll.style.marginBottom = "6px";
    showAll.addEventListener("click", () => clearClusterFilter());
    wrap.appendChild(showAll);
  }

  for (const c of STATE.clusters) {
    const card = document.createElement("div");
    card.className = "cluster-card";
    if (c.cluster_id === -1) card.classList.add("noise");
    if (STATE.selectedCluster === c.cluster_id) card.classList.add("active");
    const label = c.cluster_id === -1 ? "Noise" : `Cluster ${c.cluster_id}`;
    const repThumbUrl = `/api/window_thumb?library=${encodeURIComponent(STATE.library)}`
      + `&window_id=${encodeURIComponent(c.representative_window_id)}`
      + `&rel=${encodeURIComponent(c.representative_relative_path)}`
      + `&start=${encodeURIComponent(c.representative_window_start_s)}`
      + `&end=${encodeURIComponent(c.representative_window_end_s)}`;
    const tagBits = [c.top_mood, c.top_scene_type].filter(Boolean).join(" · ");
    card.innerHTML = `
      <img class="cluster-thumb" loading="lazy" src="${esc(repThumbUrl)}" alt="" />
      <div class="cluster-meta">
        <div class="cluster-title">
          <span>${esc(label)}</span>
          <span class="cluster-count">${c.count} window${c.count === 1 ? "" : "s"}</span>
        </div>
        ${c.representative_vibe ? `<div class="cluster-vibe">${esc(c.representative_vibe)}</div>` : ""}
        ${tagBits ? `<div class="cluster-tags">${esc(tagBits)}</div>` : ""}
      </div>
    `;
    card.addEventListener("click", () => setClusterFilter(c.cluster_id));
    wrap.appendChild(card);
  }

  if (STATE.unclusteredCount > 0) {
    const u = document.createElement("div");
    u.className = "cluster-unclustered";
    u.textContent = `${STATE.unclusteredCount} window${STATE.unclusteredCount === 1 ? "" : "s"} not yet clustered`;
    wrap.appendChild(u);
  }
}

function setClusterFilter(cid) {
  STATE.selectedCluster = cid;
  STATE.lastQueryHits = null;  // cluster filter exits query mode
  $("query-input").value = "";
  refreshWindows();
  renderClusterList();
}

function clearClusterFilter() {
  STATE.selectedCluster = null;
  refreshWindows();
  renderClusterList();
}

// ── Window detail (right pane) ───────────────────────────────────────────────

async function showWindowDetail(w) {
  STATE.detailWindowId = w.window_id;
  setRightTab("detail");
  // Re-render the grid to update selected-card outline.
  renderWindowList(applyAllFilters(STATE.lastQueryHits !== null ? STATE.lastQueryHits : STATE.windows),
                   STATE.lastQueryHits !== null);

  const detail = $("window-detail");
  detail.classList.remove("muted");
  detail.innerHTML = `<div>Loading…</div>`;

  const data = await api(`/api/clip/${encodeURIComponent(w.clip_id)}?library=${encodeURIComponent(STATE.library)}`);
  if (STATE.detailWindowId !== w.window_id) return;

  // Find the matching window inside caption.json.
  const captionWindows = ((data.caption || {}).windows) || [];
  const matched = captionWindows.find(cw =>
    Math.abs((cw.window_start_s || 0) - w.window_start_s) < 0.01
  ) || {};
  const fields = matched.fields || {};
  const desc = fields.description || {};
  const u = data.user || {hidden: false, favorite: false, tags: []};
  applyClipUserToWindows(w.clip_id, u);

  const videoUrl = `/api/video?library=${encodeURIComponent(STATE.library)}&rel=${encodeURIComponent(w.relative_path)}`;
  const peopleStr = (w.people || []).join(", ");

  const tagsHTML = (u.tags || []).map(t =>
    `<span class="tag-pill" data-tag="${esc(t)}">${esc(t)}<button type="button" class="tag-remove" aria-label="Remove tag ${esc(t)}">×</button></span>`
  ).join("");

  detail.innerHTML = `
    <div class="detail-banner">
      W${windowIndex(w)} · ${w.window_start_s.toFixed(2)}–${w.window_end_s.toFixed(2)}s
      ${matched.low_quality_samples ? `· <span style="color: var(--error)">low-quality samples</span>` : ""}
      ${(w.cluster_id !== null && w.cluster_id !== undefined)
        ? `· <a href="#" id="goto-cluster" class="link-btn">${w.cluster_id === -1 ? "noise" : "cluster " + w.cluster_id}</a>`
        : ""}
    </div>
    <video src="${esc(videoUrl)}" controls preload="metadata"></video>
    <div class="range-controls">
      <button type="button" class="btn-sm" id="btn-replay">Replay window</button>
      <button type="button" class="btn-sm secondary" id="btn-free">Free play</button>
    </div>
    <div class="field"><span class="k">filename</span><div class="v">${esc(w.clip_filename)}</div></div>
    <div class="field"><span class="k">path</span><div class="v">${esc(w.relative_path)}</div></div>
    <div class="field"><span class="k">capture</span><div class="v">${esc(w.capture_datetime_utc)}</div></div>
    <div class="field"><span class="k">people (window)</span><div class="v">${esc(peopleStr)}</div></div>
    <div class="field tag-editor">
      <span class="k">tags (clip-level)</span>
      <div class="v">
        <div class="tag-pills">${tagsHTML || `<span class="muted">no tags</span>`}</div>
        <div class="tag-add-row">
          <input id="tag-input" type="text" list="tag-vocab" placeholder="Add tag (Enter)…" autocomplete="off" />
          <button id="tag-add-btn" type="button">Add</button>
        </div>
      </div>
    </div>
    <div class="field"><span class="k">vibe</span><div class="v">${esc(fields.vibe || "")}</div></div>
    <div class="field"><span class="k">scene</span><div class="v">${esc(fields.scene || "")}</div></div>
    <div class="field"><span class="k">subjects / action</span><div class="v">${esc(desc.subjects_action || "")}</div></div>
    <div class="field"><span class="k">framing</span><div class="v">${esc(desc.framing || "")}</div></div>
    <div class="field"><span class="k">mood / energy</span><div class="v">${esc(fields.mood || "")} / ${esc(fields.energy_level || "")}</div></div>
    <div class="field"><span class="k">scene_type</span><div class="v">${esc(fields.scene_type || "")}</div></div>
    <div class="field"><span class="k">aesthetic</span><div class="v">${esc(fields.aesthetic_score)}</div></div>
    <div class="field"><span class="k">notes</span><div class="v">${esc(fields.notes || "")}</div></div>
    <div class="field"><span class="k">window_id</span><div class="v">${esc(w.window_id)}</div></div>
    ${data.error ? `<div class="field"><span class="k">last error</span><div class="v">${esc(data.error.error)}</div></div>` : ""}
  `;

  // Wire range playback — seek + stop at end_s.
  const video = detail.querySelector("video");
  let stopAtEnd = true;
  function pinToWindow() {
    if (!stopAtEnd) return;
    if (video.currentTime + 0.05 < w.window_start_s ||
        video.currentTime > w.window_end_s + 0.05) {
      video.currentTime = w.window_start_s;
    }
  }
  function onTimeUpdate() {
    if (!stopAtEnd) return;
    if (video.currentTime >= w.window_end_s - 0.05) {
      video.pause();
      video.currentTime = w.window_start_s;
    }
  }
  video.addEventListener("loadedmetadata", () => { video.currentTime = w.window_start_s; });
  video.addEventListener("timeupdate", onTimeUpdate);
  video.addEventListener("seeked", pinToWindow);

  detail.querySelector("#btn-replay").addEventListener("click", () => {
    stopAtEnd = true;
    video.currentTime = w.window_start_s;
    video.play();
  });
  detail.querySelector("#btn-free").addEventListener("click", () => {
    stopAtEnd = false;
  });
  const gotoCluster = detail.querySelector("#goto-cluster");
  if (gotoCluster) {
    gotoCluster.addEventListener("click", (e) => {
      e.preventDefault();
      setClusterFilter(w.cluster_id);
      setRightTab("clusters");
    });
  }

  // Tag handlers (clip-level for MVP).
  detail.querySelectorAll(".tag-remove").forEach(btn => {
    btn.addEventListener("click", () => {
      const tag = btn.parentElement.dataset.tag;
      removeTag(w, tag);
    });
  });
  const input = $("tag-input");
  const addBtn = $("tag-add-btn");
  const submitTag = () => {
    const raw = (input.value || "").trim();
    if (!raw) return;
    addTag(w, raw);
    input.value = "";
  };
  addBtn.addEventListener("click", submitTag);
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") { e.preventDefault(); submitTag(); }
  });
}

async function writeClipTags(w, newTags) {
  const state = await postClipUser(w.clip_id, {tags: newTags});
  if (!state) return null;
  return state.tags || [];
}

async function addTag(w, raw) {
  const current = w.tags || [];
  const next = [...current, raw];
  const merged = await writeClipTags(w, next);
  if (merged === null) return;
  await applyTagUpdateLocal(w, merged);
}

async function removeTag(w, tag) {
  const next = (w.tags || []).filter(t => t !== tag);
  const merged = await writeClipTags(w, next);
  if (merged === null) return;
  await applyTagUpdateLocal(w, merged);
}

async function applyTagUpdateLocal(w, mergedTags) {
  applyClipUserToWindows(w.clip_id, {hidden: w.hidden, favorite: w.favorite, tags: mergedTags});
  await loadTags();
  if (STATE.detailWindowId === w.window_id) {
    showWindowDetail({...w, tags: mergedTags});
  }
  refreshWindows();
}

// ── Right-pane tabs ──────────────────────────────────────────────────────────

function setRightTab(tab) {
  STATE.rightTab = tab;
  document.querySelectorAll(".tab-btn").forEach(b => {
    b.classList.toggle("active", b.dataset.tab === tab);
  });
  $("tab-clusters").classList.toggle("hidden", tab !== "clusters");
  $("tab-detail").classList.toggle("hidden", tab !== "detail");
}

// ── Op runner ────────────────────────────────────────────────────────────────

async function runOp(op) {
  if (!STATE.library) return;
  const target = $("scope-select").value === "library" ? null : $("scope-target").value || null;
  const body = {
    op, library: STATE.library, target,
    force: $("opt-force").checked,
    dry_run: $("opt-dry").checked,
    retry_errors: $("opt-retry").checked,
  };
  const r = await api("/api/op", {
    method: "POST", headers: {"Content-Type": "application/json"},
    body: JSON.stringify(body),
  });
  if (!r.ok) appendLogs([{level: "ERROR", line: `op rejected: ${r.reason}`}]);
}

function setOpButtonsEnabled(enabled) {
  document.querySelectorAll(".op-buttons button").forEach(b => b.disabled = !enabled);
}

// ── Query bar ────────────────────────────────────────────────────────────────

async function runQuery() {
  const q = $("query-input").value.trim();
  if (!q) { clearQuery(); return; }
  const sh = STATE.showHidden ? 1 : 0;
  const r = await api(
    `/api/query?library=${encodeURIComponent(STATE.library)}&q=${encodeURIComponent(q)}&k=15&show_hidden=${sh}`
  );
  // /api/query returns ranges by default (§1c adjacent-merge). Each hit:
  //   {clip_id, start_s, end_s, best_distance, best_window_id,
  //    best_metadata, best_document, constituent_ids[], constituent_metas[],
  //    n_windows}
  // We map to the same shape as a window row so makeWindowCard can render
  // either browse-windows or query-ranges without branching.
  const hits = (r.hits || []).map(rng => {
    const m = rng.best_metadata || rng.metadata || {};
    return {
      window_id: rng.best_window_id || rng.window_id,
      clip_id: rng.clip_id || (rng.best_window_id || rng.window_id || "").split(":")[0],
      distance: rng.best_distance !== undefined ? rng.best_distance : rng.distance,
      // Span = merged range (NOT the representative window's bounds). The
      // range pill + range-player on detail open use these.
      window_start_s: +(rng.start_s !== undefined ? rng.start_s : (m.window_start_s || 0)),
      window_end_s:   +(rng.end_s   !== undefined ? rng.end_s   : (m.window_end_s   || 0)),
      n_windows: rng.n_windows || 1,
      constituent_ids: rng.constituent_ids || [rng.window_id || rng.best_window_id],
      clip_filename: m.clip_filename || "",
      relative_path: m.relative_path || "",
      location: m.location || "",
      event_path: m.event_path || "",
      capture_datetime_utc: m.capture_datetime_utc || "",
      duration_s: m.duration_s || 0,
      is_cut: m.is_cut,
      source_clip_name: m.source_clip_name || "",
      people: (m.people || "").split(",").filter(Boolean),
      description_subjects_action: m.description_subjects_action || "",
      description_framing: m.description_framing || "",
      scene: m.scene || "", vibe: m.vibe || "",
      mood: m.mood || "", energy_level: m.energy_level || "",
      scene_type: m.scene_type || "",
      aesthetic_score: m.aesthetic_score,
      low_quality_samples: !!m.low_quality_samples,
      cluster_id: (m.cluster_id !== undefined ? m.cluster_id : null),
      hidden: !!m.hidden, favorite: !!m.favorite,
      tags: (m.tags || "").split(",").filter(Boolean),
    };
  });
  STATE.lastQueryHits = hits;
  // Query mode exits cluster filter for clarity.
  STATE.selectedCluster = null;
  renderClusterList();
  renderWindowList(applyAllFilters(hits), true);
  updateActiveClusterChip();
}

function clearQuery() {
  STATE.lastQueryHits = null;
  $("query-input").value = "";
  refreshWindows();
}

// ── Wire up ──────────────────────────────────────────────────────────────────

window.addEventListener("DOMContentLoaded", () => {
  const last = localStorage.getItem(LS_KEY);
  if (last) {
    $("path-input").value = last;
    tryOpenPath(last);
  }

  $("btn-open").addEventListener("click", () => {
    tryOpenPath($("path-input").value.trim());
  });
  $("path-input").addEventListener("keydown", (e) => {
    if (e.key === "Enter") $("btn-open").click();
  });
  $("btn-init").addEventListener("click", () => {
    initLibrary($("init-prompt").dataset.path);
  });
  $("btn-init-cancel").addEventListener("click", () => {
    $("init-prompt").classList.add("hidden");
  });
  $("btn-change-library").addEventListener("click", () => {
    // Keep the remembered path in the input so the user can edit it; they
    // can either type a new path or clear it. localStorage is only updated
    // once a successful open lands.
    showSetup();
  });

  $("scope-select").addEventListener("change", (e) => {
    if (e.target.value === "library") {
      $("scope-target").classList.add("hidden");
    } else {
      $("scope-target").classList.remove("hidden");
      $("scope-target").placeholder = e.target.value === "folder"
        ? "Folder relative to library root (e.g. Ibiza)"
        : "Clip relative path (e.g. Ibiza/20260416_140547_a3f5e8.MP4)";
    }
  });

  document.querySelectorAll(".op-buttons button").forEach(b => {
    b.addEventListener("click", () => runOp(b.dataset.op));
  });

  $("btn-query").addEventListener("click", runQuery);
  $("query-input").addEventListener("keydown", (e) => {
    if (e.key === "Enter") runQuery();
  });
  $("btn-clear-query").addEventListener("click", clearQuery);

  $("view-mode").addEventListener("change", () => refreshWindows());
  $("group-by-clip").addEventListener("change", (e) => {
    STATE.groupByClip = !!e.target.checked;
    refreshWindows();
  });
  $("show-hidden").addEventListener("change", (e) => {
    STATE.showHidden = !!e.target.checked;
    if (STATE.lastQueryHits !== null) runQuery();
    else refreshWindows();
  });
  $("favorites-only").addEventListener("change", (e) => {
    STATE.favoritesOnly = !!e.target.checked;
    refreshWindows();
  });
  $("btn-clear-cluster").addEventListener("click", () => clearClusterFilter());

  document.querySelectorAll(".tab-btn").forEach(b => {
    b.addEventListener("click", () => setRightTab(b.dataset.tab));
  });

  $("status-errors").addEventListener("click", async () => {
    if (!STATE.library) return;
    const r = await api(`/api/errors?library=${encodeURIComponent(STATE.library)}`);
    const lines = (r.errors || []).map(e =>
      ({level: "ERROR", line: `[${e.operation}] ${e.clip_filename}: ${e.error}`})
    );
    if (!lines.length) appendLogs([{level: "INFO", line: "no errors recorded"}]);
    else appendLogs(lines);
  });
});
