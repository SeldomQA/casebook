const SIDEBAR_STORAGE_KEY = "casebook.sidebarWidth";
const CURRENT_RUN_STORAGE_PREFIX = "casebook.currentRun";
const LANGUAGE_STORAGE_KEY = "casebook.language";

const ZH_TRANSLATIONS = {
  "Test quality workspace": "测试质量工作台", "Toggle sidebar": "切换侧边栏",
  "Open SeldomQA casebook on GitHub": "在 GitHub 打开 SeldomQA Casebook", "Sidebar": "侧边栏",
  "Case Files": "用例文件", "Loading cases...": "正在加载用例...", "Loading...": "正在加载...",
  "Resize sidebar": "调整侧边栏宽度", "AI-NATIVE TEST ENGINEERING": "AI 原生测试工程",
  "Test case workspace": "测试用例工作台",
  "Review test assets, focus risk, and track execution in one local workspace.": "在一个本地工作台中评审测试资产、聚焦风险并跟踪执行。",
  "Project overview": "项目概览", "Files": "文件", "Cases": "用例", "P0 risk": "P0 风险", "Automated": "自动化",
  "The YAML files changed while you were editing.": "编辑期间 YAML 文件已发生变化。", "Reload now": "立即重新加载",
  "Test plan": "测试计划", "No plan selected": "未选择计划", "Manage plan": "管理计划",
  "Progress": "进度", "Not enabled": "未启用", "No file selected": "未选择文件",
  "Choose a YAML file from the Case Files navigation to review and edit its cases.": "从用例文件导航中选择 YAML 文件以评审和编辑用例。",
  "ID sorting": "ID 排序", "Execution result filter": "执行结果筛选", "Filter current file": "筛选当前文件",
  "Title": "标题", "Priority": "优先级", "Type": "类型", "Tags": "标签", "Plans": "计划", "Actions": "操作",
  "No matching cases": "没有匹配的用例", "Adjust the current file filter and try again.": "请调整当前文件筛选条件后重试。",
  "test execution": "测试执行", "Close test plan drawer": "关闭测试计划抽屉", "Current plan": "当前计划",
  "Select the plan used for case execution.": "选择用于执行用例的测试计划。", "Select current test plan": "选择当前测试计划",
  "Create plan": "创建计划", "Create a full run or retest unresolved cases.": "创建全量执行计划或重测未解决用例。",
  "New test plan mode": "新测试计划模式", "Full run": "全量执行",
  "Retest failed/blocked/deferred": "重测失败、阻塞或延期用例", "Source test plan": "来源测试计划",
  "New test plan name": "新测试计划名称", "Complete plan": "完成计划", "Select a test plan first.": "请先选择测试计划。",
  "Environment": "测试环境", "Tester": "测试人员", "Test report name": "测试报告名称",
  "Complete plan & generate report": "完成计划并生成报告", "Generated reports": "已生成报告",
  "edit case": "编辑用例", "Untitled": "未命名", "Close editor": "关闭编辑器", "case id": "用例 ID",
  "title": "标题", "description": "描述", "priority": "优先级", "type": "类型", "tags": "标签",
  "preconditions": "前置条件", "steps": "步骤", "expected results": "预期结果", "automated case": "自动化用例",
  "add to plan": "加入计划", "Select a test plan": "选择测试计划", "Add to plan": "加入计划", "Save": "保存",
  "Close screenshot preview": "关闭截图预览", "Screenshot preview": "截图预览", "Screenshot": "截图",
  "Execution screenshot preview": "执行截图预览", "No scan directory": "没有扫描目录", "No YAML cases found.": "未找到 YAML 用例。",
  "Module": "模块", "Feature": "功能", "Owner": "负责人", "Reviewed": "评审日期", "Path": "路径", "Unknown": "未知",
  "Current plan: none": "当前计划：无", "Source plan": "来源计划", "New retest plan name": "新重测计划名称",
  "Create retest": "创建重测计划", "Generate report": "生成报告", "Selected plan": "已选择计划",
  "All": "全部", "Passed": "通过", "Failed": "失败", "Blocked": "阻塞", "Deferred": "延期", "Untested": "未测试",
  "Pass": "通过", "Fail": "失败", "Block": "阻塞", "Defer": "延期", "Edit": "编辑", "Auto": "自动化",
  "Preconditions": "前置条件", "Steps": "步骤", "Expected Results": "预期结果", "Execution": "执行信息",
  "Execution status": "执行状态", "Mark": "标记", "Describe what should be updated": "描述需要更新的内容",
  "Save review": "保存评审", "Actual Result": "实际结果",
  "Actual result observed during execution": "记录执行过程中观察到的实际结果", "Notes": "备注",
  "Execution notes": "执行备注", "Defects": "缺陷", "Bug links or defect IDs, one per line": "缺陷链接或缺陷 ID，每行一个",
  "Screenshots": "截图", "Upload screenshot": "上传截图", "Save execution": "保存执行信息",
  "No screenshots": "暂无截图", "Delete screenshot": "删除截图", "None": "无", "Select an active plan": "选择进行中的计划",
  "Select language": "选择语言",
  "{files} files - {cases} cases": "{files} 个文件 - {cases} 条用例", "Scope: {scope}": "范围：{scope}",
  "Scope: {scope} - {mode} - {count} cases": "范围：{scope} - {mode} - {count} 条用例",
  "{executed} / {total} executed - {percent}%": "已执行 {executed} / {total} - {percent}%",
  "{count} cases": "{count} 条用例", "No records": "暂无记录", "Open {name}": "打开 {name}",
  "Full": "全量", "Retest": "重测", "Collapse case details": "收起用例详情", "Expand case details": "展开用例详情",
  "Expand all cases": "全部展开", "Collapse all cases": "全部收起",
  "Copy case ID": "复制用例 ID", "Copy case ID {id}": "复制用例 ID {id}",
  "Completed test plans cannot be updated": "已完成的测试计划不能修改",
  "Update IDs and preserve execution results in the current test plan": "更新 ID 并保留当前计划的执行结果",
  "Update case IDs using the current YAML order": "按当前 YAML 顺序更新用例 ID",
  "This test plan is completed. Enter a report name to generate it again.": "该测试计划已完成。输入报告名称可再次生成报告。",
  "{count} untested cases remain before completion.": "完成计划前还有 {count} 条未测试用例。",
  "All cases are executed. Add the report name, then complete the plan.": "所有用例均已执行。填写报告名称后完成计划。",
  "Included in: {plans}": "已加入：{plans}", "Not included in a test plan.": "尚未加入测试计划。",
  "Enter a test plan name": "请输入测试计划名称", "Select a source test plan": "请选择来源测试计划",
  "Create a full test plan for the current scope": "为当前范围创建全量测试计划",
  "Create a new plan from the selected plan's failed, blocked, and deferred cases": "根据所选计划中失败、阻塞和延期的用例创建重测计划",
  "Select an active test plan": "请选择进行中的测试计划", "Case added to test plan": "用例已加入测试计划",
  "Case is already in this test plan": "用例已在该测试计划中", "Saved to YAML": "已保存到 YAML",
  "Review details saved": "评审信息已保存", "Enter a test plan name before creating the plan": "创建计划前请输入测试计划名称",
  "Select a source test plan before creating a retest plan": "创建重测计划前请选择来源测试计划",
  "Retest plan created": "重测计划已创建", "Test plan created": "测试计划已创建",
  "Select or create a test plan first": "请先选择或创建测试计划", "Enter a test report name": "请输入测试报告名称",
  "Test report generated": "测试报告已生成", "Test plan completed": "测试计划已完成",
  "Execution details saved": "执行信息已保存", "Choose a screenshot first": "请先选择截图",
  "Screenshot uploaded": "截图已上传", "Screenshot deleted": "截图已删除", "Delete this screenshot?": "确定删除这张截图吗？",
  "Update case IDs and synchronize this file with the current test plan? Existing execution results will be retained by case mapping.": "是否更新用例 ID 并将该文件同步到当前测试计划？现有执行结果会按用例映射保留。",
  "Update case IDs using the current YAML order? The case order will not change.": "是否按当前 YAML 顺序更新用例 ID？用例顺序不会改变。",
  "Generate a report for this completed test plan": "为已完成的测试计划生成报告",
  "Complete the test plan and generate its report": "完成测试计划并生成报告",
  "Cannot complete: {count} untested cases remain": "无法完成：还有 {count} 条用例未测试",
  "{name} report": "{name} 报告", "Report": "报告", "No scope": "无范围",
  "Enter a valid report name": "请输入有效的报告名称"
};
const SIDEBAR_MIN_WIDTH = 260;
const SIDEBAR_MAX_WIDTH = 560;

const state = {
  language: readStoredLanguage(),
  summary: null,
  tree: [],
  marks: {},
  runs: [],
  currentRunId: null,
  currentRun: null,
  generatedReport: null,
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
    "languageToggle",
    "summaryText",
    "overviewFiles",
    "overviewCases",
    "overviewP0",
    "overviewAuto",
    "treePanel",
    "sidebarToggle",
    "sidebarResizer",
    "reloadNotice",
    "reloadNowButton",
    "emptyState",
    "fileView",
    "executionPanel",
    "executionSummary",
    "executionToggle",
    "executionPanelBody",
    "executionScopeText",
    "currentRunSummaryLabel",
    "testPlanProgressOverview",
    "testPlanDrawer",
    "closeTestPlanDrawerButton",
    "runSelect",
    "runModeSelect",
    "sourceRunSelect",
    "runNameInput",
    "createRunButton",
    "completionControlRow",
    "runEnvironmentInput",
    "runTesterInput",
    "reportNameInput",
    "reportOutputList",
    "completeRunButton",
    "executionProgressBar",
    "executionProgressText",
    "executionStats",
    "completionHint",
    "fileMeta",
    "caseSearch",
    "priorityFilters",
    "executionFilter",
    "renumberIdsButton",
    "toggleAllCasesButton",
    "caseRows",
    "noResults",
    "editorDrawer",
    "drawerScrim",
    "screenshotViewer",
    "screenshotViewerBackdrop",
    "screenshotViewerClose",
    "screenshotViewerTitle",
    "screenshotViewerImage",
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
    "casePlanSelect",
    "addCaseToPlanButton",
    "casePlanMembership",
    "saveCaseButton",
    "toast",
  ].forEach((id) => {
    els[id] = document.getElementById(id);
  });
}

function bindEvents() {
  els.languageToggle.addEventListener("change", () => {
    setLanguage(els.languageToggle.value);
  });
  els.sidebarToggle.addEventListener("click", toggleSidebar);
  els.sidebarResizer.addEventListener("pointerdown", startSidebarResize);
  els.sidebarResizer.addEventListener("keydown", handleSidebarResizeKeydown);
  window.addEventListener("resize", syncSidebarWidthToViewport);
  els.reloadNowButton.addEventListener("click", () => reloadAfterExternalChange(true));
  els.executionSummary.addEventListener("click", (event) => {
    if (event.target.closest("button")) return;
    toggleTestPlanPanel();
  });
  els.executionToggle.addEventListener("click", toggleTestPlanPanel);
  els.runSelect.addEventListener("change", () => selectRun(els.runSelect.value));
  els.runModeSelect.addEventListener("change", renderExecutionPanel);
  els.sourceRunSelect.addEventListener("change", renderExecutionPanel);
  els.runNameInput.addEventListener("input", syncCreateRunButtonState);
  els.createRunButton.addEventListener("click", createRun);
  els.completeRunButton.addEventListener("click", completeRun);
  els.renumberIdsButton.addEventListener("click", renumberCurrentFile);
  els.toggleAllCasesButton.addEventListener("click", toggleAllCaseDetails);
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
    const copyCaseIdButton = event.target.closest("button[data-copy-case-id]");
    if (copyCaseIdButton) {
      event.stopPropagation();
      copyCaseId(copyCaseIdButton.dataset.copyCaseId);
      return;
    }
    const deleteScreenshotButton = event.target.closest("button[data-delete-screenshot]");
    if (deleteScreenshotButton) {
      event.stopPropagation();
      deleteExecutionScreenshot(deleteScreenshotButton.dataset.screenshotId);
      return;
    }
    const screenshotPreviewButton = event.target.closest("button[data-screenshot-preview]");
    if (screenshotPreviewButton) {
      event.stopPropagation();
      openScreenshotViewer(
        screenshotPreviewButton.dataset.src,
        screenshotPreviewButton.dataset.name || t("Screenshot"),
      );
      return;
    }
    const uploadScreenshotButton = event.target.closest("button[data-upload-screenshot]");
    if (uploadScreenshotButton) {
      event.stopPropagation();
      uploadExecutionScreenshot(uploadScreenshotButton.dataset.caseId);
      return;
    }
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
  els.closeTestPlanDrawerButton.addEventListener("click", closeTestPlanDrawer);
  els.drawerScrim.addEventListener("click", closeActiveDrawer);
  els.screenshotViewerBackdrop.addEventListener("click", closeScreenshotViewer);
  els.screenshotViewerClose.addEventListener("click", closeScreenshotViewer);
  els.saveCaseButton.addEventListener("click", saveCase);
  els.addCaseToPlanButton?.addEventListener("click", addCurrentCaseToPlan);
  els.caseForm.addEventListener("input", (event) => {
    if (event.target.closest(".case-plan-assignment")) return;
    state.dirty = true;
  });
  window.addEventListener("hashchange", () => {
    const path = decodeURIComponent(window.location.hash.replace(/^#/, ""));
    if (path && path !== state.currentFile) loadFile(path);
  });
  window.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !els.screenshotViewer.hidden) {
      closeScreenshotViewer();
      return;
    }
    if (event.key === "Escape" && state.testPlanExpanded) {
      closeTestPlanDrawer();
      return;
    }
    if (event.key === "Escape" && els.editorDrawer.classList.contains("open")) {
      closeDrawer();
    }
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
  applyStaticTranslations();
  await refreshAll();
  connectEvents();
  const hashPath = decodeURIComponent(window.location.hash.replace(/^#/, ""));
  if (hashPath) {
    await loadFile(hashPath);
  }
}

function readStoredLanguage() {
  try {
    return window.localStorage.getItem(LANGUAGE_STORAGE_KEY) === "zh-CN" ? "zh-CN" : "en";
  } catch (_error) {
    return "en";
  }
}

function t(key, values = {}) {
  const template = state.language === "zh-CN" ? (ZH_TRANSLATIONS[key] || key) : key;
  return Object.entries(values).reduce(
    (text, [name, value]) => text.replaceAll(`{${name}}`, String(value)),
    template,
  );
}

function setLanguage(language) {
  state.language = language === "zh-CN" ? "zh-CN" : "en";
  try {
    window.localStorage.setItem(LANGUAGE_STORAGE_KEY, state.language);
  } catch (_error) {
    // Language switching still works when browser storage is unavailable.
  }
  applyStaticTranslations();
  if (state.summary) renderShell();
  renderExecutionPanel();
  if (state.currentData) {
    renderFileMeta();
    renderFilters();
    renderCaseRows();
  }
  if (state.selectedCaseId) {
    const selected = findCase(state.selectedCaseId);
    if (selected) fillDrawer(selected);
  }
}

function setText(selector, key) {
  const node = document.querySelector(selector);
  if (node) node.textContent = t(key);
}

function setAttribute(selector, attribute, key) {
  const node = document.querySelector(selector);
  if (node) node.setAttribute(attribute, t(key));
}

function setFormLabel(controlId, key) {
  const label = document.getElementById(controlId)?.closest("label")?.querySelector(":scope > span");
  if (label) label.textContent = t(key);
}

function applyStaticTranslations() {
  document.documentElement.lang = state.language;
  els.languageToggle.value = state.language;
  els.languageToggle.setAttribute("aria-label", t("Select language"));
  [
    [".app-brand-copy small", "Test quality workspace"], [".sidebar-heading h2", "Case Files"],
    ["#summaryText", "Loading cases..."], ["#scanDirs", "Loading..."],
    [".dashboard-kicker", "AI-NATIVE TEST ENGINEERING"], ["#workspaceTitle", "Test case workspace"],
    [".dashboard-hero-copy > p:last-child", "Review test assets, focus risk, and track execution in one local workspace."],
    [".overview-files span", "Files"], [".overview-cases span", "Cases"], [".overview-risk span", "P0 risk"],
    [".overview-auto span", "Automated"], ["#reloadNotice span", "The YAML files changed while you were editing."],
    ["#reloadNowButton", "Reload now"], [".test-plan-title h3", "Test plan"], ["#executionToggle", "Manage plan"],
    [".test-plan-progress-heading span", "Progress"], ["#emptyState h3", "No file selected"],
    ["#emptyState p", "Choose a YAML file from the Case Files navigation to review and edit its cases."],
    ["#renumberIdsButton", "ID sorting"], ["#noResults h3", "No matching cases"],
    ["#noResults p", "Adjust the current file filter and try again."], [".test-plan-drawer .eyebrow", "test execution"],
    [".test-plan-drawer .drawer-header h2", "Test plan"], [".plan-drawer-section:nth-child(1) .plan-section-heading span", "Current plan"],
    [".plan-drawer-section:nth-child(1) .plan-section-heading small", "Select the plan used for case execution."],
    [".plan-drawer-section:nth-child(2) .plan-section-heading span", "Create plan"],
    [".plan-drawer-section:nth-child(2) .plan-section-heading small", "Create a full run or retest unresolved cases."],
    [".completion-section .plan-section-heading span", "Complete plan"], ["#editorDrawer .eyebrow", "edit case"],
    ["#addCaseToPlanButton", "Add to plan"], ["#saveCaseButton", "Save"],
    ["#screenshotViewerTitle", "Screenshot"],
  ].forEach(([selector, key]) => setText(selector, key));
  [
    ["fieldId", "case id"], ["fieldTitle", "title"], ["fieldDescription", "description"],
    ["fieldPriority", "priority"], ["fieldType", "type"], ["fieldTags", "tags"],
    ["fieldPreconditions", "preconditions"], ["fieldSteps", "steps"],
    ["fieldExpectedResults", "expected results"], ["fieldAuto", "automated case"],
    ["casePlanSelect", "add to plan"],
  ].forEach(([controlId, key]) => setFormLabel(controlId, key));
  const tableLabels = ["", "ID", "Title", "Priority", "Type", "Tags", "Plans", "Actions"];
  document.querySelectorAll(".case-table-head > span").forEach((node, index) => {
    if (tableLabels[index]) node.textContent = t(tableLabels[index]);
  });
  const modeOptions = els.runModeSelect.options;
  if (modeOptions[0]) modeOptions[0].textContent = t("Full run");
  if (modeOptions[1]) modeOptions[1].textContent = t("Retest failed/blocked/deferred");
  setAttribute("#sidebarToggle", "aria-label", "Toggle sidebar");
  setAttribute(".dashboard-overview", "aria-label", "Project overview");
  setAttribute(".github-link", "aria-label", "Open SeldomQA casebook on GitHub");
  setAttribute(".sidebar", "aria-label", "Sidebar");
  setAttribute("#sidebarResizer", "aria-label", "Resize sidebar");
  setAttribute("#caseSearch", "placeholder", "Filter current file");
  setAttribute("#closeTestPlanDrawerButton", "aria-label", "Close test plan drawer");
  setAttribute("#closeDrawerButton", "aria-label", "Close editor");
  setAttribute("#screenshotViewerBackdrop", "aria-label", "Close screenshot preview");
  setAttribute(".screenshot-viewer-dialog", "aria-label", "Screenshot preview");
  setAttribute("#screenshotViewerImage", "alt", "Execution screenshot preview");
  setAttribute("#runSelect", "aria-label", "Select current test plan");
  setAttribute("#runModeSelect", "aria-label", "New test plan mode");
  setAttribute("#sourceRunSelect", "aria-label", "Source test plan");
  setAttribute("#executionFilter", "aria-label", "Execution result filter");
  setAttribute("#casePlanSelect", "aria-label", "Select a test plan");
  setAttribute("#reportOutputList", "aria-label", "Generated reports");
  setAttribute("#runNameInput", "placeholder", "New test plan name");
  setAttribute("#runEnvironmentInput", "placeholder", "Environment");
  setAttribute("#runTesterInput", "placeholder", "Tester");
  setAttribute("#reportNameInput", "placeholder", "Test report name");
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
  if (!state.currentRunId) {
    state.currentRunId = storedCurrentRunId();
  }
  if (state.currentRunId && !state.runs.some((run) => run.id === state.currentRunId)) {
    state.currentRunId = null;
    state.currentRun = null;
    persistCurrentRunId(null);
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
  const isFormData = options.body instanceof FormData;
  const headers = isFormData
    ? (options.headers || {})
    : { "Content-Type": "application/json", ...(options.headers || {}) };
  const response = await fetch(path, {
    ...options,
    headers,
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
      persistCurrentRunId(null);
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
  const stats = summary.stats || {};
  els.scanDirs.textContent = (summary.scan_dirs || []).join(", ") || t("No scan directory");
  els.summaryText.textContent = t("{files} files - {cases} cases", { files: summary.files || 0, cases: summary.cases || 0 });
  els.overviewFiles.textContent = summary.files || 0;
  els.overviewCases.textContent = summary.cases || 0;
  els.overviewP0.textContent = stats.priorities?.P0 || 0;
  els.overviewAuto.textContent = stats.auto_count || 0;
  els.treePanel.innerHTML = renderTree(state.tree, 0);
  markActiveTreeItem();
}

function renderTree(items, depth) {
  if (!items || !items.length) {
    return depth === 0 ? `<div class="empty-tree">${t("No YAML cases found.")}</div>` : "";
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
    [t("Module"), data.module || t("Unknown")],
    [t("Feature"), data.feature || t("Untitled")],
    [t("Owner"), data.owner || "N/A"],
    [t("Reviewed"), data.last_reviewed || "N/A"],
  ];
  els.fileMeta.innerHTML = `
    <div class="file-meta-row">
      ${items.map(([label, value]) => renderMetaItem(label, value)).join("")}
    </div>
    <div class="file-meta-row path-row">
      ${renderMetaItem(t("Path"), data.path || "", true)}
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

  els.testPlanDrawer.classList.toggle("open", state.testPlanExpanded);
  els.testPlanDrawer.setAttribute("aria-hidden", String(!state.testPlanExpanded));
  els.executionToggle.setAttribute("aria-expanded", String(state.testPlanExpanded));
  els.executionScopeText.textContent = run
    ? t("Scope: {scope} - {mode} - {count} cases", { scope, mode: runModeLabel(run.mode), count: stats.total })
    : t("Scope: {scope}", { scope });
  els.executionProgressText.textContent = run
    ? t("{executed} / {total} executed - {percent}%", { executed: stats.executed, total: stats.total, percent })
    : t("Not enabled");
  els.testPlanProgressOverview.hidden = !state.currentRunId;
  els.currentRunSummaryLabel.textContent = run
    ? (run.name || run.id || t("Selected plan"))
    : t("No plan selected");

  const options = [
    `<option value="">${t("Current plan: none")}</option>`,
    ...runs.map((item) => `<option value="${escapeAttr(item.id)}">${escapeHtml(runOptionLabel(item))}</option>`),
  ];
  els.runSelect.innerHTML = options.join("");
  els.runSelect.value = state.currentRunId || "";
  const createMode = els.runModeSelect.value || "full";
  const previousSourceRunId = els.sourceRunSelect.value;
  const sourceOptions = [
    `<option value="">${t("Source plan")}</option>`,
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
    ? t("New retest plan name")
    : t("New test plan name");
  els.createRunButton.textContent = createMode === "retest_unresolved"
    ? t("Create retest")
    : t("Create plan");
  syncCreateRunButtonState();
  const isCompleted = run?.status === "completed";
  const canFinishRun = Boolean(state.currentRunId && stats.total > 0 && stats.untested === 0);
  const canCompleteRun = canFinishRun && !isCompleted;
  els.completionControlRow.hidden = !state.currentRunId;
  els.runEnvironmentInput.value = run?.environment || defaults.environment;
  els.runTesterInput.value = run?.tester || defaults.tester;
  if (run && !els.reportNameInput.value.trim()) {
    els.reportNameInput.value = t("{name} report", { name: run.name || run.id || "test-plan" });
  }
  els.runEnvironmentInput.disabled = !canCompleteRun;
  els.runTesterInput.disabled = !canCompleteRun;
  els.reportNameInput.disabled = !canFinishRun;
  els.completeRunButton.disabled = !canFinishRun;
  els.completeRunButton.textContent = isCompleted
    ? t("Generate report")
    : t("Complete plan & generate report");
  els.completeRunButton.title = state.currentRunId && stats.untested > 0
    ? t("Cannot complete: {count} untested cases remain", { count: stats.untested })
    : isCompleted
      ? t("Generate a report for this completed test plan")
      : t("Complete the test plan and generate its report");
  const reports = Array.isArray(run?.reports)
    ? [...run.reports].sort((left, right) => String(left.name || left.filename || "")
      .localeCompare(String(right.name || right.filename || "")))
    : [];
  els.reportOutputList.hidden = reports.length === 0;
  els.reportOutputList.innerHTML = reports.length ? `
    <span class="report-output-heading">${t("Generated reports")}</span>
    ${reports.map((report) => `
    <a class="outline-button report-output-link"
      href="/reports/${encodeURIComponent(report.filename || "")}" target="_blank"
      rel="noopener noreferrer" title="${escapeAttr(t("Open {name}", { name: report.name || report.filename || "report" }))}">
      ${escapeHtml(report.name || report.filename || t("Report"))}
    </a>
    `).join("")}
  ` : "";
  els.completionHint.textContent = !state.currentRunId
    ? t("Select a test plan first.")
    : isCompleted
      ? t("This test plan is completed. Enter a report name to generate it again.")
      : stats.untested > 0
        ? t("{count} untested cases remain before completion.", { count: stats.untested })
        : t("All cases are executed. Add the report name, then complete the plan.");
  syncRenumberButton();

  els.executionProgressBar.style.width = `${percent}%`;
  els.executionStats.innerHTML = [
    ["total", t("Cases"), stats.total],
    ["passed", t("Passed"), stats.passed],
    ["failed", t("Failed"), stats.failed],
    ["blocked", t("Blocked"), stats.blocked],
    ["deferred", t("Deferred"), stats.deferred],
    ["untested", t("Untested"), stats.untested],
  ].map(([status, label, value]) => `
    <div class="execution-stat status-${status}">
      <strong>${value}</strong>
      <span>${label}</span>
    </div>
  `).join("");
}

function syncRenumberButton() {
  if (!els.renumberIdsButton) return;
  const completedPlan = Boolean(state.currentRunId && state.currentRun?.run?.status === "completed");
  const disabled = !state.currentData || completedPlan;
  els.renumberIdsButton.disabled = disabled;
  els.renumberIdsButton.title = completedPlan
    ? t("Completed test plans cannot be updated")
    : state.currentRunId
      ? t("Update IDs and preserve execution results in the current test plan")
      : t("Update case IDs using the current YAML order");
}

function runOptionLabel(run) {
  const name = run.name || run.id;
  const hasCaseTotal = run.case_total !== null && run.case_total !== undefined && run.case_total !== "";
  const count = hasCaseTotal && Number.isFinite(Number(run.case_total))
    ? ` - ${t("{count} cases", { count: Number(run.case_total) })}`
    : "";
  return `${name} - ${runModeLabel(run.mode)}${count}`;
}

function runModeLabel(mode) {
  return mode === "retest_unresolved" ? t("Retest") : t("Full");
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
    ["all", t("All"), counts.all],
    ["P0", "P0", counts.P0],
    ["P1", "P1", counts.P1],
    ["P2", "P2", counts.P2],
    ["needs", t("Mark"), counts.needs],
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
    return `<option value="${value}">${escapeHtml(t(label))} (${count || 0})</option>`;
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
  const visibleCases = currentCasePool().filter(matchesCurrentFilter);
  renderCaseExpansionButton(visibleCases);
  const rows = visibleCases
    .map((caseItem) => {
      const key = markKey(state.currentData.path, caseItem.id);
      const mark = reviewMark(caseItem.id);
      const marked = Boolean(mark.needs_update);
      const selected = state.selectedCaseId === caseItem.id;
      const expanded = state.expandedCaseIds.has(caseItem.id);
      const execStatus = executionStatus(caseItem.id);
      const tags = [
        ...(caseItem.tags || []).map((tag) => `<span class="tag">${escapeHtml(tag)}</span>`),
        marked ? `<span class="tag mark-tag">${t("Mark")}</span>` : "",
      ].join("");
      const description = caseItem.description
        ? `<p class="case-description">${escapeHtml(caseItem.description)}</p>`
        : "";
      return `
        <article class="case-item${selected ? " selected" : ""}${expanded ? " expanded" : ""} exec-${escapeAttr(execStatus)}" data-case-id="${escapeAttr(caseItem.id)}">
          <div class="case-summary" data-case-summary data-case-id="${escapeAttr(caseItem.id)}">
            <div class="case-toggle-cell">
              <button class="chevron-button" type="button" data-toggle-case="1" data-case-id="${escapeAttr(caseItem.id)}" aria-expanded="${expanded}" aria-label="${t(expanded ? "Collapse case details" : "Expand case details")}">
                <span class="chevron-icon" aria-hidden="true">›</span>
              </button>
            </div>
            <div class="case-id-cell">
              <button class="case-id copy-case-id" type="button" data-copy-case-id="${escapeAttr(caseItem.id)}"
                title="${t("Copy case ID")}" aria-label="${escapeAttr(t("Copy case ID {id}", { id: caseItem.id }))}">${escapeHtml(caseItem.id)}</button>
            </div>
            <div class="case-main-cell">
              <div class="case-title-line">
                <h4 class="case-title">${escapeHtml(caseItem.title)}</h4>
                ${caseItem.auto ? `<span class="auto-pill">${t("Auto")}</span>` : ""}
              </div>
              ${description}
            </div>
            <div class="case-priority-cell">
              <span class="badge priority-${escapeAttr(caseItem.priority).toLowerCase()}">${escapeHtml(caseItem.priority)}</span>
            </div>
            <div class="case-type-cell">${escapeHtml(caseItem.type)}</div>
            <div class="case-tags-cell"><div class="tag-list">${tags}</div></div>
            <div class="case-plans-cell">${renderCasePlans(caseItem)}</div>
            <div class="case-actions">
              ${state.currentRun ? renderExecutionActions(caseItem.id, execStatus) : ""}
              ${state.currentRun ? "" : `<button class="text-action" type="button" data-edit-case="1" data-case-id="${escapeAttr(caseItem.id)}">${t("Edit")}</button>`}
            </div>
          </div>
          ${expanded ? renderCaseDetails(caseItem) : ""}
        </article>`;
    });
  els.caseRows.innerHTML = rows.join("");
  els.noResults.hidden = rows.length > 0;
}

function plansForCase(caseItem) {
  if (!state.currentData || !caseItem) return [];
  const key = markKey(state.currentData.path, caseItem.id);
  return (state.runs || []).filter(
    (run) => Array.isArray(run.case_scope) && run.case_scope.includes(key),
  );
}

function renderCasePlans(caseItem) {
  const plans = plansForCase(caseItem);
  if (!plans.length) return `<span class="case-plan-empty">—</span>`;
  return `<div class="case-plan-list">${plans.map((run) => `
    <span class="case-plan-pill${run.status === "completed" ? " completed" : ""}" title="${escapeAttr(run.name || run.id)}">
      ${escapeHtml(run.name || run.id)}
    </span>`).join("")}</div>`;
}

function renderCaseDetails(caseItem) {
  return `
    <div class="case-details">
      <div class="case-details-card">
        <div class="case-detail-column">
          ${renderDetailList(t("Preconditions"), caseItem.preconditions, false)}
          ${renderDetailList(t("Steps"), caseItem.steps, true)}
        </div>
        <div class="case-detail-column">
          ${renderDetailList(t("Expected Results"), caseItem.expected_results, false)}
        </div>
      </div>
      <div class="case-side-panel">
        ${state.currentRun ? renderExecutionDetails(caseItem) : renderReviewDetails(caseItem)}
      </div>
    </div>`;
}

function renderExecutionActions(caseId, currentStatus) {
  const statuses = [
    ["passed", t("Pass")],
    ["failed", t("Fail")],
    ["blocked", t("Block")],
    ["deferred", t("Defer")],
  ];
  const disabled = state.currentRun ? "" : " disabled";
  return `
    <div class="execution-actions" aria-label="${t("Execution status")}">
      <select class="execution-select status-${escapeAttr(currentStatus)}" data-exec-select="1" data-case-id="${escapeAttr(caseId)}" aria-label="${t("Execution status")}"${disabled}>
        <option value="untested"${currentStatus === "untested" ? " selected" : ""} disabled>${t("Untested")}</option>
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
        <span>${t("Mark")}</span>
      </label>
      <textarea data-review-notes="${escapeAttr(caseItem.id)}" rows="5" placeholder="${t("Describe what should be updated")}">${escapeHtml(mark.notes || "")}</textarea>
      <button class="outline-button review-save-button" type="button" data-save-review="1" data-case-id="${escapeAttr(caseItem.id)}">${t("Save review")}</button>
    </aside>`;
}

function renderExecutionDetails(caseItem) {
  const result = executionResult(caseItem.id) || {};
  const defects = Array.isArray(result.defects) ? result.defects.join("\n") : (result.defects || "");
  const screenshots = Array.isArray(result.screenshots) ? result.screenshots : [];
  return `
    <section class="detail-section execution-detail-section">
      <h5>${detailIcon("Execution")}<span>${t("Execution")}</span></h5>
      <div class="execution-detail-grid">
        <label>
          <span>${t("Actual Result")}</span>
          <textarea data-exec-actual-result="${escapeAttr(caseItem.id)}" rows="3" placeholder="${t("Actual result observed during execution")}">${escapeHtml(result.actual_result || "")}</textarea>
        </label>
        <label>
          <span>${t("Notes")}</span>
          <textarea data-exec-notes="${escapeAttr(caseItem.id)}" rows="3" placeholder="${t("Execution notes")}">${escapeHtml(result.notes || "")}</textarea>
        </label>
        <label>
          <span>${t("Defects")}</span>
          <textarea data-exec-defects="${escapeAttr(caseItem.id)}" rows="2" placeholder="${t("Bug links or defect IDs, one per line")}">${escapeHtml(defects)}</textarea>
        </label>
        <div class="execution-screenshot-field">
          <span>${t("Screenshots")}</span>
          <div class="screenshot-upload-row">
            <input data-exec-screenshot="${escapeAttr(caseItem.id)}" type="file" accept="image/png,image/jpeg,image/gif,image/webp">
            <button class="outline-button screenshot-upload-button" type="button" data-upload-screenshot="1" data-case-id="${escapeAttr(caseItem.id)}"${state.currentRun ? "" : " disabled"}>${t("Upload screenshot")}</button>
          </div>
          ${renderScreenshotList(screenshots)}
        </div>
        <button class="outline-button execution-save-button" type="button" data-save-execution="1" data-case-id="${escapeAttr(caseItem.id)}"${state.currentRun ? "" : " disabled"}>${t("Save execution")}</button>
      </div>
    </section>`;
}

function renderScreenshotList(screenshots) {
  if (!screenshots.length) {
    return `<div class="screenshot-list empty">${t("No screenshots")}</div>`;
  }
  return `
    <div class="screenshot-list">
      ${screenshots.map((screenshot) => {
    const src = screenshotUrl(screenshot);
    const name = screenshot.name || t("Screenshot");
    const screenshotId = screenshot.id || "";
    return `
          <div class="screenshot-thumb-wrap">
            <button class="screenshot-thumb" type="button" data-screenshot-preview="1" data-src="${escapeAttr(src)}" data-name="${escapeAttr(name)}" title="${escapeAttr(name)}">
              <img src="${escapeAttr(src)}" alt="${escapeAttr(name)}">
              <span>${escapeHtml(name)}</span>
            </button>
            <button class="screenshot-delete-button" type="button" data-delete-screenshot="1" data-screenshot-id="${escapeAttr(screenshotId)}" aria-label="${t("Delete screenshot")}">×</button>
          </div>`;
  }).join("")}
    </div>`;
}

function renderDetailList(title, items, ordered) {
  const values = items || [];
  const content = values.length
    ? values.map((item) => `<li>${escapeHtml(item)}</li>`).join("")
    : `<li class="empty-detail">${t("None")}</li>`;
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

function renderCaseExpansionButton(visibleCases) {
  const allExpanded = visibleCases.length > 0
    && visibleCases.every((caseItem) => state.expandedCaseIds.has(caseItem.id));
  const label = t(allExpanded ? "Collapse all cases" : "Expand all cases");
  els.toggleAllCasesButton.disabled = visibleCases.length === 0;
  els.toggleAllCasesButton.title = label;
  els.toggleAllCasesButton.setAttribute("aria-label", label);
  els.toggleAllCasesButton.setAttribute("aria-expanded", String(allExpanded));
  els.toggleAllCasesButton.classList.toggle("all-expanded", allExpanded);
}

function toggleAllCaseDetails() {
  const visibleCases = currentCasePool().filter(matchesCurrentFilter);
  const allExpanded = visibleCases.length > 0
    && visibleCases.every((caseItem) => state.expandedCaseIds.has(caseItem.id));
  visibleCases.forEach((caseItem) => {
    if (allExpanded) {
      state.expandedCaseIds.delete(caseItem.id);
    } else {
      state.expandedCaseIds.add(caseItem.id);
    }
  });
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
  closeTestPlanDrawer();
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
  syncDrawerScrim();
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
  renderCasePlanAssignment(caseItem);
  state.dirty = false;
}

function renderCasePlanAssignment(caseItem) {
  if (!els.casePlanSelect || !els.addCaseToPlanButton || !els.casePlanMembership) return;
  const memberships = plansForCase(caseItem);
  const memberIds = new Set(memberships.map((run) => run.id));
  const available = (state.runs || []).filter(
    (run) => run.status === "in_progress" && !memberIds.has(run.id),
  );
  els.casePlanSelect.innerHTML = [
    `<option value="">${t("Select an active plan")}</option>`,
    ...available.map((run) => `<option value="${escapeAttr(run.id)}">${escapeHtml(runOptionLabel(run))}</option>`),
  ].join("");
  els.casePlanSelect.disabled = !available.length;
  els.addCaseToPlanButton.disabled = !available.length;
  els.casePlanMembership.textContent = memberships.length
    ? t("Included in: {plans}", { plans: memberships.map((run) => run.name || run.id).join(", ") })
    : t("Not included in a test plan.");
}

async function addCurrentCaseToPlan() {
  if (!state.currentData || !state.selectedCaseId || !els.casePlanSelect) return;
  const runId = els.casePlanSelect.value;
  if (!runId) {
    showToast("Select an active test plan");
    return;
  }
  try {
    const response = await api(`/api/test-runs/${encodeURIComponent(runId)}/cases`, {
      method: "POST",
      body: JSON.stringify({
        file_path: state.currentData.path,
        case_id: state.selectedCaseId,
      }),
    });
    await refreshAll();
    const selected = findCase(state.selectedCaseId);
    if (selected) renderCasePlanAssignment(selected);
    renderCaseRows();
    showToast(response.added ? "Case added to test plan" : "Case is already in this test plan");
  } catch (error) {
    showToast(error.message);
  }
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
  if (state.currentRunId && state.currentRun?.run?.status === "completed") {
    showToast("Completed test plans cannot be updated");
    return;
  }
  const message = state.currentRunId
    ? "Update case IDs and synchronize this file with the current test plan? Existing execution results will be retained by case mapping."
    : "Update case IDs using the current YAML order? The case order will not change.";
  const confirmed = window.confirm(t(message));
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
    if (response.run_sync?.run) state.currentRun = response.run_sync.run;
    state.expandedCaseIds = new Set();
    if (state.selectedCaseId) closeDrawer();
    await refreshAll();
    await loadFile(filePath, { keepFilter: true });
    const changed = Number(response.result?.changed || 0);
    const total = Number(response.result?.total || 0);
    const removed = Number(response.run_sync?.removed_results || 0);
    const planNote = response.run_sync
      ? `; plan synchronized${removed ? `, removed ${removed} deleted result${removed === 1 ? "" : "s"}` : ""}`
      : "";
    showToast(changed ? `Updated ${changed}/${total} case IDs${planNote}` : `Case IDs are already sequential${planNote}`);
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
  state.generatedReport = null;
  els.reportNameInput.value = "";
  const nextRunId = runId || null;
  const nextRun = nextRunId ? await api(`/api/test-runs/${encodeURIComponent(nextRunId)}`) : null;
  state.currentRunId = nextRunId;
  state.currentRun = nextRun;
  persistCurrentRunId(state.currentRunId);
  if (state.currentRunId) state.testPlanExpanded = true;
  normalizeCurrentFilter();
  renderExecutionPanel();
  renderFilters();
  renderCaseRows();
}

async function createRun() {
  const mode = els.runModeSelect.value || "full";
  const sourceRunId = mode === "retest_unresolved" ? els.sourceRunSelect.value : "";
  const name = els.runNameInput.value.trim();
  if (!name) {
    syncCreateRunButtonState();
    showToast("Enter a test plan name before creating the plan");
    return;
  }
  if (mode === "retest_unresolved" && !sourceRunId) {
    showToast("Select a source test plan before creating a retest plan");
    return;
  }
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
    persistCurrentRunId(state.currentRunId);
    state.generatedReport = null;
    els.reportNameInput.value = "";
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
  const reportName = els.reportNameInput.value.trim();
  if (!reportName) {
    showToast("Enter a test report name");
    els.reportNameInput.focus();
    return;
  }
  try {
    const response = await api(`/api/test-runs/${encodeURIComponent(state.currentRunId)}`, {
      method: "PATCH",
      body: JSON.stringify({
        environment: els.runEnvironmentInput.value.trim() || defaults.environment,
        tester: els.runTesterInput.value.trim() || defaults.tester,
        report_name: reportName,
        language: state.language,
      }),
    });
    state.currentRun = response;
    state.generatedReport = response.report || null;
    state.runs = await api("/api/test-runs");
    renderExecutionPanel();
    renderCaseRows();
    showToast(state.generatedReport ? "Test report generated" : "Test plan completed");
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
  const actualResult = document.querySelector(`[data-exec-actual-result="${cssEscape(caseId)}"]`)?.value || "";
  const defects = document.querySelector(`[data-exec-defects="${cssEscape(caseId)}"]`)?.value || "";
  const response = await api(`/api/test-runs/${encodeURIComponent(state.currentRunId)}/results`, {
    method: "PATCH",
    body: JSON.stringify({
      file_path: state.currentData.path,
      case_id: caseId,
      notes,
      actual_result: actualResult,
      defects: arrayFromText(defects),
    }),
  });
  state.currentRun = response.run;
  state.runs = await api("/api/test-runs");
  renderExecutionPanel();
  renderCaseRows();
  showToast("Execution details saved");
}

async function uploadExecutionScreenshot(caseId) {
  if (!state.currentData || !caseId) return;
  if (!state.currentRunId) {
    showToast("Select or create a test plan first");
    return;
  }
  const input = document.querySelector(`[data-exec-screenshot="${cssEscape(caseId)}"]`);
  const file = input?.files?.[0];
  if (!file) {
    showToast("Choose a screenshot first");
    return;
  }
  const body = new FormData();
  body.append("file_path", state.currentData.path);
  body.append("case_id", caseId);
  body.append("screenshot", file);
  try {
    const response = await api(`/api/test-runs/${encodeURIComponent(state.currentRunId)}/results/screenshots`, {
      method: "POST",
      body,
    });
    state.currentRun = response.run;
    state.runs = await api("/api/test-runs");
    renderExecutionPanel();
    renderCaseRows();
    showToast("Screenshot uploaded");
  } catch (error) {
    showToast(error.message);
  } finally {
    if (input) input.value = "";
  }
}

async function deleteExecutionScreenshot(screenshotId) {
  if (!screenshotId || !state.currentRunId) return;
  const confirmed = window.confirm(t("Delete this screenshot?"));
  if (!confirmed) return;
  try {
    const response = await api(`/api/test-runs/${encodeURIComponent(state.currentRunId)}/screenshots/${encodeURIComponent(screenshotId)}`, {
      method: "DELETE",
    });
    state.currentRun = response.run;
    state.runs = await api("/api/test-runs");
    closeScreenshotViewer();
    renderExecutionPanel();
    renderCaseRows();
    showToast("Screenshot deleted");
  } catch (error) {
    showToast(error.message);
  }
}

function syncCreateRunButtonState() {
  const mode = els.runModeSelect.value || "full";
  const hasName = Boolean(els.runNameInput.value.trim());
  const hasSource = mode !== "retest_unresolved" || Boolean(els.sourceRunSelect.value);
  els.createRunButton.disabled = !hasName || !hasSource;
  if (!hasName) {
    els.createRunButton.title = t("Enter a test plan name");
  } else if (!hasSource) {
    els.createRunButton.title = t("Select a source test plan");
  } else {
    els.createRunButton.title = mode === "retest_unresolved"
      ? t("Create a new plan from the selected plan's failed, blocked, and deferred cases")
      : t("Create a full test plan for the current scope");
  }
}

function currentRunStorageKey() {
  const scope = (state.summary?.scan_dirs || [])
    .map((item) => String(item || "").trim().replace(/[\\/]+$/, ""))
    .filter(Boolean)
    .join("|") || "default";
  return `${CURRENT_RUN_STORAGE_PREFIX}:${scope}`;
}

function storedCurrentRunId() {
  try {
    return window.localStorage.getItem(currentRunStorageKey()) || null;
  } catch (_error) {
    return null;
  }
}

function persistCurrentRunId(runId) {
  try {
    const key = currentRunStorageKey();
    if (runId) {
      window.localStorage.setItem(key, runId);
    } else {
      window.localStorage.removeItem(key);
    }
  } catch (_error) {
    // Keep plan selection functional when browser storage is unavailable.
  }
}

function toggleTestPlanPanel() {
  if (state.testPlanExpanded) {
    closeTestPlanDrawer();
    return;
  }
  openTestPlanDrawer();
}

function openTestPlanDrawer() {
  if (els.editorDrawer.classList.contains("open")) closeDrawer();
  state.testPlanExpanded = true;
  renderExecutionPanel();
  syncDrawerScrim();
}

function closeTestPlanDrawer() {
  state.testPlanExpanded = false;
  els.testPlanDrawer.classList.remove("open");
  els.testPlanDrawer.setAttribute("aria-hidden", "true");
  els.executionToggle.setAttribute("aria-expanded", "false");
  syncDrawerScrim();
}

function closeActiveDrawer() {
  if (state.testPlanExpanded) {
    closeTestPlanDrawer();
    return;
  }
  if (els.editorDrawer.classList.contains("open")) closeDrawer();
}

function syncDrawerScrim() {
  const anyDrawerOpen = state.testPlanExpanded || els.editorDrawer.classList.contains("open");
  els.drawerScrim.hidden = !anyDrawerOpen;
}

function scopeLabel() {
  return (state.summary?.scan_dirs || []).join(", ") || t("No scope");
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

async function copyCaseId(caseId) {
  if (!caseId) return;
  try {
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(caseId);
    } else {
      fallbackCopyText(caseId);
    }
    showToast(`Copied ${caseId}`);
  } catch (error) {
    try {
      fallbackCopyText(caseId);
      showToast(`Copied ${caseId}`);
    } catch (fallbackError) {
      showToast(`Unable to copy ${caseId}`);
    }
  }
}

function fallbackCopyText(text) {
  const textarea = document.createElement("textarea");
  textarea.value = text;
  textarea.style.position = "fixed";
  textarea.style.opacity = "0";
  document.body.appendChild(textarea);
  textarea.select();
  const copied = document.execCommand("copy");
  textarea.remove();
  if (!copied) throw new Error("Copy command was rejected");
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

function screenshotUrl(screenshot) {
  if (!state.currentRunId || !screenshot?.id) return "";
  return `/api/test-runs/${encodeURIComponent(state.currentRunId)}/screenshots/${encodeURIComponent(screenshot.id)}`;
}

function openScreenshotViewer(src, title) {
  if (!src) return;
  els.screenshotViewerImage.src = src;
  els.screenshotViewerTitle.textContent = title || t("Screenshot");
  els.screenshotViewer.hidden = false;
}

function closeScreenshotViewer() {
  els.screenshotViewer.hidden = true;
  els.screenshotViewerImage.removeAttribute("src");
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
  if (title === "Preconditions" || title === t("Preconditions")) {
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
  els.toast.textContent = localizeRuntimeMessage(message);
  els.toast.hidden = false;
  clearTimeout(showToast.timer);
  showToast.timer = setTimeout(() => {
    els.toast.hidden = true;
  }, 2600);
}

function localizeRuntimeMessage(message) {
  const source = String(message || "");
  const translated = t(source);
  if (state.language !== "zh-CN" || translated !== source) return translated;
  const patterns = [
    [/^Copied (.+)$/, "已复制 $1"],
    [/^Unable to copy (.+)$/, "无法复制 $1"],
    [/^Cannot complete test plan: (\d+) untested cases remain$/, "无法完成测试计划：还有 $1 条用例未测试"],
    [/^Updated (\d+)\/(\d+) case IDs/, "已更新 $1/$2 个用例 ID"],
    [/^Case IDs are already sequential/, "用例 ID 已连续，无需更新"],
    [/^Test plan name is required\.$/, "必须填写测试计划名称。"],
    [/^Unable to generate report: (.+)$/, "无法生成报告：$1"],
    [/^Case not found: (.+)$/, "未找到用例：$1"],
    [/^Test run not found: (.+)$/, "未找到测试计划：$1"],
  ];
  for (const [pattern, replacement] of patterns) {
    if (pattern.test(source)) return source.replace(pattern, replacement);
  }
  return source;
}
