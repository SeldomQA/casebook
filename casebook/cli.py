from __future__ import annotations

import sys
import webbrowser
from pathlib import Path
from typing import Annotated

import typer
from loguru import logger

from . import __version__


CASEBOOK_BANNER = r"""
   ______                 __                __
  / ____/___ _________   / /_  ____  ____  / /__
 / /   / __ `/ ___/ _ \ / __ \/ __ \/ __ \/ //_/
/ /___/ /_/ (__  )  __// /_/ / /_/ / /_/ / ,<
\____/\__,_/____/\___//_.___/\____/\____/_/|_|
"""

app = typer.Typer(
    help="Render, review, and edit YAML test cases locally.",
    no_args_is_help=True,
    add_completion=False,
)


def configure_logging() -> None:
    logger.remove()
    logger.add(
        sys.stderr,
        level="INFO",
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level:<8}</level> | <cyan>casebook</cyan> - <level>{message}</level>",
    )


def version_callback(value: bool) -> None:
    if value:
        typer.echo(f"casebook {__version__}")
        raise typer.Exit()


def _shorten_banner_value(value: object, max_length: int = 72) -> str:
    text = str(value or "").strip()
    if len(text) <= max_length:
        return text
    return f"{text[:max_length - 3]}..."


def _serve_banner(
    url: str,
    scan_dirs: list[str],
    files: object,
    cases: object,
    watch: bool,
) -> str:
    rows = [
        ("Version", f"v{__version__}"),
        ("Local UI", url),
        ("Scope", _shorten_banner_value(", ".join(scan_dirs) or ".")),
        ("Loaded", f"{files or 0} files, {cases or 0} cases"),
        ("Watch", "enabled" if watch else "disabled"),
        ("Stop", "Press Ctrl+C"),
    ]
    width = max(len(f"{label}: {value}") for label, value in rows)
    box_width = width + ((width + 1) // 2)
    line = f"+-{'-' * box_width}-+"
    body = "\n".join(
        f"| {label}: {value}{' ' * (box_width - len(f'{label}: {value}'))} |"
        for label, value in rows
    )
    return f"{CASEBOOK_BANNER}\n{line}\n{body}\n{line}"


@app.callback()
def root(
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            help="Show the Casebook version and exit.",
            callback=version_callback,
            is_eager=True,
        ),
    ] = False,
) -> None:
    configure_logging()


def serve_project(
    paths: list[str],
    host: str = "127.0.0.1",
    port: int = 8089,
    open_browser: bool = False,
    watch: bool = True,
) -> None:
    from werkzeug.serving import WSGIRequestHandler, make_server

    from .app import create_app

    class LoguruRequestHandler(WSGIRequestHandler):
        def log(self, type: str, message: str, *args: object) -> None:
            level = type.upper()
            if level not in {"TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"}:
                level = "INFO"
            address = self.address_string().replace("%", "%%")
            logger.log(level, "{} - - [{}] {}", address,
                       self.log_date_time_string(), message % args)

    project_root = Path.cwd()
    flask_app = create_app(project_root=project_root,
                           scan_dirs=paths, watch=watch)
    summary = flask_app.config.get("CASEBOOK_INITIAL_SUMMARY", {})
    url = f"http://{host}:{port}"
    browser_url = f"http://localhost:{port}" if host in {
        "127.0.0.1", "::"} else url
    scan_dirs = summary.get("scan_dirs", paths or [])

    typer.echo(_serve_banner(
        url=url,
        scan_dirs=scan_dirs,
        files=summary.get("files", 0),
        cases=summary.get("cases", 0),
        watch=watch,
    ))

    if open_browser:
        webbrowser.open(browser_url)

    server = make_server(host, port, flask_app, threaded=True,
                         request_handler=LoguruRequestHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Stopping Casebook")
    finally:
        server.server_close()


@app.command(help="Start the local Casebook web UI.")
def serve(
    paths: Annotated[
        list[str] | None,
        typer.Argument(
            help="YAML case directories relative to the current project root.",
        ),
    ] = None,
    host: Annotated[
        str,
        typer.Option("--host", help="Host to bind."),
    ] = "127.0.0.1",
    port: Annotated[
        int,
        typer.Option("--port", "-p", help="Port to bind."),
    ] = 8089,
    open_browser: Annotated[
        bool,
        typer.Option("--open", "-o", help="Open the web UI in a browser."),
    ] = False,
    no_watch: Annotated[
        bool,
        typer.Option("--no-watch", help="Disable filesystem auto-refresh."),
    ] = False,
) -> None:
    serve_project(
        paths=paths or [],
        host=host,
        port=port,
        open_browser=open_browser,
        watch=not no_watch,
    )


def initialize_project(project: str, force: bool = False) -> None:
    from .initializer import ProjectInitError, init_project

    try:
        result = init_project(project, force=force)
    except ProjectInitError as exc:
        typer.echo(f"casebook init: {exc}", err=True)
        raise typer.Exit(1) from exc

    typer.echo(f"Initialized Casebook project at {result.project_root}")
    if result.created:
        typer.echo("\nCreated:")
        for path in result.created:
            typer.echo(f"  {path.as_posix()}")
    if result.skipped:
        typer.echo("\nSkipped existing files:")
        for path in result.skipped:
            typer.echo(f"  {path.as_posix()}")
        typer.echo("\nUse --force to overwrite scaffold files.")
    typer.echo("\nNext steps:")
    typer.echo(f"  cd {result.project_root}")
    typer.echo("  casebook serve releases")


@app.command(help="Create a new Casebook test case project.")
def init(
    project: Annotated[
        str,
        typer.Argument(help="Project directory to create or initialize."),
    ],
    force: Annotated[
        bool,
        typer.Option("--force", help="Overwrite existing scaffold files."),
    ] = False,
) -> None:
    initialize_project(project, force=force)


@app.command(help="Generate an HTML test report from a test run JSON file.")
def report(
    run_file: Annotated[
        Path,
        typer.Argument(
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            help="Path to a test-runs/*.json file.",
        ),
    ],
    output: Annotated[
        Path | None,
        typer.Option("--output", "-o",
                     help="Output HTML path. Defaults to <run-file>.html."),
    ] = None,
    project_root: Annotated[
        Path | None,
        typer.Option(
            "--project-root", help="Project root. Defaults to the parent of test-runs/ or cwd."),
    ] = None,
) -> None:
    from .report import ReportError, generate_report

    try:
        target = generate_report(
            run_file, output_file=output, project_root=project_root)
    except ReportError as exc:
        typer.echo(f"casebook report: {exc}", err=True)
        raise typer.Exit(1) from exc
    typer.echo(f"Generated report: {target}")


@app.command(help="Renumber test case IDs in one YAML file.")
def renumber(
    yaml_file: Annotated[
        Path,
        typer.Argument(
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            help="YAML test case file to renumber.",
        ),
    ],
) -> None:
    from .renumber import CaseIdRenumberError, CaseIdRenumberer

    try:
        result = CaseIdRenumberer(Path.cwd()).renumber_file(str(yaml_file))
    except FileNotFoundError:
        typer.echo(f"casebook renumber: file not found: {yaml_file}", err=True)
        raise typer.Exit(1) from None
    except CaseIdRenumberError as exc:
        typer.echo(f"casebook renumber: {exc}", err=True)
        raise typer.Exit(1) from exc

    typer.echo(
        f"Renumbered {result['file_path']}: "
        f"{result['changed']}/{result['total']} IDs changed."
    )
    for item in result["mapping"]:
        if item["changed"]:
            typer.echo(f"  {item['old_id']} -> {item['new_id']}")


def main(argv: list[str] | None = None) -> None:
    app(args=argv)


if __name__ == "__main__":
    main()
