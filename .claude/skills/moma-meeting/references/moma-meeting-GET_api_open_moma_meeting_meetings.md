# moma meeting api GET_api_open_moma_meeting_meetings

> **Prerequisites:** Please read `../../moma-shared/SKILL.md` to understand login, permission handling, update notices, and security rules.

查询当前登录员工参与或相关的会议列表。

## Recommended Commands

> **必须添加 `--json`。** 本 Skill 的所有 `moma moma-meeting list/schema/api` 命令都必须添加 `--json`。

```bash
# 查看服务已接入 API
moma moma-meeting list --json

# 查看该 API 参数结构
moma moma-meeting schema GET_api_open_moma_meeting_meetings --json

# 查询会议列表，query 参数必须是 GET 顶层 query 参数，不要包成 req 或 JSON body
moma moma-meeting api GET_api_open_moma_meeting_meetings --json -q "startTime=<timestamp>&endTime=<timestamp>&pageNum=1&pageSize=20&sortOrder=desc"

# 示例：查询北京时间 2026-06-04 当天会议，秒级时间戳
moma moma-meeting api GET_api_open_moma_meeting_meetings --json -q "startTime=1780502400&endTime=1780588799&pageNum=1&pageSize=100&sortOrder=asc"

# 同一天也可使用毫秒级时间戳
moma moma-meeting api GET_api_open_moma_meeting_meetings --json -q "startTime=1780502400000&endTime=1780588799000&pageNum=1&pageSize=100&sortOrder=asc"
```

## Options

```text
-q, --query <querystring>   追加 query string，格式：key1=v1&key2=v2
```

常用 query 字段：

| 字段 | 含义 |
|------|------|
| `startTime` | 开始时间，支持秒级或毫秒级 Unix 时间戳；必须作为顶层 query 参数传入 |
| `endTime` | 结束时间，支持秒级或毫秒级 Unix 时间戳；必须作为顶层 query 参数传入 |
| `keyword` | 会议标题、名称或会议号关键词 |
| `organizer` | 组织者姓名或系统号关键词 |
| `meetingStatus` | 会议状态：`1=会议中`、`2=未开始`、`3=会议结束` |
| `pageNum` | 页码，从 1 开始 |
| `pageSize` | 每页数量，最大 100 |
| `sortOrder` | 排序方向：`asc` 或 `desc` |

## Time Parameters

- `startTime` / `endTime` 使用 Unix 时间戳，秒级 10 位或毫秒级 13 位都支持。
- 按北京时间 `Asia/Shanghai` 解释用户说的自然日期。
- 单日查询使用闭区间边界：`startTime=当天 00:00:00`，`endTime=当天 23:59:59`。
- 示例：`2026-06-04` 的秒级时间戳是 `startTime=1780502400&endTime=1780588799`；毫秒级是 `startTime=1780502400000&endTime=1780588799000`。
- query 必须写成顶层参数：`-q "startTime=...&endTime=..."`。不要写成 `req.startTime`、`req={...}`、`-d '{...}'` 或未加引号的 `&` 链式 shell 命令。

## Workflow

1. 确认用户要查询的时间范围、关键词、组织者、状态和分页要求。
2. 如果用户给的是自然语言日期，例如“六月四号”，先换算成北京时间当天的 `startTime/endTime`。
3. 如参数不明确，先执行 `moma moma-meeting schema GET_api_open_moma_meeting_meetings --json`。
4. 控制单次查询时间范围不超过 90 天。
5. 执行命令，确保 `-q` 的 query string 整体加引号。
6. 如果返回明显不是目标时间范围，不要把默认 30 天结果直接本地过滤；先检查 query 是否按顶层参数传入并重试。
7. 汇报会议标题、会议 ID、开始/结束时间、组织者、状态、是否已有转写、是否已有智能纪要。

## Notes

- `hasTranscription` 和 `hasSmartSummary` 只表示内容已生成，不代表当前用户一定有查看权限。
- 获取转写或纪要时仍会再次进行权限校验。
