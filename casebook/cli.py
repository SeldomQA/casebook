from __future__ import annotations

import argparse
import logging
import sys
import webbrowser
from pathlib import Path

from werkzeug.serving import make_server

from . import __version__


LOGGER = logging.getLogger("casebook.main")


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s/%(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="casebook",
        description="Render, review, and edit YAML test cases locally.",
    )
    parser.add_argument("--version", action="version",
                        version=f"casebook {__version__}")
    subparsers = parser.add_subparsers(dest="command")

    serve = subparsers.add_parser(
        "serve", help="Start the local Casebook web UI")
    serve.add_argument(
        "paths",
        nargs="*",
        help="YAML case directories relative to the current project root",
    )
    serve.add_argument("--host", default="127.0.0.1",
                       help="Host to bind (default: 127.0.0.1)")
    serve.add_argument("--port", "-p", type=int, default=8089,
                       help="Port to bind (default: 8089)")
    serve.add_argument("--open", "-o", action="store_true",
                       help="Open the web UI in a browser")
    serve.add_argument("--no-watch", action="store_true",
                       help="Disable filesystem auto-refresh")
    return parser


def run_serve(args: argparse.Namespace) -> int:
    from .app import create_app

    project_root = Path.cwd()
    app = create_app(project_root=project_root,
                     scan_dirs=args.paths, watch=not args.no_watch)
    summary = app.config.get("CASEBOOK_INITIAL_SUMMARY", {})
    url = f"http://{args.host}:{args.port}"
    browser_url = f"http://localhost:{args.port}" if args.host in {
        "127.0.0.1", "::"} else url

    LOGGER.info("Starting web interface at %s", url)
    LOGGER.info("Starting Casebook %s", __version__)
    LOGGER.info("Watching YAML cases in %s", ", ".join(
        summary.get("scan_dirs", args.paths or [])))
    LOGGER.info("Loaded %s files, %s cases", summary.get(
        "files", 0), summary.get("cases", 0))

    if args.open:
        webbrowser.open(browser_url)

    server = make_server(args.host, args.port, app, threaded=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        LOGGER.info("Stopping Casebook")
    finally:
        server.server_close()
    return 0


def main(argv: list[str] | None = None) -> int:
    configure_logging()
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "serve":
        return run_serve(args)
    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
