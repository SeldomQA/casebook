from __future__ import annotations

from collections import Counter, OrderedDict
from pathlib import Path
from threading import RLock
from typing import Any

from ruamel.yaml import YAML


DEFAULT_SCAN_DIRS = ["releases"]


def normalize_scan_dirs(project_root: Path, scan_dirs: list[str] | None) -> list[str]:
    """Normalize user-provided scan directories and keep legacy release/ paths working."""
    normalized: list[str] = []
    for raw_dir in scan_dirs or []:
        value = str(raw_dir).strip().rstrip("/\\").replace("\\", "/")
        if not value:
            continue
        if value.startswith("release/") and not (project_root / value).exists():
            plural_value = "releases/" + value[len("release/"):]
            if (project_root / plural_value).exists():
                value = plural_value
        if value not in normalized:
            normalized.append(value)
    return normalized or DEFAULT_SCAN_DIRS.copy()


def relative_path(project_root: Path, path: Path) -> str:
    """Return a POSIX-style path relative to the Casebook project root."""
    return path.relative_to(project_root).as_posix()


def resolve_project_path(project_root: Path, rel_path: str) -> Path:
    """Resolve a project-relative path and reject path traversal."""
    candidate = (project_root / str(rel_path).replace("\\", "/")).resolve()
    root = project_root.resolve()
    if candidate != root and root not in candidate.parents:
        raise ValueError("Path escapes project root")
    return candidate


def compute_stats(cases: list[dict[str, Any]]) -> dict[str, Any]:
    """Compute summary counters used by the API, export page, and sidebar."""
    priorities = Counter()
    types = Counter()
    tags = Counter()
    auto_count = 0
    for case in cases:
        priorities[case.get("priority", "P2")] += 1
        types[case.get("type", "functional")] += 1
        for tag in case.get("tags", []):
            tags[tag] += 1
        if case.get("auto"):
            auto_count += 1
    return {
        "total": len(cases),
        "priorities": dict(priorities),
        "types": dict(types),
        "tags": dict(tags),
        "auto_count": auto_count,
    }


def normalize_list(value: Any) -> list[str]:
    """Convert a YAML scalar/list/missing value into a list of strings."""
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)]


def normalize_priority(value: Any) -> str:
    """Normalize unknown priorities to P2, the safest default."""
    priority = str(value or "P2").upper()
    return priority if priority in {"P0", "P1", "P2"} else "P2"


def case_to_api(case: dict[str, Any], index: int) -> dict[str, Any]:
    """Convert raw YAML case data into the stable frontend API shape."""
    return {
        "index": index,
        "id": str(case.get("id", "N/A")),
        "title": str(case.get("title", "Untitled")),
        "description": str(case.get("description", "") or "").strip(),
        "priority": normalize_priority(case.get("priority", "P2")),
        "type": str(case.get("type", "functional")),
        "preconditions": normalize_list(case.get("preconditions", [])),
        "steps": normalize_list(case.get("steps", [])),
        "expected_results": normalize_list(case.get("expected_results", [])),
        "tags": normalize_list(case.get("tags", [])),
        "auto": bool(case.get("auto", False)),
    }


class CasebookStore:
    """Thread-safe cache of parsed YAML case files for one Casebook scope."""

    def __init__(self, project_root: Path, scan_dirs: list[str] | None = None) -> None:
        self.project_root = project_root.resolve()
        self.scan_dirs = normalize_scan_dirs(self.project_root, scan_dirs)
        self._yaml = YAML(typ="rt")
        self._lock = RLock()
        self._entries: list[dict[str, Any]] = []
        self._entries_by_path: dict[str, dict[str, Any]] = {}
        self.version = 0

    def refresh(self) -> dict[str, Any]:
        """Re-scan YAML files and return the updated project summary."""
        entries: list[dict[str, Any]] = []
        for scan_dir in self.scan_dirs:
            root_path = resolve_project_path(self.project_root, scan_dir)
            if not root_path.exists():
                continue
            for yaml_file in sorted(root_path.rglob("*")):
                if yaml_file.suffix.lower() not in {".yaml", ".yml"}:
                    continue
                entry = self._parse_file(yaml_file)
                if entry:
                    entries.append(entry)

        with self._lock:
            self._entries = entries
            self._entries_by_path = {entry["path"]: entry for entry in entries}
            self.version += 1
            return self.summary()

    def _parse_file(self, yaml_file: Path) -> dict[str, Any] | None:
        """Parse one YAML file, ignoring files outside the Casebook schema shape."""
        try:
            data = self._yaml.load(yaml_file.read_text(encoding="utf-8"))
        except Exception as exc:
            print(f"Warning: failed to parse {yaml_file}: {exc}")
            return None
        if not isinstance(data, dict) or "test_cases" not in data:
            return None
        test_cases = data.get("test_cases") or []
        if not isinstance(test_cases, list):
            return None

        rel_path = relative_path(self.project_root, yaml_file)
        metadata = data.get("metadata") or {}
        if not isinstance(metadata, dict):
            metadata = {}

        cases = [case_to_api(case or {}, index) for index, case in enumerate(test_cases)]
        entry = {
            "path": rel_path,
            "parts": rel_path.split("/"),
            "module": str(metadata.get("module", "Unknown")),
            "feature": str(metadata.get("feature", "")),
            "owner": str(metadata.get("owner", "N/A")),
            "last_reviewed": str(metadata.get("last_reviewed", "")),
            "file_tags": normalize_list(metadata.get("tags", [])),
            "cases": cases,
            "mtime_ns": str(yaml_file.stat().st_mtime_ns),
        }
        entry["stats"] = compute_stats(cases)
        return entry

    def summary(self) -> dict[str, Any]:
        """Return aggregate statistics for the current cache."""
        with self._lock:
            cases = [case for entry in self._entries for case in entry["cases"]]
            stats = compute_stats(cases)
            owners: list[str] = []
            for entry in self._entries:
                owner = str(entry.get("owner") or "").strip()
                if owner and owner != "N/A" and owner not in owners:
                    owners.append(owner)
            return {
                "version": self.version,
                "scan_dirs": self.scan_dirs,
                "files": len(self._entries),
                "cases": len(cases),
                "owners": owners,
                "stats": stats,
            }

    def list_files(self) -> list[dict[str, Any]]:
        """Return file-level metadata without full case detail payloads."""
        with self._lock:
            return [
                {
                    "path": entry["path"],
                    "module": entry["module"],
                    "feature": entry["feature"],
                    "owner": entry["owner"],
                    "last_reviewed": entry["last_reviewed"],
                    "file_tags": entry["file_tags"],
                    "stats": entry["stats"],
                    "mtime_ns": entry["mtime_ns"],
                }
                for entry in self._entries
            ]

    def get_file(self, file_path: str) -> dict[str, Any] | None:
        """Return one file with full case details."""
        with self._lock:
            entry = self._entries_by_path.get(file_path)
            if not entry:
                return None
            return {
                "path": entry["path"],
                "module": entry["module"],
                "feature": entry["feature"],
                "owner": entry["owner"],
                "last_reviewed": entry["last_reviewed"],
                "file_tags": entry["file_tags"],
                "stats": entry["stats"],
                "cases": entry["cases"],
                "mtime_ns": entry["mtime_ns"],
            }

    def tree(self) -> list[dict[str, Any]]:
        """Build a directory tree that the sidebar can render directly."""
        with self._lock:
            root: OrderedDict[str, Any] = OrderedDict()
            for entry in self._entries:
                current = root
                parts = entry["parts"]
                for part in parts[:-1]:
                    current = current.setdefault(part, OrderedDict())
                current[parts[-1]] = {"_file": entry}
            return self._build_tree(root)

    def _build_tree(self, children: OrderedDict[str, Any]) -> list[dict[str, Any]]:
        """Convert nested OrderedDict nodes into sorted tree dictionaries."""
        items: list[dict[str, Any]] = []
        for name, value in children.items():
            if isinstance(value, dict) and "_file" in value:
                entry = value["_file"]
                items.append({
                    "type": "file",
                    "name": name,
                    "path": entry["path"],
                    "count": entry["stats"]["total"],
                    "feature": entry["feature"],
                })
            elif isinstance(value, OrderedDict):
                child_items = self._build_tree(value)
                count = sum(self._tree_count(child) for child in child_items)
                items.append({
                    "type": "dir",
                    "name": name,
                    "count": count,
                    "children": child_items,
                })
        items.sort(key=lambda item: (0 if item["type"] == "dir" else 1, item["name"]))
        return items

    def _tree_count(self, item: dict[str, Any]) -> int:
        """Count test cases in a file or directory tree node."""
        if item["type"] == "file":
            return int(item.get("count", 0))
        return sum(self._tree_count(child) for child in item.get("children", []))
