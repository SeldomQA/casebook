# Casebook

Casebook is a local web tool for browsing, reviewing, marking, and editing YAML test cases.

It is designed for test case repositories where cases are stored as structured YAML files. It starts a lightweight Flask web interface, renders a practical tool-style workspace, and writes edits back to the original YAML files while preserving comments and formatting as much as possible.

## Features

- Browse YAML test case directories in a local web UI.
- View per-file statistics, priorities, tags, and case metadata.
- Edit cases from a right-side drawer and save changes directly to YAML.
- Preserve YAML comments, field order, indentation, and inline list style where possible with `ruamel.yaml`.
- Mark cases as **Needs Update**.
- Store marks in `.casebook/marks.json` under the project root.
- Watch YAML files while running and notify the browser when data changes.
- Use JSON APIs behind a Jinja2-rendered page shell.

## Installation

From this repository while Casebook is kept as a nested project:

```bash
pip install -e ./casebook
```

After installation, the `casebook` command is available:

```bash
casebook --help
```

## Usage

Start Casebook against a YAML test case directory:

```bash
casebook serve releases/V5-UserBackend
```

Use a custom port:

```bash
casebook serve releases/V5-UserBackend --port 8089
```

Open the browser automatically:

```bash
casebook serve releases/V5-UserBackend --open
```

Disable filesystem watching:

```bash
casebook serve releases/V5-UserBackend --no-watch
```

The default port is `8089`.

## YAML Format

Casebook expects YAML files with this general shape:

```yaml
metadata:
  module: User Backend
  feature: Package management
  owner: QA
  last_reviewed: "2026-06-23"
  tags:
    - v5
    - packages

test_cases:
  - id: TC_EXAMPLE_001
    title: Create a package successfully
    description: Verify the happy path.
    priority: P0
    type: functional
    preconditions:
      - User is logged in
    steps:
      - Open package page
      - Submit valid package data
    expected_results:
      - Package is created
    tags:
      - smoke
    auto: false
```

## Editing Behavior

Casebook edits the original YAML file directly.

To keep diffs clean, it uses `ruamel.yaml` round-trip loading and dumping. This means comments, field order, block style, inline arrays, and indentation are preserved as much as the YAML library can safely preserve them.

When a field does not already exist, Casebook inserts it in a predictable order. Empty missing fields are not added just because a case was opened and saved.

## Project State

Marks are stored outside the YAML files:

```text
.casebook/marks.json
```

The mark format is intentionally simple for the first version:

```json
{
  "releases/example.yaml#TC_EXAMPLE_001": {
    "needs_update": true,
    "updated_at": "2026-06-23T02:00:00+00:00"
  }
}
```

## Development

Install Casebook from this nested project, then run it from the root of a YAML test case repository:

```bash
pip install -e ./casebook
casebook serve releases/V5-UserBackend
```

When running from inside a test case repository, paths are resolved relative to the current working directory.
