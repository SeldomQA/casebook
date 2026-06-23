from __future__ import annotations

import threading
from pathlib import Path
from typing import Callable

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer


class _YamlChangeHandler(FileSystemEventHandler):
    def __init__(self, on_change: Callable[[], None], debounce_seconds: float = 0.35):
        self.on_change = on_change
        self.debounce_seconds = debounce_seconds
        self._timer: threading.Timer | None = None
        self._lock = threading.Lock()

    def on_any_event(self, event: FileSystemEvent) -> None:
        if event.is_directory:
            return
        paths = [event.src_path]
        dest_path = getattr(event, "dest_path", None)
        if dest_path:
            paths.append(dest_path)
        if not any(path.lower().endswith((".yaml", ".yml")) for path in paths):
            return
        self._schedule()

    def _schedule(self) -> None:
        with self._lock:
            if self._timer:
                self._timer.cancel()
            self._timer = threading.Timer(self.debounce_seconds, self.on_change)
            self._timer.daemon = True
            self._timer.start()


class CasebookWatcher:
    def __init__(self, project_root: Path, scan_dirs: list[str], on_change: Callable[[], None]):
        self.project_root = project_root.resolve()
        self.scan_dirs = scan_dirs
        self.on_change = on_change
        self.observer = Observer()

    def start(self) -> None:
        handler = _YamlChangeHandler(self.on_change)
        watched = set()
        for scan_dir in self.scan_dirs:
            path = (self.project_root / scan_dir).resolve()
            if not path.exists() or path in watched:
                continue
            watched.add(path)
            self.observer.schedule(handler, str(path), recursive=True)
        if watched:
            self.observer.start()

    def stop(self) -> None:
        if self.observer.is_alive():
            self.observer.stop()
            self.observer.join(timeout=2)
