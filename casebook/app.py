from __future__ import annotations

import json
import queue
import atexit
from pathlib import Path
from typing import Any

from flask import Flask, Response, jsonify, render_template, request, stream_with_context

from . import __version__
from .editor import CaseEditor, CaseNotFoundError, EditConflictError
from .marks import MarksStore
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
    marks = MarksStore(project_root=project_root)
    broker = EventBroker()

    initial_summary = store.refresh()
    app.config["CASEBOOK_INITIAL_SUMMARY"] = initial_summary

    def refresh_and_publish(reason: str) -> dict[str, Any]:
        summary = store.refresh()
        broker.publish({"type": "reload", "reason": reason, "summary": summary})
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
        return Response(status=204)

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
        entry["marks"] = {
            f"{file_path}#{case['id']}": all_marks.get(f"{file_path}#{case['id']}")
            for case in entry["cases"]
            if all_marks.get(f"{file_path}#{case['id']}")
        }
        entry["needs_update_count"] = len(entry["marks"])
        return jsonify(entry)

    @app.get("/api/marks")
    def api_marks():
        return jsonify(marks.all())

    @app.post("/api/marks/toggle")
    def api_toggle_mark():
        payload = request.get_json(silent=True) or {}
        file_path = str(payload.get("file_path") or payload.get("filePath") or "")
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
            result = editor.update_case(file_path, case_id, updates, mtime_ns=mtime_ns)
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
