# moma moma-space api POST_api_v1_tools_write_file

> **Prerequisites:** Please read `../../moma-shared/SKILL.md` to understand login, permission handling, update notices, and security rules.

创建、覆盖或追加文件内容。支持 `temporary:true` 草稿（scratch，不落库、免 `--yes`）与持久化写入（需确认）。

## Recommended Commands

> **必须添加 `--json`。** 命令里的 apiName 必须是完整 Gateway 名；决策树短名不能直接当 api 参数。本 reference 已写清字段时直接 `api`，不要先 `schema`/`list`/`--help`。

```bash
# 草稿（temporary:true，无需 --yes）
moma moma-space api POST_api_v1_tools_write_file --json --data '{
  "filepath":"report.md",
  "content":"draft line\n",
  "space_root":"<SPACE_id>",
  "task_id":"<TASK>",
  "temporary":true
}'

# 持久化写入：先 dry-run
moma moma-space api POST_api_v1_tools_write_file --json --dry-run --data '{
  "filepath":"docs/a.md",
  "content":"hello\n",
  "space_root":"<SPACE_id>",
  "task_id":"<TASK>",
  "expected_mtime":1710000000.0
}'

# 用户明确确认后
moma moma-space api POST_api_v1_tools_write_file --json --yes --data '{
  "filepath":"docs/a.md",
  "content":"hello\n",
  "space_root":"<SPACE_id>",
  "task_id":"<TASK>",
  "expected_mtime":1710000000.0
}'

# 追加
moma moma-space api POST_api_v1_tools_write_file --json --dry-run --data '{
  "filepath":"docs/a.md",
  "content":"more\n",
  "space_root":"<SPACE_id>",
  "task_id":"<TASK>",
  "append":true,
  "expected_mtime":1710000000.0
}'
```

## Options

```text
--data <json-string>   POST JSON body
--dry-run              预览高风险写（持久化）
--yes                  用户明确确认后执行
```

### body 参数

| 字段 | 是否必填 | 含义 |
|------|---------|------|
| `filepath` | **必填** | 目标相对路径（落库后的逻辑路径） |
| `content` | **必填** | 文件内容；多行用 `\n` |
| `space_root` | **必填** | SPACE id |
| `task_id` | **必填** | 任务内复用 |
| `temporary` | 可选 | `true` → 写入 `.ks_tmp/<task_id>/...`，不落库、不可搜索、免确认 |
| `append` | 可选 | `true` 追加；默认覆盖 |
| `expected_mtime` | 覆盖已有持久化文件时建议必填 | 优先从 `file_presigned_url` 响应获取；未返回时再从 `files_query` 获取 |

## 响应结构

### 草稿成功（temporary:true）

```json
{
  "success": true,
  "filepath": ".ks_tmp/<TASK>/report.md",
  "logical_path": "report.md",
  "mtime": 1710000000.5,
  "temporary": true
}
```

| 字段 | 含义 |
|------|------|
| `filepath` | **真实路径**；后续 read/patch/exec 必须用这个 |
| `logical_path` | 对用户展示的逻辑路径 |
| `mtime` | 草稿文件 mtime |

### 持久化成功

```json
{
  "success": true,
  "filepath": "docs/a.md",
  "mtime": 1710000001.0
}
```

### 错误响应

| code | 含义 | Agent 处理 |
|------|------|-----------|
| `GATEWAY_CONFIRMATION_REQUIRED` | 需要确认（exit 10） | 按 `moma-shared`：dry-run → 展示 → 明确 yes → `--yes` |
| `CONFLICT` | mtime 不匹配 | 重读拿新 mtime，再写 |
| `PROTECTED_FILE` | 写了 SPACE.md 等受保护文件 | **停止**；改走 `space_md_upsert` |
| `FILE_EDIT_LOCKED` | 文件被锁 | 告知用户，等待或换路径，不强行覆盖 |
| `PERMISSION_DENIED` | 无写权限 | **停止，不重试** |
| `INTERNAL_STATUS_TEXT` | 把工具响应当成了 content | 只写入真正业务内容，不要塞整段 tool JSON |

## Workflow

### 探索阶段写草稿

1. 使用 `temporary:true`，无需 `--yes`。
2. 保存返回的 `filepath`（`.ks_tmp/...`），后续操作跟这个路径。
3. 对用户只展示 `logical_path`。

### 持久化落库

1. 若目标已存在：先调用 `file_presigned_url`，若响应包含 `mtime` 则直接用于 `expected_mtime`；若未返回 `mtime`，再调用 `files_query` 单独获取 `mtime`（仅取该字段，忽略其他返回参数）。
2. 执行 `--dry-run`，向用户说明将写入的路径与影响。
3. **仅当用户明确同意本次预览** 后加 `--yes`；「好的/你弄吧」不算确认。
4. 若改了 body 任何字段，原确认失效，重新 dry-run。

## Notes

- **禁止**用本 API 写 `SPACE.md`（会 `PROTECTED_FILE`）。
- `temporary:true` 时风险视为豁免确认；一旦要落库仍须走确认协议。
- 不要同时带 `--dry-run` 和 `--yes` 当作真实执行。
