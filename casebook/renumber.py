from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML

from .scanner import resolve_project_path


CASE_ID_PATTERN = re.compile(r"^(?P<prefix>.+?)(?P<number>\d+)$")


class CaseIdRenumberError(Exception):
    pass


class CaseIdRenumberer:
    def __init__(self, project_root: Path):
        self.project_root = project_root.resolve()
        self.yaml = YAML(typ="rt")
        self.yaml.preserve_quotes = True
        self.yaml.indent(mapping=2, sequence=4, offset=2)
        self.yaml.width = 4096

    def renumber_file(self, file_path: str, mtime_ns: int | str | None = None) -> dict[str, Any]:
        try:
            target = resolve_project_path(self.project_root, file_path)
        except ValueError as exc:
            raise CaseIdRenumberError(str(exc)) from exc
        if not target.exists():
            raise FileNotFoundError(file_path)
        if target.suffix.lower() not in {".yaml", ".yml"}:
            raise CaseIdRenumberError("Only YAML files can be renumbered.")

        current_mtime = target.stat().st_mtime_ns
        if mtime_ns is not None and int(mtime_ns) != current_mtime:
            raise CaseIdRenumberError("The file changed after it was loaded.")

        data = self.yaml.load(target.read_text(encoding="utf-8"))
        test_cases = data.get("test_cases") if isinstance(data, dict) else None
        if not isinstance(test_cases, list) or not test_cases:
            raise CaseIdRenumberError("No test cases found in this file.")

        first_case = test_cases[0] or {}
        first_id = str(first_case.get("id") or "").strip()
        match = CASE_ID_PATTERN.match(first_id)
        if not match:
            raise CaseIdRenumberError(f"First case ID is not renumberable: {first_id or 'empty'}")

        prefix = match.group("prefix")
        start = int(match.group("number"))
        width = len(match.group("number"))
        mapping: list[dict[str, Any]] = []
        changed = 0

        for index, case in enumerate(test_cases):
            if not isinstance(case, dict):
                raise CaseIdRenumberError(f"Case at position {index + 1} is not an object.")
            old_value = case.get("id", "")
            old_id = str(old_value or "").strip()
            new_id = f"{prefix}{start + index:0{width}d}"
            mapping.append({
                "index": index,
                "old_id": old_id,
                "new_id": new_id,
                "changed": old_id != new_id,
            })
            if old_id != new_id:
                case["id"] = self._styled_id(old_value, new_id)
                changed += 1

        if changed:
            with target.open("w", encoding="utf-8") as handle:
                self.yaml.dump(data, handle)

        return {
            "file_path": self._display_path(target),
            "total": len(test_cases),
            "changed": changed,
            "mapping": mapping,
            "mtime_ns": str(target.stat().st_mtime_ns),
        }

    def _styled_id(self, old_value: Any, new_id: str) -> str:
        if isinstance(old_value, str) and type(old_value) is not str:
            return type(old_value)(new_id)
        return new_id

    def _display_path(self, target: Path) -> str:
        try:
            return target.relative_to(self.project_root).as_posix()
        except ValueError:
            return target.as_posix()
