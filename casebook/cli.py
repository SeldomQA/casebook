from __future__ import annotations

import logging
import webbrowser
from pathlib import Path
from typing import Annotated

import typer

from . import __version__


LOGGER = logging.getLogger("casebook.main")

app = typer.Typer(
    help="Render, review, and edit YAML test cases locally.",
    no_args_is_help=True,
    add_completion=False,
)


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s/%(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def version_callback(value: bool) -> None:
    if value:
        typer.echo(f"casebook {__version__}")
        raise typer.Exit()


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
    from werkzeug.serving import make_server

    from .app import create_app

    project_root = Path.cwd()
    flask_app = create_app(project_root=project_root, scan_dirs=paths, watch=watch)
    summary = flask_app.config.get("CASEBOOK_INITIAL_SUMMARY", {})
    url = f"http://{host}:{port}"
    browser_url = f"http://localhost:{port}" if host in {
        "127.0.0.1", "::"} else url

    LOGGER.info("Starting web interface at %s", url)
    LOGGER.info("Starting Casebook %s", __version__)
    LOGGER.info("Watching YAML cases in %s", ", ".join(
        summary.get("scan_dirs", paths or [])))
    LOGGER.info("Loaded %s files, %s cases", summary.get(
        "files", 0), summary.get("cases", 0))

    if open_browser:
        webbrowser.open(browser_url)

    server = make_server(host, port, flask_app, threaded=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        LOGGER.info("Stopping Casebook")
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
        typer.Option("--output", "-o", help="Output HTML path. Defaults to <run-file>.html."),
    ] = None,
    project_root: Annotated[
        Path | None,
        typer.Option("--project-root", help="Project root. Defaults to the parent of test-runs/ or cwd."),
    ] = None,
) -> None:
    from .report import ReportError, generate_report

    try:
        target = generate_report(run_file, output_file=output, project_root=project_root)
    except ReportError as exc:
        typer.echo(f"casebook report: {exc}", err=True)
        raise typer.Exit(1) from exc
    typer.echo(f"Generated report: {target}")


def main(argv: list[str] | None = None) -> None:
    app(args=argv)


if __name__ == "__main__":
    main()
