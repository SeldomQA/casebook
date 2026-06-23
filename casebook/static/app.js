const SIDEBAR_STORAGE_KEY = "casebook.sidebarWidth";
const SIDEBAR_MIN_WIDTH = 260;
const SIDEBAR_MAX_WIDTH = 560;

const state = {
  summary: null,
  tree: [],
  marks: {},
  currentFile: null,
  currentData: null,
  selectedCaseId: null,
  expandedCaseIds: new Set(),
  dirty: false,
  pendingReload: false,
  filter: "all",
  query: "",
};

const els = {};

document.addEventListener("DOMContentLoaded", () => {
  bindElements();
  restoreSidebarWidth();
  bindEvents();
  boot();
});

function bindElements() {
  [
    "scanDirs",
    "summaryText",
    "treePanel",
    "sidebarToggle",
    "sidebarResizer",
    "refreshButton",
    "reloadNotice",
    "reloadNowButton",
    "emptyState",
    "fileView",
    "fileMeta",
    "metrics",
    "caseSearch",
    "priorityFilters",
    "caseRows",
    "noResults",
    "editorDrawer",
    "drawerScrim",
    "closeDrawerButton",
    "drawerTitle",
    "caseForm",
    "fieldId",
    "fieldTitle",
    "fieldDescription",
    "fieldPriority",
    "fieldType",
    "fieldAuto",
    "fieldTags",
    "fieldPreconditions",
    "fieldSteps",
    "fieldExpectedResults",
    "saveCaseButton",
    "toast",
  ].forEach((id) => {
    els[id] = document.getElementById(id);
  });
}

function bindEvents() {
  els.sidebarToggle.addEventListener("click", toggleSidebar);
  els.sidebarResizer.addEventListener("pointerdown", startSidebarResize);
  els.sidebarResizer.addEventListener("keydown", handleSidebarResizeKeydown);
  window.addEventListener("resize", syncSidebarWidthToViewport);
  els.refreshButton.addEventListener("click", refreshAll);
  els.reloadNowButton.addEventListener("click", () => reloadAfterExternalChange(true));
  els.caseSearch.addEventListener("input", () => {
    state.query = els.caseSearch.value.trim().toLowerCase();
    renderCaseRows();
  });
  els.priorityFilters.addEventListener("click", (event) => {
    const button = event.target.closest("button[data-filter]");
    if (!button) return;
    state.filter = button.dataset.filter;
    renderFilters();
    renderCaseRows();
  });
  els.caseRows.addEventListener("click", (event) => {
    const markButton = event.target.closest("button[data-mark]");
    if (markButton) {
      event.stopPropagation();
      toggleNeedsUpdate(markButton.dataset.caseId);
      return;
    }
    const editButton = event.target.closest("button[data-edit-case]");
    if (editButton) {
      event.stopPropagation();
      openDrawer(editButton.dataset.caseId);
      return;
    }
    const toggleButton = event.target.closest("button[data-toggle-case]");
    if (toggleButton) {
      event.stopPropagation();
      toggleCaseDetails(toggleButton.dataset.caseId);
      return;
    }
    const summaryRow = event.target.closest("[data-case-summary]");
    if (summaryRow) toggleCaseDetails(summaryRow.dataset.caseId);
  });
  els.closeDrawerButton.addEventListener("click", closeDrawer);
  els.drawerScrim.addEventListener("click", closeDrawer);
  els.saveCaseButton.addEventListener("click", saveCase);
  els.caseForm.addEventListener("input", () => {
    state.dirty = true;
  });
  window.addEventListener("hashchange", () => {
    const path = decodeURIComponent(window.location.hash.replace(/^#/, ""));
    if (path && path !== state.currentFile) loadFile(path);
  });
}

function toggleSidebar() {
  const collapsed = document.body.classList.toggle("sidebar-collapsed");
  els.sidebarToggle.setAttribute("aria-expanded", String(!collapsed));
}

function restoreSidebarWidth() {
  const stored = Number(window.localStorage.getItem(SIDEBAR_STORAGE_KEY));
  updateSidebarWidth(Number.isFinite(stored) ? stored : SIDEBAR_MIN_WIDTH + 60, false);
}

function startSidebarResize(event) {
  if (window.matchMedia("(max-width: 720px)").matches) return;
  event.preventDefault();
  const startX = event.clientX;
  const startWidth = currentSidebarWidth();
  document.body.classList.add("resizing-sidebar");

  const handleMove = (moveEvent) => {
    updateSidebarWidth(startWidth + moveEvent.clientX - startX, false);
  };
  const handleUp = () => {
    document.body.classList.remove("resizing-sidebar");
    window.localStorage.setItem(SIDEBAR_STORAGE_KEY, String(currentSidebarWidth()));
    window.removeEventListener("pointermove", handleMove);
    window.removeEventListener("pointerup", handleUp);
    window.removeEventListener("pointercancel", handleUp);
  };

  window.addEventListener("pointermove", handleMove);
  window.addEventListener("pointerup", handleUp);
  window.addEventListener("pointercancel", handleUp);
}

function handleSidebarResizeKeydown(event) {
  if (!["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) return;
  event.preventDefault();
  const step = event.shiftKey ? 40 : 16;
  let nextWidth = currentSidebarWidth();
  if (event.key === "ArrowLeft") nextWidth -= step;
  if (event.key === "ArrowRight") nextWidth += step;
  if (event.key === "Home") nextWidth = SIDEBAR_MIN_WIDTH;
  if (event.key === "End") nextWidth = sidebarMaxWidth();
  updateSidebarWidth(nextWidth, true);
}

function syncSidebarWidthToViewport() {
  updateSidebarWidth(currentSidebarWidth(), true);
}

function currentSidebarWidth() {
  const value = getComputedStyle(document.documentElement).getPropertyValue("--sidebar-width");
  return Number.parseInt(value, 10) || SIDEBAR_MIN_WIDTH + 60;
}

function updateSidebarWidth(width, persist) {
  const nextWidth = Math.round(clamp(width, SIDEBAR_MIN_WIDTH, sidebarMaxWidth()));
  document.documentElement.style.setProperty("--sidebar-width", `${nextWidth}px`);
  els.sidebarResizer.setAttribute("aria-valuemin", String(SIDEBAR_MIN_WIDTH));
  els.sidebarResizer.setAttribute("aria-valuemax", String(sidebarMaxWidth()));
  els.sidebarResizer.setAttribute("aria-valuenow", String(nextWidth));
  if (persist) {
    window.localStorage.setItem(SIDEBAR_STORAGE_KEY, String(nextWidth));
  }
}

function sidebarMaxWidth() {
  const viewportBound = window.innerWidth - 420;
  return Math.max(SIDEBAR_MIN_WIDTH, Math.min(SIDEBAR_MAX_WIDTH, viewportBound));
}

function clamp(value, min, max) {
  return Math.min(Math.max(value, min), max);
}

async function boot() {
  await refreshAll();
  connectEvents();
  const hashPath = decodeURIComponent(window.location.hash.replace(/^#/, ""));
  if (hashPath) {
    await loadFile(hashPath);
  }
}

async function refreshAll() {
  const [summary, tree, marks] = await Promise.all([
    api("/api/summary"),
    api("/api/tree"),
    api("/api/marks"),
  ]);
  state.summary = summary;
  state.tree = tree;
  state.marks = marks;
  renderShell();
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: {"Content-Type": "application/json", ...(options.headers || {})},
    ...options,
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.error || response.statusText);
  }
  return data;
}

function connectEvents() {
  if (!window.EventSource) return;
  const source = new EventSource("/api/events");
  source.addEventListener("reload", () => reloadAfterExternalChange(false));
  source.addEventListener("marks", async () => {
    state.marks = await api("/api/marks");
    renderCaseRows();
  });
}

async function reloadAfterExternalChange(force) {
  if (state.dirty && !force) {
    state.pendingReload = true;
    els.reloadNotice.hidden = false;
    return;
  }
  state.pendingReload = false;
  els.reloadNotice.hidden = true;
  const current = state.currentFile;
  await refreshAll();
  if (current) {
    await loadFile(current, {keepDrawer: true, keepFilter: true, keepExpanded: true});
  }
}

function renderShell() {
  const summary = state.summary || {};
  els.scanDirs.textContent = (summary.scan_dirs || []).join(", ") || "No scan directory";
  els.summaryText.textContent = `${summary.files || 0} files · ${summary.cases || 0} cases`;
  els.treePanel.innerHTML = renderTree(state.tree, 0);
  markActiveTreeItem();
}

function renderTree(items, depth) {
  if (!items || !items.length) {
    return depth === 0 ? `<div class="empty-tree">No YAML cases found.</div>` : "";
  }
  const rows = items.map((item) => {
    const pad = 12 + depth * 16;
    if (item.type === "dir") {
      return `
        <li>
          <button class="tree-button open" type="button" style="padding-left:${pad}px" onclick="toggleTreeDir(this)">
            <span class="tree-caret">›</span>
            <span class="tree-icon folder-icon" aria-hidden="true">${folderIcon()}</span>
            <span class="tree-name">${escapeHtml(item.name)}</span>
            <span class="tree-count">${item.count || 0}</span>
          </button>
          <div class="tree-children">${renderTree(item.children || [], depth + 1)}</div>
        </li>`;
    }
    return `
      <li>
        <button class="tree-button" type="button" data-file-path="${escapeAttr(item.path)}" style="padding-left:${pad}px" onclick="selectTreeFile(this)">
          <span class="tree-caret tree-caret-spacer"></span>
          <span class="tree-icon file-icon" aria-hidden="true">${fileIcon()}</span>
          <span class="tree-name">${escapeHtml(item.name)}</span>
          <span class="tree-count">${item.count || 0}</span>
        </button>
      </li>`;
  }).join("");
  return `<ul class="tree-list">${rows}</ul>`;
}

window.toggleTreeDir = function toggleTreeDir(button) {
  button.classList.toggle("open");
  const children = button.nextElementSibling;
  if (children) children.hidden = !button.classList.contains("open");
};

window.selectTreeFile = function selectTreeFile(button) {
  const path = button.dataset.filePath;
  if (!path) return;
  window.location.hash = encodeURIComponent(path);
  loadFile(path);
};

async function loadFile(filePath, options = {}) {
  const data = await api(`/api/files/${encodePath(filePath)}`);
  state.currentFile = filePath;
  state.currentData = data;
  state.marks = {...state.marks, ...(data.marks || {})};
  state.filter = options.keepFilter ? state.filter : "all";
  state.query = options.keepFilter ? state.query : "";
  if (!options.keepExpanded) {
    state.expandedCaseIds = new Set();
  }
  els.caseSearch.value = state.query;
  els.emptyState.hidden = true;
  els.fileView.hidden = false;
  renderFileMeta();
  renderMetrics();
  renderFilters();
  renderCaseRows();
  markActiveTreeItem();
  if (options.keepDrawer && state.selectedCaseId) {
    const selected = findCase(state.selectedCaseId);
    if (selected) fillDrawer(selected);
  }
}

function renderFileMeta() {
  if (!state.currentData) return;
  const data = state.currentData;
  const items = [
    ["Module", data.module || "Unknown"],
    ["Feature", data.feature || "Untitled"],
    ["Owner", data.owner || "N/A"],
    ["Reviewed", data.last_reviewed || "N/A"],
  ];
  els.fileMeta.innerHTML = `
    <div class="file-meta-row">
      ${items.map(([label, value]) => renderMetaItem(label, value)).join("")}
    </div>
    <div class="file-meta-row path-row">
      ${renderMetaItem("Path", data.path || "", true)}
    </div>`;
}

function renderMetaItem(label, value, wide = false) {
  return `
    <div class="file-meta-item${wide ? " wide" : ""}">
      <span>${escapeHtml(label)}</span>
      <strong>${escapeHtml(value)}</strong>
    </div>`;
}

function renderMetrics() {
  const stats = state.currentData.stats || {};
  const priorities = stats.priorities || {};
  const needs = countNeedsUpdate();
  const metrics = [
    {label: "Cases", value: stats.total || 0, accent: "primary", icon: "all"},
    {label: "P0", value: priorities.P0 || 0, accent: "p0", icon: "p0"},
    {label: "P1", value: priorities.P1 || 0, accent: "p1", icon: "p1"},
    {label: "P2", value: priorities.P2 || 0, accent: "p2", icon: "p2"},
    {label: "Mark", value: needs, accent: "mark", icon: "mark"},
  ];
  els.metrics.innerHTML = metrics.map((metric) => `
    <div class="metric accent-${metric.accent}">
      <div>
        <strong>${metric.value}</strong>
        <span>${escapeHtml(metric.label)}</span>
      </div>
      <div class="metric-icon">${escapeHtml(metric.icon)}</div>
    </div>
  `).join("");
}

function renderFilters() {
  const filters = [
    ["all", "All"],
    ["P0", "P0"],
    ["P1", "P1"],
    ["P2", "P2"],
    ["needs", "Mark"],
  ];
  els.priorityFilters.innerHTML = filters.map(([value, label]) => {
    const active = state.filter === value ? " active" : "";
    const mark = value === "needs" ? " mark" : "";
    return `<button class="filter-button${active}${mark}" type="button" data-filter="${value}">${label}</button>`;
  }).join("");
}

function renderCaseRows() {
  if (!state.currentData) return;
  const rows = state.currentData.cases
    .filter(matchesCurrentFilter)
    .map((caseItem) => {
      const key = markKey(state.currentData.path, caseItem.id);
      const marked = Boolean(state.marks[key] && state.marks[key].needs_update);
      const selected = state.selectedCaseId === caseItem.id;
      const expanded = state.expandedCaseIds.has(caseItem.id);
      const tags = (caseItem.tags || []).map((tag) => `<span class="tag">${escapeHtml(tag)}</span>`).join("");
      const description = caseItem.description
        ? `<p class="case-description">${escapeHtml(caseItem.description)}</p>`
        : "";
      return `
        <article class="case-item${marked ? " needs-update" : ""}${selected ? " selected" : ""}${expanded ? " expanded" : ""}" data-case-id="${escapeAttr(caseItem.id)}">
          <div class="case-summary" data-case-summary data-case-id="${escapeAttr(caseItem.id)}">
            <div class="case-toggle-cell">
              <button class="chevron-button" type="button" data-toggle-case="1" data-case-id="${escapeAttr(caseItem.id)}" aria-expanded="${expanded}" aria-label="${expanded ? "Collapse case details" : "Expand case details"}"></button>
            </div>
            <div class="case-id-cell">
              <span class="case-id">${escapeHtml(caseItem.id)}</span>
            </div>
            <div class="case-main-cell">
              <div class="case-title-line">
                <h4 class="case-title">${escapeHtml(caseItem.title)}</h4>
                ${caseItem.auto ? `<span class="auto-pill">Auto</span>` : ""}
              </div>
              ${description}
            </div>
            <div class="case-priority-cell">
              <span class="badge priority-${escapeAttr(caseItem.priority).toLowerCase()}">${escapeHtml(caseItem.priority)}</span>
            </div>
            <div class="case-type-cell">${escapeHtml(caseItem.type)}</div>
            <div class="case-tags-cell"><div class="tag-list">${tags}</div></div>
            <div class="case-actions">
              <button class="mark-action${marked ? " active" : ""}" type="button" data-mark="1" data-case-id="${escapeAttr(caseItem.id)}">${marked ? "Marked" : "Mark"}</button>
              <button class="text-action" type="button" data-edit-case="1" data-case-id="${escapeAttr(caseItem.id)}">Edit</button>
            </div>
          </div>
          ${expanded ? renderCaseDetails(caseItem) : ""}
        </article>`;
    });
  els.caseRows.innerHTML = rows.join("");
  els.noResults.hidden = rows.length > 0;
  renderMetrics();
}

function renderCaseDetails(caseItem) {
  return `
    <div class="case-details">
      <div class="case-details-card">
        <div class="case-detail-column">
          ${renderDetailList("Preconditions", caseItem.preconditions, false)}
          ${renderDetailList("Steps", caseItem.steps, true)}
        </div>
        <div class="case-detail-column">
          ${renderDetailList("Expected Results", caseItem.expected_results, false)}
        </div>
      </div>
    </div>`;
}

function renderDetailList(title, items, ordered) {
  const values = items || [];
  const content = values.length
    ? values.map((item) => `<li>${escapeHtml(item)}</li>`).join("")
    : `<li class="empty-detail">None</li>`;
  const tag = ordered ? "ol" : "ul";
  return `
    <section class="detail-section">
      <h5>${detailIcon(title)}<span>${escapeHtml(title)}</span></h5>
      <${tag}>${content}</${tag}>
    </section>`;
}

function toggleCaseDetails(caseId) {
  if (!caseId) return;
  if (state.expandedCaseIds.has(caseId)) {
    state.expandedCaseIds.delete(caseId);
  } else {
    state.expandedCaseIds.add(caseId);
  }
  renderCaseRows();
}

function matchesCurrentFilter(caseItem) {
  if (state.filter === "needs" && !isMarked(caseItem.id)) return false;
  if (["P0", "P1", "P2"].includes(state.filter) && caseItem.priority !== state.filter) return false;
  if (!state.query) return true;
  const haystack = [
    caseItem.id,
    caseItem.title,
    caseItem.description,
    caseItem.type,
    ...(caseItem.preconditions || []),
    ...(caseItem.steps || []),
    ...(caseItem.expected_results || []),
    ...(caseItem.tags || []),
  ].join(" ").toLowerCase();
  return haystack.includes(state.query);
}

function openDrawer(caseId) {
  const caseItem = findCase(caseId);
  if (!caseItem) return;
  state.selectedCaseId = caseId;
  fillDrawer(caseItem);
  els.editorDrawer.classList.add("open");
  els.editorDrawer.setAttribute("aria-hidden", "false");
  els.drawerScrim.hidden = false;
  renderCaseRows();
}

function closeDrawer() {
  els.editorDrawer.classList.remove("open");
  els.editorDrawer.setAttribute("aria-hidden", "true");
  els.drawerScrim.hidden = true;
  state.selectedCaseId = null;
  state.dirty = false;
  renderCaseRows();
}

function fillDrawer(caseItem) {
  if (!caseItem) return;
  els.drawerTitle.textContent = caseItem.title || caseItem.id;
  els.fieldId.textContent = caseItem.id || "";
  els.fieldTitle.value = caseItem.title || "";
  els.fieldDescription.value = caseItem.description || "";
  els.fieldPriority.value = caseItem.priority || "P2";
  els.fieldType.value = caseItem.type || "functional";
  els.fieldAuto.checked = Boolean(caseItem.auto);
  els.fieldTags.value = (caseItem.tags || []).join("\n");
  els.fieldPreconditions.value = (caseItem.preconditions || []).join("\n");
  els.fieldSteps.value = (caseItem.steps || []).join("\n");
  els.fieldExpectedResults.value = (caseItem.expected_results || []).join("\n");
  state.dirty = false;
}

async function saveCase() {
  if (!state.currentData || !state.selectedCaseId) return;
  const payload = {
    file_path: state.currentData.path,
    case_id: state.selectedCaseId,
    mtime_ns: state.currentData.mtime_ns,
    updates: {
      title: els.fieldTitle.value.trim(),
      description: els.fieldDescription.value,
      priority: els.fieldPriority.value,
      type: els.fieldType.value.trim(),
      auto: els.fieldAuto.checked,
      tags: arrayFromText(els.fieldTags.value),
      preconditions: arrayFromText(els.fieldPreconditions.value),
      steps: arrayFromText(els.fieldSteps.value),
      expected_results: arrayFromText(els.fieldExpectedResults.value),
    },
  };
  try {
    state.dirty = false;
    const response = await api("/api/cases", {
      method: "PATCH",
      body: JSON.stringify(payload),
    });
    showToast("Saved to YAML");
    await refreshAll();
    await loadFile(state.currentData.path, {keepDrawer: true, keepFilter: true, keepExpanded: true});
    if (response.result && response.result.case) {
      state.selectedCaseId = response.result.case.id;
    }
  } catch (error) {
    state.dirty = true;
    showToast(error.message);
  }
}

async function toggleNeedsUpdate(caseId) {
  if (!state.currentData || !caseId) return;
  const result = await api("/api/marks/toggle", {
    method: "POST",
    body: JSON.stringify({file_path: state.currentData.path, case_id: caseId}),
  });
  state.marks = result.marks || state.marks;
  renderCaseRows();
}

function findCase(caseId) {
  return state.currentData?.cases.find((caseItem) => caseItem.id === caseId);
}

function isMarked(caseId) {
  if (!state.currentData) return false;
  const mark = state.marks[markKey(state.currentData.path, caseId)];
  return Boolean(mark && mark.needs_update);
}

function countNeedsUpdate() {
  if (!state.currentData) return 0;
  return state.currentData.cases.filter((caseItem) => isMarked(caseItem.id)).length;
}

function markKey(filePath, caseId) {
  return `${filePath}#${caseId}`;
}

function markActiveTreeItem() {
  document.querySelectorAll("[data-file-path]").forEach((button) => {
    button.classList.toggle("active", button.dataset.filePath === state.currentFile);
  });
}

function encodePath(path) {
  return path.split("/").map(encodeURIComponent).join("/");
}

function arrayFromText(text) {
  return text.split(/\r?\n/).map((line) => line.trim()).filter(Boolean);
}

function folderIcon() {
  return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>`;
}

function fileIcon() {
  return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>`;
}

function detailIcon(title) {
  if (title === "Preconditions") {
    return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>`;
  }
  return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>`;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function escapeAttr(value) {
  return escapeHtml(value);
}

function showToast(message) {
  els.toast.textContent = message;
  els.toast.hidden = false;
  clearTimeout(showToast.timer);
  showToast.timer = setTimeout(() => {
    els.toast.hidden = true;
  }, 2600);
}
