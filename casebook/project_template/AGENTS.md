# Casebook Agent Instructions

## Test Case Generation

When generating, extending, reviewing, or validating Casebook YAML test cases, read and follow:

`./.agents/skills/casebook-test-cases/SKILL.md`

Use that skill as the source of truth for how to understand requirements, design test scenarios, write cases like a tester, and produce YAML files that work with Casebook.

## Test Process Records

When generating or updating Markdown test process records, test execution logs, release review notes, or evidence-based QA summaries from Casebook data, read and follow:

`./.agents/skills/casebook-test-process-record/SKILL.md`

Use that skill to combine requirements, YAML cases, `test-runs/*.json`, screenshots, defects, notes, and the user's requested template or output format. Do not fabricate execution evidence.

## Project Inputs

- Read requirements and product notes from `docs/`.
- Read schema constraints from `schema/test-case-schema.json`.
- Inspect existing test cases under `releases/` before creating or updating YAML.
- Read execution data from `test-runs/` when producing process records or release review material.

## Output Rules

- Write real test cases under `releases/`.
- Write generated test process records under `docs/test-logs/` unless the user specifies another path.
- Keep `releases/example/` for scaffold examples only.
- Do not invent YAML fields outside `schema/test-case-schema.json`.
- Preserve existing case IDs unless the user explicitly asks to rename or delete them.

## Local Review

Use `casebook serve releases` to browse, review, mark, and edit generated cases locally.
