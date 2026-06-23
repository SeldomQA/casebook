from __future__ import annotations

from pathlib import Path
from typing import Any

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap, CommentedSeq
from ruamel.yaml.scalarstring import LiteralScalarString

from .scanner import case_to_api, resolve_project_path


ALLOWED_FIELDS = {
    "title",
    "description",
    "priority",
    "type",
    "preconditions",
    "steps",
    "expected_results",
    "tags",
    "auto",
}
LIST_FIELDS = {"preconditions", "steps", "expected_results", "tags"}
FIELD_ORDER = [
    "id",
    "title",
    "description",
    "priority",
    "type",
    "preconditions",
    "steps",
    "expected_results",
    "tags",
    "auto",
]


class EditConflictError(Exception):
    pass


class CaseNotFoundError(Exception):
    pass


class CaseEditor:
    def __init__(self, project_root: Path):
        self.project_root = project_root.resolve()
        self.yaml = YAML(typ="rt")
        self.yaml.preserve_quotes = True
        self.yaml.indent(mapping=2, sequence=4, offset=2)
        self.yaml.width = 4096

    def update_case(
        self,
        file_path: str,
        case_id: str,
        updates: dict[str, Any],
        mtime_ns: int | None = None,
    ) -> dict[str, Any]:
        target = resolve_project_path(self.project_root, file_path)
        if not target.exists():
            raise FileNotFoundError(file_path)
        current_mtime = target.stat().st_mtime_ns
        if mtime_ns is not None and int(mtime_ns) != current_mtime:
            raise EditConflictError("The file changed after it was loaded.")

        data = self.yaml.load(target.read_text(encoding="utf-8"))
        test_cases = data.get("test_cases") if isinstance(data, dict) else None
        if not isinstance(test_cases, list):
            raise CaseNotFoundError(case_id)

        for index, case in enumerate(test_cases):
            if str(case.get("id", "")) != str(case_id):
                continue
            self._apply_updates(case, updates)
            with target.open("w", encoding="utf-8") as handle:
                self.yaml.dump(data, handle)
            return {
                "case": case_to_api(case, index),
                "mtime_ns": str(target.stat().st_mtime_ns),
            }
        raise CaseNotFoundError(case_id)

    def _apply_updates(self, case: dict[str, Any], updates: dict[str, Any]) -> None:
        for field, value in updates.items():
            if field not in ALLOWED_FIELDS:
                continue
            if field not in case and self._empty_missing_value(field, value):
                continue
            if field in LIST_FIELDS:
                self._set_field(case, field, self._list_value(value, case.get(field)))
            elif field == "auto":
                self._set_field(case, field, bool(value))
            elif field == "description":
                text = "" if value is None else str(value)
                self._set_field(
                    case,
                    field,
                    LiteralScalarString(text) if "\n" in text else text,
                )
            else:
                self._set_field(case, field, "" if value is None else str(value))

    def _empty_missing_value(self, field: str, value: Any) -> bool:
        if field == "auto":
            return value in {False, None, ""}
        if field in LIST_FIELDS:
            if isinstance(value, str):
                return not value.strip()
            if isinstance(value, list):
                return not any(str(item).strip() for item in value)
            return True
        if value is None:
            return True
        if isinstance(value, str):
            return not value.strip()
        return False

    def _set_field(self, case: dict[str, Any], field: str, value: Any) -> None:
        if field in case:
            case[field] = value
            return
        if isinstance(case, CommentedMap):
            case.insert(self._insert_index(case, field), field, value)
            return
        case[field] = value

    def _insert_index(self, case: CommentedMap, field: str) -> int:
        keys = list(case.keys())
        try:
            field_order_index = FIELD_ORDER.index(field)
        except ValueError:
            return len(keys)
        for previous in reversed(FIELD_ORDER[:field_order_index]):
            if previous in case:
                return keys.index(previous) + 1
        return len(keys)

    def _list_value(self, value: Any, existing: Any) -> CommentedSeq:
        seq = CommentedSeq()
        if isinstance(value, str):
            items = [line.strip() for line in value.splitlines()]
        elif isinstance(value, list):
            items = [str(item).strip() for item in value]
        else:
            items = []
        seq.extend([item for item in items if item])
        if isinstance(existing, CommentedSeq) and existing.fa.flow_style():
            seq.fa.set_flow_style()
        return seq
