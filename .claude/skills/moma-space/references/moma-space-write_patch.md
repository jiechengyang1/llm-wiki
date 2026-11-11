# moma moma-space api POST_api_v1_tools_write_patch

> **Prerequisites:** Please read `../../moma-shared/SKILL.md` to understand login, permission handling, update notices, and security rules.

对已有文件做精确编辑。优先于整文件 `write_file` 覆盖。支持字符串替换（`mode=replace`）与 V4A patch（`mode=patch`）。

## Recommended Commands

> **必须添加 `--json`。** 命令里的 apiName 必须是完整 Gateway 名；决策树短名不能直接当 api 参数。本 reference 已写清字段时直接 `api`，不要先 `schema`/`list`/`--help`。

```bash
mkdir -p /tmp/.moma-tmp && moma moma-space api POST_api_v1_tools_file_presigned_url --json --data '{"filepath":"notes.md","space_root":"<SPACE_root>","task_id":"<TASK>"}' > /tmp/.moma-tmp/resp.json
URL=$(python3 -c "import sys,json; print(json.load(sys.stdin)['url'])" < /tmp/.moma-tmp/resp.json) && MTIME=$(python3 -c "import sys,json; print(json.load(sys.stdin).get('mtime', ''))" < /tmp/.moma-tmp/resp.json) && curl -sSfL -o "/tmp/.moma-tmp/notes.md" "$URL"

# 1b) 若 file_presigned_url 未返回 mtime，再用 files_query 单独获取 mtime，忽略其他字段的返回
moma moma-space api GET_api_v1_tools_files_query --json -q "space_root=<SPACE_id>&path=notes.md"

# 2) 字符串替换预览
moma moma-space api POST_api_v1_tools_write_patch --json --dry-run --data '{
  "filepath":"notes.md",
  "space_root":"<SPACE_id>",
  "task_id":"<TASK>",
  "mode":"replace",
  "old_string":"旧文本，尽量带上下文保证唯一",
  "new_string":"新文本",
  "replace_all":false,
  "expected_mtime":1710000000.0
}'

# 3) 用户明确确认后执行
moma moma-space api POST_api_v1_tools_write_patch --json --yes --data '{
  "filepath":"notes.md",
  "space_root":"<SPACE_id>",
  "task_id":"<TASK>",
  "mode":"replace",
  "old_string":"旧文本，尽量带上下文保证唯一",
  "new_string":"新文本",
  "expected_mtime":1710000000.0
}'
```

## Options

```text
--data <json-string>   POST JSON body
--dry-run / --yes      高风险确认协议（见 moma-shared）
```

### body 参数

| 字段 | 是否必填 | 含义 |
|------|---------|------|
| `filepath` | **必填** | 相对路径（或 scratch 返回的真实 `filepath`） |
| `space_root` | **必填** | SPACE id |
| `task_id` | **必填** | 任务内复用 |
| `mode` | 可选 | `replace`（默认）或 `patch` |
| `old_string` | `mode=replace` 时需要 | 被替换原文；应唯一，可加上下文 |
| `new_string` | `mode=replace` 时需要 | 替换后文本 |
| `replace_all` | 可选 | `true` 替换全部匹配；默认 false |
| `patch` | `mode=patch` 时需要 | V4A 正文（含 `*** Begin Patch` / `*** End Patch`） |
| `expected_mtime` | 编辑已有持久化文件时强烈建议 | 优先从 `file_presigned_url` 响应获取；未返回时再从 `files_query` 获取 |

## 响应结构

### 成功

```json
{
  "success": true,
  "filepath": "notes.md",
  "mtime": 1710000002.0,
  "replacements": 1
}
```

| 字段 | 含义 |
|------|------|
| `mtime` | 新 mtime；后续继续编辑要用新值 |
| `replacements` / 变更摘要 | 实际替换次数或 patch 结果（以返回为准） |

### 错误响应

| code | 含义 | Agent 处理 |
|------|------|-----------|
| `GATEWAY_CONFIRMATION_REQUIRED` | 需要确认 | dry-run → 明确 yes → `--yes` |
| `CONFLICT` | mtime 冲突 | **重读**，用新 `mtime` 重建 patch，不要盲重试同一 body |
| `PROTECTED_FILE` | 试图 patch SPACE.md | 停止；改 `space_md_upsert` |
| `FILE_EDIT_LOCKED` | 文件锁定 | 告知用户，等待解锁 |
| `PERMISSION_DENIED` | 无写权限 | 停止并让用户找管理员/owner，不重试 |
| old_string 未命中 / 多次命中 | 替换失败 | 收紧或放宽上下文；`replace_all` 仅在用户意图明确时使用 |

## Workflow

1. 确认目标是本轮 @ref 文件；用 `file_presigned_url` 下载获取当前内容，若响应包含 `mtime` 则直接使用；若未返回 `mtime`，再调用 `files_query` 单独获取 `mtime`（仅取该字段，忽略其他返回参数）。若不是 @ref，先按 search 流程解锁。
2. 构造最小、唯一的 `old_string`（必要时包含前后几行）。
3. `--dry-run` 展示将改动的片段；等用户明确同意。
4. `--yes` 执行；检查返回的新 `mtime`。
5. 若 `CONFLICT`：完整重读 → 重新构造 old/new → 再 dry-run/确认。

## Notes

- 优先 patch，避免整文件 rewrite 丢他人并发修改。
- 禁止 patch `SPACE.md`。
- 模糊附和语不能当作确认。
