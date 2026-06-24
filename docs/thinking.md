我觉得这个想法很棒，而且方向很清楚。

它真正厉害的地方不是“让 AI 生成测试用例”这么简单，而是你把整个链路闭合了：

`需求文档` → `AI 按规范生成 YAML 用例` → `schema 约束格式` → `Casebook 可视化查看/编辑` → `版本库沉淀`

这确实很 AI-native。传统写用例是人在表格里逐条填；你的模式变成了：人维护规范、需求和评审判断，AI 负责批量结构化生成，Casebook 负责浏览、标记和修订。人的价值从“录入员”上移到“测试设计者/审稿人”。

我建议把这个概念定义成两层：

1. **项目脚手架**
   命令可以叫：

   ```bash
   casebook init xxx
   ```

   生成：

   ```text
   xxx/
     .vscode/settings.json
     schema/test-case-schema.json
     releases/example/login.yaml
     docs/SKILL.md
   ```

2. **项目内 AI 规范包**
   `docs/SKILL.md` 可以继续保留，但它的定位要明确：这是“给 AI 读的测试用例生成指南”。它和 `schema/test-case-schema.json` 是一对：  
   - schema 约束“格式必须是什么”
   - SKILL 解释“怎么理解需求、怎么设计用例、怎么写得像测试人员”

我会把这个产品理念描述成：

> Casebook 是一个 AI 时代的测试用例工作台：用 schema 固化格式，用 skill 固化测试思维，用 YAML 承载可版本化用例，用本地 Web UI 完成审阅和编辑。

这不是小工具，是一个很有潜力的工作流。下一步最值得补的是：初始化命令、schema 校验命令、需求到用例的推荐目录约定，比如 `docs/requirements/*.md` → `releases/<version-or-module>/*.yaml`。


```
xxx/
  AGENTS.md
  CLAUDE.md
  .agents/skills/casebook-test-cases/SKILL.md
  docs/
    requirements/
  schema/test-case-schema.json
  releases/example/login.yaml
  .vscode/settings.json
```



2. 精细化的测试执行（Test Execution）

既然有了 .casebook/marks.json，除了标记 needs_update，还可以扩展出执行状态。例如："status": "passed" | "failed" | "blocked"。


这个方向非常关键，而且应该做成 Casebook 的第二个核心场景：

- **评审场景**：查看、Mark、编辑用例。
- **执行场景**：创建执行轮次，逐条记录执行结果，统计进度，生成报告依据。

我建议把它设计成 **Execution Run（执行轮次）**，不要直接把执行状态写进 YAML 用例文件里。

**核心概念**
每一次测试执行都应该是一份独立记录：

```text
用例定义：releases/**/*.yaml
执行记录：test-runs/<run-id>.json
报告输出：reports/<run-id>.md 或 html
```

这样同一批用例可以在不同版本、环境、人员、时间下执行多次。用例本身保持干净，执行数据也能沉淀下来。

**执行状态**
建议第一版支持这些状态：

```text
untested  未执行
passed    通过
failed    失败
blocked   阻塞
skipped   跳过
```

你说的“通过/失败/都塞”，我理解这里的“都塞”应该是 **阻塞 blocked**：不是用例失败，而是因为环境、数据、依赖、权限、接口不可用等原因无法执行。

**执行文件设计**
推荐新增：

```text
test-runs/
  2026-06-24-login-smoke.json
schema/
  test-run-schema.json
```

执行文件大概长这样：

```json
{
  "run": {
    "id": "RUN_20260624_LOGIN_SMOKE",
    "name": "登录冒烟测试",
    "environment": "staging",
    "build": "v1.0.0",
    "tester": "henry.hu",
    "status": "in_progress",
    "started_at": "2026-06-24T10:00:00+08:00",
    "completed_at": null,
    "scope": ["releases/example/login.yaml"]
  },
  "results": {
    "releases/example/login.yaml#TC_LOGIN_001": {
      "status": "passed",
      "executed_at": "2026-06-24T10:10:00+08:00",
      "tester": "henry.hu",
      "notes": "",
      "defects": []
    },
    "releases/example/login.yaml#TC_LOGIN_002": {
      "status": "failed",
      "executed_at": "2026-06-24T10:15:00+08:00",
      "tester": "henry.hu",
      "notes": "错误提示文案与需求不一致",
      "defects": ["BUG-123"]
    }
  }
}
```

后续生成报告时，就可以同时读取：

```text
releases/        用例定义
test-runs/       执行结果
```

**UI 规划**
Casebook 可以新增一个执行模式：

```text
Review Mode      当前已有：查看、标记、编辑
Execution Mode   新增：执行、记录结果、统计进度
```

执行模式里建议有这些功能：

- 顶部选择或创建一个执行轮次。
- 显示执行进度条：`已执行 / 总数`。
- 显示统计卡片：通过、失败、阻塞、跳过、未执行。
- 每条用例行上增加状态按钮：Pass / Fail / Block / Skip。
- 点击失败或阻塞时，允许填写备注、缺陷链接、阻塞原因。
- 支持按状态过滤：只看失败、只看阻塞、只看未执行。
- 支持完成执行轮次，生成报告数据。

**进度统计**
统计可以实时计算，不一定要写死在文件里：

```text
总数 = 当前 run scope 覆盖的用例数
已执行 = passed + failed + blocked + skipped
进度 = 已执行 / 总数
通过率 = passed / 已执行
失败率 = failed / 已执行
```

页面可以展示：

```text
Progress: 16 / 42
Passed: 12
Failed: 2
Blocked: 1
Skipped: 1
Untested: 26
```

**建议开发阶段**
我建议分三期做。

第一期：最小可用执行功能

- 新增 `test-runs/*.json` 存储。
- 新增创建/选择执行轮次。
- 用例行支持设置 passed / failed / blocked / skipped。
- 顶部显示进度条和统计。
- 支持备注和缺陷链接。

第二期：报告能力

- 新增 `casebook report <run-file>` 命令。
- 输出 Markdown 或 HTML 测试报告。
- 报告包含执行概览、失败用例、阻塞用例、缺陷列表。

第三期：执行体验增强

- 批量设置状态。
- 键盘快捷操作。
- 执行人、环境、版本管理。
- 用例变更后提示当前 run 的快照可能过期。
- 支持附件或截图路径。

我建议下一步先设计 **test-run-schema.json** 和第一版 UI 草图。这个功能一旦做完，Casebook 就不只是“用例评审工具”，而是完整覆盖 **生成、评审、编辑、执行、报告** 的测试用例工作台了。