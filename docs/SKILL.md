# 生成测试用例 (Generate Test Cases)

## 目的

基于项目定义的测试用例格式规范 (`schema/test-case-schema.json`)，辅助生成符合规范的 YAML 格式测试用例文档。确保所有生成的用例在结构、字段完整性和数据类型上与规范保持一致。

## 何时使用此技能

- **新建用例文件**：需要为新功能模块创建 YAML 格式的测试用例集合
- **扩展现有用例**：为已有功能补充新的测试场景
- **格式验证**：校验用例结构是否符合规范要求
- **模板生成**：快速生成符合规范的用例框架

## 核心规范

### 根对象结构

所有用例文件必须包含 `metadata` 和 `test_cases` 两个顶级字段。

```yaml
metadata:
  module: "模块名称"              # 必需，所属大模块
  feature: "功能描述"              # 必需，当前文件聚焦功能
  owner: "name"                   # 必需，负责人英文名
  last_reviewed: "YYYY-MM-DD"     # 必需，最后评审日期
  tags: [tag1, tag2]              # 可选，全局标签列表

test_cases:
  - # 用例对象
```

### 用例对象必需字段

| 字段 | 类型 | 格式约束 | 说明 |
|---|---|---|---|
| `id` | string | `^TC_[A-Z0-9_]{3,}_[0-9]{3}$` | 全局唯一 ID，格式 `TC_<功能缩写>_<三位序号>` |
| `title` | string | 无 | 简洁动词开头的标题（例："验证登录成功"、"处理异常密码"） |
| `priority` | string | P0 \| P1 \| P2 | 优先级：P0（关键）、P1（重要）、P2（低） |
| `type` | string | functional \| ui \| security \| performance \| accessibility \| business \| other \| data-consistency | 用例类型 |
| `steps` | array[string] | 至少 1 条 | 操作步骤列表，每步一句话 |
| `expected_results` | array[string] | 至少 1 条 | 预期结果列表，可多条 |

### 用例对象可选字段

| 字段 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `description` | string | 无 | 补充说明用例背景或特殊场景 |
| `preconditions` | array[string] | 无 | 执行前提条件列表 |
| `tags` | array[string] | 无 | 用例级标签（如 smoke、regression、negative 等） |
| `auto` | boolean | false | 是否计划自动化 |

## 编写指南

### ID 命名规范

- 格式：`TC_<功能缩写>_<三位序号>`
- 例子：`TC_LOGIN_001`、`TC_PAYMENT_REFUND_002`
- 确保 ID 全局唯一

### 标题编写

- 使用动词开头，明确表达用例目标
- 例子：✅ "验证有效用户名密码可成功登录" / ❌ "登录页面"
- 避免过长，控制在 20 字以内

### 步骤描述

- 仅描述**业务意图**，不编写技术实现细节
- 每个步骤一条（不合并多个操作）
- 例子：
  - ✅ "输入有效用户名和密码"
  - ❌ "在用户名输入框中输入文本，使用 JavaScript 检查长度，然后提交表单"

### 预期结果

- 描述**全链路断言**：API 响应、数据库状态、UI 显示
- 多个结果分条列出
- 例子：
  - ✅ "API 返回 200"、"数据库记录该操作"、"页面显示成功提示"
  - ❌ "登录成功"（过于模糊）

### 优先级选择

- **P0**：核心功能、关键业务流、安全相关
- **P1**：重要功能、常用操作
- **P2**：边界场景、增强特性

### 类型分类

| 类型 | 适用场景 |
|---|---|
| `functional` | 功能正确性验证 |
| `ui` | 界面、布局、交互验证 |
| `security` | 安全验证、权限控制 |
| `performance` | 性能、响应时间 |
| `accessibility` | 无障碍、国际化 |
| `business` | 业务规则、版本兼容性 |
| `data-consistency` | 数据一致性、状态同步 |
| `other` | 其他 |

## 生成流程

1. **确定模块和功能**：识别用例所属模块和聚焦功能
2. **列出测试场景**：正常流、异常流、边界条件
3. **为每个场景编写用例**：按照规范格式填充字段
4. **校验格式**：确保 ID 唯一、字段完整、枚举值正确
5. **评审内容**：步骤清晰、预期结果可验证

## 示例

### 示例 1：功能性用例

```yaml
- id: "TC_LOGIN_001"
  title: "有效用户名和密码登录成功"
  description: "验证用户使用正确的登录凭证可以成功进入系统。"
  priority: "P0"
  type: "functional"
  preconditions:
    - 用户已注册并处于正常可登录状态
  steps:
    - 输入有效用户名和对应密码
    - 点击登录按钮
  expected_results:
    - 登录成功，进入系统首页
    - 显示当前用户姓名和欢迎信息
  tags: [smoke, login]
  auto: true
```

### 示例 2：安全性用例

```yaml
- id: "TC_LOGIN_003"
  title: "连续三次错误密码后提示图形验证码"
  description: "验证用户连续三次登录失败后，系统要求输入图形验证码进行校验。"
  priority: "P2"
  type: "security"
  preconditions:
    - 用户已注册并处于正常可登录状态
  steps:
    - 依次使用相同用户名输入错误密码三次并尝试登录
    - 在第四次登录时观察登录页面变化
  expected_results:
    - 前三次登录失败，显示密码错误提示
    - 第四次登录页面出现图形验证码输入框
    - 必须输入正确验证码才能继续登录
  tags: [login, security]
  auto: false
```

### 示例 3：业务性用例

```yaml
- id: "TC_FEATURE_COMPAT_001"
  title: "历史用户可访问旧版本功能"
  description: "验证拥有历史权限的用户能够使用系统升级后的兼容模式访问旧功能。"
  priority: "P1"
  type: "business"
  preconditions:
    - 用户账户标记为遗留版本许可
    - 系统已升级到新版本
  steps:
    - 用户登录系统
    - 导航到旧版本功能模块
  expected_results:
    - 旧版本功能按钮可见且可交互
    - API 返回兼容模式响应
    - 审计日志记录版本访问信息
  tags: [compatibility, legacy]
  auto: false
```

## 常见问题

**Q：ID 如何确保唯一性？**  
A：建议使用版本控制系统追踪，或在团队内部维护 ID 分配表。

**Q：如果用例不符合现有枚举值怎么办？**  
A：请先联系团队讨论是否需要扩展 `schema/test-case-schema.json`，再更新文档。

**Q：步骤和预期结果的数量有限制吗？**  
A：无严格限制，但建议保持简洁（步骤 3-5 条，结果 2-4 条），过于复杂的用例可拆分为多个用例。

**Q：`auto` 字段如何确定？**  
A：由自动化测试团队评估，通常 P0 和明确的功能性用例设为 `true`；复杂、依赖 UI 的用例可设为 `false`。

## 参考文档

- Schema 定义：[schema/test-case-schema.json](../schema/test-case-schema.json)
- 格式详解：[docs/test-case-format.md](./test-case-format.md)
- 示例文件：[releases/function-v1/login.yaml](../releases/function-v1/login.yaml)
