# moma meeting api GET_api_open_moma_meeting_meetings_{meetingId}_transcription

> **Prerequisites:** Please read `../../moma-shared/SKILL.md` to understand login, permission handling, update notices, and security rules.

获取指定会议的腾讯会议转写下载链接。

## Recommended Commands

> **必须添加 `--json`。** 本 Skill 的所有 `moma moma-meeting list/schema/api` 命令都必须添加 `--json`。

```bash
# 查看该 API 参数结构
moma moma-meeting schema GET_api_open_moma_meeting_meetings_{meetingId}_transcription --json

# 获取转写下载链接
moma moma-meeting api GET_api_open_moma_meeting_meetings_{meetingId}_transcription --json -p "meetingId=<meetingId>"
```

## Options

```text
-p, --path-params <params>  路径参数，格式：key1=v1&key2=v2
```

路径参数：

| 字段 | 含义 |
|------|------|
| `meetingId` | 会议实例 ID，通常来自会议列表返回值 |

## Workflow

1. 确认目标会议 ID；如果用户没有提供，先查询会议列表。
2. 如参数不明确，先查看 `gateway schema`。
3. 执行命令。
4. 返回 `status`、`version` 和 `downloadUrls`。
5. 如果 `status=READY`，向用户展示下载链接；如果 `status=EMPTY` 或链接为空，说明暂无可用转写。

## Notes

- 该接口返回的是腾讯会议转写下载链接，不是逐字稿正文。
- 业务服务内部会使用会议 host 或 creator 查询腾讯会议转写；Agent 不需要也不能传入腾讯会议 operator 信息。
- 当前用户必须具备该会议会后查看权限。
