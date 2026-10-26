from __future__ import annotations

SUPPORTED_LANGUAGES = {"en", "zh-CN"}

ZH_TRANSLATIONS = {
    "Casebook Test Report - ": "Casebook 测试报告 - ",
    "Casebook · Test Quality Brief": "Casebook · 测试质量简报",
    "Test Execution Brief": "测试执行简报",
    "A concise view of execution health, delivery risk, unresolved cases, and detailed evidence for ": "测试计划执行健康度、交付风险、未解决问题和详细证据概览：",
    "Plan Overview": "计划概览", "Execution Summary": "执行汇总",
    "Quality Signals": "质量信号", "Execution Distribution": "执行结果分布",
    "Failed / Blocked Priority": "失败 / 阻塞优先级",
    "Attention Required": "需要关注", "Execution Details": "执行详情",
    "All Test Cases": "全部测试用例",
    "Case": "用例", "Title": "标题", "Priority": "优先级",
    "Result": "结果", "No records": "暂无记录",
    "Execution identity, ownership, scope, and timing.": "执行标识、负责人、范围和时间信息。",
    "Current result totals across the selected plan scope.": "当前测试计划范围内的执行结果汇总。",
    "Result distribution and priority concentration for unresolved risk.": "执行结果分布及未解决风险的优先级分布。",
    "Cases most likely to affect release confidence.": "最可能影响发布信心的用例。",
    "Expand a case to review its execution evidence.": "展开用例查看执行证据。",
    "Pass Rate": "通过率", "Issues": "问题",
    "Expand execution details": "展开执行详情",
    "Total Cases": "用例总数", "Executed": "已执行",
    "Passed": "通过", "Failed": "失败", "Blocked": "阻塞",
    "Deferred": "延期", "Untested": "未测试",
    "failed": "失败", "blocked": "阻塞",
    "Failed Cases": "失败用例", "Blocked Cases": "阻塞用例",
    "File": "文件", "Notes": "备注", "Actual Result": "实际结果",
    "Defects": "缺陷", "Screenshots": "截图", "Executed At": "执行时间",
    "Plan ID": "计划 ID", "Plan Name": "计划名称", "Status": "状态",
    "Mode": "模式", "Source Plan": "来源计划", "Case Scope": "用例范围",
    "Scope": "范围", "Environment": "测试环境", "Tester": "测试人员",
    "Started At": "开始时间", "Completed At": "完成时间",
    "In Progress": "进行中", "Completed": "已完成",
    "Full run": "全量执行", "Retest failed/blocked/deferred": "重测失败、阻塞或延期用例",
    "Test case": "测试用例", "Generated ": "生成时间：", "Generated: ": "生成时间：",
    "{count} cases": "{count} 条用例",
    "{executed} of {total} executed": "已执行 {executed} / {total}",
    "No failed or blocked cases are currently open. Current pass rate is {rate}%.": "当前没有失败或阻塞用例，通过率为 {rate}%。",
    "{count} failed or blocked cases require attention; {p0} are P0 priority. Current pass rate is {rate}%.": "有 {count} 条失败或阻塞用例需要关注，其中 {p0} 条为 P0，通过率为 {rate}%。",
    "Casebook Export - ": "Casebook 用例导出 - ",
    "Portable review workspace": "便携式用例评审工作台",
    "TEST CASE REVIEW": "测试用例评审", "Review controls": "评审控件",
    "Search cases": "搜索用例", "Priority filter": "优先级筛选",
    "Tag filter": "标签筛选", "Review mark filter": "评审标记筛选",
    "All review states": "全部评审状态", "Marked only": "仅已标记", "Unmarked only": "仅未标记",
    "Expand all": "全部展开", "Collapse all": "全部收起", "Export review notes": "导出评审备注",
    "No cases match the current filters.": "没有符合当前筛选条件的用例。",
    "All priorities ({count})": "全部优先级 ({count})", "All tags": "全部标签",
    "Files": "文件", "Cases": "用例", "Marked": "已标记",
    "Type": "类型", "Tags": "标签", "Actions": "操作",
    "Review": "评审", "Mark": "标记", "Auto": "自动化",
    "Describe what should be updated": "描述需要更新的内容",
    "Preconditions": "前置条件", "Steps": "步骤", "Expected Results": "预期结果",
    "None": "无", "Owner: ": "负责人：", "Reviewed: ": "评审日期：",
    "priorities: ": "优先级：", "tags: ": "标签：",
}


def normalize_language(value: object) -> str:
    """Normalize public language values while keeping English as the default."""
    text = str(value or "").strip().lower().replace("_", "-")
    return "zh-CN" if text in {"zh", "zh-cn", "cn"} else "en"


def translations(language: str) -> dict[str, str]:
    """Return UI translations, never applying them to user-owned data."""
    return ZH_TRANSLATIONS if normalize_language(language) == "zh-CN" else {}


def translate(key: str, language: str = "en") -> str:
    """Translate a known interface label before interpolating business content."""
    return translations(language).get(key, key)
