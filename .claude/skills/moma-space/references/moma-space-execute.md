# moma moma-space api POST_api_v1_tools_execute_command

> **Prerequisites:** Please read `../../moma-shared/SKILL.md` to understand login, permission handling, update notices, and security rules.

在空间存储上下文中执行 shell 命令来读文件，如通过`pdftotext/pdfinfo`读pdf文件中的文本内容。

## Recommended Commands

> **必须添加 `--json`。** 命令里的 apiName 必须是完整 Gateway 名；决策树短名不能直接当 api 参数。本 reference 已写清字段时直接 `api`，不要先 `schema`/`list`/`--help`。

```bash
# 只读命令
moma moma-space api POST_api_v1_tools_execute_command --json --data '{
  "command":"ls -la docs",
  "space_root":"<SPACE_id>",
  "task_id":"<TASK>",
  "exec_intent":"read",
  "timeout":30
}'

```

## execute_command body

| 字段 | 是否必填 | 含义                          |
|------|---------|-----------------------------|
| `command` | **必填** | shell 命令                    |
| `space_root` / `task_id` | **必填** | 上下文                         |
| `exec_intent` | **必填** | 执行意图，当前仅支持读文件，必须指定值为：`read` |
| `workdir` | 可选 | 工作目录（相对空间）                  |
| `timeout` | 可选 | 秒，默认 30，最大 300              |


## 响应结构

```json
{
  "success": true,
  "stdout": "...",
  "stderr": "",
  "exit_code": 0
}
```

以 CLI 实际字段名为准；向用户转述 stdout/stderr 时不要夹带鉴权信息。

### 错误响应

| code | 含义               | Agent 处理                              |
|------|------------------|---------------------------------------|
| `EXEC_INTENT_MISMATCH` | 声明的 intent 弱于实际影响 | 请勿进行非read操作                           |
| `EXEC_PATHS_UNRESOLVED` | 代码/命令中路径无法解析     | 路径必须在代码里以字面量出现（如 `open('docs/a.md')`） |
| `PERMISSION_DENIED` | 无权限              | 停止                                    |
| `GATEWAY_CONFIRMATION_REQUIRED` | 非read操作需确认       | 按 moma-shared                         |

## Workflow

1. 能用其他 API 如 `file_presigned_url` / `search_files` / `files_children` 完成的，不要用 exec。
2. 字段 `exec_intent` 只能传 `read`，禁止传其他值。
3. 不支持：`cd`、递归 `grep`/`find`、直接跑脚本文件（如 `python build.py`）——改用对应 Tools API。



