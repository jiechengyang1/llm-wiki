# moma moma-space api POST_api_v1_tools_space-md_upsert

> **Prerequisites:** Please read `../../moma-shared/SKILL.md` to understand login, permission handling, update notices, and security rules.

结构化更新目录下的 `SPACE.md`。这是更新 SPACE.md 的 **唯一** 合法写入口；`write_file` / `write_patch` 会返回 `PROTECTED_FILE`。

## Recommended Commands

> **必须添加 `--json`。** 命令里的 apiName 必须是完整 Gateway 名；决策树短名不能直接当 api 参数。本 reference 已写清字段时直接 `api`，不要先 `schema`/`list`/`--help`。

```bash
# 先 search 定位并解锁现有 SPACE.md（若本轮已 @该文件，可直接 read + edit_intent=true）
moma moma-space api POST_api_v1_tools_kb-search_files --json --data '{
  "task_id":"<TASK>",
  "query":"SPACE.md",
  "mode":"file_name",
  "space_ids":["<SPACE_id>"]
}'

# 再读现有 SPACE.md（可选但推荐）
mkdir -p /tmp/.moma-tmp && moma moma-space api POST_api_v1_tools_file_presigned_url --json --data '{"filepath":"SPACE.md","space_root":"<SPACE_root>","task_id":"<TASK>"}' > /tmp/.moma-tmp/resp.json
URL=$(python3 -c "import sys,json; print(json.load(sys.stdin)['url'])" < /tmp/.moma-tmp/resp.json) && MTIME=$(python3 -c "import sys,json; print(json.load(sys.stdin).get('mtime', ''))" < /tmp/.moma-tmp/resp.json) && curl -sSfL -o "/tmp/.moma-tmp/SPACE.md" "$URL"

# CLI 预览最终真实请求：不调用服务端，body 与确认后执行保持一致
moma moma-space api POST_api_v1_tools_space-md_upsert --json --dry-run --data '{
  "space_root":"<SPACE_id>",
  "directory":"",
  "sections":[
    {"heading":"目录用途","content":"本目录存放团队对接文档。"},
    {"heading":"关键文件","content":"- `docs/流程.md`：主流程说明"}
  ],
  "expected_mtime":1710000000.0,
  "dry_run":false
}'

# 用户针对上述预览明确确认后：仅移除 --dry-run、追加 --yes
moma moma-space api POST_api_v1_tools_space-md_upsert --json --yes --data '{
  "space_root":"<SPACE_id>",
  "directory":"",
  "sections":[
    {"heading":"目录用途","content":"本目录存放团队对接文档。"},
    {"heading":"关键文件","content":"- `docs/流程.md`：主流程说明"}
  ],
  "expected_mtime":1710000000.0,
  "dry_run":false
}'
```

## Options

```text
--data <json-string>   POST JSON body
--dry-run / --yes      高风险确认（dry_run=false 时）
```

### body 参数

| 字段 | 是否必填 | 含义 |
|------|---------|------|
| `space_root` | **必填** | SPACE id |
| `sections` | **必填** | `{heading, content}[]`，1–6 条，heading 不可重复 |
| `directory` | 可选 | 相对目录；空间根用 `""`（默认） |
| `expected_mtime` | 可选 | 冲突检测 |
| `dry_run` | MOMA 真实流程固定为 false | `true` 仅是服务端预览语义，**不会**降低 Gateway 静态风险；MOMA Agent 用 CLI `--dry-run` 预览最终请求 |

### 允许的 `heading`（必须完全匹配）

| heading |
|---------|
| `目录用途` |
| `关键文件` |
| `子目录导航` |
| `检索关键词` |
| `Agent 注意事项` |
| `待确认事项` |

其它 heading 会被校验拒绝。

## 响应结构

### dry_run 预览（示意）

```json
{
  "success": true,
  "dry_run": true,
  "filepath": "SPACE.md",
  "content": "# 空间标题\n\n## 目录用途\n\n...\n",
  "mtime": null
}
```

### 写入成功（示意）

```json
{
  "success": true,
  "dry_run": false,
  "filepath": "SPACE.md",
  "mtime": 1710000010.0
}
```

向用户展示将变更的章节摘要；完整 `content` 可按需展示。

### 错误响应

| code | 含义 | Agent 处理 |
|------|------|-----------|
| `PROTECTED_FILE`（来自误用 write/patch） | 禁止普通写 | 改用本 API |
| validation（非法 heading / 重复 heading） | 参数错误 | 改成允许的 heading 后重试 |
| `CONFLICT` | mtime 冲突 | 重读 SPACE.md，带新 mtime |
| `PERMISSION_DENIED` | 无权限 | 停止并让用户找管理员/owner，不重试 |
| `SPACE_MD_AUTH_REQUIRED` | 未带 Moma-Token（未 login） | `moma login "$MOMA_SPACE_TOKEN"` 后重试 |
| `SPACE_MD_GENERATOR_REQUIRED` / `CLI_USER_AGENT_REQUIRED` | 仅旧 Hermes/ks-cli 脚本路径 | `moma` 登录后不应再出现；不要用 write_file 绕过 |
| `GATEWAY_CONFIRMATION_REQUIRED` | 需确认 | 按 moma-shared：dry-run → 确认 → `--yes` |
| schema 返回 `read` / unknown / `GATEWAY_INVALID_RISK` | Gateway 风险注册漂移 | **停止真实写入**；不得降级为仅靠语言确认，联系平台用最新公开 OpenAPI 重注册 |

## Workflow

1. 确认目标 `directory`（根或子目录）。
2. 先 search 解锁，再 `file_presigned_url` 下载现有 `SPACE.md`，避免覆盖有用章节。
3. 只提交需要更新的 `sections`（未提交的章节会按服务端合并规则保留/重排）。
4. 用 CLI `--dry-run` 预览 body 中 `dry_run:false` 的最终真实请求。
5. 用户明确同意后，保持所有业务参数不变，移除 `--dry-run`、追加 `--yes` 执行。
6. 不要用 `write_file` / `write_patch`「图省事」改 SPACE.md。

## Notes

- `heading` 必须与上表完全一致（中文）。
- 本 operation 静态注册为 **high-risk-write**；body `dry_run:true` 不会把 schema 降为 read。
- SPACE.md 可在 search 解锁后做定向；写只能走本 operationId。
