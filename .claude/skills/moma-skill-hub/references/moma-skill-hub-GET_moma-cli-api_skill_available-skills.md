# moma skill hub api GET_moma-cli-api_skill_available-skills

> **Prerequisites:** Please read `../../moma-shared/SKILL.md` to understand login, permission handling, update notices, and security rules.

查询当前用户可用的技能列表，包含个人技能、广场公开技能及有权限的团队空间技能。用于**按用户需求推荐技能**场景。

## Recommended Commands

> **必须添加 `--json`。** 本 Skill 的所有 `moma moma-skill-hub list/schema/api` 命令都必须添加 `--json`。

```bash
# 查看该 API 参数结构
moma moma-skill-hub schema GET_moma-cli-api_skill_available-skills --json

# 推荐场景：拉取候选技能池（固定参数）
moma moma-skill-hub api GET_moma-cli-api_skill_available-skills --json -q "pageNum=1&pageSize=300&roles=consumer&orderField=usedCount"
```

## Options

```text
-q, --query <querystring>   追加 query string，格式：key1=v1&key2=v2
```

推荐场景固定 query 参数：

| 字段 | 值 | 含义 |
|------|---|------|
| `pageNum` | `1` | 第一页 |
| `pageSize` | `300` | 一次拉取最多 300 条候选 |
| `roles` | `consumer` | 筛选消费者角色可访问的技能 |
| `orderField` | `usedCount` | 按使用次数排序 |

其它可选 query 字段（推荐场景通常不需要）：

| 字段 | 是否必填 | 含义 |
|------|---------|------|
| `keyword` | 可选 | 模糊查询关键字 |
| `orderBy` | 可选 | 排序方向：`asc` / `desc`（默认 `desc`） |

## 响应格式

成功时 `code=0`，`data` 为分页对象，`data.skills` 为技能数组：

```json
{
  "code": 0,
  "message": "",
  "data": {
    "page": {
      "offset": 0,
      "size": 300,
      "total": 53,
      "hasMore": false
    },
    "skills": [
      {
        "skillId": "skill_square_447",
        "skillName": "industry-info-search",
        "description": "行业信息检索技能..."
      }
    ]
  }
}
```

| 字段 | 含义 |
|------|------|
| `data.page.total` | 符合条件的技能总数 |
| `data.page.hasMore` | 是否还有更多页 |
| `data.skills[].skillId` | 技能标识（如 `skill_square_447`） |
| `data.skills[].skillName` | 技能名称 |
| `data.skills[].description` | 技能描述 |

> 推荐匹配仅使用 `skillId`、`skillName`、`description`。不要向用户输出 `downloadUrl`、`filePath`。

### skillId 链接规则

`skillId` 为下划线分隔字符串，详情页链接取**最后一段**：

| skillId | 链接中 skillId 参数 |
|---------|-------------------|
| `skill_square_447` | `447` |
| `skill_square_887` | `887` |

链接格式：`https://moma.ke.com/skills-hub?tab=team&skillId={末段}`

### 错误响应

| code | 含义 | Agent 处理 |
|------|------|-----------|
| 非 0 | 业务错误 | 转述 `message`，不要伪造推荐 |

## Workflow

1. 确认用户有**任务/场景需求**，想找合适的 skill（非查询已安装列表）。
2. 提取用户输入原文作为「用户需求」。
3. 执行固定参数查询，从 `data.skills` 构建候选池。
4. 将用户需求与每条技能的 `skillName`、`description` 语义匹配，选出最多 5 条（可以 0 条）。
5. 按推荐输出格式展示，附简要推荐理由。

## 推荐匹配原则

- 优先看 `description` 中的适用场景、触发条件、功能说明。
- `skillName` 作为辅助信号。
- 按相关度降序，最多 5 条；相关性不足不凑数。
- 无匹配时告知用户，不要编造推荐。

## 输出格式

```text
技能名称：{skillName}
技能描述：{description}
推荐理由：{简述匹配原因}
[点击试一试](https://moma.ke.com/skills-hub?tab=team&skillId={skillId末段})
```

多条之间：

```text
---
```

## Notes

- 本接口为读取类能力，不包含安装/卸载操作。
- 推荐场景固定 `pageSize=300`，在返回的候选池内做语义匹配，不要自行调大 pageSize。
- 鉴权由 moma CLI 自动处理，调用方不需要手工拼接鉴权头。
