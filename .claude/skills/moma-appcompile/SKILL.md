---
name: moma-appcompile
version: 1.0.0
description: "遇到`moma-appcompile`、操作 MOMA 应用（App Build）数据资源（数据库表/对象存储桶/数据库函数）、或用户提到「查应用表结构」「列桶文件」「执行只读 SQL」时，立即使用本 Skill 通过 `moma moma-appcompile api <apiName>` 操作。apiName 用完整 Gateway 名；字段名只用 API 属性名。"
metadata:
  requires:
    bins: ["moma"]
  cliHelp: "moma --help"
---

# MOMA App Compile（moma-appcompile）

**CRITICAL — 本 Skill 的 `<service>` 固定为 `moma-appcompile`。所有命令必须使用 `moma moma-appcompile ...`。**
**CRITICAL — 使用 `moma` CLI；不要直接 curl 业务域名或手工拼鉴权头。**
**CRITICAL — 开始前 MUST 先用 Read 工具读取 [`../moma-shared/SKILL.md`](../moma-shared/SKILL.md)，其中包含登录、权限处理、更新和安全规则。**
**CRITICAL — 本业务 Skill 只能补充业务域规则，不得覆盖或放宽 `moma-shared` 中的登录、权限、敏感信息和高风险确认要求。**
**CRITICAL — `moma moma-appcompile ...` 必须作为宿主命令工具的顶层进程执行；禁止通过远端 subprocess、`os.system`、`sh -c` 或 `shell=true` 包装。**
**CRITICAL — 下方表格里的 apiName 必须照抄，禁止短名或自拼。**
**CRITICAL — 所有写/查询操作只允许针对调用者自有应用（`chat_id` 必须是当前用户 owner 的应用），非 owner 返回 `errno=404 应用不存在或已删除`（后端不区分"不存在"与"无权访问"）。**

## 首轮路由

- **应用数据资源操作：** 用户提到「查表」「列桶」「执行 SQL」「查应用子资源」「列出我的应用」时，加载本 Skill。
- **chat_id 定位：** 若用户只给出应用名/标题而非 `chat_id`，先用 [`list`](references/moma-appcompile-list.md) 精确映射后再继续；多个命中时让用户选择，不取第一项。
- **认证分流：** 未登录时停止业务调用并提示用户先完成登录，不要求终端执行 `moma login`。

## 快速决策

- 列出我的应用 → [`list`](references/moma-appcompile-list.md)
- 列出应用的数据库表 → [`tables`](references/moma-appcompile-tables.md)
- 查看某表的列信息 → [`columns`](references/moma-appcompile-columns.md)
- 列出对象存储桶 → [`buckets`](references/moma-appcompile-buckets.md)
- 列出桶内文件 → [`objects`](references/moma-appcompile-objects.md)
- 执行只读 SQL / 列桶文件（统一入口） → [`query`](references/moma-appcompile-query.md)
## API 命令表

| 动作 | apiName（照抄） | 详情 |
|------|----------------|------|
| 列出自有应用 | `GET_api_moma-app-build_list` | [ref](references/moma-appcompile-list.md) |
| 列出应用数据库表 | `GET_api_moma-app-build_tables` | [ref](references/moma-appcompile-tables.md) |
| 获取表列信息 | `GET_api_moma-app-build_columns` | [ref](references/moma-appcompile-columns.md) |
| 列出对象存储桶 | `GET_api_moma-app-build_buckets` | [ref](references/moma-appcompile-buckets.md) |
| 列出桶内文件 | `GET_api_moma-app-build_objects` | [ref](references/moma-appcompile-objects.md) |
| 执行只读 SQL / 列桶文件 | `POST_api_moma-app-build_query` | [ref](references/moma-appcompile-query.md) |

## 权限与错误处理

后端为避免泄露资源存在性，对"不存在"与"无权访问"统一返回 `errno=404`；写操作 / 参数错误统一 `errno=400`。

| code / 情况 | 含义 | Agent 处理 |
|-------------|------|-----------|
| `401` / `NOT_AUTHENTICATED` | 未登录 | 停止业务调用，提示用户先登录 |
| `errno=404` + `应用不存在或已删除` | chat_id 不存在，或存在但当前用户不是 owner（后端不区分二者） | 停止调用；先用 `list` 让用户确认自己有权访问的 chat_id，再重试 |
| `errno=404` + `表 '...' 不存在，可用表：...` | 表名拼错或不存在 | 从 `errmsg` 的"可用表"列表中就近匹配，转述让用户选，再重试 |
| `errno=404` + `Not Found`（gateway 层） | apiName 拼错 | 检查 apiName 是否照抄本 Skill 表格中的完整名 |
| `errno=400` + SQL 相关 | 提交了 DDL / DML / 语法错的 SQL；后端只放行 `SELECT` / `WITH` | 转述 `errmsg`，修正 SQL 后重试一次 |
| `errno=400` + 其他参数错 | body / query 缺字段 | 按 `errmsg` 补齐参数重试 |
| 空 `items` | 应用无表/桶/文件 | 如实告知，不编造数据 |

## 安全规则

- 不输出 API Key、AccessToken、鉴权头。
- `query` 接口的 SQL 仅允许只读（SELECT / EXPLAIN）；禁止提交 DDL、DML（INSERT / UPDATE / DELETE）。
- 不得操作非当前用户自有的应用（非 owner 会 403，不绕过）。
- 不得把业务数据静默写入本地文件系统（用户明确要求除外）。

## References

- [列出自有应用 list](references/moma-appcompile-list.md)
- [列出数据库表 tables](references/moma-appcompile-tables.md)
- [获取表列信息 columns](references/moma-appcompile-columns.md)
- [列出对象存储桶 buckets](references/moma-appcompile-buckets.md)
- [列出桶内文件 objects](references/moma-appcompile-objects.md)
- [执行只读 SQL / 列桶文件 query](references/moma-appcompile-query.md)
