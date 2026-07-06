我读完 `docs/thinking.md` 后的判断是：Casebook 前 6 个版本已经把“用例资产怎么被查看、评审、执行、报告”这条链路打通了。下一阶段最值得做的，不是继续堆页面功能，而是往前推进一层：

**让 AI 更可靠地理解需求。**

也就是从：

```text
需求文档 -> AI 生成 YAML 用例
```

升级成：

```text
原始需求 / Figma / API / 业务规则
  -> 结构化需求理解
  -> 测试策略与覆盖地图
  -> AI 生成 YAML 用例
  -> Casebook 评审、执行、报告
```

**核心定位**
Casebook 不应该变成“内置 AI 生成按钮的平台”。它更应该成为：

> AI Agent 时代的测试资产工程基础设施：负责把需求、设计稿、接口文档、测试策略、用例、执行证据组织成 AI 可读、人可审、Git 可追踪的工程资产。

也就是说，模型负责推理，Casebook 负责给模型准备好高质量上下文。

**建议路线图**

**0.7.0：需求标准化能力**

目标：把模糊 PRD 变成 AI 容易理解的结构化需求。

建议新增：

```text
docs/requirements/raw/         原始需求材料
docs/requirements/<feature>.md 标准化需求文档
schema/requirement-schema.json 需求结构约束
```

标准化需求文档建议包含：

- 背景与目标
- 用户角色
- 功能范围
- 不做什么
- 业务规则
- 页面/入口
- 字段规则
- 状态流转
- 权限规则
- 异常场景
- 验收标准
- 未确认问题
- Figma / API / Jira 引用

配套命令可以是：

```bash
casebook requirement new login
casebook requirement check docs/requirements/login.md
casebook context docs/requirements/login.md
```

其中 `casebook context` 很关键：它不调用模型，而是生成一份 AI Agent 可以直接读取的上下文包，里面聚合需求、schema、skill、已有 YAML、相关设计引用。

**0.8.0：Figma / 设计稿理解能力**

目标：让 UI 需求不再只是“贴一个 Figma 链接”，而是转成测试人员可用的信息。

建议先不要做复杂的 Figma 渲染平台，先做轻量结构化：

```text
docs/designs/login.md
```

内容包括：

- Figma 链接
- 页面/Frame 名称
- 核心组件
- 字段与校验
- 默认态、加载态、空态、错误态、禁用态
- 弹窗、Toast、确认框
- 权限可见性
- 响应式要求
- 可访问性注意点
- 与需求规则的对应关系

配套命令可以是：

```bash
casebook design scan docs/requirements/login.md
casebook design new login --figma <url>
```

第一阶段只需要识别和索引 Figma URL，生成设计理解模板。后续再考虑接 Figma MCP，把 Frame 信息、截图、节点文本提取出来。

**0.9.0：需求覆盖与追踪**

目标：让 Casebook 能回答三个问题：

- 哪些需求已经有用例覆盖？
- 哪些需求没有覆盖？
- 哪些用例找不到需求依据？

这里有两种方案：

方案 A：在 YAML 用例中增加字段，例如：

```yaml
requirement_refs: [REQ_LOGIN_001]
design_refs: [FIGMA_LOGIN_FORM]
```

方案 B：不污染 YAML，用独立文件维护映射：

```text
.casebook/trace.json
```

我更建议第一阶段用方案 B。因为当前 YAML schema 很克制，先把追踪能力做在外部，风险更小。等模型和团队习惯稳定后，再决定是否把 `requirement_refs` 纳入正式 schema。

配套命令：

```bash
casebook coverage docs/requirements/login.md releases/v1-auth
```

输出：

- 需求总数
- 已覆盖需求
- 未覆盖需求
- 无需求来源的用例
- 只覆盖 happy path 的需求
- 缺少异常/边界/权限/状态覆盖的需求

**1.0.0：测试策略生成与质量门禁**

目标：AI 不只是生成用例，而是先生成测试策略。

在生成 YAML 之前，先产出：

```text
docs/strategies/login.md
```

内容包括：

- 测试范围
- 风险分级
- 测试层级建议：API / UI / E2E / 手工
- P0/P1/P2 分布预期
- 冒烟用例建议
- 自动化建议
- 不值得写成用例的检查项
- 需要产品确认的问题

然后再由 AI 根据策略生成用例。

这一步会让 Casebook 从“用例工作台”升级成“测试设计工作台”。

**1.1.0：评审反馈反哺 AI**

现在 Casebook 已经有 Mark 和 Notes。下一步可以把这些评审意见变成 AI 修复任务。

命令可以是：

```bash
casebook prompt marks releases/v1-auth
```

生成一段给 AI Agent 的修复提示：

```text
请根据以下 Casebook 评审意见修改 YAML 用例：
- TC_LOGIN_003: 预期结果不够可验证
- TC_LOGIN_006: 缺少权限异常场景
- TC_LOGIN_009: 与 REQ_LOGIN_004 重复
```

这非常符合 Casebook 的理念：页面负责评审，AI 负责维护。

**我建议的优先级**

第一优先级：`casebook context`

这是最小但最关键的能力。它能把需求、skill、schema、已有用例打包成 AI 可读上下文，直接提升 AI 生成质量。

第二优先级：标准化需求模板 + `casebook requirement check`

先把需求写法规范住。需求质量上来了，用例质量才会稳定。

第三优先级：Figma 链接识别 + 设计理解模板

先解决“Figma 链接只是链接，AI 不一定知道该看什么”的问题。

第四优先级：coverage / trace

等需求 ID、设计 ID、用例 ID 都稳定后，再做覆盖分析。

**不建议现在做的事**

- 不建议做平台式“上传需求，一键生成用例”。
- 不建议一开始深度集成 Figma API，容易变重。
- 不建议马上做复杂 Regression selection 树。
- 不建议把 Casebook 变成需求管理系统。
- 不建议把所有 AI 能力都内置到 Casebook 命令里。

Casebook 最强的方向仍然是：让 AI Agent 在工程项目里工作，让需求、设计、用例、执行记录都变成可追踪的工程资产。

我建议下一步就定为 **0.7.0：Requirement Context Pack**。先实现 `casebook context`、标准化需求模板、需求检查清单和文档更新。这一步小，但会把 Casebook 从“AI 生成用例后的工作台”，推进到“AI 理解需求前的基础设施”。