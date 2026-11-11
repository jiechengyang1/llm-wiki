# moma moma-space api POST_api_v1_tools_file_rename / file_move

> **Prerequisites:** Please read `../../moma-shared/SKILL.md` to understand login, permission handling, update notices, and security rules.

重命名或移动空间内文件/文件夹。高风险写操作：必须先 `dry_run:true` 预览源/目标。

## Recommended Commands

> **必须添加 `--json`。** 命令里的 apiName 必须是完整 Gateway 名；决策树短名不能直接当 api 参数。本 reference 已写清字段时直接 `api`，不要先 `schema`/`list`/`--help`。

```bash
# 重命名预览
moma moma-space api POST_api_v1_tools_file_rename --json --data '{
  "space_root":"<SPACE_id>",
  "task_id":"<TASK>",
  "filepath":"docs/old.md",
  "new_name":"new.md",
  "dry_run":true
}'

# 确认后执行
moma moma-space api POST_api_v1_tools_file_rename --json --yes --data '{
  "space_root":"<SPACE_id>",
  "task_id":"<TASK>",
  "filepath":"docs/old.md",
  "new_name":"new.md",
  "dry_run":false
}'

# 移动预览
moma moma-space api POST_api_v1_tools_file_move --json --data '{
  "space_root":"<SPACE_id>",
  "task_id":"<TASK>",
  "filepath":"docs/a.md",
  "target_dir":"archive",
  "dry_run":true
}'
```

## file_rename body

| 字段 | 是否必填 | 含义 |
|------|---------|------|
| `space_root` | **必填** | SPACE id |
| `task_id` | **必填** | 任务内复用 |
| `filepath` | **必填** | 源相对路径 |
| `new_name` | **必填** | 新文件名（不是完整路径） |
| `dry_run` | 强烈建议先 true | 预览源/目标 |

## file_move body

| 字段 | 是否必填 | 含义 |
|------|---------|------|
| `space_root` / `task_id` / `filepath` | **必填** | 同上 |
| `target_dir` | **必填** | 目标目录相对路径 |
| `dry_run` | 强烈建议先 true | 预览 |

## 响应结构

### dry_run 预览（示意）

```json
{
  "success": true,
  "dry_run": true,
  "source": "docs/old.md",
  "target": "docs/new.md"
}
```

向用户清晰展示 **source → target**，确认无误后再执行。

### 错误响应

| code | 含义 | Agent 处理 |
|------|------|-----------|
| `PERMISSION_DENIED` | 无权限 | 停止，不重试 |
| `FILE_NOT_FOUND` | 源不存在 | 核对 filepath |
| `FILE_EDIT_LOCKED` | 锁定 | 等待/告知用户 |
| `GATEWAY_CONFIRMATION_REQUIRED` | 需确认 | 按 moma-shared |
| 目标已存在 | 冲突 | 询问是否换名/换目录，不要静默覆盖 |

## Workflow

1. 确认源路径；不清楚时用 `files_children` / `search_files`。
2. `dry_run:true` 拿到 source/target。
3. 展示给用户，明确同意后 `dry_run:false` + `--yes`。
4. 参数若有改动，重新 dry-run。

## Notes

- `new_name` 只是名字，不含目录；跨目录用 `file_move`。
- 不要与 `delete_batch` 混用「先删再传」来完成重命名。
