from __future__ import annotations

import json
import queue
import atexit
from pathlib import Path
from typing import Any

from flask import Flask, Response, jsonify, render_template, request, send_from_directory, stream_with_context

from . import __version__
from .editor import CaseEditor, CaseNotFoundError, EditConflictError
from .marks import MarksStore
from .renumber import CaseIdRenumberError, CaseIdRenumberer
from .runs import InvalidRunError, RunNotFoundError, TestRunStore
from .scanner import CasebookStore
from .watcher import CasebookWatcher


class EventBroker:
    def __init__(self):
        self._subscribers: list[queue.Queue[dict[str, Any]]] = []

    def subscribe(self) -> queue.Queue[dict[str, Any]]:
        subscriber: queue.Queue[dict[str, Any]] = queue.Queue()
        self._subscribers.append(subscriber)
        return subscriber

    def unsubscribe(self, subscriber: queue.Queue[dict[str, Any]]) -> None:
        try:
            self._subscribers.remove(subscriber)
        except ValueError:
            pass

    def publish(self, event: dict[str, Any]) -> None:
        for subscriber in list(self._subscribers):
            subscriber.put(event)


def create_app(
    project_root: Path,
    scan_dirs: list[str] | None = None,
    watch: bool = True,
) -> Flask:
    app = Flask(__name__)
    store = CasebookStore(project_root=project_root, scan_dirs=scan_dirs)
    editor = CaseEditor(project_root=project_root)
    renumberer = CaseIdRenumberer(project_root=project_root)
    marks = MarksStore(project_root=project_root)
    runs = TestRunStore(project_root=project_root)
    broker = EventBroker()

    initial_summary = store.refresh()
    app.config["CASEBOOK_INITIAL_SUMMARY"] = initial_summary

    def current_case_keys() -> list[str]:
        keys: list[str] = []
        for file_item in store.list_files():
            file_path = str(file_item.get("path") or "")
            if not file_path:
                continue
            entry = store.get_file(file_path)
            if not entry:
                continue
            for case in entry.get("cases") or []:
                case_id = str(case.get("id") or "")
                if case_id:
                    keys.append(runs.key(file_path, case_id))
        return keys

    def case_keys_for_run(run_id: str) -> list[str]:
        data = runs.get_run(run_id, scope=store.scan_dirs)
        run = data.get("run") or {}
        if isinstance(run, dict):
            case_scope = run.get("case_scope")
            if isinstance(case_scope, list):
                return [str(item or "") for item in case_scope if str(item or "").strip()]
        return current_case_keys()

    def unresolved_case_keys(source_run_id: str) -> list[str]:
        source = runs.get_run(source_run_id, scope=store.scan_dirs)
        source_run = source.get("run") or {}
        if not isinstance(source_run, dict) or source_run.get("status") != "completed":
            raise InvalidRunError(
                "Complete the source test plan before creating a retest plan."
            )
        results = source.get("results") or {}
        if not isinstance(results, dict):
            results = {}
        unresolved_statuses = {"failed", "blocked", "deferred"}
        keys = []
        for key in current_case_keys():
            result = results.get(key)
            status = ""
            if isinstance(result, dict):
                status = str(result.get("status") or "").strip().lower()
            if status in unresolved_statuses:
                keys.append(key)
        if not keys:
            raise InvalidRunError(
                "No failed, blocked, or deferred cases found in the source test plan."
            )
        return keys

    def refresh_and_publish(reason: str) -> dict[str, Any]:
        summary = store.refresh()
        broker.publish(
            {"type": "reload", "reason": reason, "summary": summary})
        return summary

    watcher: CasebookWatcher | None = None
    if watch:
        watcher = CasebookWatcher(
            project_root=store.project_root,
            scan_dirs=store.scan_dirs,
            on_change=lambda: refresh_and_publish("filesystem"),
        )
        watcher.start()
        app.config["CASEBOOK_WATCHER"] = watcher
        atexit.register(watcher.stop)

    @app.after_request
    def add_no_cache_headers(response):
        if request.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store"
        return response

    @app.route("/")
    def index():
        return render_template("index.html", casebook_version=__version__)

    @app.get("/favicon.ico")
    def favicon():
        return send_from_directory(app.static_folder, "favicon.svg", mimetype="image/svg+xml")

    @app.get("/api/summary")
    def api_summary():
        return jsonify(store.summary())

    @app.get("/api/tree")
    def api_tree():
        return jsonify(store.tree())

    @app.get("/api/files")
    def api_files():
        return jsonify(store.list_files())

    @app.get("/api/files/<path:file_path>")
    def api_file(file_path: str):
        entry = store.get_file(file_path)
        if not entry:
            return jsonify({"error": f"File not found: {file_path}"}), 404
        all_marks = marks.all()
        file_marks = {}
        for case in entry["cases"]:
            key = f"{file_path}#{case['id']}"
            mark = all_marks.get(key)
            if mark:
                file_marks[key] = mark
        entry["marks"] = file_marks
        entry["needs_update_count"] = sum(
            1
            for mark in file_marks.values()
            if isinstance(mark, dict) and mark.get("needs_update")
        )
        return jsonify(entry)

    @app.post("/api/files/<path:file_path>/renumber")
    def api_renumber_file(file_path: str):
        payload = request.get_json(silent=True) or {}
        current_run_id = payload.get(
            "current_run_id") or payload.get("currentRunId")
        if current_run_id:
            return jsonify({"error": "Case IDs cannot be updated while a test plan is selected"}), 409
        try:
            result = renumberer.renumber_file(
                file_path, mtime_ns=payload.get("mtime_ns"))
        except FileNotFoundError:
            return jsonify({"error": f"File not found: {file_path}"}), 404
        except CaseIdRenumberError as exc:
            code = "edit_conflict" if "changed after it was loaded" in str(
                exc) else "renumber_failed"
            status = 409 if code == "edit_conflict" else 400
            return jsonify({"error": str(exc), "code": code}), status
        updated_marks = marks.remap_case_ids(file_path, result["mapping"])
        summary = refresh_and_publish("renumber")
        broker.publish({
            "type": "marks",
            "file_path": file_path,
        })
        return jsonify({
            "status": "ok",
            "result": result,
            "marks": updated_marks,
            "summary": summary,
        })

    @app.get("/api/marks")
    def api_marks():
        return jsonify(marks.all())

    @app.post("/api/marks/toggle")
    def api_toggle_mark():
        payload = request.get_json(silent=True) or {}
        file_path = str(payload.get("file_path")
                        or payload.get("filePath") or "")
        case_id = str(payload.get("case_id") or payload.get("caseId") or "")
        if not file_path or not case_id:
            return jsonify({"error": "Missing file_path or case_id"}), 400
        result = marks.toggle_needs_update(file_path, case_id)
        broker.publish({
            "type": "marks",
            "file_path": file_path,
            "case_id": case_id,
            "marked": result["marked"],
        })
        return jsonify(result)

    @app.patch("/api/marks")
    def api_update_mark():
        payload = request.get_json(silent=True) or {}
        file_path = str(payload.get("file_path")
                        or payload.get("filePath") or "")
        case_id = str(payload.get("case_id") or payload.get("caseId") or "")
        if not file_path or not case_id:
            return jsonify({"error": "Missing file_path or case_id"}), 400
        needs_update = (
            payload.get("needs_update")
            if "needs_update" in payload
            else payload.get("needsUpdate")
        )
        notes = payload.get("notes") if "notes" in payload else None
        if needs_update is None and notes is None:
            return jsonify({"error": "Missing needs_update or notes"}), 400
        result = marks.update_mark(
            file_path=file_path,
            case_id=case_id,
            needs_update=needs_update if needs_update is None else bool(needs_update),
            notes=notes,
        )
        broker.publish({
            "type": "marks",
            "file_path": file_path,
            "case_id": case_id,
            "marked": result["marked"],
        })
        return jsonify(result)

    @app.get("/api/test-runs")
    def api_test_runs():
        return jsonify(runs.list_runs(scope=store.scan_dirs))

    @app.post("/api/test-runs")
    def api_create_test_run():
        payload = request.get_json(silent=True) or {}
        mode = str(payload.get("mode") or "full").strip().lower()
        if mode == "retest":
            mode = "retest_unresolved"
        source_run_id = str(payload.get("source_run_id")
                            or payload.get("sourceRunId") or "").strip()
        try:
            if mode == "retest_unresolved":
                if not source_run_id:
                    raise InvalidRunError(
                        "Select a source test plan before creating a retest plan."
                    )
                case_scope = unresolved_case_keys(source_run_id)
            elif mode == "full":
                case_scope = current_case_keys()
                source_run_id = ""
            else:
                raise InvalidRunError(f"Invalid test plan mode: {mode}")
            result = runs.create_run(
                name=payload.get("name"),
                scope=store.scan_dirs,
                environment=payload.get("environment"),
                tester=payload.get("tester"),
                mode=mode,
                source_run_id=source_run_id or None,
                case_scope=case_scope,
            )
        except RunNotFoundError:
            return jsonify({"error": f"Test run not found: {source_run_id}"}), 404
        except InvalidRunError as exc:
            return jsonify({"error": str(exc)}), 400
        broker.publish({
            "type": "test_run",
            "action": "created",
            "run_id": result["run"]["id"],
        })
        return jsonify(result), 201

    @app.get("/api/test-runs/<run_id>")
    def api_test_run(run_id: str):
        try:
            return jsonify(runs.get_run(run_id, scope=store.scan_dirs))
        except RunNotFoundError:
            return jsonify({"error": f"Test run not found: {run_id}"}), 404

    @app.patch("/api/test-runs/<run_id>")
    def api_complete_test_run(run_id: str):
        payload = request.get_json(silent=True) or {}
        try:
            result = runs.complete_run(
                run_id=run_id,
                environment=payload.get("environment"),
                tester=payload.get("tester"),
                scope=store.scan_dirs,
                required_case_keys=case_keys_for_run(run_id),
            )
        except RunNotFoundError:
            return jsonify({"error": f"Test run not found: {run_id}"}), 404
        except InvalidRunError as exc:
            return jsonify({"error": str(exc)}), 400
        broker.publish({
            "type": "test_run",
            "action": "completed",
            "run_id": run_id,
        })
        return jsonify(result)

    @app.patch("/api/test-runs/<run_id>/results")
    def api_update_test_result(run_id: str):
        payload = request.get_json(silent=True) or {}
        file_path = str(payload.get("file_path")
                        or payload.get("filePath") or "")
        case_id = str(payload.get("case_id") or payload.get("caseId") or "")
        if not file_path or not case_id:
            return jsonify({"error": "Missing file_path or case_id"}), 400
        try:
            result = runs.update_result(
                run_id=run_id,
                file_path=file_path,
                case_id=case_id,
                status=payload.get("status"),
                notes=payload.get("notes") if "notes" in payload else None,
                defects=payload.get(
                    "defects") if "defects" in payload else None,
                tester=payload.get("tester") if "tester" in payload else None,
                scope=store.scan_dirs,
            )
        except RunNotFoundError:
            return jsonify({"error": f"Test run not found: {run_id}"}), 404
        except InvalidRunError as exc:
            return jsonify({"error": str(exc)}), 400
        broker.publish({
            "type": "test_run",
            "action": "result_updated",
            "run_id": run_id,
            "file_path": file_path,
            "case_id": case_id,
        })
        return jsonify(result)

    @app.patch("/api/cases")
    def api_update_case():
        payload = request.get_json(silent=True) or {}
        file_path = str(payload.get("file_path") or "")
        case_id = str(payload.get("case_id") or "")
        updates = payload.get("updates") or {}
        mtime_ns = payload.get("mtime_ns")
        if not file_path or not case_id or not isinstance(updates, dict):
            return jsonify({"error": "Missing file_path, case_id, or updates"}), 400
        try:
            result = editor.update_case(
                file_path, case_id, updates, mtime_ns=mtime_ns)
        except EditConflictError as exc:
            return jsonify({"error": str(exc), "code": "edit_conflict"}), 409
        except CaseNotFoundError:
            return jsonify({"error": f"Case not found: {case_id}"}), 404
        except FileNotFoundError:
            return jsonify({"error": f"File not found: {file_path}"}), 404
        summary = refresh_and_publish("edit")
        return jsonify({"status": "ok", "result": result, "summary": summary})

    @app.route("/api/refresh", methods=["GET", "POST"])
    def api_refresh():
        return jsonify(refresh_and_publish("manual"))

    @app.get("/api/events")
    def api_events():
        subscriber = broker.subscribe()

        def stream():
            try:
                yield "event: hello\ndata: {}\n\n"
                while True:
                    try:
                        event = subscriber.get(timeout=15)
                        data = json.dumps(event, ensure_ascii=False)
                        yield f"event: {event.get('type', 'message')}\ndata: {data}\n\n"
                    except queue.Empty:
                        yield "event: ping\ndata: {}\n\n"
            finally:
                broker.unsubscribe(subscriber)

        return Response(
            stream_with_context(stream()),
            mimetype="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    return app
