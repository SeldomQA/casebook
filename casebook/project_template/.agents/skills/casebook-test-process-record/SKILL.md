---
name: casebook-test-process-record
description: Generate or update flexible Markdown test process records, test execution logs, release review notes, or evidence-based QA summaries from Casebook requirements in docs/, YAML cases in releases/, execution data in test-runs/*.json, screenshots under test-runs/screenshots/, and user-provided output templates.
---

# Casebook Test Process Record Skill

Use this skill to turn Casebook execution evidence into a human-readable test process record. The goal is not to force one fixed template; the goal is to help the user produce a useful document for release review, process archiving, or knowledge sharing.

## Core Principle

Casebook stores facts. AI writes the document.

- Use `docs/requirements/` for requirement intent and business context.
- Use `releases/` YAML files for designed test scenarios.
- Use `test-runs/<run-id>.json` for recorded execution results.
- Use `test-runs/screenshots/<run-id>/` for image evidence.
- Use the user's requested template or output example as the target shape.

Do not invent evidence. If a needed detail is absent from the sources, mark it as `待补充` or state that it is not recorded.

## Input Discovery

When the user asks for a test process record, identify these inputs:

1. Requirement source: specific files under `docs/requirements/`, broader docs under `docs/`, or product notes named by the user.
2. Case source: YAML files or directories under `releases/`.
3. Execution source: one or more `test-runs/*.json` files.
4. Evidence source: screenshot metadata in the run JSON and files under `test-runs/screenshots/<run-id>/`.
5. Output format: a named template, an existing document to imitate, or a free-form request such as "上线评审记录" or "L2 测试过程记录".
6. Output path: usually `docs/test-logs/<feature-or-run>-test-process-record.md`, unless the user specifies another path.

If a required input is missing and cannot be inferred, ask a concise clarification. If multiple likely files exist, prefer the newest relevant run file and mention the assumption.

## Reading Workflow

1. Read the requested template or example first, if provided.
2. Read requirement files enough to understand business background, core logic, risk, and acceptance criteria.
3. Read the run JSON completely. Pay attention to:
   - `run.name`, `run.mode`, `run.scope`, `run.case_scope`, `run.environment`, `run.tester`, `run.started_at`, `run.completed_at`
   - `results[*].status`
   - `results[*].actual_result`
   - `results[*].notes`
   - `results[*].defects`
   - `results[*].screenshots`
4. Resolve each result key in the form `path/to/file.yaml#TC_ID` to the matching YAML case.
5. Read matching YAML cases for title, description, preconditions, steps, expected results, priority, type, tags, and automation flag.
6. Inspect screenshot names and paths. Open images only when the user asks for visual interpretation or when the document needs a screenshot description that cannot be inferred from metadata.

## Writing Rules

- Write in Chinese unless the user asks otherwise or the source template is in another language.
- Adapt the output structure to the user's target format. Do not hard-code a single L1/L2 layout.
- Preserve the user's headings and ordering when a template is provided.
- Separate facts from interpretation:
  - Facts: recorded status, actual result, notes, defects, screenshots, timestamps, test case steps.
  - Interpretation: risk analysis, release recommendation, summary of remaining issues.
- Highlight `failed`, `blocked`, `deferred`, and `untested` cases. Do not bury them inside long tables.
- Keep passed cases concise unless they contain important evidence, screenshots, SQL, API payloads, or business-critical checks.
- Include defect links exactly as recorded. Do not fabricate Jira IDs or bug URLs.
- Link screenshots using project-relative Markdown links when possible.
- When evidence is missing, use `待补充` instead of inventing SQL, API payloads, logs, tester names, environments, or conclusions.

## Suggested Output Sections

Use these sections only when they fit the user's requested format:

- 需求说明：业务背景、核心逻辑、关联需求文档。
- 测试范围：本次覆盖的模块、功能、接口、页面或数据链路。
- 测试准备：环境、账号、配置、数据准备、日志入口、接口调用方式。
- 执行概览：总数、通过、失败、阻塞、延期、未执行。
- 测试过程：按模块、用例文件、业务场景或执行阶段组织。
- 关键证据：实际结果、截图、SQL/API/日志、前后数据对比。
- 缺陷与风险：失败、阻塞、延期、未执行项及影响分析。
- 测试结论：上线建议、遗留风险、需要产品/开发确认的点。

## Evidence Checklist

Before finishing, verify:

- The document references the requirement files used.
- The document references the run file used.
- Status counts match the run JSON, or any filtering is clearly stated.
- Failed, blocked, deferred, and untested cases are visible.
- Actual results, notes, defects, and screenshots from the run JSON are not dropped.
- Missing data is marked as `待补充` rather than guessed.
- The output path is the one requested by the user.

## Example User Prompt

```text
请生成一份测试过程记录。

需求文档：
docs/requirements/login.md

测试用例：
releases/auth/

执行结果：
test-runs/run-20260714093000-login.json

截图证据：
test-runs/screenshots/run-20260714093000-login/

输出格式参考：
docs/templates/l2-test-process-record.md

输出到：
docs/test-logs/login-test-process-record.md
```
