from __future__ import annotations

import json
from datetime import datetime
from html import escape
from pathlib import Path
from typing import Any

from .scanner import CasebookStore, compute_stats, relative_path


class ExportError(Exception):
    pass


def generate_export(
    source: Path,
    output_file: Path | None = None,
    priorities: list[str] | None = None,
    tags: list[str] | None = None,
    project_root: Path | None = None,
) -> Path:
    root = (project_root or Path.cwd()).expanduser().resolve()
    source_path = _resolve_source(root, source)
    priority_filters = _normalize_priorities(priorities or [])
    tag_filters = _normalize_tags(tags or [])
    entries = _collect_entries(root, source_path)
    entries = _filter_entries(entries, priority_filters, tag_filters)
    if not entries:
        raise ExportError("No test cases matched the export filters.")

    data = _build_export_data(root, source_path, entries, priority_filters, tag_filters)
    target = _default_output(source_path, output_file)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_export_html(data), encoding="utf-8")
    return target


def render_export_html(data: dict[str, Any]) -> str:
    export_json = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    title = f"Casebook Export - {data['title']}"
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{_html(title)}</title>
  <style>
    :root {{
      color-scheme: light;
      --canvas: #f2f6fc;
      --surface: #ffffff;
      --surface-soft: #f8fafc;
      --line: #d4dae3;
      --line-soft: #e0e5ec;
      --text: #1f2d41;
      --muted: #69707a;
      --primary: #0061f2;
      --primary-soft: #e0ecff;
      --mark: #7c3aed;
      --mark-soft: #ede9fe;
      --p0: #e81500;
      --p0-soft: #fbe4e0;
      --p1: #f4a100;
      --p1-soft: #fff4dc;
      --p2: #008f94;
      --p2-soft: #dcfbfc;
      --shadow: 0 1px 3px rgba(31,45,65,.12);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--canvas);
      color: var(--text);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      font-size: 14px;
    }}
    button, input, select, textarea {{ font: inherit; }}
    button {{ cursor: pointer; }}
    .app-bar {{
      position: sticky;
      top: 0;
      z-index: 10;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      min-height: 48px;
      padding: 10px 24px;
      background: #212832;
      color: #fff;
      box-shadow: var(--shadow);
    }}
    .brand {{ font-weight: 900; letter-spacing: .08em; }}
    .app-meta {{ color: rgba(255,255,255,.74); font-size: 12px; }}
    .page {{ max-width: 1280px; margin: 0 auto; padding: 22px 18px 48px; }}
    .hero {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 16px;
      align-items: end;
      margin-bottom: 14px;
    }}
    h1 {{ margin: 0; font-size: 28px; line-height: 1.15; }}
    .subtitle {{ margin: 8px 0 0; color: var(--muted); }}
    .stats {{ display: flex; flex-wrap: wrap; gap: 8px; justify-content: flex-end; }}
    .stat {{
      min-width: 88px;
      border: 1px solid var(--stat-line, var(--line));
      border-radius: 4px;
      background: var(--stat-soft, var(--surface));
      color: var(--stat-color, var(--text));
      padding: 8px 10px;
      text-align: center;
      box-shadow: var(--shadow);
    }}
    .stat strong {{ display: block; font-size: 20px; line-height: 1; }}
    .stat span {{ display: block; margin-top: 5px; color: var(--stat-label, var(--muted)); font-size: 11px; font-weight: 800; text-transform: uppercase; }}
    .stat-files {{
      --stat-color: #334155;
      --stat-soft: #f1f5f9;
      --stat-line: #cbd5e1;
      --stat-label: #64748b;
    }}
    .stat-cases {{
      --stat-color: var(--primary);
      --stat-soft: var(--primary-soft);
      --stat-line: #b7d4ff;
      --stat-label: #245ca8;
    }}
    .stat-p0 {{
      --stat-color: var(--p0);
      --stat-soft: var(--p0-soft);
      --stat-line: #f5b7af;
      --stat-label: #b42318;
    }}
    .stat-marked {{
      --stat-color: var(--mark);
      --stat-soft: var(--mark-soft);
      --stat-line: #c4b5fd;
      --stat-label: #6d28d9;
    }}
    .stat-notes {{
      --stat-color: #0f766e;
      --stat-soft: #ccfbf1;
      --stat-line: #99f6e4;
      --stat-label: #0f766e;
    }}
    .toolbar {{
      position: sticky;
      top: 48px;
      z-index: 9;
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;
      margin-bottom: 14px;
      border: 1px solid var(--line);
      border-radius: 4px;
      background: rgba(255,255,255,.96);
      padding: 10px;
      box-shadow: var(--shadow);
      backdrop-filter: blur(8px);
    }}
    .toolbar input, .toolbar select {{
      height: 34px;
      border: 1px solid #bdbdbd;
      border-radius: 4px;
      background: var(--surface);
      color: var(--text);
      padding: 0 10px;
    }}
    .search {{ flex: 1 1 280px; min-width: 220px; }}
    .button {{
      min-height: 34px;
      border: 1px solid var(--line);
      border-radius: 4px;
      background: var(--surface);
      color: var(--primary);
      padding: 5px 10px;
      font-weight: 800;
    }}
    .button.primary {{ border-color: var(--primary); background: var(--primary); color: #fff; }}
    .file-card {{
      margin-top: 14px;
      overflow: hidden;
      border: 1px solid var(--line);
      border-radius: 4px;
      background: var(--surface);
      box-shadow: var(--shadow);
    }}
    .file-header {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 12px;
      padding: 16px 18px;
      border-bottom: 1px solid var(--line-soft);
      background: #fbfcfe;
    }}
    .file-header h2 {{ margin: 0; font-size: 18px; }}
    .file-path {{ margin-top: 5px; color: var(--muted); font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: 12px; overflow-wrap: anywhere; }}
    .file-meta {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px; }}
    .pill {{
      display: inline-flex;
      align-items: center;
      min-height: 24px;
      border-radius: 999px;
      background: var(--surface-soft);
      color: #475569;
      padding: 3px 9px;
      font-size: 12px;
      font-weight: 800;
    }}
    .file-count {{ align-self: start; color: var(--muted); font-weight: 900; }}
    .case-table-head,
    .case-summary {{
      display: grid;
      grid-template-columns: 24px minmax(128px, 170px) minmax(280px, 1fr) 86px 92px minmax(180px, .7fr) minmax(128px, 148px);
      gap: 12px;
      align-items: flex-start;
    }}
    .case-table-head {{
      border-bottom: 1px solid var(--line-soft);
      background: #fbfcfe;
      color: #6b7a90;
      padding: 10px 16px;
      font-size: 12px;
      font-weight: 900;
      letter-spacing: .08em;
      text-transform: uppercase;
    }}
    .case-list {{ display: grid; gap: 0; }}
    .case-card {{ border-bottom: 1px solid var(--line-soft); }}
    .case-card:last-child {{ border-bottom: 0; }}
    .case-summary {{
      width: 100%;
      border: 0;
      background: transparent;
      color: inherit;
      padding: 12px 16px;
      text-align: left;
    }}
    .case-summary:hover {{ background: #fbfcfe; }}
    .case-main-cell,
    .case-tags-cell {{ min-width: 0; }}
    .case-id-cell,
    .case-priority-cell,
    .case-type-cell,
    .case-tags-cell,
    .case-actions-cell {{ padding-top: 2px; }}
    .toggle {{
      width: 24px;
      height: 24px;
      display: inline-grid;
      place-items: center;
      border-radius: 4px;
      color: var(--muted);
      font-weight: 900;
    }}
    .case-card.open .toggle {{ color: var(--primary); transform: rotate(90deg); }}
    .case-id {{
      display: inline-block;
      border-radius: 4px;
      background: var(--primary-soft);
      color: var(--primary);
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      font-size: 13px;
      font-weight: 900;
      padding: 2px 6px;
      white-space: nowrap;
    }}
    .case-title-line {{ display: flex; align-items: center; gap: 8px; min-width: 0; }}
    .case-title {{ min-width: 0; color: #263244; font-size: 13px; font-weight: 900; line-height: 1.35; }}
    .case-description {{ display: block; margin: 3px 0 0; color: #8fa0b8; font-size: 12px; line-height: 1.45; }}
    .auto-pill {{
      display: inline-flex;
      align-items: center;
      min-height: 18px;
      border-radius: 999px;
      background: var(--mark-soft);
      color: var(--mark);
      font-size: 12px;
      font-weight: 900;
      padding: 1px 8px;
      white-space: nowrap;
    }}
    .badge {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-width: 44px;
      min-height: 22px;
      border-radius: 999px;
      padding: 2px 9px;
      font-size: 12px;
      font-weight: 900;
    }}
    .priority-p0 {{ color: var(--p0); background: var(--p0-soft); }}
    .priority-p1 {{ color: #9a6500; background: var(--p1-soft); }}
    .priority-p2 {{ color: var(--p2); background: var(--p2-soft); }}
    .case-type-cell {{ color: #637089; font-size: 12px; }}
    .tag-list {{ display: flex; flex-wrap: wrap; gap: 5px; }}
    .tag {{
      border-radius: 999px;
      background: var(--primary-soft);
      color: #245ca8;
      font-size: 11px;
      font-weight: 500;
      padding: 2px 8px;
      white-space: nowrap;
    }}
    .case-actions-cell {{ display: flex; justify-content: flex-end; }}
    .case-action-text {{ color: var(--primary); font-size: 13px; font-weight: 900; }}
    .case-body {{
      display: none;
      grid-template-columns: minmax(0, 1fr) minmax(280px, 360px);
      gap: 14px;
      padding: 12px 16px 16px 60px;
      border-top: 1px solid var(--line-soft);
      background: #f8fafc;
    }}
    .case-card.open .case-body {{ display: grid; }}
    .detail-grid {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
      gap: 28px;
      align-self: start;
      border: 1px solid #dbe5f0;
      border-radius: 8px;
      background: #ffffff;
      box-shadow: 0 1px 2px rgba(15, 23, 42, 0.06);
      padding: 14px 18px 16px;
    }}
    .detail-section + .detail-section {{ margin-top: 16px; }}
    .detail-section h5 {{
      display: flex;
      align-items: center;
      gap: 7px;
      margin: 0 0 8px;
      color: #2f3b4f;
      font-size: 13px;
      font-weight: 800;
    }}
    .detail-section h5 svg {{
      width: 15px;
      height: 15px;
      flex: 0 0 15px;
      color: #94a3b8;
    }}
    .detail-section ol,
    .detail-section ul {{
      margin: 0;
      padding-left: 22px;
      color: #4d5d73;
      font-size: 13px;
      font-weight: 400;
      line-height: 1.55;
    }}
    .detail-section li + li {{ margin-top: 3px; }}
    .empty-detail {{ color: var(--muted); }}
    .review-panel {{
      display: grid;
      gap: 10px;
      align-self: start;
      border: 1px solid var(--line);
      border-radius: 4px;
      background: #fff;
      padding: 12px;
    }}
    .mark-row {{ display: flex; align-items: center; gap: 8px; font-weight: 900; color: var(--mark); }}
    .review-panel textarea {{
      min-height: 110px;
      resize: vertical;
      border: 1px solid #bdbdbd;
      border-radius: 4px;
      padding: 9px 10px;
      color: var(--text);
    }}
    .mark-tag {{ color: var(--mark); background: var(--mark-soft); }}
    .empty {{ padding: 32px 18px; color: var(--muted); text-align: center; font-weight: 800; }}
    @media (max-width: 1280px) {{
      .case-table-head,
      .case-summary {{
        grid-template-columns: 24px minmax(120px, 150px) minmax(240px, 1fr) 76px 84px minmax(150px, .6fr) minmax(128px, 140px);
        gap: 10px;
      }}
    }}
    @media (max-width: 860px) {{
      .hero, .file-header, .case-body {{ grid-template-columns: 1fr; }}
      .case-table-head {{ display: none; }}
      .stats {{ justify-content: flex-start; }}
      .case-summary {{ grid-template-columns: 24px minmax(120px, 1fr); gap: 8px 12px; }}
      .case-id-cell,
      .case-main-cell,
      .case-priority-cell,
      .case-type-cell,
      .case-tags-cell,
      .case-actions-cell {{ grid-column: 2; justify-content: flex-start; }}
      .case-body {{ padding-left: 16px; }}
      .detail-grid {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <header class="app-bar">
    <div class="brand">CASEBOOK EXPORT</div>
    <div class="app-meta" id="generatedAt"></div>
  </header>
  <main class="page">
    <section class="hero">
      <div>
        <h1 id="pageTitle"></h1>
        <p class="subtitle" id="subtitle"></p>
      </div>
      <div class="stats" id="stats"></div>
    </section>
    <section class="toolbar" aria-label="Review controls">
      <input class="search" id="searchInput" type="search" placeholder="Search cases">
      <select id="priorityFilter" aria-label="Priority filter"></select>
      <select id="tagFilter" aria-label="Tag filter"></select>
      <select id="markFilter" aria-label="Review mark filter">
        <option value="all">All review states</option>
        <option value="marked">Marked only</option>
        <option value="unmarked">Unmarked only</option>
      </select>
      <button class="button" id="expandAllButton" type="button">Expand all</button>
      <button class="button" id="collapseAllButton" type="button">Collapse all</button>
      <button class="button primary" id="downloadReviewButton" type="button">Export review notes</button>
    </section>
    <section id="content"></section>
    <div class="empty" id="emptyState" hidden>No cases match the current filters.</div>
  </main>
  <script>
    const exportData = {export_json};
    const storageKey = "casebook-export-review:" + exportData.export_id;
    const state = {{
      review: loadReviewState(),
      query: "",
      priority: "all",
      tag: "all",
      mark: "all",
      open: new Set(),
    }};

    const els = {{
      generatedAt: document.getElementById("generatedAt"),
      pageTitle: document.getElementById("pageTitle"),
      subtitle: document.getElementById("subtitle"),
      stats: document.getElementById("stats"),
      search: document.getElementById("searchInput"),
      priority: document.getElementById("priorityFilter"),
      tag: document.getElementById("tagFilter"),
      mark: document.getElementById("markFilter"),
      content: document.getElementById("content"),
      empty: document.getElementById("emptyState"),
      expandAll: document.getElementById("expandAllButton"),
      collapseAll: document.getElementById("collapseAllButton"),
      downloadReview: document.getElementById("downloadReviewButton"),
    }};

    boot();

    function boot() {{
      els.generatedAt.textContent = "Generated: " + exportData.generated_at;
      els.pageTitle.textContent = exportData.title;
      els.subtitle.textContent = exportData.source_label + filterLabel();
      renderFilterOptions();
      bindEvents();
      render();
    }}

    function bindEvents() {{
      els.search.addEventListener("input", () => {{ state.query = els.search.value.trim().toLowerCase(); render(); }});
      els.priority.addEventListener("change", () => {{ state.priority = els.priority.value; render(); }});
      els.tag.addEventListener("change", () => {{ state.tag = els.tag.value; render(); }});
      els.mark.addEventListener("change", () => {{ state.mark = els.mark.value; render(); }});
      els.expandAll.addEventListener("click", () => {{ allCases().forEach((item) => state.open.add(item.key)); render(); }});
      els.collapseAll.addEventListener("click", () => {{ state.open.clear(); render(); }});
      els.downloadReview.addEventListener("click", downloadReviewNotes);
      els.content.addEventListener("click", (event) => {{
        const summary = event.target.closest("[data-case-summary]");
        if (!summary) return;
        const key = summary.dataset.caseKey;
        if (state.open.has(key)) state.open.delete(key);
        else state.open.add(key);
        render();
      }});
      els.content.addEventListener("change", (event) => {{
        const checkbox = event.target.closest("[data-review-mark]");
        if (!checkbox) return;
        const key = checkbox.dataset.reviewMark;
        const item = ensureReviewItem(key);
        item.marked = checkbox.checked;
        item.updated_at = new Date().toISOString();
        saveReviewState();
        renderStats();
        render();
      }});
      els.content.addEventListener("input", (event) => {{
        const textarea = event.target.closest("[data-review-notes]");
        if (!textarea) return;
        const key = textarea.dataset.reviewNotes;
        const item = ensureReviewItem(key);
        item.notes = textarea.value;
        item.updated_at = new Date().toISOString();
        saveReviewState();
        renderStats();
      }});
    }}

    function renderFilterOptions() {{
      const stats = exportData.stats;
      els.priority.innerHTML = [
        option("all", "All priorities (" + stats.total + ")"),
        option("P0", "P0 (" + (stats.priorities.P0 || 0) + ")"),
        option("P1", "P1 (" + (stats.priorities.P1 || 0) + ")"),
        option("P2", "P2 (" + (stats.priorities.P2 || 0) + ")"),
      ].join("");
      const tags = Object.keys(stats.tags).sort();
      els.tag.innerHTML = [option("all", "All tags"), ...tags.map((tag) => option(tag, tag + " (" + stats.tags[tag] + ")"))].join("");
    }}

    function render() {{
      renderStats();
      const filtered = exportData.files
        .map((file) => ({{ ...file, cases: file.cases.filter(matchesCase) }}))
        .filter((file) => file.cases.length);
      els.content.innerHTML = filtered.map(renderFile).join("");
      els.empty.hidden = filtered.length > 0;
    }}

    function renderStats() {{
      const cases = allCases();
      const marked = cases.filter((item) => reviewItem(item.key).marked).length;
      const withNotes = cases.filter((item) => reviewItem(item.key).notes.trim()).length;
      els.stats.innerHTML = [
        stat(exportData.stats.files, "Files", "files"),
        stat(exportData.stats.total, "Cases", "cases"),
        stat(exportData.stats.priorities.P0 || 0, "P0", "p0"),
        stat(marked, "Marked", "marked"),
        stat(withNotes, "Notes", "notes"),
      ].join("");
    }}

    function renderFile(file) {{
      return `
        <article class="file-card">
          <header class="file-header">
            <div>
              <h2>${{escapeHtml(file.module)}} / ${{escapeHtml(file.feature || "Untitled")}}</h2>
              <div class="file-path">${{escapeHtml(file.path)}}</div>
              <div class="file-meta">
                ${{pill("Owner: " + (file.owner || "N/A"))}}
                ${{pill("Reviewed: " + (file.last_reviewed || "N/A"))}}
                ${{file.file_tags.map((tag) => pill(tag)).join("")}}
              </div>
            </div>
            <div class="file-count">${{file.cases.length}} cases</div>
          </header>
          <div class="case-table-head" aria-hidden="true">
            <span></span>
            <span>ID</span>
            <span>Title</span>
            <span>Priority</span>
            <span>Type</span>
            <span>Tags</span>
            <span>Actions</span>
          </div>
          <div class="case-list">${{file.cases.map((caseItem) => renderCase(file, caseItem)).join("")}}</div>
        </article>`;
    }}

    function renderCase(file, caseItem) {{
      const key = caseItem.key;
      const review = reviewItem(key);
      const open = state.open.has(key);
      const marked = Boolean(review.marked);
      const tags = [
        ...caseItem.tags.map((tag) => `<span class="tag">${{escapeHtml(tag)}}</span>`),
        marked ? '<span class="tag mark-tag">Mark</span>' : "",
      ].join("");
      return `
        <article class="case-card ${{open ? "open" : ""}}" data-case-key="${{escapeAttr(key)}}">
          <button class="case-summary" type="button" data-case-summary data-case-key="${{escapeAttr(key)}}">
            <span class="toggle">›</span>
            <span class="case-id-cell"><span class="case-id">${{escapeHtml(caseItem.id)}}</span></span>
            <span class="case-main-cell">
              <span class="case-title-line">
                <span class="case-title">${{escapeHtml(caseItem.title)}}</span>
                ${{caseItem.auto ? '<span class="auto-pill">Auto</span>' : ""}}
              </span>
              ${{caseItem.description ? `<span class="case-description">${{escapeHtml(caseItem.description)}}</span>` : ""}}
            </span>
            <span class="case-priority-cell">
              <span class="badge priority-${{escapeAttr(caseItem.priority.toLowerCase())}}">${{escapeHtml(caseItem.priority)}}</span>
            </span>
            <span class="case-type-cell">${{escapeHtml(caseItem.type)}}</span>
            <span class="case-tags-cell"><span class="tag-list">${{tags}}</span></span>
            <span class="case-actions-cell"><span class="case-action-text">Review</span></span>
          </button>
          <div class="case-body">
            <div class="detail-grid">
              <div class="case-detail-column">
                ${{detailList("Preconditions", caseItem.preconditions, false)}}
                ${{detailList("Steps", caseItem.steps, true)}}
              </div>
              <div class="case-detail-column">
                ${{detailList("Expected Results", caseItem.expected_results, false)}}
              </div>
            </div>
            <aside class="review-panel">
              <label class="mark-row">
                <input type="checkbox" data-review-mark="${{escapeAttr(key)}}" ${{marked ? "checked" : ""}}>
                <span>Needs update</span>
              </label>
              <textarea data-review-notes="${{escapeAttr(key)}}" placeholder="Describe what should be updated">${{escapeHtml(review.notes)}}</textarea>
            </aside>
          </div>
        </article>`;
    }}

    function detailList(title, items, ordered) {{
      const tag = ordered ? "ol" : "ul";
      const rows = items.length ? items.map((item) => `<li>${{escapeHtml(item)}}</li>`).join("") : '<li class="empty-detail">None</li>';
      return `<section class="detail-section"><h5>${{detailIcon(title)}}<span>${{escapeHtml(title)}}</span></h5><${{tag}}>${{rows}}</${{tag}}></section>`;
    }}

    function detailIcon(title) {{
      if (title === "Preconditions") {{
        return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>`;
      }}
      return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>`;
    }}

    function matchesCase(caseItem) {{
      if (state.priority !== "all" && caseItem.priority !== state.priority) return false;
      if (state.tag !== "all" && !caseItem.tags.includes(state.tag) && !caseItem.file_tags.includes(state.tag)) return false;
      const review = reviewItem(caseItem.key);
      if (state.mark === "marked" && !review.marked) return false;
      if (state.mark === "unmarked" && review.marked) return false;
      if (!state.query) return true;
      const haystack = [
        caseItem.id,
        caseItem.title,
        caseItem.description,
        caseItem.type,
        caseItem.priority,
        ...caseItem.tags,
        ...caseItem.file_tags,
        ...caseItem.preconditions,
        ...caseItem.steps,
        ...caseItem.expected_results,
      ].join(" ").toLowerCase();
      return haystack.includes(state.query);
    }}

    function allCases() {{
      return exportData.files.flatMap((file) => file.cases);
    }}

    function ensureReviewItem(key) {{
      if (!state.review.items[key]) state.review.items[key] = {{ marked: false, notes: "", updated_at: "" }};
      return state.review.items[key];
    }}

    function reviewItem(key) {{
      return ensureReviewItem(key);
    }}

    function loadReviewState() {{
      try {{
        const raw = window.localStorage.getItem(storageKey);
        if (raw) return JSON.parse(raw);
      }} catch (error) {{}}
      return {{ export_id: exportData.export_id, items: {{}} }};
    }}

    function saveReviewState() {{
      try {{ window.localStorage.setItem(storageKey, JSON.stringify(state.review)); }} catch (error) {{}}
    }}

    function downloadReviewNotes() {{
      const payload = {{
        export_id: exportData.export_id,
        title: exportData.title,
        source: exportData.source_label,
        generated_at: exportData.generated_at,
        exported_at: new Date().toISOString(),
        items: state.review.items,
      }};
      const blob = new Blob([JSON.stringify(payload, null, 2)], {{ type: "application/json" }});
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = exportData.slug + "-review-notes.json";
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
    }}

    function filterLabel() {{
      const parts = [];
      if (exportData.filters.priorities.length) parts.push("priorities: " + exportData.filters.priorities.join(", "));
      if (exportData.filters.tags.length) parts.push("tags: " + exportData.filters.tags.join(", "));
      return parts.length ? " - " + parts.join(" - ") : "";
    }}

    function option(value, label) {{
      return `<option value="${{escapeAttr(value)}}">${{escapeHtml(label)}}</option>`;
    }}

    function stat(value, label, kind) {{
      return `<div class="stat stat-${{escapeAttr(kind)}}"><strong>${{value}}</strong><span>${{escapeHtml(label)}}</span></div>`;
    }}

    function pill(value) {{
      return `<span class="pill">${{escapeHtml(value)}}</span>`;
    }}

    function escapeHtml(value) {{
      return String(value ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");
    }}

    function escapeAttr(value) {{
      return escapeHtml(value);
    }}
  </script>
</body>
</html>
"""


def _build_export_data(
    project_root: Path,
    source_path: Path,
    entries: list[dict[str, Any]],
    priorities: list[str],
    tags: list[str],
) -> dict[str, Any]:
    files = [_entry_for_export(entry) for entry in entries]
    stats = _compute_export_stats(files)
    slug = _slug(source_path.stem if source_path.is_file() else source_path.name or "casebook")
    source_label = _source_label(project_root, source_path)
    return {
        "export_id": f"{source_label}|priority={','.join(priorities)}|tag={','.join(tags)}",
        "title": source_path.stem if source_path.is_file() else f"Casebook {source_path.name or 'Export'}",
        "slug": slug,
        "source_label": source_label,
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "filters": {
            "priorities": priorities,
            "tags": tags,
        },
        "stats": stats,
        "files": files,
    }


def _entry_for_export(entry: dict[str, Any]) -> dict[str, Any]:
    file_tags = [str(tag) for tag in entry.get("file_tags", [])]
    cases = []
    for case in entry.get("cases", []):
        key = f"{entry['path']}#{case['id']}"
        cases.append({
            **case,
            "key": key,
            "file_path": entry["path"],
            "file_tags": file_tags,
        })
    return {
        "path": entry["path"],
        "module": entry.get("module", "Unknown"),
        "feature": entry.get("feature", ""),
        "owner": entry.get("owner", "N/A"),
        "last_reviewed": entry.get("last_reviewed", ""),
        "file_tags": file_tags,
        "cases": cases,
    }


def _compute_export_stats(files: list[dict[str, Any]]) -> dict[str, Any]:
    cases = [case for file in files for case in file["cases"]]
    stats = compute_stats(cases)
    tags: dict[str, int] = {}
    for case in cases:
        for tag in sorted({*case.get("tags", []), *case.get("file_tags", [])}):
            tags[str(tag)] = tags.get(str(tag), 0) + 1
    stats["tags"] = tags
    stats["files"] = len(files)
    return stats


def _collect_entries(project_root: Path, source_path: Path) -> list[dict[str, Any]]:
    if source_path.is_file():
        if source_path.suffix.lower() not in {".yaml", ".yml"}:
            raise ExportError("Export source must be a YAML file or a directory.")
        scan_dir = _relative_or_dot(project_root, source_path.parent)
        store = CasebookStore(project_root=project_root, scan_dirs=[scan_dir])
        store.refresh()
        file_path = relative_path(project_root, source_path)
        entry = store.get_file(file_path)
        return [entry] if entry else []

    if not source_path.is_dir():
        raise ExportError(f"Export source not found: {source_path}")

    scan_dir = _relative_or_dot(project_root, source_path)
    store = CasebookStore(project_root=project_root, scan_dirs=[scan_dir])
    store.refresh()
    entries = []
    for file_meta in store.list_files():
        entry = store.get_file(file_meta["path"])
        if entry:
            entries.append(entry)
    return entries


def _filter_entries(
    entries: list[dict[str, Any]],
    priorities: list[str],
    tags: list[str],
) -> list[dict[str, Any]]:
    filtered_entries: list[dict[str, Any]] = []
    tag_set = {tag.lower() for tag in tags}
    priority_set = set(priorities)
    for entry in entries:
        file_tags = [str(tag) for tag in entry.get("file_tags", [])]
        cases = []
        for case in entry.get("cases", []):
            if priority_set and case.get("priority") not in priority_set:
                continue
            case_tags = [str(tag) for tag in case.get("tags", [])]
            all_tags = {tag.lower() for tag in [*file_tags, *case_tags]}
            if tag_set and not (all_tags & tag_set):
                continue
            cases.append(case)
        if cases:
            next_entry = {**entry, "cases": cases}
            next_entry["stats"] = compute_stats(cases)
            filtered_entries.append(next_entry)
    return filtered_entries


def _resolve_source(project_root: Path, source: Path) -> Path:
    raw = source.expanduser()
    resolved = raw.resolve() if raw.is_absolute() else (project_root / raw).resolve()
    if resolved != project_root and project_root not in resolved.parents:
        raise ExportError("Export source must be inside the current project.")
    if not resolved.exists():
        raise ExportError(f"Export source not found: {source}")
    return resolved


def _default_output(source_path: Path, output_file: Path | None) -> Path:
    if output_file:
        return output_file.expanduser().resolve()
    if source_path.is_file():
        return source_path.with_suffix(".html")
    return (Path.cwd() / f"casebook-{_slug(source_path.name or 'export')}.html").resolve()


def _normalize_priorities(values: list[str]) -> list[str]:
    priorities: list[str] = []
    for raw in values:
        for item in str(raw).split(","):
            value = item.strip().upper()
            if not value:
                continue
            if value not in {"P0", "P1", "P2"}:
                raise ExportError(f"Invalid priority: {item}")
            if value not in priorities:
                priorities.append(value)
    return priorities


def _normalize_tags(values: list[str]) -> list[str]:
    tags: list[str] = []
    for raw in values:
        for item in str(raw).split(","):
            value = item.strip()
            if value and value not in tags:
                tags.append(value)
    return tags


def _relative_or_dot(project_root: Path, path: Path) -> str:
    rel = relative_path(project_root, path)
    return rel if rel else "."


def _source_label(project_root: Path, source_path: Path) -> str:
    try:
        return relative_path(project_root, source_path)
    except ValueError:
        return source_path.as_posix()


def _slug(value: str) -> str:
    slug = "".join(ch.lower() if ch.isalnum() else "-" for ch in value).strip("-")
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug or "casebook"


def _html(value: Any) -> str:
    return escape(str(value), quote=True)
