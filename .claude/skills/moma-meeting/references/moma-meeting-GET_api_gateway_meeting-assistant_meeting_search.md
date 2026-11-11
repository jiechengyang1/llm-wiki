# moma meeting api GET_api_gateway_meeting-assistant_meeting_search

> **Prerequisites:** Please read `../../moma-shared/SKILL.md` to understand login, permission handling, update notices, and security rules.

查询当前登录员工参与或相关的会议列表。支持按会议类型、时间范围、关键词、主持人等条件筛选。

## Recommended Commands

> **必须添加 `--json`。** 本 Skill 的所有 `moma moma-meeting list/schema/api` 命令都必须添加 `--json`。

```bash
# 查看服务已接入 API
moma moma-meeting list --json

# 查看该 API 参数结构
moma moma-meeting schema GET_api_gateway_meeting-assistant_meeting_search --json

# 查询会议列表 — meetingType 必填
moma moma-meeting api GET_api_gateway_meeting-assistant_meeting_search --json -q "meetingType=3&startTime=<timestamp>&endTime=<timestamp>&pageNum=1&pageSize=20&sortOrder=desc&keyword=<keyword>&host=<host>"

# 示例：查询北京时间 2026-06-22 ~ 2026-06-28 历史会议，秒级时间戳
moma moma-meeting api GET_api_gateway_meeting-assistant_meeting_search --json -q "meetingType=3&startTime=1782057600&endTime=1782662399&pageNum=1&pageSize=100&sortOrder=desc"
```

## Options

```text
-q, --query <querystring>   追加 query string，格式：key1=v1&key2=v2
-p, --path-params <params>  路径参数，格式：key1=v1&key2=v2（当前 API 无路径参数）
```

常用 query 字段：

| 字段 | 是否必填 | 含义 |
|------|---------|------|
| `meetingType` | **必填** | 会议类型：`1=进行中`、`2=未开始`、`3=历史`、`4=近期会议`、`5=取消` |
| `startTime` | 可选 | 按会议开始时间过滤：开始时间，支持秒级或毫秒级 Unix 时间戳 |
| `endTime` | 可选 | 按会议开始时间过滤：结束时间，支持秒级或毫秒级 Unix 时间戳 |
| `keyword` | 可选 | 会议标题、名称或会议号关键词 |
| `host` | 可选 | 会议主持人姓名或系统号关键词 |
| `pageNum` | 可选 | 页码，从 1 开始（默认 1） |
| `pageSize` | 可选 | 每页数量，最大 100（默认 100） |
| `sortOrder` | 可选 | 排序方向：`asc` 或 `desc`（默认 desc） |

## 各 meetingType 说明

| meetingType | 含义 | 数据来源 |
|-------------|------|---------|
| `1` | 进行中（DOING） | 当前正在进行的会议 |
| `2` | 未开始（FUTURE） | 尚未开始的预约会议 |
| `3` | 历史（HISTORY） | 已结束的会议 — **查上周/上月会议用此类型** |
| `4` | 近期会议（RECENT） | 进行中 + 未开始的合集 |
| `5` | 取消（CANCEL） | 已取消的会议 |

> **注意**：`meetingType=3`（历史）先按用户查询所有历史会议，再在本地对结果按 `startTime`/`endTime`/`keyword`/`host` 做过滤。因此如果用户没有历史会议数据，即使传入时间范围也会返回 0 条。

## Time Parameters

- `startTime` / `endTime` 使用 Unix 时间戳，秒级 10 位或毫秒级 13 位都支持。
- 按北京时间 `Asia/Shanghai` 解释用户说的自然日期。
- 单日查询使用闭区间边界：`startTime=当天 00:00:00`，`endTime=当天 23:59:59`。
- 示例：`2026-06-04` 的秒级时间戳是 `startTime=1780502400&endTime=1780588799`；毫秒级是 `startTime=1780502400000&endTime=1780588799000`。
- query 必须写成顶层参数：`-q "startTime=...&endTime=..."`。不要写成 `req.startTime`、`req={...}`、`-d '{...}'` 或未加引号的 `&` 链式 shell 命令。

## 响应格式

所有响应使用统一信封格式。成功时 `errno=0`，`data.meetings` 为会议数组：

```json
{
  "errno": 0,
  "errmsg": "成功",
  "data": {
    "pageNum": 1,
    "pageSize": 100,
    "total": 1,
    "meetings": [
      {
        "meetingId": "会议实例ID",
        "meetingCode": "会议号",
        "title": "会议标题",
        "startTime": 1782057600000,
        "endTime": 1782662399000,
        "organizer": null,
        "organizerUserCode": null,
        "meetingStatus": 3,
        "meetingStatusName": "会议结束",
        "hasTranscription": true,
        "hasSmartSummary": false
      }
    ]
  }
}
```

| data.meetings 字段 | 含义 |
|---------|------|
| `meetingId` | 会议实例 ID |
| `meetingCode` | 会议号 |
| `title` | 会议标题 |
| `startTime` | 毫秒级 Unix 时间戳 |
| `endTime` | 毫秒级 Unix 时间戳 |
| `organizer` | 组织者（可能为 null） |
| `meetingStatus` | 会议状态码：`1=会议中`、`2=未开始`、`3=会议结束` |
| `meetingStatusName` | 会议状态中文名 |
| `hasTranscription` | 是否已有转写（不代表当前用户有查看权限） |
| `hasSmartSummary` | 是否已有智能纪要（不代表当前用户有查看权限） |

### 错误响应

| errno | 含义 | Agent 处理 |
|-------|------|-----------|
| `40001` | 参数错误 | 检查参数（meetingType 是否传入、时间戳格式、时间范围是否超 90 天、pageSize 是否超 100），修正后重试 |
| `50001` | 服务不可用 | 告知用户服务暂不可用，稍后重试（retryable=true） |

## Workflow

1. 确认用户要查询的 **meetingType** 和时间范围、关键词、主持人、分页要求。
2. 如果用户给的是自然语言日期，例如"六月四号"，先换算成北京时间当天的 `startTime/endTime`。
3. 如参数不明确，先执行 `moma moma-meeting schema GET_api_gateway_meeting-assistant_meeting_search --json`。
4. 控制单次查询时间范围不超过 90 天。
5. 执行命令，`meetingType` 参数必须传入，确保 `-q` 的 query string 整体加引号。
6. 判断 `errno`：
   - **`errno=0`**：成功，`data.meetings` 为会议列表，按业务逻辑展示。
   - **`errno=40001`**：检查参数后重试。
   - **`errno=50001`**：告知用户服务暂不可用。
7. 如果返回明显不是目标时间范围，不要把默认结果直接本地过滤；先检查 query 是否按顶层参数传入并重试。
8. 汇报会议标题、会议 ID、开始/结束时间、主持人、状态、是否已有转写、是否已有智能纪要。

## Notes

- `hasTranscription` 和 `hasSmartSummary` 只表示内容已生成，不代表当前用户一定有查看权限。
- 获取转写或纪要时仍会再次进行权限校验。
- 后端使用 `X-Moma-CLI-UCID` 请求头获取当前用户身份，由 moma CLI 自动注入。
