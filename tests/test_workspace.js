const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");

const source = fs.readFileSync(path.join(__dirname, "../casebook/static/app.js"), "utf8");

function workspace(mode) {
  const context = vm.createContext({
    document: { addEventListener() {} },
    window: { localStorage: { getItem() { return null; }, setItem() {} } },
  });
  const run = (code) => vm.runInContext(code, context);
  run(source);

  const fields = mode === "execution" ? ["actual", "notes", "defects", "screenshot"] : ["mark", "notes"];
  const rows = {
    children: [],
    set innerHTML(html) {
      this.html = html;
      // Rendering creates fresh controls, just as assigning innerHTML does in a browser.
      const row = { dataset: { caseId: "TC_LOGIN_001" }, inputs: [] };
      row.inputs = fields.map((name, index) => ({
        name, value: "saved value", checked: false, files: [], placeholder: "new placeholder",
        replaceWith(input) { row.inputs[index] = input; },
      }));
      row.querySelectorAll = () => row.inputs;
      this.children = [row];
    },
  };
  context.rows = rows;
  run(`
    els.caseRows = rows;
    els.noResults = {};
    els.toggleAllCasesButton = { setAttribute() {}, classList: { toggle() {} } };
    els.runEnvironmentInput = { value: "Custom environment" };
    els.runTesterInput = { value: "Custom tester" };
    els.reportNameInput = { value: "Custom report" };
    els.casePlanSelect = {
      value: "active-plan",
      set innerHTML(_html) { this.value = ""; }
    };
    els.addCaseToPlanButton = {};
    els.casePlanMembership = {};
    state.runs = [{ id: "active-plan", name: "Plan", status: "in_progress", case_scope: [] }];
    state.currentData = {
      path: "releases/login.yaml",
      cases: [{ id: "TC_LOGIN_001", title: "Saved title", priority: "P0", type: "functional" }]
    };
    state.expandedCaseIds.add("TC_LOGIN_001");
    applyStaticTranslations = () => {};
    renderFileMeta = () => {};
    renderFilters = () => {};
    renderExecutionPanel = () => {
      els.runEnvironmentInput.value = "Saved environment";
      els.runTesterInput.value = "Saved tester";
      if (!els.reportNameInput.value) els.reportNameInput.value = "Default report";
    };
  `);
  if (mode === "execution") {
    run(`
      state.currentRun = {
        run: { case_scope: ["releases/login.yaml#TC_LOGIN_001"] },
        results: { "releases/login.yaml#TC_LOGIN_001": { status: "failed" } }
      };
    `);
  }
  run("renderCaseRows()");
  return { run, rows };
}

test("language switching preserves unsaved execution evidence and selected files", () => {
  const { run, rows } = workspace("execution");
  const inputs = [...rows.children[0].inputs];
  inputs[0].value = 'Actual <result> & "quotes"';
  inputs[1].value = ""; // Clearing a saved value is also a draft.
  inputs[2].value = "https://jira.example/browse/BUG-1\nBUG-2";
  const files = [{ name: "evidence.png" }];
  inputs[3].files = files;

  for (const language of ["zh-CN", "en"]) {
    run(`setLanguage(${JSON.stringify(language)})`);
    const current = rows.children[0].inputs;
    inputs.forEach((input, index) => assert.strictEqual(current[index], input));
    assert.equal(current[0].value, 'Actual <result> & "quotes"');
    assert.equal(current[1].value, "");
    assert.equal(current[2].value, "https://jira.example/browse/BUG-1\nBUG-2");
    assert.strictEqual(current[3].files, files);
    assert.ok(rows.html.includes(language === "zh-CN" ? "实际结果" : "Actual Result"));
  }
});

test("language switching preserves review notes and mark checkbox", () => {
  const { run, rows } = workspace("review");
  const [mark, notes] = rows.children[0].inputs;
  mark.checked = true;
  notes.value = "Review draft\nSecond line";
  run("setLanguage('zh-CN'); setLanguage('en')");
  assert.strictEqual(rows.children[0].inputs[0], mark);
  assert.equal(mark.checked, true);
  assert.strictEqual(rows.children[0].inputs[1], notes);
  assert.equal(notes.value, "Review draft\nSecond line");
});

test("language switching keeps editor drafts dirty and preserves plan selection", () => {
  const { run } = workspace("review");
  run(`
    ["fieldTitle", "fieldDescription", "fieldPriority", "fieldType", "fieldTags",
     "fieldPreconditions", "fieldSteps", "fieldExpectedResults"].forEach((id) => {
      els[id] = { value: "Unsaved " + id };
    });
    els.drawerTitle = {};
    els.fieldId = {};
    els.fieldAuto = { checked: true };
    state.selectedCaseId = "TC_LOGIN_001";
    state.dirty = true;
    setLanguage("zh-CN");
  `);
  assert.equal(run("els.fieldTitle.value"), "Unsaved fieldTitle");
  assert.equal(run("els.fieldAuto.checked"), true);
  assert.equal(run("state.dirty"), true);
  assert.equal(run("els.casePlanSelect.value"), "active-plan");
});

test("language switching preserves completion form drafts, including empty report names", () => {
  const { run } = workspace("execution");
  run("els.reportNameInput.value = ''; setLanguage('zh-CN')");
  assert.equal(run("els.runEnvironmentInput.value"), "Custom environment");
  assert.equal(run("els.runTesterInput.value"), "Custom tester");
  assert.equal(run("els.reportNameInput.value"), "");
});
