from __future__ import annotations

import json
import tempfile
import textwrap
import unittest
from pathlib import Path

from casebook.app import create_app
from casebook.editor import CaseEditor, EditConflictError
from casebook.exporter import generate_export
from casebook.initializer import init_project
from casebook.marks import MarksStore
from casebook.renumber import CaseIdRenumberer
from casebook.report import generate_report
from casebook.runs import InvalidRunError, TestRunStore
from casebook.scanner import CasebookStore


def write_cases(project_root: Path, relative_path: str = "releases/login.yaml") -> Path:
    """Write a small Casebook YAML fixture and return its path."""
    target = project_root / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        textwrap.dedent(
            """
            metadata:
              module: "Auth"
              feature: "Login"
              owner: "qa.owner"
              last_reviewed: "2026-07-04"
              tags: [auth, smoke]

            test_cases:
              - id: "TC_LOGIN_001"
                title: "Successful login"
                description: "User can log in with valid credentials."
                priority: "P0"
                type: "functional"
                preconditions:
                  - User exists
                steps:
                  - Enter username and password
                  - Submit the form
                expected_results:
                  - User lands on the dashboard
                tags: [login, smoke]
                auto: true

              - id: "TC_LOGIN_004"
                title: "Wrong password is rejected"
                priority: "P1"
                type: "functional"
                steps:
                  - Enter valid username
                  - Enter wrong password
                  - Submit the form
                expected_results:
                  - Login is rejected
                tags: [login, negative]

              - id: "TC_LOGIN_002"
                title: "Locked user is blocked"
                priority: "P2"
                type: "business"
                steps:
                  - Enter locked user credentials
                  - Submit the form
                expected_results:
                  - Login is blocked
                tags: [login, blocked]
            """
        ).strip()
        + "\n",
        encoding="utf-8",
    )
    return target


class CasebookCoreTests(unittest.TestCase):

    def test_init_project_creates_scaffold_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir) / "my-casebook"
            result = init_project(project_root)

            self.assertEqual(result.project_root, project_root.resolve())
            self.assertTrue((project_root / "docs" / "requirements" / "login.md").exists())
            self.assertTrue((project_root / "releases" / "example" / "login.yaml").exists())
            self.assertTrue((project_root / "schema" / "test-case-schema.json").exists())
            self.assertIn(Path("docs/requirements/login.md"), result.created)
            self.assertIn(Path("releases/example/login.yaml"), result.created)

    def test_scanner_normalizes_backslash_scan_dirs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            write_cases(project_root)

            store = CasebookStore(project_root, scan_dirs=[r"releases\\"])
            summary = store.refresh()

            self.assertEqual(summary["files"], 1)
            self.assertEqual(summary["cases"], 3)

    def test_scanner_builds_summary_tree_and_file_payload(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            write_cases(project_root)

            store = CasebookStore(project_root, scan_dirs=["releases"])
            summary = store.refresh()
            file_payload = store.get_file("releases/login.yaml")
            tree = store.tree()

            self.assertEqual(summary["files"], 1)
            self.assertEqual(summary["cases"], 3)
            self.assertEqual(summary["owners"], ["qa.owner"])
            self.assertIsNotNone(file_payload)
            self.assertEqual(file_payload["stats"]["priorities"]["P0"], 1)
            self.assertEqual(tree[0]["name"], "releases")
            self.assertEqual(tree[0]["count"], 3)
            self.assertEqual(tree[0]["children"][0]["name"], "login.yaml")

    def test_editor_updates_case_and_detects_conflicts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            yaml_file = write_cases(project_root)
            editor = CaseEditor(project_root)
            mtime_ns = yaml_file.stat().st_mtime_ns

            result = editor.update_case(
                "releases/login.yaml",
                "TC_LOGIN_001",
                {
                    "description": "Line one\nLine two",
                    "priority": "P1",
                    "tags": "login\nreviewed",
                },
                mtime_ns=mtime_ns,
            )

            text = yaml_file.read_text(encoding="utf-8")
            self.assertEqual(result["case"]["priority"], "P1")
            self.assertEqual(result["case"]["tags"], ["login", "reviewed"])
            self.assertIn("|-", text)
            self.assertLess(text.index("tags:"), text.index("auto:"))
            with self.assertRaises(EditConflictError):
                editor.update_case(
                    "releases/login.yaml",
                    "TC_LOGIN_001",
                    {"priority": "P2"},
                    mtime_ns=mtime_ns,
                )

    def test_marks_can_toggle_update_and_remap_case_ids(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = MarksStore(Path(temp_dir))

            result = store.update_mark(
                "releases/login.yaml",
                "TC_LOGIN_004",
                needs_update=True,
                notes="Add boundary case",
            )
            self.assertTrue(result["marked"])

            toggled = store.toggle_needs_update("releases/login.yaml", "TC_LOGIN_004")
            self.assertFalse(toggled["marked"])
            self.assertEqual(toggled["mark"]["notes"], "Add boundary case")

            remapped = store.remap_case_ids(
                "releases/login.yaml",
                [{"old_id": "TC_LOGIN_004", "new_id": "TC_LOGIN_002"}],
            )
            self.assertIn("releases/login.yaml#TC_LOGIN_002", remapped)
            self.assertNotIn("releases/login.yaml#TC_LOGIN_004", remapped)

    def test_renumber_uses_first_case_prefix_start_and_width(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            yaml_file = write_cases(project_root)
            text = yaml_file.read_text(encoding="utf-8")
            yaml_file.write_text(
                text.replace("TC_LOGIN_001", "TC_LOGIN_018", 1),
                encoding="utf-8",
            )

            result = CaseIdRenumberer(project_root).renumber_file("releases/login.yaml")
            rewritten = yaml_file.read_text(encoding="utf-8")

            self.assertEqual(result["total"], 3)
            self.assertEqual(result["changed"], 2)
            self.assertIn('id: "TC_LOGIN_018"', rewritten)
            self.assertIn('id: "TC_LOGIN_019"', rewritten)
            self.assertIn('id: "TC_LOGIN_020"', rewritten)

    def test_run_store_requires_scoped_cases_before_completion(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = TestRunStore(Path(temp_dir))
            case_keys = [
                "releases/login.yaml#TC_LOGIN_001",
                "releases/login.yaml#TC_LOGIN_002",
            ]
            run = store.create_run(name="Round 1", scope=["releases"], case_scope=case_keys)
            run_id = run["run"]["id"]

            store.update_result(run_id, "releases/login.yaml", "TC_LOGIN_001", status="passed")
            with self.assertRaises(InvalidRunError):
                store.complete_run(run_id, required_case_keys=case_keys)

            with self.assertRaises(InvalidRunError):
                store.update_result(run_id, "releases/login.yaml", "TC_LOGIN_999", status="passed")

            store.update_result(
                run_id,
                "releases/login.yaml",
                "TC_LOGIN_002",
                status="deferred",
                defects="BUG-1\nhttps://jira.example/browse/BUG-2",
            )
            completed = store.complete_run(run_id, required_case_keys=case_keys)
            self.assertEqual(completed["run"]["status"], "completed")
            self.assertEqual(completed["run"]["case_scope"], case_keys)
            self.assertEqual(
                store.list_runs(scope=["releases"])[0]["result_counts"]["deferred"],
                1,
            )

    def test_app_retest_plan_uses_failed_blocked_and_deferred_cases(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            write_cases(project_root)
            app = create_app(project_root, scan_dirs=["releases"], watch=False)
            client = app.test_client()

            first = client.post(
                "/api/test-runs",
                json={"name": "Round 1", "mode": "full"},
            )
            self.assertEqual(first.status_code, 201)
            first_run_id = first.get_json()["run"]["id"]

            client.patch(
                f"/api/test-runs/{first_run_id}/results",
                json={
                    "file_path": "releases/login.yaml",
                    "case_id": "TC_LOGIN_001",
                    "status": "passed",
                },
            )
            client.patch(
                f"/api/test-runs/{first_run_id}/results",
                json={
                    "file_path": "releases/login.yaml",
                    "case_id": "TC_LOGIN_004",
                    "status": "failed",
                },
            )
            incomplete = client.patch(f"/api/test-runs/{first_run_id}", json={})
            self.assertEqual(incomplete.status_code, 400)

            client.patch(
                f"/api/test-runs/{first_run_id}/results",
                json={
                    "file_path": "releases/login.yaml",
                    "case_id": "TC_LOGIN_002",
                    "status": "deferred",
                },
            )
            completed = client.patch(f"/api/test-runs/{first_run_id}", json={})
            self.assertEqual(completed.status_code, 200)

            retest = client.post(
                "/api/test-runs",
                json={
                    "name": "Round 2",
                    "mode": "retest_unresolved",
                    "source_run_id": first_run_id,
                },
            )
            self.assertEqual(retest.status_code, 201)
            case_scope = retest.get_json()["run"]["case_scope"]
            self.assertEqual(
                case_scope,
                [
                    "releases/login.yaml#TC_LOGIN_004",
                    "releases/login.yaml#TC_LOGIN_002",
                ],
            )

    def test_export_and_report_generate_html_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            write_cases(project_root)

            export_path = generate_export(
                project_root / "releases",
                output_file=project_root / "review.html",
                priorities=["P0"],
                tags=["smoke"],
                project_root=project_root,
            )
            export_html = export_path.read_text(encoding="utf-8")
            self.assertIn("Casebook Export", export_html)
            self.assertIn("TC_LOGIN_001", export_html)
            self.assertNotIn("TC_LOGIN_004", export_html)

            run_file = project_root / "test-runs" / "run-report.json"
            run_file.parent.mkdir(parents=True, exist_ok=True)
            run_file.write_text(
                json.dumps(
                    {
                        "run": {
                            "id": "run-report",
                            "name": "Report Run",
                            "status": "completed",
                            "mode": "full",
                            "scope": ["releases"],
                            "case_scope": [
                                "releases/login.yaml#TC_LOGIN_001",
                                "releases/login.yaml#TC_LOGIN_004",
                            ],
                            "started_at": "2026-07-04T00:00:00+00:00",
                            "completed_at": "2026-07-04T01:00:00+00:00",
                        },
                        "results": {
                            "releases/login.yaml#TC_LOGIN_001": {"status": "passed"},
                            "releases/login.yaml#TC_LOGIN_004": {
                                "status": "failed",
                                "notes": "Wrong message",
                                "defects": ["https://jira.example/browse/BUG-1"],
                            },
                        },
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            report_path = generate_report(
                run_file,
                output_file=project_root / "report.html",
                project_root=project_root,
            )
            report_html = report_path.read_text(encoding="utf-8")
            self.assertIn("Casebook Test Report", report_html)
            self.assertIn("Failed Cases", report_html)
            self.assertIn("Wrong password is rejected", report_html)
            self.assertNotIn("Locked user is blocked", report_html)


if __name__ == "__main__":
    unittest.main()
