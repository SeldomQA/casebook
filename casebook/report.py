from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from html import escape
from pathlib import Path
from typing import Any

from .scanner import CasebookStore


EXECUTION_STATUS_LABELS = {
    "passed": "Passed",
    "failed": "Failed",
    "blocked": "Blocked",
    "deferred": "Deferred",
    "untested": "Untested",
}

EXECUTION_STATUS_COLORS = {
    "passed": "#27b36a",
    "failed": "#e74c3c",
    "blocked": "#f5b400",
    "deferred": "#7c3aed",
    "untested": "#cfd4dc",
}


class ReportError(Exception):
    """Raised when a test report cannot be generated from a run file."""

    pass


@dataclass(frozen=True)
class CaseRecord:
    """Flattened case definition plus execution result for report rendering."""

    key: str
    file_path: str
    case_id: str
    title: str
    priority: str
    case_type: str
    status: str
    notes: str
    actual_result: str
    defects: list[str]
    screenshots: list[dict[str, Any]]
    executed_at: str


def generate_report(
    run_file: Path,
    output_file: Path | None = None,
    project_root: Path | None = None,
) -> Path:
    """Generate and write an HTML report for one test run JSON file."""
    run_path = run_file.expanduser().resolve()
    if not run_path.exists() or not run_path.is_file():
        raise ReportError(f"Run file not found: {run_file}")

    root = (project_root.expanduser().resolve()
            if project_root else _infer_project_root(run_path))
    run_data = _load_run_data(run_path)
    report_data = build_report_data(run_data, root)
    html = render_report_html(report_data)

    target = output_file.expanduser().resolve(
    ) if output_file else run_path.with_suffix(".html")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(html, encoding="utf-8")
    return target


def build_report_data(run_data: dict[str, Any], project_root: Path) -> dict[str, Any]:
    """Merge run JSON with current YAML case definitions for report rendering."""
    run = run_data.get("run") or {}
    if not isinstance(run, dict):
        raise ReportError("Invalid run file: missing run object")

    results = run_data.get("results") or {}
    if not isinstance(results, dict):
        results = {}

    scope = _normalize_scope(run.get("scope"))
    case_scope = _normalize_case_scope(run.get("case_scope"))
    case_records = _collect_case_records(project_root, scope, results, case_scope)
    stats = _build_stats(case_records)
    failed_cases = [
        record for record in case_records if record.status == "failed"]
    blocked_cases = [
        record for record in case_records if record.status == "blocked"]

    return {
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "project_root": project_root.as_posix(),
        "run": {
            "id": str(run.get("id") or ""),
            "name": str(run.get("name") or run.get("id") or "Test Plan"),
            "status": str(run.get("status") or ""),
            "mode": str(run.get("mode") or "full"),
            "source_run_id": str(run.get("source_run_id") or ""),
            "case_total": len(case_scope) if case_scope is not None else len(case_records),
            "scope": scope,
            "environment": str(run.get("environment") or ""),
            "tester": str(run.get("tester") or ""),
            "started_at": str(run.get("started_at") or ""),
            "completed_at": str(run.get("completed_at") or run.get("updated_at") or ""),
        },
        "stats": stats,
        "cases": case_records,
        "failed_cases": failed_cases,
        "blocked_cases": blocked_cases,
        "chart_data": _chart_data(stats, failed_cases, blocked_cases),
    }


def render_report_html(data: dict[str, Any]) -> str:
    """Render a standalone HTML report string."""
    run = data["run"]
    stats = data["stats"]
    failed_cases = data["failed_cases"]
    blocked_cases = data["blocked_cases"]
    chart_data = json.dumps(
        data["chart_data"], ensure_ascii=False).replace("</", "<\\/")
    title = f"Casebook Test Report - {run['name']}"
    total = stats["total"] or 0
    completion_rate = (stats["executed"] / total * 100) if total else 0
    pass_rate = (stats["passed"] / total * 100) if total else 0
    issue_total = stats["failed"] + stats["blocked"]
    priority_rows = data["chart_data"]["priority"]
    p0_issues = next((row["value"] for row in priority_rows if row["label"] == "P0"), 0)
    scope_text = ", ".join(run["scope"]) or "N/A"
    status_label = _run_status_label(run.get("status")) or "In Progress"
    attention_class = " clear" if issue_total == 0 else ""
    attention_text = (
        f"No failed or blocked cases are currently open. Current pass rate is {pass_rate:.0f}%."
        if issue_total == 0
        else f"{issue_total} failed or blocked cases require attention; {p0_issues} are P0 priority. Current pass rate is {pass_rate:.0f}%."
    )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{_html(title)}</title>
  <script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
  <style>
    :root {{
      --blue: #0876dd;
      --card: #ffffff;
      --text: #2b2f36;
      --muted: #8a93a3;
      --line: #dfe5ee;
      --passed: {EXECUTION_STATUS_COLORS["passed"]};
      --failed: {EXECUTION_STATUS_COLORS["failed"]};
      --blocked: {EXECUTION_STATUS_COLORS["blocked"]};
      --deferred: {EXECUTION_STATUS_COLORS["deferred"]};
      --untested: {EXECUTION_STATUS_COLORS["untested"]};
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--blue);
      color: var(--text);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
    }}
    .page {{ max-width: 1440px; margin: 0 auto; padding: 28px 28px 44px; }}
    .title {{ margin: 0 0 26px; color: #fff; font-size: 34px; font-weight: 900; text-align: center; }}
    .meta {{ margin: -14px 0 24px; color: rgba(255,255,255,.82); text-align: center; font-size: 14px; }}
    .card {{
      border: 1px solid rgba(13, 71, 161, .24);
      border-radius: 6px;
      background: var(--card);
      box-shadow: 0 2px 6px rgba(0,0,0,.12);
    }}
    .section-title {{ margin: 0; padding: 28px 36px 8px; font-size: 28px; font-weight: 900; }}
    .plan-card {{ margin-bottom: 28px; padding-bottom: 22px; }}
    .overview {{ margin-bottom: 34px; padding-bottom: 22px; }}
    .stats-grid {{
      display: grid;
      grid-template-columns: repeat(6, minmax(120px, 1fr));
      gap: 0;
      padding: 34px 16px 0;
    }}
    .stat {{ min-height: 132px; display: grid; place-items: center; text-align: center; border-left: 1px solid var(--line); }}
    .stat:first-child {{ border-left: 0; }}
    .stat strong {{ display: block; font-size: 46px; line-height: 1; font-weight: 900; }}
    .stat small {{ display: block; margin-top: 26px; color: var(--muted); font-size: 21px; font-weight: 700; }}
    .stat.failed strong, .stat.blocked strong {{ color: #cf3328; }}
    .plan-info {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 20px 36px;
      padding: 28px 36px 8px;
    }}
    .plan-info-item {{
      display: grid;
      grid-template-columns: 120px minmax(0, 1fr);
      gap: 18px;
      align-items: baseline;
      min-width: 0;
    }}
    .plan-info-item span {{
      display: block;
      color: var(--text);
      font-size: 16px;
      font-weight: 900;
    }}
    .plan-info-item strong {{
      display: block;
      min-width: 0;
      overflow-wrap: anywhere;
      color: #4a5565;
      font-size: 16px;
      font-weight: 700;
      line-height: 1.4;
    }}
    .chart-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 34px; margin-bottom: 34px; }}
    .chart-card {{ min-height: 460px; padding-bottom: 26px; }}
    .chart-body {{ display: grid; grid-template-columns: minmax(280px, 1fr) minmax(230px, 300px); gap: 22px; align-items: center; padding: 20px 34px; }}
    .chart {{ width: 100%; min-height: 300px; }}
    .legend {{ display: grid; gap: 18px; font-size: 20px; }}
    .legend-row {{ display: grid; grid-template-columns: 14px 1fr auto auto; gap: 12px; align-items: baseline; }}
    .dot {{ width: 12px; height: 12px; border-radius: 50%; }}
    .legend-row strong {{ font-size: 22px; min-width: 32px; text-align: right; }}
    .legend-row code {{ color: var(--text); font-family: inherit; font-size: 20px; min-width: 78px; text-align: right; }}
    .tables {{ display: grid; gap: 28px; }}
    .table-card {{ overflow: hidden; }}
    .table-header {{ display: flex; align-items: center; justify-content: space-between; gap: 16px; padding: 24px 30px; border-bottom: 1px solid var(--line); }}
    .table-header h2 {{ margin: 0; font-size: 24px; }}
    .table-header span {{ color: var(--muted); font-weight: 800; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th, td {{ padding: 14px 18px; border-bottom: 1px solid #edf1f6; text-align: left; vertical-align: top; }}
    th {{ color: #6b7483; background: #f8fafc; font-size: 13px; text-transform: uppercase; letter-spacing: .06em; }}
    td {{ font-size: 14px; line-height: 1.5; }}
    .case-id {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-weight: 800; color: #0759b8; }}
    .priority {{ display: inline-block; border-radius: 4px; padding: 2px 7px; font-weight: 900; }}
    .priority-p0 {{ color: #c62920; background: #ffe5e2; }}
    .priority-p1 {{ color: #996900; background: #fff1cc; }}
    .priority-p2 {{ color: #007c82; background: #dff8fa; }}
    .notes {{ max-width: 360px; white-space: pre-wrap; color: #394253; }}
    .actual-result {{ max-width: 360px; white-space: pre-wrap; color: #394253; }}
    .defects {{ max-width: 280px; color: #394253; }}
    .defects a {{ color: #0759b8; font-weight: 800; text-decoration: none; word-break: break-all; }}
    .defects a:hover {{ text-decoration: underline; }}
    .screenshots {{ max-width: 240px; color: #394253; }}
    .empty {{ padding: 26px 30px; color: var(--muted); font-weight: 700; }}
    @media (max-width: 980px) {{
      .stats-grid {{ grid-template-columns: repeat(2, minmax(120px, 1fr)); }}
      .stat:nth-child(odd) {{ border-left: 0; }}
      .plan-info {{ grid-template-columns: 1fr; }}
      .plan-info-item {{ grid-template-columns: 104px minmax(0, 1fr); }}
      .chart-grid {{ grid-template-columns: 1fr; }}
      .chart-body {{ grid-template-columns: 1fr; }}
      .page {{ padding: 20px 14px 34px; }}
    }}

    /* Brief-style report layout. */
    :root {{
      --blue: #347ff0;
      --blue-dark: #1858b7;
      --blue-soft: #edf5ff;
      --page: #f3f7fc;
      --text: #29486f;
      --muted: #8195af;
      --line: #dce7f3;
      --line-soft: #eaf0f7;
    }}
    html {{ background: var(--page); }}
    body {{
      background: radial-gradient(circle at 84% 3%, rgba(77,145,244,.13), transparent 22rem), var(--page);
      color: var(--text);
    }}
    .page {{ max-width: 1240px; padding: 28px 24px 52px; }}
    .card {{
      border: 1px solid var(--line);
      border-radius: 14px;
      box-shadow: 0 6px 22px rgba(36,73,121,.07);
    }}
    .hero {{
      position: relative;
      display: grid;
      grid-template-columns: minmax(0,1fr) auto;
      gap: 28px;
      align-items: center;
      overflow: hidden;
      min-height: 238px;
      margin-bottom: 18px;
      padding: 34px 42px;
      border: 1px solid #d4e4f8;
      border-radius: 18px;
      background: linear-gradient(135deg,#fff 0%,#edf5ff 100%);
      box-shadow: 0 10px 30px rgba(36,73,121,.08);
    }}
    .hero::after {{
      content: "";
      position: absolute;
      top: -110px;
      right: 70px;
      width: 290px;
      height: 290px;
      border: 1px solid rgba(52,127,240,.16);
      border-radius: 50%;
      box-shadow: 0 0 0 34px rgba(52,127,240,.035),0 0 0 70px rgba(52,127,240,.025);
    }}
    .hero-copy {{ position: relative; z-index: 1; min-width: 0; }}
    .brand {{ margin: 0 0 7px; color: #5e84b4; font-size: 12px; font-weight: 900; letter-spacing: .16em; text-transform: uppercase; }}
    .title {{ margin: 0; color: #2365bd; font-size: clamp(34px,5vw,58px); font-weight: 900; letter-spacing: -.045em; line-height: 1; text-align: left; }}
    .subtitle {{ max-width: 720px; margin: 16px 0 20px; color: #6982a1; font-size: 15px; line-height: 1.7; }}
    .hero-meta {{ display: flex; flex-wrap: wrap; gap: 8px; }}
    .meta-pill {{ border: 1px solid #d6e4f6; border-radius: 999px; background: rgba(255,255,255,.8); color: #577391; font-size: 12px; font-weight: 750; padding: 6px 10px; }}
    .health-ring {{
      --completion: {completion_rate:.2f}%;
      position: relative;
      z-index: 1;
      display: grid;
      place-items: center;
      width: 142px;
      height: 142px;
      border-radius: 50%;
      background: conic-gradient(var(--blue) var(--completion),#e7eef7 0);
      box-shadow: 0 10px 26px rgba(47,114,232,.16);
    }}
    .health-ring::before {{ content: ""; position: absolute; inset: 12px; border-radius: 50%; background: #fff; }}
    .health-ring div {{ position: relative; text-align: center; }}
    .health-ring strong {{ display: block; color: var(--blue); font-size: 34px; line-height: 1; }}
    .health-ring span {{ display: block; margin-top: 6px; color: var(--muted); font-size: 11px; font-weight: 800; text-transform: uppercase; }}
    .attention {{ display: flex; align-items: center; gap: 12px; margin-bottom: 18px; padding: 13px 18px; border: 1px solid #ffd5d5; border-radius: 12px; background: #fff6f6; color: #9d4242; font-size: 13px; font-weight: 750; }}
    .attention-dot {{ flex: 0 0 9px; width: 9px; height: 9px; border-radius: 50%; background: var(--failed); box-shadow: 0 0 0 5px rgba(231,76,60,.09); }}
    .attention.clear {{ border-color: #ccebdc; background: #f3fcf7; color: #2d7d59; }}
    .attention.clear .attention-dot {{ background: var(--passed); box-shadow: 0 0 0 5px rgba(39,179,106,.09); }}
    .section {{ margin-top: 18px; }}
    .section-heading {{ display: flex; align-items: flex-end; justify-content: space-between; gap: 18px; margin: 0 2px 10px; }}
    .section-heading h2 {{ margin: 0; color: #29486f; font-size: 19px; font-weight: 900; }}
    .section-heading p {{ margin: 4px 0 0; color: var(--muted); font-size: 12px; }}
    .section-heading > span {{ color: var(--muted); font-size: 12px; font-weight: 800; }}
    .section-title {{ margin: 0; padding: 20px 22px 4px; color: #29486f; font-size: 17px; font-weight: 900; }}
    .plan-card {{ margin: 0; padding-bottom: 18px; }}
    .plan-info {{ grid-template-columns: repeat(4,minmax(0,1fr)); gap: 0; padding: 12px 20px 2px; }}
    .plan-info-item {{ display: block; min-width: 0; border-left: 1px solid var(--line-soft); padding: 10px 14px; }}
    .plan-info-item:nth-child(4n+1) {{ border-left: 0; }}
    .plan-info-item span {{ margin-bottom: 6px; color: #91a2b7; font-size: 9px; letter-spacing: .1em; text-transform: uppercase; }}
    .plan-info-item strong {{ color: #29486f; font-size: 12px; font-weight: 800; }}
    .stats-grid {{ grid-template-columns: repeat(7,minmax(100px,1fr)); gap: 10px; padding: 16px; }}
    .stat {{ min-height: 92px; display: flex; align-items: center; border: 1px solid var(--line); border-radius: 10px; background: #f8fbff; padding: 15px; text-align: left; }}
    .stat strong {{ color: var(--blue); font-size: 27px; }}
    .stat small {{ margin-top: 8px; color: var(--muted); font-size: 11px; }}
    .stat.failed {{ border-color: #ffd1d4; background: #fff4f5; }}
    .stat.blocked {{ border-color: #ffe0ae; background: #fff9ef; }}
    .stat.passed {{ border-color: #c9ebdc; background: #f1fbf6; }}
    .stat.deferred {{ border-color: #dcd0ff; background: #f7f3ff; }}
    .stat.untested {{ border-color: #dce4ee; background: #f4f7fb; }}
    .stat.failed strong {{ color: var(--failed); }}
    .stat.blocked strong {{ color: #ee9b28; }}
    .stat.passed strong {{ color: var(--passed); }}
    .stat.deferred strong {{ color: var(--deferred); }}
    .stat.untested strong {{ color: #7087a3; }}
    .insight-grid,.focus-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}
    .focus-card {{ overflow: hidden; }}
    .focus-list {{ display: grid; gap: 8px; padding: 12px; }}
    .focus-item {{ display: grid; grid-template-columns: auto minmax(0,1fr) auto; gap: 10px; align-items: start; border: 1px solid var(--line-soft); border-radius: 9px; background: #fbfdff; padding: 11px 12px; }}
    .focus-item.failed {{ border-color: #ffd9dc; background: #fff8f8; }}
    .focus-item.blocked {{ border-color: #ffe3b8; background: #fffbf3; }}
    .focus-copy {{ min-width: 0; }}
    .focus-copy strong {{ display: block; overflow: hidden; color: #29486f; font-size: 12px; text-overflow: ellipsis; white-space: nowrap; }}
    .focus-copy p {{ margin: 4px 0 0; color: var(--muted); font-size: 10px; line-height: 1.45; }}
    .status-pill {{ border-radius: 5px; font-size: 9px; font-weight: 900; padding: 3px 7px; text-transform: uppercase; }}
    .status-pill.failed {{ background: #ffe8ea; color: var(--failed); }}
    .status-pill.blocked {{ background: #fff0d6; color: #dc8b17; }}
    .chart-card {{ min-height: 330px; padding-bottom: 14px; }}
    .chart-body {{ grid-template-columns: minmax(180px,1fr) minmax(170px,220px); gap: 12px; padding: 4px 18px 16px; }}
    .chart {{ min-height: 245px; }}
    .legend {{ gap: 10px; font-size: 12px; }}
    .legend-row {{ grid-template-columns: 9px 1fr auto auto; gap: 8px; color: #607995; }}
    .dot {{ width: 8px; height: 8px; }}
    .legend-row strong {{ color: #29486f; font-size: 13px; min-width: 24px; }}
    .legend-row code {{ color: var(--muted); font-size: 11px; min-width: 48px; }}
    .tables {{ gap: 16px; }}
    .table-card {{ overflow: hidden; }}
    .table-scroll {{ overflow-x: auto; }}
    .table-header {{ padding: 16px 20px; }}
    .table-header h2 {{ color: #29486f; font-size: 15px; }}
    .table-header span {{ border-radius: 999px; background: var(--blue-soft); color: var(--blue); font-size: 11px; padding: 4px 9px; }}
    table {{ min-width: 980px; }}
    th,td {{ padding: 11px 13px; border-bottom-color: var(--line-soft); }}
    th {{ color: #8da0b8; background: #f7faff; font-size: 9px; }}
    td {{ color: #59718e; font-size: 11px; }}
    tbody tr:hover {{ background: #fbfdff; }}
    .case-id {{ border-radius: 5px; background: var(--blue-soft); color: #3377dc; font-size: 10px; line-height: 1.35; padding: 3px 6px; white-space: nowrap; }}
    .priority {{ min-width: 30px; border-radius: 5px; text-align: center; }}
    .notes,.actual-result {{ min-width: 170px; max-width: 300px; color: #59718e; }}
    .defects {{ min-width: 100px; max-width: 220px; color: #59718e; }}
    .screenshots {{ min-width: 110px; max-width: 200px; color: #59718e; }}
    .empty {{ padding: 22px 20px; font-size: 12px; }}
    .execution-list-card {{ overflow: hidden; }}
    .execution-list-head,.execution-summary {{ display: grid; grid-template-columns: 28px minmax(130px,170px) minmax(280px,1fr) 76px 104px; gap: 12px; align-items: start; }}
    .execution-list-head {{ border-bottom: 1px solid var(--line); background: #f7faff; color: #8da0b8; font-size: 9px; font-weight: 900; letter-spacing: .08em; padding: 10px 16px; text-transform: uppercase; }}
    .execution-case {{ border-bottom: 1px solid var(--line-soft); background: #fff; }}
    .execution-case:last-child {{ border-bottom: 0; }}
    .execution-summary {{ min-height: 60px; padding: 12px 16px; }}
    .execution-toggle {{ position: relative; width: 22px; height: 22px; border: 0; border-radius: 5px; background: transparent; color: #7890ac; cursor: pointer; }}
    .execution-toggle::before {{ content: "›"; position: absolute; inset: 0; display: grid; place-items: center; font-size: 18px; font-weight: 900; transition: transform .16s ease; }}
    .execution-toggle[aria-expanded="true"]::before {{ transform: rotate(90deg); }}
    .execution-title {{ min-width: 0; }}
    .execution-title strong {{ display: block; color: #29486f; font-size: 12px; line-height: 1.4; }}
    .execution-title small {{ display: block; overflow: hidden; margin-top: 4px; color: var(--muted); font-size: 10px; text-overflow: ellipsis; white-space: nowrap; }}
    .result-pill {{ display: inline-flex; align-items: center; justify-content: center; min-width: 72px; border-radius: 6px; font-size: 10px; font-weight: 900; padding: 5px 9px; text-transform: capitalize; }}
    .execution-summary .priority {{ min-width: 28px; border: 1px solid transparent; border-radius: 5px; font-size: 9px; font-weight: 800; line-height: 1.2; padding: 3px 6px; }}
    .execution-summary .priority-p0 {{ border-color: #f4dada; background: #fff5f5; color: #d46a6a; }}
    .execution-summary .priority-p1 {{ border-color: #eee3c8; background: #fffaf0; color: #aa8750; }}
    .execution-summary .priority-p2 {{ border-color: #d4e8e9; background: #f3fbfb; color: #5d999c; }}
    .execution-summary .result-pill {{ min-width: 84px; font-size: 11px; padding: 6px 10px; }}
    .result-passed {{ background: #eaf9f2; color: var(--passed); }}
    .result-failed {{ background: #fff0f1; color: var(--failed); }}
    .result-blocked {{ background: #fff6e8; color: #df8d18; }}
    .result-deferred {{ background: #f3edff; color: var(--deferred); }}
    .result-untested {{ background: #eef2f7; color: #7087a3; }}
    .execution-detail {{ display: grid; grid-template-columns: repeat(3,minmax(0,1fr)); gap: 14px; border-top: 1px solid var(--line-soft); background: #f8fbff; padding: 14px 16px 16px 56px; }}
    .execution-detail[hidden] {{ display: none; }}
    .detail-item {{ min-width: 0; }}
    .detail-item.wide {{ grid-column: 1 / -1; }}
    .detail-item span {{ display: block; margin-bottom: 5px; color: #91a2b7; font-size: 9px; font-weight: 900; letter-spacing: .08em; text-transform: uppercase; }}
    .detail-item strong {{ display: block; overflow-wrap: anywhere; color: #526b89; font-size: 11px; font-weight: 650; line-height: 1.55; white-space: pre-wrap; }}
    .footer {{ display: flex; align-items: center; justify-content: space-between; gap: 20px; margin-top: 24px; padding: 15px 18px; border: 1px solid var(--line); border-radius: 12px; background: #fff; color: var(--muted); font-size: 10px; box-shadow: 0 4px 16px rgba(36,73,121,.05); }}
    .footer strong {{ color: #29486f; font-size: 12px; }}
    @media (max-width:980px) {{
      .hero {{ padding: 28px; }}
      .stats-grid {{ grid-template-columns: repeat(4,minmax(100px,1fr)); }}
      .plan-info {{ grid-template-columns: repeat(2,minmax(0,1fr)); }}
      .plan-info-item:nth-child(4n+1) {{ border-left: 1px solid var(--line-soft); }}
      .plan-info-item:nth-child(2n+1) {{ border-left: 0; }}
      .insight-grid,.focus-grid {{ grid-template-columns: 1fr; }}
      .execution-list-head,.execution-summary {{ grid-template-columns: 28px minmax(120px,150px) minmax(220px,1fr) 68px 92px; gap: 9px; }}
      .execution-detail {{ grid-template-columns: repeat(2,minmax(0,1fr)); }}
    }}
    @media (max-width:640px) {{
      .hero {{ grid-template-columns: 1fr; padding: 24px 20px; }}
      .health-ring {{ width: 118px; height: 118px; }}
      .stats-grid {{ grid-template-columns: repeat(2,minmax(100px,1fr)); }}
      .plan-info {{ grid-template-columns: 1fr; }}
      .plan-info-item {{ border-left: 0 !important; }}
      .section-heading,.footer {{ align-items: flex-start; flex-direction: column; gap: 4px; }}
      .execution-list-head,.execution-summary {{ grid-template-columns: 24px minmax(0,1fr) 84px; }}
      .execution-list-head > :nth-child(2),.execution-summary > :nth-child(2) {{ display: none; }}
      .execution-list-head > :nth-child(4),.execution-summary > :nth-child(4) {{ display: none; }}
      .execution-detail {{ grid-template-columns: 1fr; padding-left: 50px; }}
      .detail-item.wide {{ grid-column: 1; }}
    }}
  </style>
</head>
<body>
  <main class="page">
    <header class="hero">
      <div class="hero-copy">
        <p class="brand">Casebook · Test Quality Brief</p>
        <h1 class="title">Test Execution Brief</h1>
        <p class="subtitle">A concise view of execution health, delivery risk, unresolved cases, and detailed evidence for <strong>{_html(run["name"])}</strong>.</p>
        <div class="hero-meta">
          <span class="meta-pill">{_html(status_label)}</span>
          <span class="meta-pill">{_html(_run_mode_label(run["mode"]))}</span>
          <span class="meta-pill">Scope: {_html(scope_text)}</span>
          <span class="meta-pill">Generated: {_html(data["generated_at"])}</span>
        </div>
      </div>
      <div class="health-ring"><div><strong>{completion_rate:.0f}%</strong><span>Executed</span></div></div>
    </header>

    <div class="attention{attention_class}">
      <span class="attention-dot"></span>
      <span>{_html(attention_text)}</span>
    </div>

    <section class="section">
      <div class="section-heading">
        <div><h2>Plan Overview</h2><p>Execution identity, ownership, scope, and timing.</p></div>
      </div>
      <div class="card plan-card">{_plan_info(run)}</div>
    </section>

    <section class="section">
      <div class="section-heading">
        <div><h2>Execution Summary</h2><p>Current result totals across the selected plan scope.</p></div>
        <span>{stats["executed"]} of {stats["total"]} executed</span>
      </div>
      <div class="card stats-grid">
        {_stat("Total Cases", stats["total"], "total")}
        {_stat("Executed", stats["executed"], "executed")}
        {_stat("Passed", stats["passed"], "passed")}
        {_stat("Failed", stats["failed"], "failed")}
        {_stat("Blocked", stats["blocked"], "blocked")}
        {_stat("Deferred", stats["deferred"], "deferred")}
        {_stat("Untested", stats["untested"], "untested")}
      </div>
    </section>

    <section class="section">
      <div class="section-heading">
        <div><h2>Quality Signals</h2><p>Result distribution and priority concentration for unresolved risk.</p></div>
      </div>
      <div class="insight-grid">
        <div class="card chart-card">
          <h3 class="section-title">Execution Distribution</h3>
          <div class="chart-body">
            <div class="chart" id="executionChart"></div>
            {_legend(data["chart_data"]["execution"])}
          </div>
        </div>
        <div class="card chart-card">
          <h3 class="section-title">Failed / Blocked Priority</h3>
          <div class="chart-body">
            <div class="chart" id="priorityChart"></div>
            {_legend(data["chart_data"]["priority"])}
          </div>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="section-heading">
        <div><h2>Attention Required</h2><p>Cases most likely to affect release confidence.</p></div>
        <span>{issue_total} cases</span>
      </div>
      <div class="focus-grid">
        {_focus_list("Failed Cases", failed_cases, "failed")}
        {_focus_list("Blocked Cases", blocked_cases, "blocked")}
      </div>
    </section>

    <section class="section">
      <div class="section-heading">
        <div><h2>Execution Details</h2><p>Expand a case to review its execution evidence.</p></div>
        <span>{len(data["cases"])} cases</span>
      </div>
      <div class="tables">{_execution_details(data["cases"])}</div>
    </section>

    <footer class="footer"><strong>Casebook</strong><span>{_html(run["name"])} · {_html(scope_text)}</span><span>Generated {_html(data["generated_at"])}</span></footer>
  </main>
  <script>
    const reportData = {chart_data};
    const hasEcharts = typeof echarts !== "undefined";
    function renderDonut(id, rows, centerText) {{
      if (!hasEcharts) return;
      const node = document.getElementById(id);
      const chart = echarts.init(node);
      chart.setOption({{
        color: rows.map((row) => row.color),
        tooltip: {{ trigger: "item" }},
        title: {{
          text: centerText.value,
          subtext: centerText.label,
          left: "center",
          top: "center",
          textStyle: {{ fontSize: 28, fontWeight: 900, color: "#29486f" }},
          subtextStyle: {{ fontSize: 12, color: "#8195af" }}
        }},
        series: [{{
          type: "pie",
          radius: ["58%", "78%"],
          avoidLabelOverlap: true,
          label: {{ show: false }},
          emphasis: {{ label: {{ show: false }} }},
          data: rows.map((row) => ({{ name: row.label, value: row.value }}))
        }}]
      }});
      window.addEventListener("resize", () => chart.resize());
    }}
    renderDonut("executionChart", reportData.execution, {{
      value: reportData.passRateText,
      label: "Pass Rate"
    }});
    renderDonut("priorityChart", reportData.priority, {{
      value: String(reportData.issueTotal),
      label: "Issues"
    }});
    document.addEventListener("click", (event) => {{
      const button = event.target.closest("[data-detail-toggle]");
      if (!button) return;
      const detail = document.getElementById(button.dataset.detailToggle);
      if (!detail) return;
      const expanded = button.getAttribute("aria-expanded") === "true";
      button.setAttribute("aria-expanded", String(!expanded));
      detail.hidden = expanded;
      button.closest(".execution-case").classList.toggle("expanded", !expanded);
    }});
  </script>
</body>
</html>
"""


def _collect_case_records(
    project_root: Path,
    scope: list[str],
    results: dict[str, Any],
    case_scope: list[str] | None = None,
) -> list[CaseRecord]:
    """Collect report records, including historical results for missing YAML cases."""
    store = CasebookStore(project_root=project_root, scan_dirs=scope or None)
    store.refresh()

    records: list[CaseRecord] = []
    seen_keys: set[str] = set()
    case_scope_set = set(case_scope) if case_scope is not None else None
    for file_meta in store.list_files():
        entry = store.get_file(file_meta["path"])
        if not entry:
            continue
        for case in entry["cases"]:
            key = f"{entry['path']}#{case['id']}"
            if case_scope_set is not None and key not in case_scope_set:
                continue
            seen_keys.add(key)
            result = results.get(key) if isinstance(
                results.get(key), dict) else {}
            records.append(_record_from_case(entry["path"], case, key, result))

    for key, result in results.items():
        if case_scope_set is not None and key not in case_scope_set:
            continue
        if key in seen_keys or not isinstance(result, dict):
            continue
        file_path, case_id = _split_result_key(str(key))
        records.append(_record_from_case(
            file_path=file_path,
            case={
                "id": case_id,
                "title": case_id or "Unknown case",
                "priority": "P2",
                "type": "unknown",
            },
            key=str(key),
            result=result,
        ))

    records.sort(key=lambda record: (record.file_path, record.case_id))
    return records


def _record_from_case(
    file_path: str,
    case: dict[str, Any],
    key: str,
    result: dict[str, Any],
) -> CaseRecord:
    """Build one report row from a normalized case and result object."""
    status = _normalize_status(result.get("status"))
    return CaseRecord(
        key=key,
        file_path=file_path,
        case_id=str(case.get("id") or ""),
        title=str(case.get("title") or ""),
        priority=str(case.get("priority") or "P2").upper(),
        case_type=str(case.get("type") or ""),
        status=status,
        notes=str(result.get("notes") or ""),
        actual_result=str(result.get("actual_result") or ""),
        defects=_normalize_defects(result.get("defects")),
        screenshots=_normalize_screenshots(result.get("screenshots")),
        executed_at=str(result.get("executed_at") or ""),
    )


def _build_stats(records: list[CaseRecord]) -> dict[str, int]:
    """Count execution statuses for the overview section."""
    stats = {
        "total": len(records),
        "executed": 0,
        "passed": 0,
        "failed": 0,
        "blocked": 0,
        "deferred": 0,
        "untested": 0,
    }
    for record in records:
        stats[record.status] += 1
        if record.status != "untested":
            stats["executed"] += 1
    return stats


def _chart_data(
    stats: dict[str, int],
    failed_cases: list[CaseRecord],
    blocked_cases: list[CaseRecord],
) -> dict[str, Any]:
    """Prepare ECharts-friendly data without leaking presentation logic upward."""
    total = stats["total"] or 0
    pass_rate = (stats["passed"] / total * 100) if total else 0
    priority_counts = {"P0": 0, "P1": 0, "P2": 0}
    for record in [*failed_cases, *blocked_cases]:
        priority = record.priority if record.priority in priority_counts else "P2"
        priority_counts[priority] += 1

    return {
        "passRateText": f"{pass_rate:.0f}%",
        "issueTotal": len(failed_cases) + len(blocked_cases),
        "execution": [
            _chart_row("Passed", stats["passed"],
                       EXECUTION_STATUS_COLORS["passed"], total),
            _chart_row("Failed", stats["failed"],
                       EXECUTION_STATUS_COLORS["failed"], total),
            _chart_row("Blocked", stats["blocked"],
                       EXECUTION_STATUS_COLORS["blocked"], total),
            _chart_row("Deferred", stats["deferred"],
                       EXECUTION_STATUS_COLORS["deferred"], total),
            _chart_row("Untested", stats["untested"],
                       EXECUTION_STATUS_COLORS["untested"], total),
        ],
        "priority": [
            _chart_row("P0", priority_counts["P0"], "#e74c3c", max(
                sum(priority_counts.values()), 1)),
            _chart_row("P1", priority_counts["P1"], "#f5b400", max(
                sum(priority_counts.values()), 1)),
            _chart_row("P2", priority_counts["P2"], "#46c7d4", max(
                sum(priority_counts.values()), 1)),
        ],
    }


def _chart_row(label: str, value: int, color: str, total: int) -> dict[str, Any]:
    """Build one chart legend row with a preformatted percentage."""
    percent = (value / total * 100) if total else 0
    return {
        "label": label,
        "value": value,
        "percent": f"{percent:.2f}%",
        "color": color,
    }


def _case_table(title: str, records: list[CaseRecord]) -> str:
    """Render a failure or blocked-case section."""
    rows = "\n".join(_case_row(record) for record in records)
    body = rows if rows else '<div class="empty">No records</div>'
    return f"""
      <div class="card table-card">
        <div class="table-header">
          <h2>{_html(title)}</h2>
          <span>{len(records)} cases</span>
        </div>
        {f'<div class="table-scroll"><table><thead><tr><th>Case</th><th>Title</th><th>Priority</th><th>File</th><th>Notes</th><th>Actual Result</th><th>Defects</th><th>Screenshots</th><th>Executed At</th></tr></thead><tbody>{rows}</tbody></table></div>' if rows else body}
      </div>
    """


def _focus_list(title: str, records: list[CaseRecord], status: str) -> str:
    """Render a compact brief-style list for failed or blocked cases."""
    if records:
        items = "\n".join(
            f"""
            <div class="focus-item {_html(status)}">
              <span class="case-id">{_html(record.case_id)}</span>
              <div class="focus-copy">
                <strong>{_html(record.title)}</strong>
                <p>{_html(record.notes or record.actual_result or record.file_path)}</p>
              </div>
              <span class="status-pill {_html(status)}">{_html(status)}</span>
            </div>
            """
            for record in records
        )
    else:
        items = '<div class="empty">No records</div>'
    return f"""
      <div class="card focus-card">
        <div class="table-header">
          <h2>{_html(title)}</h2>
          <span>{len(records)} cases</span>
        </div>
        <div class="focus-list">{items}</div>
      </div>
    """


def _execution_details(records: list[CaseRecord]) -> str:
    """Render collapsible execution rows matching the interactive case list."""
    rows = "\n".join(
        _execution_detail_row(record, index)
        for index, record in enumerate(records)
    )
    body = rows if rows else '<div class="empty">No records</div>'
    return f"""
      <div class="card execution-list-card">
        <div class="table-header">
          <h2>All Test Cases</h2>
          <span>{len(records)} cases</span>
        </div>
        <div class="execution-list-head" aria-hidden="true">
          <span></span><span>Case</span><span>Title</span><span>Priority</span><span>Result</span>
        </div>
        <div class="execution-list">{body}</div>
      </div>
    """


def _execution_detail_row(record: CaseRecord, index: int) -> str:
    """Render one collapsed execution summary plus its hidden evidence panel."""
    detail_id = f"execution-detail-{index}"
    priority_class = f"priority-{_html(record.priority.lower())}"
    status = record.status if record.status in EXECUTION_STATUS_LABELS else "untested"
    status_label = EXECUTION_STATUS_LABELS.get(status, status.title())
    return f"""
      <article class="execution-case">
        <div class="execution-summary">
          <button class="execution-toggle" type="button" data-detail-toggle="{detail_id}"
            aria-expanded="false" aria-controls="{detail_id}" aria-label="Expand execution details"></button>
          <span class="case-id">{_html(record.case_id)}</span>
          <div class="execution-title">
            <strong>{_html(record.title)}</strong>
            <small>{_html(record.case_type or "Test case")}</small>
          </div>
          <span><span class="priority {priority_class}">{_html(record.priority)}</span></span>
          <span><span class="result-pill result-{_html(status)}">{_html(status_label)}</span></span>
        </div>
        <div class="execution-detail" id="{detail_id}" hidden>
          {_detail_item("File", _html(record.file_path), True)}
          {_detail_item("Notes", _html(record.notes or "--"))}
          {_detail_item("Actual Result", _html(record.actual_result or "--"))}
          {_detail_item("Defects", _defects_html(record.defects))}
          {_detail_item("Screenshots", _screenshots_text(record.screenshots))}
          {_detail_item("Executed At", _html(record.executed_at or "--"))}
        </div>
      </article>
    """


def _detail_item(label: str, value_html: str, wide: bool = False) -> str:
    """Render one evidence field inside an expanded execution row."""
    return f"""
      <div class="detail-item{' wide' if wide else ''}">
        <span>{_html(label)}</span>
        <strong>{value_html}</strong>
      </div>
    """


def _case_row(record: CaseRecord) -> str:
    """Render one report table row."""
    priority_class = f"priority-{_html(record.priority.lower())}"
    return f"""
      <tr>
        <td><span class="case-id">{_html(record.case_id)}</span></td>
        <td>{_html(record.title)}</td>
        <td><span class="priority {priority_class}">{_html(record.priority)}</span></td>
        <td>{_html(record.file_path)}</td>
        <td class="notes">{_html(record.notes or "-")}</td>
        <td class="actual-result">{_html(record.actual_result or "-")}</td>
        <td class="defects">{_defects_html(record.defects)}</td>
        <td class="screenshots">{_screenshots_text(record.screenshots)}</td>
        <td>{_html(record.executed_at or "-")}</td>
      </tr>
    """


def _normalize_defects(value: Any) -> list[str]:
    """Accept legacy string/list defect fields and return clean links or IDs."""
    if isinstance(value, list):
        items = value
    elif isinstance(value, str):
        items = value.replace(",", "\n").splitlines()
    else:
        items = []
    return [str(item).strip() for item in items if str(item).strip()]


def _normalize_screenshots(value: Any) -> list[dict[str, Any]]:
    """Accept screenshot metadata from run JSON."""
    if not isinstance(value, list):
        return []
    screenshots: list[dict[str, Any]] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        screenshot_id = str(item.get("id") or "").strip()
        if screenshot_id:
            screenshots.append(item)
    return screenshots


def _defects_html(defects: list[str]) -> str:
    """Render defect IDs and links with safe escaping."""
    if not defects:
        return "-"
    items = []
    for defect in defects:
        if defect.startswith(("http://", "https://")):
            items.append(
                f'<a href="{_html(defect)}" target="_blank" rel="noopener noreferrer">{_html(defect)}</a>')
        else:
            items.append(_html(defect))
    return "<br>".join(items)


def _screenshots_text(screenshots: list[dict[str, Any]]) -> str:
    """Render screenshot names without assuming report-relative image paths."""
    if not screenshots:
        return "-"
    return "<br>".join(
        _html(str(item.get("name") or item.get("stored_name") or item.get("id") or "Screenshot"))
        for item in screenshots
    )


def _legend(rows: list[dict[str, Any]]) -> str:
    """Render a chart legend used next to each donut chart."""
    items = "\n".join(
        f"""
        <div class="legend-row">
          <span class="dot" style="background:{_html(row['color'])}"></span>
          <span>{_html(row['label'])}</span>
          <strong>{row['value']}</strong>
          <code>{_html(row['percent'])}</code>
        </div>
        """
        for row in rows
    )
    return f'<div class="legend">{items}</div>'


def _stat(label: str, value: int, class_name: str) -> str:
    """Render one top-level statistic tile."""
    return f"""
      <div class="stat {_html(class_name)}">
        <div>
          <strong>{value}</strong>
          <small>{_html(label)}</small>
        </div>
      </div>
    """


def _plan_info(run: dict[str, Any]) -> str:
    """Render the test plan metadata block above the statistics."""
    fields = [
        ("Plan ID", run.get("id")),
        ("Plan Name", run.get("name")),
        ("Status", _run_status_label(run.get("status"))),
        ("Mode", _run_mode_label(run.get("mode"))),
        ("Source Plan", run.get("source_run_id")),
        ("Case Scope", run.get("case_total")),
        ("Scope", ", ".join(run.get("scope") or [])),
        ("Environment", run.get("environment")),
        ("Tester", run.get("tester")),
        ("Started At", run.get("started_at")),
        ("Completed At", run.get("completed_at")),
    ]
    items = "\n".join(
        f"""
        <div class="plan-info-item">
          <span>{_html(label)}</span>
          <strong>{_html(_display_value(value))}</strong>
        </div>
        """
        for label, value in fields
    )
    return f'<div class="plan-info">{items}</div>'


def _load_run_data(run_path: Path) -> dict[str, Any]:
    """Load run JSON and fail with report-specific errors."""
    try:
        data = json.loads(run_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ReportError(f"Invalid run JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ReportError("Invalid run file: expected a JSON object")
    return data


def _infer_project_root(run_path: Path) -> Path:
    """Infer project root from test-runs/<run>.json when not provided."""
    if run_path.parent.name == "test-runs":
        return run_path.parent.parent.resolve()
    return Path.cwd().resolve()


def _normalize_scope(scope: Any) -> list[str]:
    """Normalize a run scope for CasebookStore scanning."""
    if not isinstance(scope, list):
        return []
    return [str(item).strip().rstrip("/\\") for item in scope if str(item).strip()]


def _normalize_case_scope(case_scope: Any) -> list[str] | None:
    """Return None for legacy reports that should include all scanned cases."""
    if not isinstance(case_scope, list):
        return None
    return [str(item or "").strip() for item in case_scope if str(item or "").strip()]


def _normalize_status(status: Any) -> str:
    """Map unknown or missing execution statuses to untested."""
    value = str(status or "").strip().lower()
    return value if value in {"passed", "failed", "blocked", "deferred"} else "untested"


def _split_result_key(key: str) -> tuple[str, str]:
    """Split canonical file#case keys while tolerating legacy bare IDs."""
    if "#" not in key:
        return "", key
    file_path, case_id = key.rsplit("#", 1)
    return file_path, case_id


def _html(value: Any) -> str:
    """Escape dynamic HTML content."""
    return escape(str(value), quote=True)


def _display_value(value: Any) -> str:
    """Display empty metadata consistently."""
    text = str(value or "").strip()
    return text if text else "--"


def _run_status_label(value: Any) -> str:
    """Convert stored run status codes into report labels."""
    labels = {
        "in_progress": "In Progress",
        "completed": "Completed",
        "done": "Completed",
        "closed": "Closed",
        "cancelled": "Cancelled",
        "canceled": "Cancelled",
    }
    text = str(value or "").strip()
    return labels.get(text.lower(), text)


def _run_mode_label(value: Any) -> str:
    """Convert stored run mode codes into report labels."""
    labels = {
        "full": "Full run",
        "retest_unresolved": "Retest failed/blocked/deferred",
    }
    text = str(value or "full").strip()
    return labels.get(text.lower(), text)
