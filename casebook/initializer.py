from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from importlib.abc import Traversable
from importlib import resources
from pathlib import Path


class ProjectInitError(Exception):
    """Raised when a project scaffold cannot be written safely."""

    pass


@dataclass(frozen=True)
class ProjectInitResult:
    """Result of copying the Casebook project template."""

    project_root: Path
    created: list[Path]
    skipped: list[Path]


def init_project(project_path: str | Path, force: bool = False) -> ProjectInitResult:
    """Create or update a Casebook project from bundled scaffold files."""
    project_root = Path(project_path).expanduser().resolve()
    if project_root.exists() and not project_root.is_dir():
        raise ProjectInitError(f"Target exists and is not a directory: {project_root}")

    project_root.mkdir(parents=True, exist_ok=True)
    created: list[Path] = []
    skipped: list[Path] = []

    template_root = resources.files("casebook").joinpath("project_template")
    for relative_path, template_file in _iter_template_files(template_root):
        target = project_root / relative_path
        if target.exists() and not force:
            skipped.append(relative_path)
            continue
        if target.exists() and target.is_dir():
            raise ProjectInitError(f"Target path is a directory: {target}")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(template_file.read_bytes())
        created.append(relative_path)

    return ProjectInitResult(
        project_root=project_root,
        created=created,
        skipped=skipped,
    )


def _iter_template_files(
    root: Traversable,
    prefix: Path = Path(),
) -> Iterator[tuple[Path, Traversable]]:
    """Yield scaffold files with stable relative paths for reproducible output."""
    for child in sorted(root.iterdir(), key=lambda item: item.name):
        relative_path = prefix / child.name
        if child.is_dir():
            yield from _iter_template_files(child, relative_path)
        elif child.is_file():
            yield relative_path, child
