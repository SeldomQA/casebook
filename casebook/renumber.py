from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML

from .scanner import resolve_project_path


CASE_ID_PATTERN = re.compile(r"^(?P<prefix>.+?)(?P<number>\d+)$")


class CaseIdRenumberError(Exception):
    """Raised when a YAML file cannot be safely renumbered."""
    pass


class CaseIdRenumberer:
    """Renumber case IDs in-place while preserving YAML formatting."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root.resolve()
        self.yaml = YAML(typ="rt")
        self.yaml.preserve_quotes = True
        self.yaml.indent(mapping=2, sequence=4, offset=2)
        self.yaml.width = 4096

    def renumber_file(self, file_path: str, mtime_ns: int | str | None = None) -> dict[str, Any]:
        """Renumber each ID prefix independently and return an ID mapping."""
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

        mapping: list[dict[str, Any]] = []
        prefix_sequences: dict[str, dict[str, int]] = {}
        changed = 0

        # Each prefix uses the number and width from its first occurrence. Cases
        # with the same prefix share one sequence even when another prefix sits
        # between them in the YAML order.
        for index, case in enumerate(test_cases):
            if not isinstance(case, dict):
                raise CaseIdRenumberError(
                    f"Case at position {index + 1} is not an object.")
            old_value = case.get("id", "")
            old_id = str(old_value or "").strip()
            match = CASE_ID_PATTERN.match(old_id)
            if not match:
                raise CaseIdRenumberError(
                    f"Case ID at position {index + 1} is not renumberable: {old_id or 'empty'}"
                )

            prefix = match.group("prefix")
            number = match.group("number")
            sequence = prefix_sequences.setdefault(
                prefix,
                {
                    "start": int(number),
                    "width": len(number),
                    "offset": 0,
                },
            )
            new_number = sequence["start"] + sequence["offset"]
            new_id = f"{prefix}{new_number:0{sequence['width']}d}"
            sequence["offset"] += 1
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
        """Preserve ruamel scalar subclasses such as quoted strings."""
        if isinstance(old_value, str) and type(old_value) is not str:
            return type(old_value)(new_id)
        return new_id

    def _display_path(self, target: Path) -> str:
        """Return project-relative paths in CLI/API responses when possible."""
        try:
            return target.relative_to(self.project_root).as_posix()
        except ValueError:
            return target.as_posix()
