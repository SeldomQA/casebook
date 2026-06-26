---
name: casebook-test-cases
description: Generate, extend, and review Casebook YAML test cases from product requirements, PRDs, API notes, UI specs, or issue descriptions. Use when converting requirements in docs/ into structured files under releases/, updating existing YAML cases, checking coverage, or validating output against schema/test-case-schema.json.
---

# Casebook Test Case Skill

Use this skill to turn requirements into structured YAML test cases that can be viewed and edited with Casebook.

## Inputs

- Read requirement material from `docs/` first. Treat Markdown, text notes, copied PRD sections, API descriptions, UI behavior notes, and screenshots converted to text as requirement sources.
- Read `schema/test-case-schema.json` before writing cases. The schema is the source of truth for required fields, allowed enum values, and extra-field restrictions.
- Inspect existing files under `releases/` before adding cases. Reuse the local naming style, metadata style, tags, and ID prefix where possible.
- If updating an existing feature, preserve existing case IDs unless the user explicitly asks to rename or delete them.

## Output Location

- Write generated test cases under `releases/`.
- Use one YAML file per focused feature or feature slice.
- Prefer paths like `releases/<version-or-module>/<feature>.yaml`.
- Keep `releases/example/` for scaffold examples only. Do not put real project cases under `example`.

## Required YAML Shape

Each YAML file must contain exactly these top-level sections:

```yaml
metadata:
  module: "Module name"
  feature: "Feature name"
  owner: "owner"
  last_reviewed: "YYYY-MM-DD"
  tags: [tag1, tag2]

test_cases:
  - id: "TC_FEATURE_001"
    title: "Verify a clear behavior"
    description: "Explain the scenario or risk being covered."
    priority: "P0"
    type: "functional"
    preconditions:
      - Required starting state
    steps:
      - Perform one business action
    expected_results:
      - Observable system result
    tags: [smoke]
    auto: false
```

Allowed case fields are `id`, `title`, `description`, `priority`, `type`, `preconditions`, `steps`, `expected_results`, `tags`, and `auto`. Do not invent extra fields.

Allowed `priority` values are `P0`, `P1`, and `P2`.

Allowed `type` values are `functional`, `ui`, `security`, `performance`, `accessibility`, `business`, `other`, and `data-consistency`.

## Requirement Reading Workflow

1. Identify the feature boundary: module, feature, actors, entry points, and affected pages or APIs.
2. Extract explicit rules: inputs, outputs, validation rules, state transitions, permissions, limits, async jobs, error messages, data persistence, and side effects.
3. Infer implicit risks a tester would check: missing permissions, duplicate submissions, stale data, boundary values, partial failure, concurrency, retry behavior, fallback behavior, and compatibility with existing states.
4. Separate confirmed requirements from assumptions. Cover confirmed behavior in cases. Only add assumption-based cases when they are high-risk and label them with a clear description.
5. Prefer user-visible or contract-visible assertions. Expected results should be observable through UI, API response, database/state change, emitted event, file output, audit log, or downstream side effect.

## Scenario Design Rules

- Cover the main happy path first.
- Add negative paths for invalid input, missing required fields, permission denial, unsupported state, duplicate records, and exceeded limits.
- Add boundary cases for numeric limits, string lengths, pagination sizes, date ranges, list counts, and enum values.
- Add state-transition cases when behavior depends on status, workflow stage, previous operations, or async progress.
- Add data-consistency cases when one action must refresh lists, details, counts, history, cache, search index, or related records.
- Add security cases for authorization, tenant isolation, sensitive data exposure, and destructive actions.
- Add performance cases only when the requirement includes volume, latency, export/import size, batch operation, or large-user behavior.
- Add accessibility or UI cases when the requirement explicitly changes layout, interaction, keyboard flow, copy, empty states, disabled states, or error presentation.

## Writing Style

- Write like a test engineer, not like a product summary.
- Use concise Chinese unless the requirement or product copy is in English.
- Make `title` action-oriented and specific, usually within 20 Chinese characters when possible.
- Keep each `step` to one business action. Do not describe implementation details such as JavaScript, component internals, or CSS selectors unless the requirement is technical.
- Make each `expected_results` item independently verifiable. Avoid vague results like "works correctly" or "login succeeds" without visible or contractual evidence.
- Put setup data in `preconditions`, not in the first step.
- Use `description` to record why this case matters, especially for risk, edge, compatibility, or inferred behavior.
- Use tags for searchable concepts such as `smoke`, `negative`, `permission`, `boundary`, `async`, `export`, `api`, `ui`, `data-consistency`, or domain terms from the requirement.

## ID Rules

- Use format `TC_<FEATURE_PREFIX>_<NNN>`, for example `TC_LOGIN_001`.
- Use a short uppercase English feature prefix for `{FEATURE_PREFIX}`. Use only uppercase letters, numbers, and underscores.
- Use exactly three digits for the numeric suffix. Pad with leading zeros, such as `001`, `018`, or `120`.
- Keep IDs globally unique across `releases/`.
- When extending an existing file, continue from the highest existing numeric suffix.
- When creating a new file, choose a short feature prefix from the module and feature name.

## Priority Rules

- Use `P0` for core business flows, money/data/security risks, destructive operations, authentication/authorization, or cases that block release.
- Use `P1` for important daily workflows, common negative paths, important validation, and state consistency.
- Use `P2` for rare edge cases, copy/layout details, compatibility checks, and lower-risk exploratory coverage.

## Automation Flag

- Set `auto: true` when the case is stable, deterministic, and can be checked by API, unit, integration, or reliable UI automation.
- Set `auto: false` for visual judgment, complex third-party dependency, one-off exploratory behavior, unstable async timing, or cases that need manual review.

## Generation Process

1. Read the relevant requirement files in `docs/`.
2. Read the schema and existing release YAML files.
3. Build a short coverage map mentally: happy path, negative path, boundary, permission, state, data consistency, and non-functional risk.
4. Create or update the YAML file under `releases/`.
5. Preserve comments, field order, inline list style, and existing formatting when editing existing YAML.
6. Validate the generated YAML against `schema/test-case-schema.json` when a validator is available.
7. Review the result for duplicate IDs, vague expected results, missing required fields, invalid enum values, and cases that are too broad.

## Quality Checklist

Before finishing, ensure:

- Every file has `metadata` and `test_cases`.
- Every case has `id`, `title`, `priority`, `type`, `steps`, and `expected_results`.
- No case contains fields outside the schema.
- Every `steps` and `expected_results` list has at least one non-empty item.
- IDs are unique and match `^TC_[A-Z0-9_]{3,}_[0-9]{3}$`.
- Expected results include concrete UI/API/data assertions.
- The generated set covers both expected behavior and meaningful risks.
- The cases are useful in Casebook without needing the original requirement open beside them.
