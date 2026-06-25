from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock
from typing import Any


EXECUTION_STATUSES = {"passed", "failed", "blocked"}


class RunNotFoundError(Exception):
    pass


class InvalidRunError(Exception):
    pass


class TestRunStore:
    def __init__(self, project_root: Path):
        self.project_root = project_root.resolve()
        self.path = self.project_root / "test-runs"
        self._lock = RLock()

    def list_runs(self, scope: list[str] | None = None) -> list[dict[str, Any]]:
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
                runs.append({
                    **run,
                    "result_counts": self._result_counts(run_data),
                    "result_total": len(run_data.get("results") or {}),
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
    ) -> dict[str, Any]:
        with self._lock:
            now = self._now()
            run_name = str(name or "").strip() or f"Test Run {now[:19]}"
            run_id = self._unique_run_id(run_name, now)
            data = {
                "run": {
                    "id": run_id,
                    "name": run_name,
                    "status": "in_progress",
                    "scope": self._normalize_scope(scope) or [],
                    "environment": str(environment or "").strip(),
                    "tester": str(tester or "").strip(),
                    "started_at": now,
                    "completed_at": None,
                },
                "results": {},
            }
            self._save(run_id, data)
            return data

    def complete_run(
        self,
        run_id: str,
        environment: str | None = None,
        tester: str | None = None,
        scope: list[str] | None = None,
    ) -> dict[str, Any]:
        with self._lock:
            data = self._load(run_id)
            expected_scope = self._normalize_scope(scope)
            if expected_scope is not None:
                run = data.get("run") or {}
                if not isinstance(run, dict) or self._normalize_scope(run.get("scope")) != expected_scope:
                    raise RunNotFoundError(run_id)

            now = self._now()
            run = data.setdefault("run", {})
            if not isinstance(run, dict):
                run = {}
                data["run"] = run
            run["status"] = "completed"
            run["environment"] = str(environment or "").strip()
            run["tester"] = str(tester or "").strip()
            run["started_at"] = str(run.get("started_at") or run.get("created_at") or now)
            run["completed_at"] = now
            run.pop("build", None)
            run.pop("created_at", None)
            run.pop("updated_at", None)
            self._save(run_id, data)
            return data

    def get_run(self, run_id: str, scope: list[str] | None = None) -> dict[str, Any]:
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
        defects: list[str] | str | None = None,
        tester: str | None = None,
        scope: list[str] | None = None,
    ) -> dict[str, Any]:
        with self._lock:
            data = self._load(run_id)
            expected_scope = self._normalize_scope(scope)
            if expected_scope is not None:
                run = data.get("run") or {}
                if not isinstance(run, dict) or self._normalize_scope(run.get("scope")) != expected_scope:
                    raise RunNotFoundError(run_id)
            key = self.key(file_path, case_id)
            results = data.setdefault("results", {})
            if not isinstance(results, dict):
                results = {}
                data["results"] = results

            existing = results.get(key) if isinstance(results.get(key), dict) else {}
            now = self._now()
            next_result = {
                "status": existing.get("status", "untested"),
                "notes": existing.get("notes", ""),
                "defects": existing.get("defects", []),
                "tester": existing.get("tester", ""),
                "updated_at": now,
            }
            if status:
                normalized_status = str(status).strip().lower()
                if normalized_status not in EXECUTION_STATUSES:
                    raise InvalidRunError(f"Invalid execution status: {status}")
                next_result["status"] = normalized_status
                next_result["executed_at"] = now
            elif existing.get("executed_at"):
                next_result["executed_at"] = existing.get("executed_at")

            if notes is not None:
                next_result["notes"] = str(notes)
            if defects is not None:
                next_result["defects"] = self._normalize_defects(defects)
            if tester is not None:
                next_result["tester"] = str(tester).strip()

            results[key] = next_result
            run = data.setdefault("run", {})
            if isinstance(run, dict):
                run["started_at"] = str(run.get("started_at") or run.get("created_at") or now)
                run["completed_at"] = now
                run.pop("build", None)
                run.pop("created_at", None)
                run.pop("updated_at", None)
            self._save(run_id, data)
            return {"key": key, "result": next_result, "run": data}

    def key(self, file_path: str, case_id: str) -> str:
        return f"{file_path}#{case_id}"

    def _load(self, run_id: str) -> dict[str, Any]:
        run_file = self._run_file(run_id)
        if not run_file.exists():
            raise RunNotFoundError(run_id)
        return self._load_file(run_file)

    def _load_file(self, run_file: Path) -> dict[str, Any]:
        data = json.loads(run_file.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {"run": {}, "results": {}}

    def _save(self, run_id: str, data: dict[str, Any]) -> None:
        self.path.mkdir(parents=True, exist_ok=True)
        self._run_file(run_id).write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _run_file(self, run_id: str) -> Path:
        safe_id = self._safe_run_id(run_id)
        if safe_id != run_id:
            raise RunNotFoundError(run_id)
        return self.path / f"{safe_id}.json"

    def _unique_run_id(self, name: str, now: str) -> str:
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
        value = str(run_id or "").strip()
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", value):
            raise RunNotFoundError(run_id)
        return value

    def _slug(self, value: str) -> str:
        slug = re.sub(r"[^A-Za-z0-9]+", "-", value.strip().lower()).strip("-")
        return slug[:48]

    def _normalize_defects(self, defects: list[str] | str) -> list[str]:
        if isinstance(defects, str):
            items = re.split(r"[\n,]+", defects)
        else:
            items = [str(item) for item in defects]
        return [item.strip() for item in items if item.strip()]

    def _normalize_scope(self, scope: Any) -> list[str] | None:
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

    def _result_counts(self, data: dict[str, Any]) -> dict[str, int]:
        counts = {status: 0 for status in sorted(EXECUTION_STATUSES)}
        results = data.get("results") or {}
        if not isinstance(results, dict):
            return counts
        for result in results.values():
            if not isinstance(result, dict):
                continue
            status = str(result.get("status") or "").lower()
            if status in counts:
                counts[status] += 1
        return counts

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()
