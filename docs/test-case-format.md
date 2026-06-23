# 用例格式规范

本文档描述 `schema/test-case-schema.json` 中定义的 YAML 用例格式规范。该规范用于保证测试用例文档结构一致、字段完整、类型正确。

## 1. 根对象

| 字段 | 类型 | 是否必需 | 说明 | 约束 / 取值 |
|---|---|---|---|---|
| `metadata` | object | 是 | 用例集合的元信息 | 不允许额外字段 |
| `test_cases` | array | 是 | 用例对象列表 | 最少 1 条用例 |

## 2. `metadata` 对象

| 字段 | 类型 | 是否必需 | 说明 | 约束 / 取值 |
|---|---|---|---|---|
| `module` | string | 是 | 所属大模块 | 任意字符串 |
| `feature` | string | 是 | 当前文件聚焦功能 | 任意字符串 |
| `owner` | string | 是 | 负责人（英文名） | 任意字符串 |
| `last_reviewed` | string | 是 | 最后评审日期 | 格式 `YYYY-MM-DD` |
| `tags` | array[string] | 否 | 全局标签 | 字符串列表 |

> `metadata` 不允许额外字段，字段列表必须严格按照规范提供。

## 3. `test_cases` 数组

`test_cases` 必须为数组，且至少包含 1 个用例对象。

### 3.1 用例对象字段说明

| 字段 | 类型 | 是否必需 | 说明 | 约束 / 取值 |
|---|---|---|---|---|
| `id` | string | 是 | 全局唯一 ID | 正则 `^TC_[A-Z0-9_]{3,}_[0-9]{3}$` |
| `title` | string | 是 | 简洁动词开头的标题 | 任意字符串 |
| `description` | string | 否 | 补充说明 | 任意字符串 |
| `priority` | string | 是 | 优先级 | 取值：`P0`, `P1`, `P2` |
| `type` | string | 是 | 用例类型 | 取值：`functional`, `ui`, `security`, `performance`, `accessibility`, `business`, `other`, `data-consistency` |
| `preconditions` | array[string] | 否 | 执行前提 | 字符串列表 |
| `steps` | array[string] | 是 | 操作步骤（每步一句话） | 至少 1 条，字符串长度不为空 |
| `expected_results` | array[string] | 是 | 预期结果（可多条） | 至少 1 条，字符串长度不为空 |
| `tags` | array[string] | 否 | 用例级标签 | 字符串列表 |
| `auto` | boolean | 否 | 是否计划自动化 | 默认 `false` |

> 用例对象同样不允许额外字段，必须严格遵守规范中的字段名称和类型。

## 4. 编写建议

- `id` 应保证全局唯一，推荐使用模块简写 + 序号，例如 `TC_AUTH_LOGIN_001`。
- `title` 应该以动词开头，描述用例执行目标。
- `steps` 和 `expected_results` 中每一条应为简洁明确的自然语言句子。
- `priority` 和 `type` 应使用规范枚举值，避免自由文本。
- `last_reviewed` 必须使用 `YYYY-MM-DD` 日期格式。

## 5. 示例结构

```yaml
metadata:
  module: auth
  feature: login
  owner: alice
  last_reviewed: 2026-06-24
  tags:
    - regression

test_cases:
  - id: TC_AUTH_LOGIN_001
    title: 验证有效凭证可以登录
    description: 用户使用正确的用户名和密码登录系统。
    priority: P0
    type: functional
    preconditions:
      - 用户已在登录页面
    steps:
      - 输入有效用户名
      - 输入有效密码
      - 点击登录按钮
    expected_results:
      - 登录成功，进入控制台页面
      - 显示用户欢迎信息
    tags:
      - smoke
    auto: false
```
