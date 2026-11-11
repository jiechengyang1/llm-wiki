# moma moma-space api POST_api_v1_tools_upload_batch / delete_batch

> **Prerequisites:** Please read `../../moma-shared/SKILL.md` to understand login, permission handling, update notices, and security rules.

批量上传本地文件到空间，或按路径批量删除。均为 **high-risk-write**，必须走确认协议。

## Recommended Commands

> **必须添加 `--json`。** 命令里的 apiName 必须是完整 Gateway 名；决策树短名不能直接当 api 参数。本 reference 已写清字段时直接 `api`，不要先 `schema`/`list`/`--help`。

```bash
# 上传：无服务端 dry_run 字段，使用 MOMA --dry-run / --yes
# multipart 具体传参以 schema 为准（space_id + relative_paths + files）
# --file 用 field=path 格式，upload_batch 字段名为 files
moma moma-space api POST_api_v1_tools_upload_batch --json --dry-run --data '{
  "space_id":"<SPACE_id>",
  "relative_paths":["docs/a.md"],
  "overwrite":false
}' --file 'files=./a.md'

# 确认目标路径与文件后
moma moma-space api POST_api_v1_tools_upload_batch --json --yes --data '{
  "space_id":"<SPACE_id>",
  "relative_paths":["docs/a.md"],
  "overwrite":false
}' --file 'files=./a.md'

# 删除预览
moma moma-space api POST_api_v1_tools_delete_batch --json --data '{
  "space_id":"<SPACE_id>",
  "paths":["docs/old.md","docs/tmp/"],
  "dry_run":true
}'

# 用户明确确认后删除
moma moma-space api POST_api_v1_tools_delete_batch --json --yes --data '{
  "space_id":"<SPACE_id>",
  "paths":["docs/old.md","docs/tmp/"],
  "dry_run":false
}'
```

## upload_batch

### 请求字段（multipart）

| 字段 | 是否必填 | 含义 |
|------|---------|------|
| `space_id` | **必填** | SPACE id（与别处 `space_root` 同值） |
| `relative_paths` | **必填** | 目标相对路径数组的 JSON 字符串，与 files 一一对应 |
| `files` | **必填** | 本地文件内容（multipart 文件部分） |
| `overwrite` | 可选 | 默认 `false`；冲突后须再次确认再设 `true` |
| `parent_id` | 可选 | 父节点 id（一般不必传，用相对路径即可） |
| `trigger_parse` | 可选 | 默认 `true`，是否触发解析 |

### 成功响应示例

```json
{
  "total": 1,
  "success_count": 1,
  "failure_count": 0,
  "results": [
    {
      "index": 0,
      "relative_path": "docs/a.md",
      "success": true,
      "overwritten": false,
      "file": { "path": "docs/a.md", "name": "a.md", "type": "file" }
    }
  ],
  "message": "Batch upload completed"
}
```

### 上传 Workflow

1. **问清目标目录**；禁止默认猜空间根 `/` 或 `.`。
2. `list_spaces` 确认 SPACE id；必要时 `files_children` 确认目录存在。
3. `--dry-run` 展示将上传的本地文件 → 远端 `relative_paths`。
4. 用户明确同意后 `--yes`。
5. 若结果含冲突 / 失败：展示 `results[].error`；需要覆盖时再次确认 `overwrite=true`。

## delete_batch

### body 参数

| 字段 | 是否必填 | 含义 |
|------|---------|------|
| `space_id` | **必填** | SPACE id |
| `paths` | **必填** | 待删相对路径列表（至少 1 个） |
| `dry_run` | 强烈建议先 true | `true` 只预览；`false` 才真正删除 |

### 成功响应示例

```json
{
  "total": 1,
  "deleted_count": 1,
  "results": [
    {
      "path": "docs/old.md",
      "success": true,
      "status": "deleted",
      "deleted_count": 1
    }
  ],
  "message": "Batch delete completed"
}
```

### dry_run 预览

`dry_run:true` 时不会真正删除；向用户展示将删除的路径与数量，获得明确同意后再 `dry_run:false` + `--yes`。

## 错误响应（共用）

| code | 含义 | Agent 处理 |
|------|------|-----------|
| `GATEWAY_CONFIRMATION_REQUIRED` | 需确认 | 按 moma-shared 协议 |
| `PERMISSION_DENIED` | 无权限 | **停止，不重试** |
| `FILE_EDIT_LOCKED` | 路径被锁 | 告知用户，不要强删 |
| `FILE_NOT_FOUND` | 路径不存在 | 核对 paths；不要重复盲删 |
| 部分失败 | `results` 中有 `success:false` | 逐条汇报，不要声称全部成功 |

## Notes

- 上传/删除字段名是 **`space_id`**，不是 `space_root`。
- 删除不可逆；预览步骤不可跳过。
- 不要把本机路径写进 `paths` / `relative_paths`（那是空间内相对路径）。
