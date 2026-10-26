from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path

from ruamel.yaml import YAML

from casebook.exporter import generate_export
from casebook.report import generate_report


class ParsedPage(HTMLParser):
    """Collect rendered text and inline scripts without rewriting HTML content."""

    def __init__(self, html: str) -> None:
        super().__init__(convert_charrefs=True)
        self.text: list[str] = []
        self.scripts: list[str] = []
        self._script: list[str] | None = None
        self.feed(html)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "script":
            self._script = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self._script is not None:
            self.scripts.append("".join(self._script))
            self._script = None

    def handle_data(self, data: str) -> None:
        if self._script is not None:
            self._script.append(data)
        else:
            self.text.append(data)


class LocalizationTests(unittest.TestCase):
    def test_export_preserves_case_payload_and_translates_controls(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "releases" / "Search cases.yaml"
            source.parent.mkdir()
            case = {
                "id": "TC_I18N_001",
                "title": "Search cases",
                "description": "TEST CASE REVIEW",
                "priority": "P0",
                "type": "functional",
                "auto": True,
                "tags": ["All tags", "Review controls"],
                "preconditions": ['Notes <tag> & "quoted"'],
                "steps": ['detailList("Steps")', "Verify TEST CASE REVIEW"],
                "expected_results": ["Search cases", "${count} cases"],
            }
            data = {
                "metadata": {
                    "module": "Portable review workspace",
                    "feature": "Review controls",
                    "owner": "Generated: Owner",
                },
                "test_cases": [case],
            }
            with source.open("w", encoding="utf-8") as stream:
                YAML().dump(data, stream)

            pages: dict[str, ParsedPage] = {}
            payloads = {}
            for language in ("en", "zh-CN"):
                output = generate_export(
                    source,
                    output_file=root / f"review-{language}.html",
                    project_root=root,
                    language=language,
                )
                pages[language] = ParsedPage(output.read_text(encoding="utf-8"))
                script = pages[language].scripts[-1]
                payloads[language], _ = json.JSONDecoder().raw_decode(
                    script.partition("const exportData = ")[2]
                )

            self.assertIn("测试用例评审", pages["zh-CN"].text)
            for key in ("files", "title", "source_label", "export_id", "filters"):
                self.assertEqual(payloads["en"][key], payloads["zh-CN"][key])
            exported_case = payloads["zh-CN"]["files"][0]["cases"][0]
            for key, value in case.items():
                self.assertEqual(exported_case[key], value)

            if node := shutil.which("node"):
                # Execute the generated script in a small DOM harness, without a browser.
                runner = r"""
const fs = require('node:fs');
const vm = require('node:vm');
const nodes = {};
const context = vm.createContext({
  document: { getElementById(id) {
    return nodes[id] ||= { innerHTML: '', textContent: '', addEventListener() {} };
  } },
  window: { localStorage: { getItem() { return null; } } },
});
vm.runInContext(fs.readFileSync(0, 'utf8'), context);
vm.runInContext("state.open.add(allCases()[0].key); render();", context);
process.stdout.write(JSON.stringify({ content: nodes.content.innerHTML, stats: nodes.stats.innerHTML }));
"""
                for language, page in pages.items():
                    with self.subTest(language=language):
                        result = subprocess.run(
                            [node, "-e", runner], input=page.scripts[-1],
                            text=True, capture_output=True, check=True,
                        )
                        rendered = json.loads(result.stdout)
                        self.assertIn("Search cases", ParsedPage(rendered["content"]).text)
                        self.assertIn("TEST CASE REVIEW", ParsedPage(rendered["content"]).text)
                        labels = ParsedPage(rendered["stats"]).text
                        self.assertIn("备注" if language == "zh-CN" else "Notes", labels)
                        self.assertIn("前置条件" if language == "zh-CN" else "Preconditions",
                                      ParsedPage(rendered["content"]).text)

    def test_report_preserves_metadata_and_execution_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run_file = root / "test-runs" / "run-i18n.json"
            run_file.parent.mkdir()
            key = "releases/Scope.yaml#TC_I18N_001"
            run = {
                "id": "run-i18n", "name": "Title", "status": "completed",
                "mode": "full", "scope": ["releases"], "case_scope": [key],
                "environment": "Environment", "tester": "Tester",
            }
            run_data = {
                "schema_version": "2.0",
                "run": run,
                "cases": {key: {
                    "id": "TC_I18N_001", "title": "Title", "priority": "P0",
                    "type": "Test case", "file_path": "releases/Scope.yaml",
                }},
                "results": {key: {
                    "status": "failed", "actual_result": "Notes",
                    "notes": 'Generated: <original> & "quoted"',
                    "defects": ["Defects", "https://jira.example/browse/Notes"],
                    "screenshots": [{"id": "shot", "name": "Screenshots"}],
                }},
            }
            run_file.write_text(json.dumps(run_data), encoding="utf-8")

            for language in ("en", "zh-CN"):
                with self.subTest(language=language):
                    output = generate_report(run_file, project_root=root, language=language)
                    page = ParsedPage(output.read_text(encoding="utf-8"))
                    for value in ("Title", "Environment", "Tester", "Test case", "Notes",
                                  'Generated: <original> & "quoted"', "Defects", "Screenshots",
                                  "https://jira.example/browse/Notes", "releases/Scope.yaml"):
                        self.assertIn(value, page.text)
                    self.assertIn("测试执行简报" if language == "zh-CN" else "Test Execution Brief", page.text)
                    chart_data, _ = json.JSONDecoder().raw_decode(
                        page.scripts[-1].partition("const reportData = ")[2]
                    )
                    self.assertEqual(chart_data["execution"][0]["label"],
                                     "通过" if language == "zh-CN" else "Passed")
                    if node := shutil.which("node"):
                        subprocess.run([node, "--check"], input=page.scripts[-1],
                                       text=True, capture_output=True, check=True)


if __name__ == "__main__":
    unittest.main()
