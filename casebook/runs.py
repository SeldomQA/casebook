from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock
from typing import Any


EXECUTION_STATUSES = {"passed", "failed", "blocked", "deferred"}
RUN_MODES = {"full", "retest_unresolved"}


class RunNotFoundError(Exception):
    """Raised when a test run file is missing or outside the requested scope."""

    pass


class InvalidRunError(Exception):
    """Raised when a test run state transition or payload is invalid."""

    pass


class TestRunStore:
    """JSON-backed storage for Casebook test plan execution data."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root.resolve()
        self.path = self.project_root / "test-runs"
        self._lock = RLock()

    def list_runs(self, scope: list[str] | None = None) -> list[dict[str, Any]]:
        """List test plans, newest activity first, optionally limited by scope."""
        expected_scope = self._normalize_scope(scope)
        with self._lock:
            runs = []
            for run_file in sorted(self.path.glob("*.json")) if self.path.exists() else []:
                try:
                    run_data = self._load_file(run_file)
                except Exception:
                    continue
                run = run_data.get("run") or {}
                if not isinstance(run, dict) or not run.get("id"):
                    continue
                if expected_scope is not None and self._normalize_scope(run.get("scope")) != expected_scope:
                    continue
                case_scope = self._run_case_scope(run_data)
                runs.append({
                    **run,
                    "result_counts": self._result_counts(run_data),
                    "result_total": len(run_data.get("results") or {}),
                    "case_total": len(case_scope) if case_scope is not None else None,
                })
            runs.sort(
                key=lambda item: str(
                    item.get("completed_at")
                    or item.get("updated_at")
                    or item.get("started_at")
                    or item.get("created_at")
                    or ""
                ),
                reverse=True,
            )
            return runs

    def create_run(
        self,
        name: str | None = None,
        scope: list[str] | None = None,
        environment: str | None = None,
        tester: str | None = None,
        mode: str | None = None,
        source_run_id: str | None = None,
        case_scope: list[str] | None = None,
    ) -> dict[str, Any]:
        """Create a full or retest plan with an explicit case scope snapshot."""
        with self._lock:
            now = self._now()
            run_name = str(name or "").strip() or f"Test Run {now[:19]}"
            run_id = self._unique_run_id(run_name, now)
            normalized_mode = str(mode or "full").strip().lower()
            if normalized_mode not in RUN_MODES:
                raise InvalidRunError(f"Invalid test plan mode: {mode}")
            # Store a stable case_scope so later YAML additions do not silently
            # change what this execution round means.
            normalized_case_scope = self._normalize_case_scope(
                case_scope or [])
            data = {
                "run": {
                    "id": run_id,
                    "name": run_name,
                    "status": "in_progress",
                    "mode": normalized_mode,
                    "scope": self._normalize_scope(scope) or [],
                    "case_scope": normalized_case_scope,
                    "environment": str(environment or "").strip(),
                    "tester": str(tester or "").strip(),
                    "started_at": now,
                    "completed_at": None,
                },
                "results": {},
            }
            if source_run_id:
                data["run"]["source_run_id"] = str(source_run_id).strip()
            if normalized_mode == "retest_unresolved":
                data["run"]["source_statuses"] = [
                    "failed", "blocked", "deferred"]
            self._save(run_id, data)
            return data

    def complete_run(
        self,
        run_id: str,
        environment: str | None = None,
        tester: str | None = None,
        scope: list[str] | None = None,
        required_case_keys: list[str] | None = None,
    ) -> dict[str, Any]:
        """Mark a plan complete only after all required cases have a result."""
        with self._lock:
            data = self._load(run_id)
            expected_scope = self._normalize_scope(scope)
            if expected_scope is not None:
                run = data.get("run") or {}
                if not isinstance(run, dict) or self._normalize_scope(run.get("scope")) != expected_scope:
                    raise RunNotFoundError(run_id)

            if required_case_keys is None:
                case_scope = self._run_case_scope(data)
                required_case_keys = case_scope or []

            untested = self.untested_case_keys(data, required_case_keys)
            if untested:
                raise InvalidRunError(
                    f"Cannot complete test plan: {len(untested)} untested cases remain."
                )

            now = self._now()
            run = data.setdefault("run", {})
            if not isinstance(run, dict):
                run = {}
                data["run"] = run
            run["status"] = "completed"
            run["environment"] = str(environment or "").strip()
            run["tester"] = str(tester or "").strip()
            run["started_at"] = str(
                run.get("started_at") or run.get("created_at") or now)
            run["completed_at"] = now
            run.pop("build", None)
            run.pop("created_at", None)
            run.pop("updated_at", None)
            self._save(run_id, data)
            return data

    def get_run(self, run_id: str, scope: list[str] | None = None) -> dict[str, Any]:
        """Load a test plan and optionally verify that it belongs to a scope."""
        with self._lock:
            data = self._load(run_id)
            expected_scope = self._normalize_scope(scope)
            if expected_scope is not None:
                run = data.get("run") or {}
                if not isinstance(run, dict) or self._normalize_scope(run.get("scope")) != expected_scope:
                    raise RunNotFoundError(run_id)
            return data

    def update_result(
        self,
        run_id: str,
        file_path: str,
        case_id: str,
        status: str | None = None,
        notes: str | None = None,
        actual_result: str | None = None,
        defects: list[str] | str | None = None,
        tester: str | None = None,
        scope: list[str] | None = None,
    ) -> dict[str, Any]:
        """Update one case execution result inside a test plan."""
        with self._lock:
            data = self._load(run_id)
            expected_scope = self._normalize_scope(scope)
            if expected_scope is not None:
                run = data.get("run") or {}
                if not isinstance(run, dict) or self._normalize_scope(run.get("scope")) != expected_scope:
                    raise RunNotFoundError(run_id)
            key = self.key(file_path, case_id)
            case_scope = self._run_case_scope(data)
            if case_scope is not None and key not in set(case_scope):
                raise InvalidRunError(
                    "Case is not included in this test plan.")
            results = data.setdefault("results", {})
            if not isinstance(results, dict):
                results = {}
                data["results"] = results

            existing = results.get(key) if isinstance(
                results.get(key), dict) else {}
            now = self._now()
            next_result = {
                "status": existing.get("status", "untested"),
                "notes": existing.get("notes", ""),
                "actual_result": existing.get("actual_result", ""),
                "defects": existing.get("defects", []),
                "screenshots": self._normalize_screenshots(
                    existing.get("screenshots", [])
                ),
                "tester": existing.get("tester", ""),
                "updated_at": now,
            }
            if status:
                normalized_status = str(status).strip().lower()
                if normalized_status not in EXECUTION_STATUSES:
                    raise InvalidRunError(
                        f"Invalid execution status: {status}")
                next_result["status"] = normalized_status
                next_result["executed_at"] = now
            elif existing.get("executed_at"):
                next_result["executed_at"] = existing.get("executed_at")

            if notes is not None:
                next_result["notes"] = str(notes)
            if actual_result is not None:
                next_result["actual_result"] = str(actual_result)
            if defects is not None:
                next_result["defects"] = self._normalize_defects(defects)
            if tester is not None:
                next_result["tester"] = str(tester).strip()

            results[key] = next_result
            run = data.setdefault("run", {})
            if isinstance(run, dict):
                run["started_at"] = str(
                    run.get("started_at") or run.get("created_at") or now)
                run["completed_at"] = now
                run.pop("build", None)
                run.pop("created_at", None)
                run.pop("updated_at", None)
            self._save(run_id, data)
            return {"key": key, "result": next_result, "run": data}

    def add_screenshot(
        self,
        run_id: str,
        file_path: str,
        case_id: str,
        screenshot: dict[str, Any],
        scope: list[str] | None = None,
    ) -> dict[str, Any]:
        """Attach one screenshot metadata record to a case execution result."""
        with self._lock:
            data = self._load(run_id)
            expected_scope = self._normalize_scope(scope)
            if expected_scope is not None:
                run = data.get("run") or {}
                if not isinstance(run, dict) or self._normalize_scope(run.get("scope")) != expected_scope:
                    raise RunNotFoundError(run_id)
            key = self.key(file_path, case_id)
            case_scope = self._run_case_scope(data)
            if case_scope is not None and key not in set(case_scope):
                raise InvalidRunError(
                    "Case is not included in this test plan.")

            results = data.setdefault("results", {})
            if not isinstance(results, dict):
                results = {}
                data["results"] = results
            existing = results.get(key) if isinstance(
                results.get(key), dict) else {}
            now = self._now()
            screenshots = self._normalize_screenshots(
                existing.get("screenshots", []))
            next_screenshot = {
                **screenshot,
                "uploaded_at": str(screenshot.get("uploaded_at") or now),
            }
            screenshots.append(next_screenshot)
            next_result = {
                "status": existing.get("status", "untested"),
                "notes": existing.get("notes", ""),
                "actual_result": existing.get("actual_result", ""),
                "defects": existing.get("defects", []),
                "screenshots": screenshots,
                "tester": existing.get("tester", ""),
                "updated_at": now,
            }
            if existing.get("executed_at"):
                next_result["executed_at"] = existing.get("executed_at")

            results[key] = next_result
            run = data.setdefault("run", {})
            if isinstance(run, dict):
                run["started_at"] = str(
                    run.get("started_at") or run.get("created_at") or now)
                run["completed_at"] = now
                run.pop("build", None)
                run.pop("created_at", None)
                run.pop("updated_at", None)
            self._save(run_id, data)
            return {"key": key, "result": next_result, "run": data}

    def remove_screenshot(
        self,
        run_id: str,
        screenshot_id: str,
        scope: list[str] | None = None,
    ) -> dict[str, Any]:
        """Remove one screenshot metadata record from a test plan."""
        with self._lock:
            data = self._load(run_id)
            expected_scope = self._normalize_scope(scope)
            if expected_scope is not None:
                run = data.get("run") or {}
                if not isinstance(run, dict) or self._normalize_scope(run.get("scope")) != expected_scope:
                    raise RunNotFoundError(run_id)

            results = data.get("results") or {}
            if not isinstance(results, dict):
                raise InvalidRunError("Screenshot not found.")

            target_key = ""
            target_result: dict[str, Any] | None = None
            removed: dict[str, Any] | None = None
            for key, result in results.items():
                if not isinstance(result, dict):
                    continue
                screenshots = self._normalize_screenshots(
                    result.get("screenshots", []))
                kept = [
                    screenshot
                    for screenshot in screenshots
                    if screenshot.get("id") != screenshot_id
                ]
                if len(kept) == len(screenshots):
                    continue
                removed = next(
                    screenshot
                    for screenshot in screenshots
                    if screenshot.get("id") == screenshot_id
                )
                result["screenshots"] = kept
                result["updated_at"] = self._now()
                target_key = str(key)
                target_result = result
                break

            if not removed or target_result is None:
                raise InvalidRunError("Screenshot not found.")

            run = data.setdefault("run", {})
            if isinstance(run, dict):
                now = self._now()
                run["started_at"] = str(
                    run.get("started_at") or run.get("created_at") or now)
                run["completed_at"] = now
                run.pop("build", None)
                run.pop("created_at", None)
                run.pop("updated_at", None)
            self._save(run_id, data)
            return {
                "key": target_key,
                "result": target_result,
                "screenshot": removed,
                "run": data,
            }

    def key(self, file_path: str, case_id: str) -> str:
        """Build the canonical execution key used in run JSON files."""
        return f"{file_path}#{case_id}"

    def untested_case_keys(
        self,
        data: dict[str, Any],
        required_case_keys: list[str],
    ) -> list[str]:
        """Return required case keys that do not yet have an execution status."""
        results = data.get("results") or {}
        if not isinstance(results, dict):
            results = {}
        untested: list[str] = []
        for key in required_case_keys:
            result = results.get(key)
            status = ""
            if isinstance(result, dict):
                status = str(result.get("status") or "").strip().lower()
            if status not in EXECUTION_STATUSES:
                untested.append(key)
        return untested

    def _run_case_scope(self, data: dict[str, Any]) -> list[str] | None:
        """Return None for legacy plans that predate case_scope snapshots."""
        run = data.get("run") or {}
        if not isinstance(run, dict) or "case_scope" not in run:
            return None
        case_scope = run.get("case_scope")
        if not isinstance(case_scope, list):
            return []
        return self._normalize_case_scope(case_scope)

    def _load(self, run_id: str) -> dict[str, Any]:
        """Load a run by ID after validating the filesystem-safe ID."""
        run_file = self._run_file(run_id)
        if not run_file.exists():
            raise RunNotFoundError(run_id)
        return self._load_file(run_file)

    def _load_file(self, run_file: Path) -> dict[str, Any]:
        """Load one run JSON file and fall back to an empty shape if needed."""
        data = json.loads(run_file.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {"run": {}, "results": {}}

    def _save(self, run_id: str, data: dict[str, Any]) -> None:
        """Persist a test plan as human-readable JSON."""
        self.path.mkdir(parents=True, exist_ok=True)
        self._run_file(run_id).write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _run_file(self, run_id: str) -> Path:
        """Return the path for a safe run ID."""
        safe_id = self._safe_run_id(run_id)
        if safe_id != run_id:
            raise RunNotFoundError(run_id)
        return self.path / f"{safe_id}.json"

    def _unique_run_id(self, name: str, now: str) -> str:
        """Generate a stable, readable run ID and avoid collisions."""
        timestamp = re.sub(r"\D", "", now[:19])
        slug = self._slug(name)
        base = f"run-{timestamp}-{slug}" if slug else f"run-{timestamp}"
        run_id = base
        suffix = 2
        while (self.path / f"{run_id}.json").exists():
            run_id = f"{base}-{suffix}"
            suffix += 1
        return run_id

    def _safe_run_id(self, run_id: str) -> str:
        """Reject path separators and empty IDs before touching test-runs/."""
        value = str(run_id or "").strip()
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", value):
            raise RunNotFoundError(run_id)
        return value

    def _slug(self, value: str) -> str:
        """Create the readable suffix used in generated run IDs."""
        slug = re.sub(r"[^A-Za-z0-9]+", "-", value.strip().lower()).strip("-")
        return slug[:48]

    def _normalize_defects(self, defects: list[str] | str) -> list[str]:
        """Accept textarea or JSON-list defect input and remove blanks."""
        if isinstance(defects, str):
            items = re.split(r"[\n,]+", defects)
        else:
            items = [str(item) for item in defects]
        return [item.strip() for item in items if item.strip()]

    def _normalize_screenshots(self, screenshots: Any) -> list[dict[str, Any]]:
        """Keep only screenshot metadata that can be served safely."""
        if not isinstance(screenshots, list):
            return []
        normalized: list[dict[str, Any]] = []
        for item in screenshots:
            if not isinstance(item, dict):
                continue
            screenshot_id = str(item.get("id") or "").strip()
            stored_name = str(item.get("stored_name") or "").strip()
            if not screenshot_id or not stored_name:
                continue
            normalized.append({
                "id": screenshot_id,
                "name": str(item.get("name") or stored_name),
                "stored_name": stored_name,
                "content_type": str(item.get("content_type") or ""),
                "size": int(item.get("size") or 0),
                "path": str(item.get("path") or ""),
                "uploaded_at": str(item.get("uploaded_at") or ""),
            })
        return normalized

    def _normalize_scope(self, scope: Any) -> list[str] | None:
        """Normalize a plan scope without inventing a default value."""
        if scope is None:
            return None
        if not isinstance(scope, list):
            scope = [scope]
        normalized: list[str] = []
        for item in scope:
            value = str(item or "").strip().rstrip("/\\")
            if value and value not in normalized:
                normalized.append(value)
        return normalized

    def _normalize_case_scope(self, case_scope: Any) -> list[str]:
        """Normalize and de-duplicate canonical case keys."""
        if not isinstance(case_scope, list):
            case_scope = [case_scope]
        normalized: list[str] = []
        for item in case_scope:
            value = str(item or "").strip()
            if value and value not in normalized:
                normalized.append(value)
        return normalized

    def _result_counts(self, data: dict[str, Any]) -> dict[str, int]:
        """Count results, respecting retest case_scope when present."""
        counts = {status: 0 for status in sorted(EXECUTION_STATUSES)}
        results = data.get("results") or {}
        if not isinstance(results, dict):
            return counts
        case_scope = self._run_case_scope(data)
        case_scope_set = set(case_scope) if case_scope is not None else None
        for key, result in results.items():
            if case_scope_set is not None and key not in case_scope_set:
                continue
            if not isinstance(result, dict):
                continue
            status = str(result.get("status") or "").lower()
            if status in counts:
                counts[status] += 1
        return counts

    def _now(self) -> str:
        """Return an ISO timestamp in UTC for portable run files."""
        return datetime.now(timezone.utc).isoformat()
