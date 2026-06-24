# Casebook Agent Instructions

## Test Case Generation

When generating, extending, reviewing, or validating Casebook YAML test cases, read and follow:

`./.agents/skills/casebook-test-cases/SKILL.md`

Use that skill as the source of truth for how to understand requirements, design test scenarios, write cases like a tester, and produce YAML files that work with Casebook.

## Project Inputs

- Read requirements and product notes from `docs/`.
- Read schema constraints from `schema/test-case-schema.json`.
- Inspect existing test cases under `releases/` before creating or updating YAML.

## Output Rules

- Write real test cases under `releases/`.
- Keep `releases/example/` for scaffold examples only.
- Do not invent YAML fields outside `schema/test-case-schema.json`.
- Preserve existing case IDs unless the user explicitly asks to rename or delete them.

## Local Review

Use `casebook serve releases` to browse, review, mark, and edit generated cases locally.
