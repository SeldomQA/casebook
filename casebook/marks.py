from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock
from typing import Any


class MarksStore:
    def __init__(self, project_root: Path):
        self.project_root = project_root.resolve()
        self.path = self.project_root / ".casebook" / "marks.json"
        self._lock = RLock()

    def _load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {}
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except Exception:
            return {}
        return data if isinstance(data, dict) else {}

    def _save(self, marks: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(marks, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def all(self) -> dict[str, Any]:
        with self._lock:
            return self._load()

    def key(self, file_path: str, case_id: str) -> str:
        return f"{file_path}#{case_id}"

    def update_mark(
        self,
        file_path: str,
        case_id: str,
        needs_update: bool | None = None,
        notes: str | None = None,
    ) -> dict[str, Any]:
        with self._lock:
            marks = self._load()
            key = self.key(file_path, case_id)
            current = marks.get(key)
            mark = current if isinstance(current, dict) else {}
            if needs_update is not None:
                mark["needs_update"] = bool(needs_update)
            if notes is not None:
                mark["notes"] = notes
            if mark.get("needs_update") or str(mark.get("notes") or "").strip():
                mark["updated_at"] = datetime.now(timezone.utc).isoformat()
                marks[key] = mark
                marked = bool(mark.get("needs_update"))
            else:
                marks.pop(key, None)
                marked = False
            self._save(marks)
            return {"key": key, "mark": marks.get(key), "marked": marked, "marks": marks}

    def toggle_needs_update(self, file_path: str, case_id: str) -> dict[str, Any]:
        with self._lock:
            marks = self._load()
            key = self.key(file_path, case_id)
            current = marks.get(key)
            marked = not bool(isinstance(current, dict) and current.get("needs_update"))
        return self.update_mark(file_path, case_id, needs_update=marked)

    def remap_case_ids(self, file_path: str, mapping: list[dict[str, Any]]) -> dict[str, Any]:
        id_map = {
            str(item.get("old_id") or ""): str(item.get("new_id") or "")
            for item in mapping
            if item.get("old_id") and item.get("new_id")
        }
        prefix = f"{file_path}#"
        with self._lock:
            marks = self._load()
            remapped: dict[str, Any] = {}
            for key, value in marks.items():
                if not key.startswith(prefix):
                    remapped[key] = value
                    continue
                old_id = key[len(prefix):]
                new_id = id_map.get(old_id)
                if new_id:
                    remapped[self.key(file_path, new_id)] = value
            self._save(remapped)
            return remapped
