const SIDEBAR_STORAGE_KEY = "casebook.sidebarWidth";
const SIDEBAR_MIN_WIDTH = 260;
const SIDEBAR_MAX_WIDTH = 560;

const state = {
  summary: null,
  tree: [],
  marks: {},
  runs: [],
  currentRunId: null,
  currentRun: null,
  testPlanExpanded: false,
  currentFile: null,
  currentData: null,
  selectedCaseId: null,
  expandedCaseIds: new Set(),
  dirty: false,
  pendingReload: false,
  filter: "all",
  executionFilter: "all",
  query: "",
};

const EXECUTION_FILTERS = [
  ["all", "All"],
  ["passed", "Passed"],
  ["failed", "Failed"],
  ["blocked", "Blocked"],
  ["deferred", "Deferred"],
  ["untested", "Untested"],
];

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
    "executionPanel",
    "executionToggle",
    "executionPanelBody",
    "executionScopeText",
    "runSelect",
    "runModeSelect",
    "sourceRunSelect",
    "runNameInput",
    "createRunButton",
    "completionControlRow",
    "runEnvironmentInput",
    "runTesterInput",
    "completeRunButton",
    "executionProgressBar",
    "executionProgressText",
    "executionStats",
    "fileMeta",
    "caseSearch",
    "priorityFilters",
    "executionFilter",
    "renumberIdsButton",
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
  els.executionToggle.addEventListener("click", toggleTestPlanPanel);
  els.runSelect.addEventListener("change", () => selectRun(els.runSelect.value));
  els.runModeSelect.addEventListener("change", renderExecutionPanel);
  els.sourceRunSelect.addEventListener("change", renderExecutionPanel);
  els.createRunButton.addEventListener("click", createRun);
  els.completeRunButton.addEventListener("click", completeRun);
  els.renumberIdsButton.addEventListener("click", renumberCurrentFile);
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
  els.executionFilter.addEventListener("change", () => {
    state.executionFilter = els.executionFilter.value;
    renderFilters();
    renderCaseRows();
  });
  els.caseRows.addEventListener("change", (event) => {
    const reviewMarkCheckbox = event.target.closest("input[data-review-mark]");
    if (reviewMarkCheckbox) {
      event.stopPropagation();
      updateReviewMark(reviewMarkCheckbox.dataset.caseId, reviewMarkCheckbox.checked);
      return;
    }
    const executionSelect = event.target.closest("select[data-exec-select]");
    if (!executionSelect) return;
    event.stopPropagation();
    updateExecutionStatus(executionSelect.dataset.caseId, executionSelect.value);
  });
  els.caseRows.addEventListener("click", (event) => {
    const executionSelect = event.target.closest("select[data-exec-select]");
    if (executionSelect) {
      event.stopPropagation();
      return;
    }
    const saveExecutionButton = event.target.closest("button[data-save-execution]");
    if (saveExecutionButton) {
      event.stopPropagation();
      saveExecutionDetails(saveExecutionButton.dataset.caseId);
      return;
    }
    const saveReviewButton = event.target.closest("button[data-save-review]");
    if (saveReviewButton) {
      event.stopPropagation();
      saveReviewDetails(saveReviewButton.dataset.caseId);
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
  const [summary, tree, marks, runs] = await Promise.all([
    api("/api/summary"),
    api("/api/tree"),
    api("/api/marks"),
    api("/api/test-runs"),
  ]);
  state.summary = summary;
  state.tree = tree;
  state.marks = marks;
  state.runs = runs;
  if (state.currentRunId && !state.runs.some((run) => run.id === state.currentRunId)) {
    state.currentRunId = null;
    state.currentRun = null;
  }
  if (state.currentRunId) {
    state.currentRun = await api(`/api/test-runs/${encodeURIComponent(state.currentRunId)}`);
  } else {
    state.currentRun = null;
  }
  normalizeCurrentFilter();
  renderShell();
  renderExecutionPanel();
  if (state.currentData) renderFilters();
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
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
    renderFilters();
    renderCaseRows();
  });
  source.addEventListener("test_run", async (event) => {
    const data = JSON.parse(event.data || "{}");
    state.runs = await api("/api/test-runs");
    if (state.currentRunId && !state.runs.some((run) => run.id === state.currentRunId)) {
      state.currentRunId = null;
      state.currentRun = null;
    }
    if (state.currentRunId && data.run_id === state.currentRunId) {
      state.currentRun = state.currentRunId ? await api(`/api/test-runs/${encodeURIComponent(state.currentRunId)}`) : null;
    }
    normalizeCurrentFilter();
    renderExecutionPanel();
    renderFilters();
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
    await loadFile(current, { keepDrawer: true, keepFilter: true, keepExpanded: true });
  }
}

function renderShell() {
  const summary = state.summary || {};
  els.scanDirs.textContent = (summary.scan_dirs || []).join(", ") || "No scan directory";
  els.summaryText.textContent = `${summary.files || 0} files - ${summary.cases || 0} cases`;
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
  state.marks = { ...state.marks, ...(data.marks || {}) };
  state.filter = options.keepFilter ? state.filter : "all";
  state.executionFilter = options.keepFilter ? state.executionFilter : "all";
  state.query = options.keepFilter ? state.query : "";
  if (!options.keepExpanded) {
    state.expandedCaseIds = new Set();
  }
  els.caseSearch.value = state.query;
  els.emptyState.hidden = true;
  els.fileView.hidden = false;
  renderExecutionPanel();
  renderFileMeta();
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

function renderExecutionPanel() {
  if (!els.executionPanel) return;
  const runs = state.runs || [];
  const scope = scopeLabel();
  const stats = testPlanStats();
  const percent = stats.total ? Math.round((stats.executed / stats.total) * 100) : 0;
  const run = state.currentRun?.run;
  const defaults = testPlanDefaults();

  els.executionPanel.classList.toggle("expanded", state.testPlanExpanded);
  els.executionPanel.classList.toggle("collapsed", !state.testPlanExpanded);
  els.executionToggle.setAttribute("aria-expanded", String(state.testPlanExpanded));
  els.executionScopeText.textContent = run
    ? `Scope: ${scope} - ${runModeLabel(run.mode)} - ${stats.total} cases`
    : `Scope: ${scope}`;
  els.executionProgressText.textContent = run
    ? `${stats.executed} / ${stats.total} executed - ${percent}%`
    : "Not enabled";

  const options = [
    `<option value="">Current plan: none</option>`,
    ...runs.map((item) => `<option value="${escapeAttr(item.id)}">${escapeHtml(runOptionLabel(item))}</option>`),
  ];
  els.runSelect.innerHTML = options.join("");
  els.runSelect.value = state.currentRunId || "";
  const createMode = els.runModeSelect.value || "full";
  const previousSourceRunId = els.sourceRunSelect.value;
  const sourceOptions = [
    `<option value="">Source plan</option>`,
    ...runs.map((item) => `<option value="${escapeAttr(item.id)}">${escapeHtml(runOptionLabel(item))}</option>`),
  ];
  els.sourceRunSelect.innerHTML = sourceOptions.join("");
  if (createMode === "retest_unresolved") {
    if (previousSourceRunId && runs.some((item) => item.id === previousSourceRunId)) {
      els.sourceRunSelect.value = previousSourceRunId;
    } else if (state.currentRunId) {
      els.sourceRunSelect.value = state.currentRunId;
    }
    if (!els.sourceRunSelect.value && runs.length) {
      els.sourceRunSelect.value = runs[0].id;
    }
  } else {
    els.sourceRunSelect.value = "";
  }
  els.sourceRunSelect.hidden = createMode !== "retest_unresolved";
  els.sourceRunSelect.disabled = createMode !== "retest_unresolved";
  els.runNameInput.placeholder = createMode === "retest_unresolved"
    ? "New retest plan name"
    : "New test plan name";
  els.createRunButton.textContent = createMode === "retest_unresolved"
    ? "Create retest"
    : "Create plan";
  els.createRunButton.title = createMode === "retest_unresolved"
    ? "Create a new plan from the selected plan's failed, blocked, and deferred cases"
    : "Create a full test plan for the current scope";
  const canCompleteRun = Boolean(state.currentRunId && stats.total > 0 && stats.untested === 0);
  els.completionControlRow.hidden = !canCompleteRun;
  els.runEnvironmentInput.value = run?.environment || defaults.environment;
  els.runTesterInput.value = run?.tester || defaults.tester;
  els.runEnvironmentInput.disabled = !canCompleteRun;
  els.runTesterInput.disabled = !canCompleteRun;
  els.completeRunButton.disabled = !canCompleteRun;
  els.completeRunButton.title = state.currentRunId && stats.untested > 0
    ? `Cannot complete: ${stats.untested} untested cases remain`
    : "Complete test plan";
  syncRenumberButton();

  els.executionProgressBar.style.width = `${percent}%`;
  els.executionStats.innerHTML = [
    ["total", "Cases", stats.total],
    ["passed", "Passed", stats.passed],
    ["failed", "Failed", stats.failed],
    ["blocked", "Blocked", stats.blocked],
    ["deferred", "Deferred", stats.deferred],
    ["untested", "Untested", stats.untested],
  ].map(([status, label, value]) => `
    <div class="execution-stat status-${status}">
      <strong>${value}</strong>
      <span>${label}</span>
    </div>
  `).join("");
}

function syncRenumberButton() {
  if (!els.renumberIdsButton) return;
  const inTestPlanMode = Boolean(state.currentRunId);
  const disabled = !state.currentData || inTestPlanMode;
  els.renumberIdsButton.disabled = disabled;
  els.renumberIdsButton.title = inTestPlanMode
    ? "Case IDs cannot be updated while a test plan is selected"
    : "Update case IDs using the current YAML order";
}

function runOptionLabel(run) {
  const name = run.name || run.id;
  const hasCaseTotal = run.case_total !== null && run.case_total !== undefined && run.case_total !== "";
  const count = hasCaseTotal && Number.isFinite(Number(run.case_total))
    ? ` - ${Number(run.case_total)} cases`
    : "";
  return `${name} - ${runModeLabel(run.mode)}${count}`;
}

function runModeLabel(mode) {
  return mode === "retest_unresolved" ? "Retest" : "Full";
}

function testPlanStats() {
  const scopedKeys = currentRunCaseKeys();
  const scopeSet = scopedKeys ? new Set(scopedKeys) : null;
  const total = scopedKeys ? scopedKeys.length : Number(state.summary?.cases || 0);
  const stats = {
    total,
    executed: 0,
    passed: 0,
    failed: 0,
    blocked: 0,
    deferred: 0,
    untested: total,
  };
  const results = state.currentRun?.results || {};
  Object.entries(results).forEach(([key, result]) => {
    if (scopeSet && !scopeSet.has(key)) return;
    if (!result || typeof result !== "object") return;
    const status = String(result.status || "").toLowerCase();
    if (status in stats && status !== "untested") {
      stats.executed += 1;
      stats[status] += 1;
    }
  });
  stats.executed = Math.min(stats.executed, total);
  stats.untested = Math.max(total - stats.executed, 0);
  return stats;
}

function currentRunCaseKeys() {
  const values = state.currentRun?.run?.case_scope;
  if (!Array.isArray(values)) return null;
  return values.map((value) => String(value || "").trim()).filter(Boolean);
}

function matchesRunCaseScope(caseItem) {
  if (!state.currentRun || !state.currentData) return true;
  const keys = currentRunCaseKeys();
  if (!keys) return true;
  return new Set(keys).has(markKey(state.currentData.path, caseItem.id));
}

function currentCasePool() {
  const cases = state.currentData?.cases || [];
  if (!state.currentRun) return cases;
  return cases.filter(matchesRunCaseScope);
}

function executionResult(caseId) {
  if (!state.currentData || !state.currentRun) return null;
  const key = markKey(state.currentData.path, caseId);
  const result = state.currentRun.results?.[key];
  return result && typeof result === "object" ? result : null;
}

function executionStatus(caseId) {
  const status = executionResult(caseId)?.status || "untested";
  return ["passed", "failed", "blocked", "deferred"].includes(status) ? status : "untested";
}

function renderFilters() {
  const counts = filterCounts();
  normalizeCurrentFilter();
  const filters = [
    ["all", "All", counts.all],
    ["P0", "P0", counts.P0],
    ["P1", "P1", counts.P1],
    ["P2", "P2", counts.P2],
    ["needs", "Mark", counts.needs],
  ];
  els.priorityFilters.innerHTML = filters.map(([value, label, count]) => {
    const active = state.filter === value ? " active" : "";
    const mark = value === "needs" ? " mark" : "";
    const priority = ["P0", "P1", "P2"].includes(value) ? ` priority-filter priority-${value.toLowerCase()}` : "";
    return `
      <button class="filter-button${active}${mark}${priority}" type="button" data-filter="${value}">
        <span class="filter-label">${escapeHtml(label)}</span>
        <span class="filter-count">${escapeHtml(count)}</span>
      </button>`;
  }).join("");
  renderExecutionFilter();
}

function renderExecutionFilter() {
  if (!els.executionFilter) return;
  normalizeCurrentFilter();
  els.executionFilter.hidden = !state.currentRun;
  els.executionFilter.disabled = !state.currentRun;
  if (!state.currentRun) return;

  const counts = executionFilterCounts();
  els.executionFilter.innerHTML = EXECUTION_FILTERS.map(([value, label]) => {
    const count = value === "all" ? counts.all : counts[value];
    return `<option value="${value}">${escapeHtml(label)} (${count || 0})</option>`;
  }).join("");
  els.executionFilter.value = state.executionFilter;
  els.executionFilter.className = `execution-filter status-${state.executionFilter}`;
}

function filterCounts() {
  const cases = currentCasePool();
  const counts = {
    all: cases.length,
    P0: 0,
    P1: 0,
    P2: 0,
    needs: cases.filter((caseItem) => isMarked(caseItem.id)).length,
  };
  cases.forEach((caseItem) => {
    const priority = String(caseItem.priority || "").toUpperCase();
    if (priority in counts) {
      counts[priority] += 1;
    }
  });
  return counts;
}

function executionFilterCounts() {
  const cases = currentCasePool().filter(matchesPrimaryFilter);
  const counts = {
    all: cases.length,
    passed: 0,
    failed: 0,
    blocked: 0,
    deferred: 0,
    untested: 0,
  };
  cases.forEach((caseItem) => {
    counts[executionStatus(caseItem.id)] += 1;
  });
  return counts;
}

function renderCaseRows() {
  if (!state.currentData) return;
  const rows = currentCasePool()
    .filter(matchesCurrentFilter)
    .map((caseItem) => {
      const key = markKey(state.currentData.path, caseItem.id);
      const mark = reviewMark(caseItem.id);
      const marked = Boolean(mark.needs_update);
      const selected = state.selectedCaseId === caseItem.id;
      const expanded = state.expandedCaseIds.has(caseItem.id);
      const execStatus = executionStatus(caseItem.id);
      const tags = [
        ...(caseItem.tags || []).map((tag) => `<span class="tag">${escapeHtml(tag)}</span>`),
        marked ? `<span class="tag mark-tag">Mark</span>` : "",
      ].join("");
      const description = caseItem.description
        ? `<p class="case-description">${escapeHtml(caseItem.description)}</p>`
        : "";
      return `
        <article class="case-item${selected ? " selected" : ""}${expanded ? " expanded" : ""} exec-${escapeAttr(execStatus)}" data-case-id="${escapeAttr(caseItem.id)}">
          <div class="case-summary" data-case-summary data-case-id="${escapeAttr(caseItem.id)}">
            <div class="case-toggle-cell">
              <button class="chevron-button" type="button" data-toggle-case="1" data-case-id="${escapeAttr(caseItem.id)}" aria-expanded="${expanded}" aria-label="${expanded ? "Collapse case details" : "Expand case details"}">
                <span class="chevron-icon" aria-hidden="true">›</span>
              </button>
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
              ${state.currentRun ? renderExecutionActions(caseItem.id, execStatus) : ""}
              <button class="text-action" type="button" data-edit-case="1" data-case-id="${escapeAttr(caseItem.id)}">Edit</button>
            </div>
          </div>
          ${expanded ? renderCaseDetails(caseItem) : ""}
        </article>`;
    });
  els.caseRows.innerHTML = rows.join("");
  els.noResults.hidden = rows.length > 0;
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
      <div class="case-side-panel">
        ${state.currentRun ? renderExecutionDetails(caseItem) : renderReviewDetails(caseItem)}
      </div>
    </div>`;
}

function renderExecutionActions(caseId, currentStatus) {
  const statuses = [
    ["passed", "Pass"],
    ["failed", "Fail"],
    ["blocked", "Block"],
    ["deferred", "Defer"],
  ];
  const disabled = state.currentRun ? "" : " disabled";
  return `
    <div class="execution-actions" aria-label="Execution status">
      <select class="execution-select status-${escapeAttr(currentStatus)}" data-exec-select="1" data-case-id="${escapeAttr(caseId)}" aria-label="Execution status"${disabled}>
        <option value="untested"${currentStatus === "untested" ? " selected" : ""} disabled>Untested</option>
        ${statuses.map(([status, label]) => `
          <option value="${status}"${currentStatus === status ? " selected" : ""}>${label}</option>
        `).join("")}
      </select>
    </div>`;
}

function renderReviewDetails(caseItem) {
  const mark = reviewMark(caseItem.id);
  const marked = Boolean(mark.needs_update);
  return `
    <aside class="review-panel">
      <label class="mark-row">
        <input type="checkbox" data-review-mark="1" data-case-id="${escapeAttr(caseItem.id)}"${marked ? " checked" : ""}>
        <span>Needs update</span>
      </label>
      <textarea data-review-notes="${escapeAttr(caseItem.id)}" rows="5" placeholder="Describe what should be updated">${escapeHtml(mark.notes || "")}</textarea>
      <button class="outline-button review-save-button" type="button" data-save-review="1" data-case-id="${escapeAttr(caseItem.id)}">Save review</button>
    </aside>`;
}

function renderExecutionDetails(caseItem) {
  const result = executionResult(caseItem.id) || {};
  const defects = Array.isArray(result.defects) ? result.defects.join("\n") : (result.defects || "");
  return `
    <section class="detail-section execution-detail-section">
      <h5>${detailIcon("Execution")}<span>Execution</span></h5>
      <div class="execution-detail-grid">
        <label>
          <span>Notes</span>
          <textarea data-exec-notes="${escapeAttr(caseItem.id)}" rows="3" placeholder="Execution notes">${escapeHtml(result.notes || "")}</textarea>
        </label>
        <label>
          <span>Defects</span>
          <textarea data-exec-defects="${escapeAttr(caseItem.id)}" rows="2" placeholder="Bug links or defect IDs, one per line">${escapeHtml(defects)}</textarea>
        </label>
        <button class="outline-button execution-save-button" type="button" data-save-execution="1" data-case-id="${escapeAttr(caseItem.id)}"${state.currentRun ? "" : " disabled"}>Save execution</button>
      </div>
    </section>`;
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
  if (!matchesRunCaseScope(caseItem)) return false;
  if (!matchesPrimaryFilter(caseItem)) return false;
  if (!matchesExecutionFilter(caseItem)) return false;
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

function matchesPrimaryFilter(caseItem) {
  if (state.filter === "needs" && !isMarked(caseItem.id)) return false;
  if (["P0", "P1", "P2"].includes(state.filter) && caseItem.priority !== state.filter) return false;
  return true;
}

function matchesExecutionFilter(caseItem) {
  if (!state.currentRun || state.executionFilter === "all") return true;
  return executionStatus(caseItem.id) === state.executionFilter;
}

function normalizeCurrentFilter() {
  if (!state.currentRun) {
    state.executionFilter = "all";
    return;
  }
  if (!EXECUTION_FILTERS.some(([value]) => value === state.executionFilter)) {
    state.executionFilter = "all";
  }
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
    await loadFile(state.currentData.path, { keepDrawer: true, keepFilter: true, keepExpanded: true });
    if (response.result && response.result.case) {
      state.selectedCaseId = response.result.case.id;
    }
  } catch (error) {
    state.dirty = true;
    showToast(error.message);
  }
}

async function renumberCurrentFile() {
  if (!state.currentData) return;
  if (state.currentRunId) {
    showToast("Case IDs cannot be updated while a test plan is selected");
    return;
  }
  const confirmed = window.confirm("Update case IDs using the current YAML order? The case order will not change.");
  if (!confirmed) return;

  const filePath = state.currentData.path;
  try {
    const response = await api(`/api/files/${encodePath(filePath)}/renumber`, {
      method: "POST",
      body: JSON.stringify({
        mtime_ns: state.currentData.mtime_ns,
        current_run_id: state.currentRunId,
      }),
    });
    state.marks = response.marks || state.marks;
    state.expandedCaseIds = new Set();
    if (state.selectedCaseId) closeDrawer();
    await refreshAll();
    await loadFile(filePath, { keepFilter: true });
    const changed = Number(response.result?.changed || 0);
    const total = Number(response.result?.total || 0);
    showToast(changed ? `Updated ${changed}/${total} case IDs` : "Case IDs are already sequential");
  } catch (error) {
    showToast(error.message);
  }
}

async function updateReviewMark(caseId, needsUpdate) {
  if (!state.currentData || !caseId) return;
  const notes = document.querySelector(`[data-review-notes="${cssEscape(caseId)}"]`)?.value || "";
  const result = await api("/api/marks", {
    method: "PATCH",
    body: JSON.stringify({
      file_path: state.currentData.path,
      case_id: caseId,
      needs_update: needsUpdate,
      notes,
    }),
  });
  state.marks = result.marks || state.marks;
  renderFilters();
  renderCaseRows();
}

async function saveReviewDetails(caseId) {
  if (!state.currentData || !caseId) return;
  const marked = document.querySelector(`[data-review-mark][data-case-id="${cssEscape(caseId)}"]`)?.checked || false;
  const notes = document.querySelector(`[data-review-notes="${cssEscape(caseId)}"]`)?.value || "";
  const result = await api("/api/marks", {
    method: "PATCH",
    body: JSON.stringify({
      file_path: state.currentData.path,
      case_id: caseId,
      needs_update: marked,
      notes,
    }),
  });
  state.marks = result.marks || state.marks;
  renderFilters();
  renderCaseRows();
  showToast("Review details saved");
}

async function selectRun(runId) {
  state.currentRunId = runId || null;
  state.currentRun = state.currentRunId ? await api(`/api/test-runs/${encodeURIComponent(state.currentRunId)}`) : null;
  if (state.currentRunId) state.testPlanExpanded = true;
  normalizeCurrentFilter();
  renderExecutionPanel();
  renderFilters();
  renderCaseRows();
}

async function createRun() {
  const mode = els.runModeSelect.value || "full";
  const sourceRunId = mode === "retest_unresolved" ? els.sourceRunSelect.value : "";
  if (mode === "retest_unresolved" && !sourceRunId) {
    showToast("Select a source test plan before creating a retest plan");
    return;
  }
  const name = els.runNameInput.value.trim() || defaultRunName();
  try {
    const response = await api("/api/test-runs", {
      method: "POST",
      body: JSON.stringify({
        name,
        mode,
        source_run_id: sourceRunId,
        scope: state.summary?.scan_dirs || [],
      }),
    });
    state.currentRun = response;
    state.currentRunId = response.run.id;
    state.testPlanExpanded = true;
    els.runNameInput.value = "";
    state.runs = await api("/api/test-runs");
    renderExecutionPanel();
    renderFilters();
    renderCaseRows();
    showToast(mode === "retest_unresolved" ? "Retest plan created" : "Test plan created");
  } catch (error) {
    showToast(error.message);
  }
}

async function completeRun() {
  if (!state.currentRunId) {
    showToast("Select or create a test plan first");
    return;
  }
  const stats = testPlanStats();
  if (stats.untested > 0) {
    showToast(`Cannot complete test plan: ${stats.untested} untested cases remain`);
    return;
  }
  const defaults = testPlanDefaults();
  try {
    const response = await api(`/api/test-runs/${encodeURIComponent(state.currentRunId)}`, {
      method: "PATCH",
      body: JSON.stringify({
        environment: els.runEnvironmentInput.value.trim() || defaults.environment,
        tester: els.runTesterInput.value.trim() || defaults.tester,
      }),
    });
    state.currentRun = response;
    state.runs = await api("/api/test-runs");
    renderExecutionPanel();
    renderCaseRows();
    showToast("Test plan completed");
  } catch (error) {
    showToast(error.message);
  }
}

async function updateExecutionStatus(caseId, status) {
  if (!state.currentData || !caseId) return;
  if (status === "untested") return;
  if (!state.currentRunId) {
    showToast("Select or create a test plan first");
    return;
  }
  const payload = {
    file_path: state.currentData.path,
    case_id: caseId,
    status,
  };
  const response = await api(`/api/test-runs/${encodeURIComponent(state.currentRunId)}/results`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
  state.currentRun = response.run;
  state.runs = await api("/api/test-runs");
  renderExecutionPanel();
  renderFilters();
  renderCaseRows();
}

async function saveExecutionDetails(caseId) {
  if (!state.currentData || !caseId) return;
  if (!state.currentRunId) {
    showToast("Select or create a test plan first");
    return;
  }
  const notes = document.querySelector(`[data-exec-notes="${cssEscape(caseId)}"]`)?.value || "";
  const defects = document.querySelector(`[data-exec-defects="${cssEscape(caseId)}"]`)?.value || "";
  const response = await api(`/api/test-runs/${encodeURIComponent(state.currentRunId)}/results`, {
    method: "PATCH",
    body: JSON.stringify({
      file_path: state.currentData.path,
      case_id: caseId,
      notes,
      defects: arrayFromText(defects),
    }),
  });
  state.currentRun = response.run;
  state.runs = await api("/api/test-runs");
  renderExecutionPanel();
  renderCaseRows();
  showToast("Execution details saved");
}

function defaultRunName() {
  if (els.runModeSelect?.value === "retest_unresolved") {
    const sourceRun = state.runs.find((item) => item.id === els.sourceRunSelect?.value);
    if (sourceRun) {
      return `${sourceRun.name || sourceRun.id} retest`;
    }
  }
  const now = new Date();
  const date = now.toISOString().slice(0, 10);
  return `${scopeLabel()} ${date}`;
}

function toggleTestPlanPanel() {
  state.testPlanExpanded = !state.testPlanExpanded;
  renderExecutionPanel();
}

function scopeLabel() {
  return (state.summary?.scan_dirs || []).join(", ") || "No scope";
}

function testPlanDefaults() {
  return {
    environment: "Test environment",
    tester: (state.summary?.owners || []).join(", "),
  };
}

function findCase(caseId) {
  return state.currentData?.cases.find((caseItem) => caseItem.id === caseId);
}

function isMarked(caseId) {
  return Boolean(reviewMark(caseId).needs_update);
}

function countNeedsUpdate() {
  if (!state.currentData) return 0;
  return state.currentData.cases.filter((caseItem) => isMarked(caseItem.id)).length;
}

function markKey(filePath, caseId) {
  return `${filePath}#${caseId}`;
}

function reviewMark(caseId) {
  if (!state.currentData || !caseId) return {};
  const mark = state.marks[markKey(state.currentData.path, caseId)];
  return mark && typeof mark === "object" ? mark : {};
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

function cssEscape(value) {
  if (window.CSS && typeof window.CSS.escape === "function") {
    return window.CSS.escape(String(value));
  }
  return String(value).replace(/["\\]/g, "\\$&");
}

function showToast(message) {
  els.toast.textContent = message;
  els.toast.hidden = false;
  clearTimeout(showToast.timer);
  showToast.timer = setTimeout(() => {
    els.toast.hidden = true;
  }, 2600);
}
