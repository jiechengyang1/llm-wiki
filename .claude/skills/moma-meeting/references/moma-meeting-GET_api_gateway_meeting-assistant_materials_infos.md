# moma meeting api GET_api_gateway_meeting-assistant_materials_infos

> **Prerequisites:** Please read `../../moma-shared/SKILL.md` to understand login, permission handling, update notices, and security rules.

获取指定会议的会议材料、会议信息（会议详情）和智能纪要。支持按会议 ID 列表或按时间范围查询。

## Recommended Commands

> **必须添加 `--json`。** 本 Skill 的所有 `moma moma-meeting list/schema/api` 命令都必须添加 `--json`。

```bash
# 查看该 API 参数结构
moma moma-meeting schema GET_api_gateway_meeting-assistant_materials_infos --json

# 按会议 ID 列表查询（获取会议材料+信息）
moma moma-meeting api GET_api_gateway_meeting-assistant_materials_infos --json -q "meetingInstanceIds=7409534133326162298"

# 按会议 ID 列表查询并同时获取智能纪要
moma moma-meeting api GET_api_gateway_meeting-assistant_materials_infos --json -q "meetingInstanceIds=7409534133326162298&includeSmartSummary=true"

# 按时间范围查询（meetingStartTime/meetingEndTime 格式 yyyy-MM-dd HH:mm:ss）
moma moma-meeting api GET_api_gateway_meeting-assistant_materials_infos --json -q "meetingStartTime=2026-07-01 00:00:00&meetingEndTime=2026-07-01 23:59:59&includeSmartSummary=true"
```

## Options

```text
-q, --query <querystring>   追加 query string，格式：key1=v1&key2=v2
```

query 参数：

| 字段 | 是否必填 | 含义 |
|------|---------|------|
| `meetingInstanceIds` | 二选一 | 会议实例 ID 列表（按 ID 查询时使用；多个 ID 以逗号分隔） |
| `meetingStartTime` | 二选一 | 会议开始时间范围起点，格式 `yyyy-MM-dd HH:mm:ss` |
| `meetingEndTime` | 二选一 | 会议开始时间范围终点，格式 `yyyy-MM-dd HH:mm:ss` |
| `includeSmartSummary` | 可选 | `true` 则额外返回 `smartSummary` 字段（默认 false） |

> `meetingInstanceIds` 与 `meetingStartTime`+`meetingEndTime` 二选一，不可同时为空。

## 响应结构

返回以会议 ID 为 key 的对象，每个会议包含：

| 字段 | 含义 |
|------|------|
| `meetingInfo` | 会议基本信息：meetingId、meetingCode、title、startTime、endTime、organizer、organizerUserCode、meetingStatus、meetingStatusName、hasTranscription、hasSmartSummary |
| `meetingMaterials` | 会议材料：`meetingMaterials`（材料列表）、`meetingSummary`（纪要摘要对象）、`meetingSummaryUrl`（纪要文档 URL） |
| `smartSummary` | 智能纪要（仅在 `includeSmartSummary=true` 时返回）：meetingId、title、content、generateState、version |

### smartSummary 字段

| 字段 | 含义 |
|------|------|
| `meetingId` | 会议实例 ID |
| `title` | 纪要标题 |
| `content` | 纪要正文 |
| `generateState` | 生成状态（具体枚举值以 CLI 返回为准） |
| `version` | 版本号 |

## 响应格式

所有响应使用统一信封格式。成功时 `errno=0`，`data` 是以会议 ID 为 key 的对象：

```json
{
  "errno": 0,
  "errmsg": "成功",
  "data": {
    "会议实例ID": {
      "meetingInfo": {
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
      },
      "meetingMaterials": {
        "meetingMaterials": [{ ... }],
        "meetingSummary": { ... },
        "meetingSummaryUrl": "https://..."
      },
      "smartSummary": {     // 仅 includeSmartSummary=true 时返回
        "meetingId": "会议实例ID",
        "title": "纪要标题",
        "content": "纪要正文...",
        "generateState": 1,
        "version": "latest"
      }
    }
  }
}
```

| 字段 | 含义 |
|------|------|
| `meetingInfo` | 会议基本信息 |
| `meetingMaterials.meetingMaterials` | 会议材料列表（Array） |
| `meetingMaterials.meetingSummary` | 纪要摘要对象 |
| `meetingMaterials.meetingSummaryUrl` | 纪要文档 URL |
| `smartSummary` | 智能纪要（仅 includeSmartSummary=true 时返回） |

### 无数据时的响应

当查询的会议没有材料、信息或纪要时，返回空状态：

```json
{
  "errno": 0,
  "errmsg": "成功",
  "data": {
    "status": "EMPTY",
    "message": "当前会议暂无材料、会议信息或智能纪要内容。"
  }
}
```

### 错误响应

| errno | 含义 | Agent 处理 |
|-------|------|-----------|
| `40001` | 参数错误 | 检查参数（meetingInstanceIds 或 meetingStartTime/meetingEndTime 是否传入），修正后重试 |
| `40301` | 权限不足 | 告知用户无权限访问该会议内容，建议联系组织者，不重试 |
| `50001` | 服务不可用 | 告知用户服务暂不可用，稍后重试（retryable=true） |

## Workflow

### 获取智能纪要

1. 确认目标会议 ID；如果用户没有提供，先查询会议列表。
2. 如参数不明确，先执行 `moma moma-meeting schema GET_api_gateway_meeting-assistant_materials_infos --json`。
3. 执行命令，传入 `meetingInstanceIds=<meetingId>&includeSmartSummary=true`。
4. 判断 `errno`：
   - **`errno=0`**：从返回的 `smartSummary` 中提取 title、content、generateState、version。
   - **`errno=40301`**：告知用户无权限。
   - **`errno=50001`**：告知用户服务暂不可用。
5. 输出纪要标题、生成状态、版本和正文摘要；如用户明确要求完整纪要，可返回完整 `content`，但避免泄露无关敏感信息。
6. 如果返回权限不足或服务异常，按 CLI 返回内容处理，不伪造纪要。

### 获取会议材料

1. 确认目标会议 ID。
2. 执行命令，传入 `meetingInstanceIds=<meetingId>`。
3. 从返回的 `meetingMaterials` 中提取材料列表。

## Notes

- 当前用户必须具备该会议会后查看权限，权限不足返回 `errno=40301`。
- `generateState` 是纪要生成状态，具体枚举以 CLI 返回为准。
- 纪要可能包含会议敏感信息，输出时遵守 `moma-shared` 的敏感信息处理规则。
- `meetingMaterials` 中 `meetingSummary` 是纪要摘要对象，不同于 `smartSummary` 智能纪要。
- 错误响应中的 `hint` 和 `retryable` 字段指导 Agent 下一步操作。
