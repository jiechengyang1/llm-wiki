# moma moma-space api GET_api_v1_tools_files_children / files_query / files_query_batch

> **Prerequisites:** Please read `../../moma-shared/SKILL.md` to understand login, permission handling, update notices, and security rules.

列出某目录下一层可读子项，或查询路径的 ID 与读/写/删权限。持久化写/删前建议先探测权限；Claude Code 文本 `@/kespace` 引用在 search 前必须用 `files_query` 解析可见圈定 ID。

## Recommended Commands

> **必须添加 `--json`。** 命令里的 apiName 必须是完整 Gateway 名；决策树短名不能直接当 api 参数。本 reference 已写清字段时直接 `api`，不要先 `schema`/`list`/`--help`。

```bash
# 列空间根目录
moma moma-space api GET_api_v1_tools_files_children --json --query "space_root=<SPACE_id>&path="

# 列子目录
moma moma-space api GET_api_v1_tools_files_children --json --query "space_root=<SPACE_id>&path=docs"

# 单路径权限
moma moma-space api GET_api_v1_tools_files_query --json --query "space_root=<SPACE_id>&path=docs/a.md"

# 批量权限
moma moma-space api POST_api_v1_tools_files_query --json --data '{
  "space_root":"<SPACE_id>",
  "paths":["docs/a.md","docs/b.md"]
}'
```

## files_children（GET）

| 字段 | 是否必填 | 含义 |
|------|---------|------|
| `space_root` | **必填** | SPACE id |
| `path` | 可选 | 相对目录；空或省略 = 空间根 |

### 响应要点

每条常见字段：

| 字段 | 含义 |
|------|------|
| `name` / `path` | 名称与相对路径 |
| `type` | `file` 或 `folder` |
| `readable` / `editable` / `deletable` | 权限提示 |
| `is_locked` | 是否锁定 |

只返回当前用户**可读**的条目（与网页树一致）。

## files_query（GET）

| 字段 | 是否必填 | 含义 |
|------|---------|------|
| `space_root` | **必填** | SPACE id |
| `path` | **必填** | 要探测的相对路径 |

### 响应要点

| 字段 | 含义                                                  |
|------|-----------------------------------------------------|
| `exists` | 路径是否存在                                              |
| `file_id` | 文件或文件夹 ID；后续应用如： search 的 `file_id`（`list[str]`）|
| `type` | `file` 或 `folder`，决定使用哪个 ID 数组                      |
| `readable` / `editable` / `deletable` | 当前用户权限                                              |
| `path` | 服务端规范化后的相对路径                                        |

## files_query_batch（POST）

| 字段 | 是否必填 | 含义 |
|------|---------|------|
| `space_root` | **必填** | SPACE id |
| `paths` | **必填** | 路径数组，1–200 条 |

## 错误响应

| code | 含义 | Agent 处理 |
|------|------|-----------|
| `PERMISSION_DENIED` | 无权限看该路径 | 停止并让用户找管理员/owner；仅路径带前导 `/` 时可去掉后重试一次 |
| `FILE_NOT_FOUND` / `exists=false` | 路径不存在 | 跟 `did_you_mean` / `hint`；必要时回到上层 `files_children`，不得自行改写路径 |

## Workflow

1. Claude Code 收到 `@/kespace/<space>/<path>` 或 Space ID + path：先确定 Space ID，再对完整相对路径调用 `files_query`。
2. 若 `type=file`，把 `file_id` 值放入后续 search 的 `file_id` 数组（`list[str]`）。普通 `@cli.py` / `@src/cli.py` 是本地路径，不调用本 API。
3. 不知道目录结构时，从 `path=`（根）开始逐层 `files_children`。
4. 写/删前对目标路径 `files_query`；`editable`/`deletable` 为 false 则先告知用户。
5. 批量操作前用 `files_query_batch` 一次探测。

## Notes

- 这是一层列表，不是递归树；需要深层内容继续对子 folder 调用。
- 列表里的 `editable` 提示不能替代真实写时的权限校验。
- **`path` 不要前导 `/`**：用 `docs` / `20260513 家装例会`，不要用 `/docs`。
  UI/DB 展示常带 `/`，调用前先去掉，否则可能被误判为无权限。
