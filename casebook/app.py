from __future__ import annotations

import atexit
import json
import queue
import uuid
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from flask import (
    Flask,
    Response,
    jsonify,
    render_template,
    request,
    send_from_directory,
    stream_with_context,
)
from flask.typing import ResponseReturnValue
from werkzeug.utils import secure_filename

from . import __version__
from .editor import CaseEditor, CaseNotFoundError, EditConflictError
from .marks import MarksStore
from .renumber import CaseIdRenumberError, CaseIdRenumberer
from .runs import InvalidRunError, RunNotFoundError, TestRunStore
from .scanner import CasebookStore
from .watcher import CasebookWatcher

SCREENSHOT_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
SCREENSHOT_MIME_TYPES = {
    ".gif": "image/gif",
    ".jpeg": "image/jpeg",
    ".jpg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
}


class EventBroker:
    """Small in-process pub/sub broker for browser live-reload events."""

    def __init__(self) -> None:
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
    """Create the Casebook Flask app for one project and one scan scope."""
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
        """Return canonical case keys for the currently loaded YAML scope."""
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
        """Resolve the cases that must be considered for a test plan."""
        data = runs.get_run(run_id, scope=store.scan_dirs)
        run = data.get("run") or {}
        if isinstance(run, dict):
            case_scope = run.get("case_scope")
            if isinstance(case_scope, list):
                return [
                    str(item or "")
                    for item in case_scope
                    if str(item or "").strip()
                ]
        return current_case_keys()

    def unresolved_case_keys(source_run_id: str) -> list[str]:
        """Build a retest scope from failed, blocked, and deferred source cases."""
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
        """Refresh YAML data and notify connected browsers."""
        summary = store.refresh()
        broker.publish(
            {"type": "reload", "reason": reason, "summary": summary})
        return summary

    def screenshot_directory(run_id: str) -> Path:
        """Return the local screenshot directory for one test plan."""
        return store.project_root / "test-runs" / "screenshots" / run_id

    def legacy_screenshot_directory(run_id: str) -> Path:
        """Return the pre-0.7 screenshot directory for compatibility."""
        return store.project_root / ".casebook" / "screenshots" / run_id

    def screenshot_file_path(run_id: str, stored_name: str) -> Path:
        """Resolve a screenshot file, preferring the current test-runs location."""
        current = screenshot_directory(run_id) / stored_name
        if current.exists():
            return current
        return legacy_screenshot_directory(run_id) / stored_name

    def find_screenshot(data: dict[str, Any], screenshot_id: str) -> dict[str, Any] | None:
        """Find screenshot metadata across all execution results in a run."""
        results = data.get("results") or {}
        if not isinstance(results, dict):
            return None
        for result in results.values():
            if not isinstance(result, dict):
                continue
            screenshots = result.get("screenshots") or []
            if not isinstance(screenshots, list):
                continue
            for screenshot in screenshots:
                if isinstance(screenshot, dict) and screenshot.get("id") == screenshot_id:
                    return screenshot
        return None

    def split_result_key(key: str) -> tuple[str, str]:
        """Split a canonical file#case execution result key."""
        if "#" not in key:
            return "", ""
        file_path, case_id = key.rsplit("#", 1)
        return file_path, case_id

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
    def add_no_cache_headers(response: Response) -> Response:
        if request.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store"
        return response

    @app.route("/")
    def index() -> ResponseReturnValue:
        return render_template("index.html", casebook_version=__version__)

    @app.get("/favicon.ico")
    def favicon() -> ResponseReturnValue:
        return send_from_directory(app.static_folder, "favicon.svg", mimetype="image/svg+xml")

    @app.get("/api/summary")
    def api_summary() -> ResponseReturnValue:
        return jsonify(store.summary())

    @app.get("/api/tree")
    def api_tree() -> ResponseReturnValue:
        return jsonify(store.tree())

    @app.get("/api/files")
    def api_files() -> ResponseReturnValue:
        return jsonify(store.list_files())

    @app.get("/api/files/<path:file_path>")
    def api_file(file_path: str) -> ResponseReturnValue:
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
    def api_renumber_file(file_path: str) -> ResponseReturnValue:
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
    def api_marks() -> ResponseReturnValue:
        return jsonify(marks.all())

    @app.post("/api/marks/toggle")
    def api_toggle_mark() -> ResponseReturnValue:
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
    def api_update_mark() -> ResponseReturnValue:
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
    def api_test_runs() -> ResponseReturnValue:
        return jsonify(runs.list_runs(scope=store.scan_dirs))

    @app.post("/api/test-runs")
    def api_create_test_run() -> ResponseReturnValue:
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
    def api_test_run(run_id: str) -> ResponseReturnValue:
        try:
            return jsonify(runs.get_run(run_id, scope=store.scan_dirs))
        except RunNotFoundError:
            return jsonify({"error": f"Test run not found: {run_id}"}), 404

    @app.patch("/api/test-runs/<run_id>")
    def api_complete_test_run(run_id: str) -> ResponseReturnValue:
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
    def api_update_test_result(run_id: str) -> ResponseReturnValue:
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
                actual_result=payload.get(
                    "actual_result") if "actual_result" in payload else None,
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

    @app.post("/api/test-runs/<run_id>/results/screenshots")
    def api_upload_test_screenshot(run_id: str) -> ResponseReturnValue:
        file_path = str(request.form.get("file_path")
                        or request.form.get("filePath") or "")
        case_id = str(request.form.get("case_id")
                      or request.form.get("caseId") or "")
        uploaded = request.files.get("screenshot")
        if not file_path or not case_id:
            return jsonify({"error": "Missing file_path or case_id"}), 400
        if not uploaded or not uploaded.filename:
            return jsonify({"error": "Missing screenshot file"}), 400

        original_name = secure_filename(uploaded.filename) or "screenshot"
        extension = Path(original_name).suffix.lower()
        if extension not in SCREENSHOT_EXTENSIONS:
            return jsonify({"error": "Screenshot must be a PNG, JPG, GIF, or WebP image"}), 400
        try:
            runs.get_run(run_id, scope=store.scan_dirs)
        except RunNotFoundError:
            return jsonify({"error": f"Test run not found: {run_id}"}), 404

        screenshot_id = uuid.uuid4().hex
        stored_name = f"{screenshot_id}{extension}"
        target_dir = screenshot_directory(run_id)
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / stored_name
        uploaded.save(target)
        metadata = {
            "id": screenshot_id,
            "name": original_name,
            "stored_name": stored_name,
            "content_type": SCREENSHOT_MIME_TYPES[extension],
            "size": target.stat().st_size,
            "path": f"test-runs/screenshots/{run_id}/{stored_name}",
        }
        try:
            result = runs.add_screenshot(
                run_id=run_id,
                file_path=file_path,
                case_id=case_id,
                screenshot=metadata,
                scope=store.scan_dirs,
            )
        except RunNotFoundError:
            target.unlink(missing_ok=True)
            return jsonify({"error": f"Test run not found: {run_id}"}), 404
        except InvalidRunError as exc:
            target.unlink(missing_ok=True)
            return jsonify({"error": str(exc)}), 400
        broker.publish({
            "type": "test_run",
            "action": "screenshot_uploaded",
            "run_id": run_id,
            "file_path": file_path,
            "case_id": case_id,
        })
        return jsonify(result), 201

    @app.delete("/api/test-runs/<run_id>/screenshots/<screenshot_id>")
    def api_delete_test_run_screenshot(run_id: str, screenshot_id: str) -> ResponseReturnValue:
        try:
            result = runs.remove_screenshot(
                run_id=run_id,
                screenshot_id=screenshot_id,
                scope=store.scan_dirs,
            )
        except RunNotFoundError:
            return jsonify({"error": f"Test run not found: {run_id}"}), 404
        except InvalidRunError as exc:
            return jsonify({"error": str(exc)}), 404

        screenshot = result.get("screenshot") or {}
        stored_name = str(screenshot.get("stored_name") or "")
        if Path(stored_name).name == stored_name:
            (screenshot_directory(run_id) / stored_name).unlink(missing_ok=True)
            (legacy_screenshot_directory(run_id) /
             stored_name).unlink(missing_ok=True)

        file_path, case_id = split_result_key(str(result.get("key") or ""))
        broker.publish({
            "type": "test_run",
            "action": "screenshot_deleted",
            "run_id": run_id,
            "file_path": file_path,
            "case_id": case_id,
        })
        return jsonify(result)

    @app.get("/api/test-runs/<run_id>/screenshots/<screenshot_id>")
    def api_test_run_screenshot(run_id: str, screenshot_id: str) -> ResponseReturnValue:
        try:
            data = runs.get_run(run_id, scope=store.scan_dirs)
        except RunNotFoundError:
            return jsonify({"error": f"Test run not found: {run_id}"}), 404
        screenshot = find_screenshot(data, screenshot_id)
        if not screenshot:
            return jsonify({"error": f"Screenshot not found: {screenshot_id}"}), 404
        stored_name = str(screenshot.get("stored_name") or "")
        if Path(stored_name).name != stored_name:
            return jsonify({"error": f"Screenshot not found: {screenshot_id}"}), 404
        screenshot_path = screenshot_file_path(run_id, stored_name)
        if not screenshot_path.exists():
            return jsonify({"error": f"Screenshot not found: {screenshot_id}"}), 404
        return send_from_directory(
            screenshot_path.parent,
            screenshot_path.name,
            mimetype=str(screenshot.get("content_type") or "image/png"),
        )

    @app.patch("/api/cases")
    def api_update_case() -> ResponseReturnValue:
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
    def api_refresh() -> ResponseReturnValue:
        return jsonify(refresh_and_publish("manual"))

    @app.get("/api/events")
    def api_events() -> ResponseReturnValue:
        subscriber = broker.subscribe()

        def stream() -> Iterator[str]:
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
