from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from html import escape
from pathlib import Path
from typing import Any

from .scanner import CasebookStore


EXECUTION_STATUS_LABELS = {
    "passed": "已通过",
    "failed": "未通过",
    "blocked": "阻塞",
    "untested": "待测试",
}

EXECUTION_STATUS_COLORS = {
    "passed": "#27b36a",
    "failed": "#e74c3c",
    "blocked": "#f5b400",
    "untested": "#cfd4dc",
}


class ReportError(Exception):
    pass


@dataclass(frozen=True)
class CaseRecord:
    key: str
    file_path: str
    case_id: str
    title: str
    priority: str
    case_type: str
    status: str
    notes: str
    defects: list[str]
    executed_at: str


def generate_report(
    run_file: Path,
    output_file: Path | None = None,
    project_root: Path | None = None,
) -> Path:
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
    run = run_data.get("run") or {}
    if not isinstance(run, dict):
        raise ReportError("Invalid run file: missing run object")

    results = run_data.get("results") or {}
    if not isinstance(results, dict):
        results = {}

    scope = _normalize_scope(run.get("scope"))
    case_records = _collect_case_records(project_root, scope, results)
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
    run = data["run"]
    stats = data["stats"]
    failed_cases = data["failed_cases"]
    blocked_cases = data["blocked_cases"]
    chart_data = json.dumps(
        data["chart_data"], ensure_ascii=False).replace("</", "<\\/")
    title = f"Casebook 测试报告 - {run['name']}"

    return f"""<!doctype html>
<html lang="zh-CN">
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
    .defects {{ max-width: 280px; color: #394253; }}
    .defects a {{ color: #0759b8; font-weight: 800; text-decoration: none; word-break: break-all; }}
    .defects a:hover {{ text-decoration: underline; }}
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
  </style>
</head>
<body>
  <main class="page">
    <h1 class="title">测试报告</h1>
    <p class="meta">{_html(run["name"])} · Scope: {_html(", ".join(run["scope"]) or "N/A")} · Generated: {_html(data["generated_at"])}</p>
    <section class="card plan-card">
      <h2 class="section-title">计划信息</h2>
      {_plan_info(run)}
    </section>
    <section class="card overview">
      <h2 class="section-title">统计信息</h2>
      <div class="stats-grid">
        {_stat("用例总数量", stats["total"], "")}
        {_stat("已执行", stats["executed"], "")}
        {_stat("已通过", stats["passed"], "")}
        {_stat("失败总数", stats["failed"], "failed")}
        {_stat("阻塞总数", stats["blocked"], "blocked")}
        {_stat("待测试", stats["untested"], "")}
      </div>
    </section>
    <section class="chart-grid">
      <div class="card chart-card">
        <h2 class="section-title">测试统计</h2>
        <div class="chart-body">
          <div class="chart" id="executionChart"></div>
          {_legend(data["chart_data"]["execution"])}
        </div>
      </div>
      <div class="card chart-card">
        <h2 class="section-title">失败/阻塞优先级</h2>
        <div class="chart-body">
          <div class="chart" id="priorityChart"></div>
          {_legend(data["chart_data"]["priority"])}
        </div>
      </div>
    </section>
    <section class="tables">
      {_case_table("失败用例", failed_cases)}
      {_case_table("阻塞用例", blocked_cases)}
    </section>
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
          textStyle: {{ fontSize: 38, fontWeight: 900, color: "#2b2f36" }},
          subtextStyle: {{ fontSize: 18, color: "#777" }}
        }},
        series: [{{
          type: "pie",
          radius: ["55%", "78%"],
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
      label: "通过率"
    }});
    renderDonut("priorityChart", reportData.priority, {{
      value: String(reportData.issueTotal),
      label: "问题数"
    }});
  </script>
</body>
</html>
"""


def _collect_case_records(
    project_root: Path,
    scope: list[str],
    results: dict[str, Any],
) -> list[CaseRecord]:
    store = CasebookStore(project_root=project_root, scan_dirs=scope or None)
    store.refresh()

    records: list[CaseRecord] = []
    seen_keys: set[str] = set()
    for file_meta in store.list_files():
        entry = store.get_file(file_meta["path"])
        if not entry:
            continue
        for case in entry["cases"]:
            key = f"{entry['path']}#{case['id']}"
            seen_keys.add(key)
            result = results.get(key) if isinstance(
                results.get(key), dict) else {}
            records.append(_record_from_case(entry["path"], case, key, result))

    for key, result in results.items():
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
        defects=_normalize_defects(result.get("defects")),
        executed_at=str(result.get("executed_at") or ""),
    )


def _build_stats(records: list[CaseRecord]) -> dict[str, int]:
    stats = {
        "total": len(records),
        "executed": 0,
        "passed": 0,
        "failed": 0,
        "blocked": 0,
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
            _chart_row("已通过", stats["passed"],
                       EXECUTION_STATUS_COLORS["passed"], total),
            _chart_row("未通过", stats["failed"],
                       EXECUTION_STATUS_COLORS["failed"], total),
            _chart_row("阻塞", stats["blocked"],
                       EXECUTION_STATUS_COLORS["blocked"], total),
            _chart_row("待测试", stats["untested"],
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
    percent = (value / total * 100) if total else 0
    return {
        "label": label,
        "value": value,
        "percent": f"{percent:.2f}%",
        "color": color,
    }


def _case_table(title: str, records: list[CaseRecord]) -> str:
    rows = "\n".join(_case_row(record) for record in records)
    body = rows if rows else '<div class="empty">暂无记录</div>'
    return f"""
      <div class="card table-card">
        <div class="table-header">
          <h2>{_html(title)}</h2>
          <span>{len(records)} cases</span>
        </div>
        {f'<table><thead><tr><th>Case</th><th>Title</th><th>Priority</th><th>File</th><th>Notes</th><th>Defects</th><th>Executed At</th></tr></thead><tbody>{rows}</tbody></table>' if rows else body}
      </div>
    """


def _case_row(record: CaseRecord) -> str:
    priority_class = f"priority-{_html(record.priority.lower())}"
    return f"""
      <tr>
        <td><span class="case-id">{_html(record.case_id)}</span></td>
        <td>{_html(record.title)}</td>
        <td><span class="priority {priority_class}">{_html(record.priority)}</span></td>
        <td>{_html(record.file_path)}</td>
        <td class="notes">{_html(record.notes or "-")}</td>
        <td class="defects">{_defects_html(record.defects)}</td>
        <td>{_html(record.executed_at or "-")}</td>
      </tr>
    """


def _normalize_defects(value: Any) -> list[str]:
    if isinstance(value, list):
        items = value
    elif isinstance(value, str):
        items = value.replace(",", "\n").splitlines()
    else:
        items = []
    return [str(item).strip() for item in items if str(item).strip()]


def _defects_html(defects: list[str]) -> str:
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


def _legend(rows: list[dict[str, Any]]) -> str:
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
    return f"""
      <div class="stat {_html(class_name)}">
        <div>
          <strong>{value}</strong>
          <small>{_html(label)}</small>
        </div>
      </div>
    """


def _plan_info(run: dict[str, Any]) -> str:
    fields = [
        ("计划ID", run.get("id")),
        ("计划名称", run.get("name")),
        ("计划状态", _run_status_label(run.get("status"))),
        ("作用范围", ", ".join(run.get("scope") or [])),
        ("测试环境", run.get("environment")),
        ("测试人员", run.get("tester")),
        ("开始时间", run.get("started_at")),
        ("完成时间", run.get("completed_at")),
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
    try:
        data = json.loads(run_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ReportError(f"Invalid run JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ReportError("Invalid run file: expected a JSON object")
    return data


def _infer_project_root(run_path: Path) -> Path:
    if run_path.parent.name == "test-runs":
        return run_path.parent.parent.resolve()
    return Path.cwd().resolve()


def _normalize_scope(scope: Any) -> list[str]:
    if not isinstance(scope, list):
        return []
    return [str(item).strip().rstrip("/\\") for item in scope if str(item).strip()]


def _normalize_status(status: Any) -> str:
    value = str(status or "").strip().lower()
    return value if value in {"passed", "failed", "blocked"} else "untested"


def _split_result_key(key: str) -> tuple[str, str]:
    if "#" not in key:
        return "", key
    file_path, case_id = key.rsplit("#", 1)
    return file_path, case_id


def _html(value: Any) -> str:
    return escape(str(value), quote=True)


def _display_value(value: Any) -> str:
    text = str(value or "").strip()
    return text if text else "--"


def _run_status_label(value: Any) -> str:
    labels = {
        "in_progress": "进行中",
        "completed": "已完成",
        "done": "已完成",
        "closed": "已关闭",
        "cancelled": "已取消",
        "canceled": "已取消",
    }
    text = str(value or "").strip()
    return labels.get(text.lower(), text)
