# 云端定时任务（moma-schedule）

> **Prerequisites:** 请先读取 `../../moma-shared/SKILL.md`，遵守其中的登录、权限、审批和安全规则。本文件只补充业务规则，不得覆盖或放宽 moma-shared 的要求。

云端任务在服务器侧执行，结果通过推送渠道（企微消息等）送达用户。通过 `moma moma-schedule api <apiName>` 调用。

## 命令速查

| 动作 | apiName（照抄） | risk |
|---|---|---|
| 查询列表 | `GET_api_scheduled-tasks` | read |
| 查询单个 | `GET_api_scheduled-tasks_{task_id}` | read |
| 查询执行记录 | `GET_api_scheduled-tasks_{task_id}_executions` | read |
| 查询已安装 skill | `GET_api_scheduled-tasks_installed_skills_{user_id}` | read |
| 创建任务 | `POST_api_scheduled-tasks` | high-risk-write |
| 立即触发 | `POST_api_scheduled-tasks_{task_id}_trigger` | high-risk-write |
| 修改任务 | `PUT_api_scheduled-tasks_{task_id}` | high-risk-write |
| 暂停任务 | `POST_api_scheduled-tasks_{task_id}_pause` | high-risk-write |

---

## 操作详情

### 1) 查询任务列表

**触发关键词**：查看、查询、列出、有哪些、我的定时任务

```bash
# 查全部
moma moma-schedule api GET_api_scheduled-tasks --json

# 带过滤
moma moma-schedule api GET_api_scheduled-tasks -q "status=active&page=1&page_size=20" --json
```

**Query 参数**（均选填，用 `-q` 传入，多参数用 `&` 拼接并加引号）：

| 参数 | 说明 |
|---|---|
| `status` | `active` / `paused` / `expired` / `deleted` |
| `trigger_type` | `cron` / `date`（仅支持这两种） |
| `trigger_types` | 逗号分隔，与 `trigger_type` 互斥，优先级更高 |
| `run_date_before` | 格式 `YYYY-MM-DD`，仅对 `date` 型有效 |
| `run_date_after` | 格式 `YYYY-MM-DD`，仅对 `date` 型有效 |
| `page` | 默认 1 |
| `page_size` | 默认 20，最大 1000 |

**结果展示**：以列表形式展示编号、任务名称、触发描述、状态、下次执行时间。

---

### 2) 查询已安装 skill 列表

创建任务时若用户要用 skill，**必须先调此接口**获取用户已安装的 skill，再让用户选择。

```bash
moma moma-schedule api GET_api_scheduled-tasks_installed_skills_{user_id} -p "user_id=<user_id>" --json
```

`user_id` 为当前登录用户的 UCID（从 `moma auth check --json` 的 `userId` 字段获取）。

返回结构：
```json
[
  {
    "sourceSkillId": 824,
    "displayName": "schedule-creator",
    "name": "schedule-creator",
    "skillSource": "personal",
    "versionId": 1,
    "downloadUrl": "..."
  }
]
```

字段映射（用于写入 execution_context）：
- `sourceSkillId` → `skill_id`
- `displayName`（为空时用 `name`）→ `name`
- `name` → `skill_name`
- `skillSource` → `source`
- `versionId` → `version`
- `downloadUrl` → `downloadUrl`

---

### 3) 查询单个任务详情

**触发关键词**：详情、某个任务、第X个

```bash
moma moma-schedule api GET_api_scheduled-tasks_{task_id} -p "task_id=<task_id>" --json
```

**task_id 缺失时**：先调用列表接口让用户选择目标任务。

---

### 4) 创建定时任务（high-risk-write，须审批）

**触发关键词**：每天/每周/每月/每小时/cron/定时 + 创建/设置/帮我

#### 步骤1：自然语言解析

从用户指令中提取：
- **trigger_type** + **trigger_config**（目前仅支持以下两种）：
  - cron：`{ "cron_expression": "0 10 * * *", "timezone": "Asia/Shanghai" }`
  - date：`{ "run_date": "YYYY-MM-DD HH:mm:ss" }`
- **name**：清除所有定时词汇，仅描述任务功能（如"生成日报"，而非"每天10点生成日报"）
- **description**：不自动提取，由用户在表单中主动输入

时间解析由 Agent 完成：将用户表达的 12 小时制时间转换为 24 小时制，再生成 cron 表达式。时间有歧义时先向用户确认。

| 用户表达 | 24 小时制 | cron 表达式 |
|---|---|---|
| 每天上午九点 | 每天 09:00 | `0 9 * * *` |
| 每天中午十二点 | 每天 12:00 | `0 12 * * *` |
| 每天下午五点 | 每天 17:00 | `0 17 * * *` |
| 每天晚上八点 | 每天 20:00 | `0 20 * * *` |
| 每天凌晨零点 | 每天 00:00 | `0 0 * * *` |
| 每天17点 | 每天 17:00 | `0 17 * * *` |

#### 步骤2：参数收集与校验

必填字段：

| 字段 | 说明 |
|---|---|
| `name` | 任务名称，不含定时词，最长 200 字符 |
| `description` | 执行内容，须清洗定时词后确认 |
| `trigger_type` | `cron` / `date`（仅支持这两种） |
| `trigger_config` | 对应触发类型的配置对象 |
| `output_format` | `message` / `report` / `table` / `alert` |
| `delivery_config` | 推送渠道数组，如 `[{"type":"message","config":{}}]` |
| `execution_context` | 执行上下文，见下方说明 |

description 处理规则：

1. **不自动提取**：description 不从用户原始输入直接复制，必须由用户主动填写或经过追问确认
2. **清除定时信息**：移除所有定时/间隔相关词汇（每天、每周、10点、周一、早上等），只保留纯动作描述
3. **充分性检查**：以下情况必须追问，不得直接提交：
   - 过于笼统：如"提醒我"（提醒做什么？）、"发一下"（发什么？给谁？）、"处理一下"（处理什么？）
   - 缺少关键信息：操作对象、范围、目标不明确
   - 用户原始描述完全是定时词汇，清除后内容为空
   - 追问示例："请描述任务具体要做什么？（不需要包含时间信息）"
4. **向用户确认最终 description**：展示清洗后的内容，用户确认后再提交
5. **前缀规则**：
   - 提醒类（含"提醒/记得/别忘了/通知我"等词）→ 加 `提醒用户：` 前缀
   - 操作类（含"生成/查询/汇总/发送/统计/整理"等词）→ 保持原文不加前缀
   - 无法判断时 → 默认加 `提醒用户：` 前缀并向用户确认

#### execution_context 结构

只填执行所需字段：普通任务只需 `user_input.text`；使用 skill 时再填 `user_input.skills` 和 `user_input.mention.skill`。不主动补齐 `attachments`、`html_snippets` 等空字段。

| 字段 | 类型 | 填写规则 |
|---|---|---|
| `user_input` | 对象 | 必填 |
| `user_input.text` | 非空字符串 | 必填，实际执行内容 |
| `user_input.skills` | 对象数组 | 有 skill 时填写完整 skill 信息，与 `mention.skill` 顺序一致 |
| `user_input.mention` | 对象 | 有 skill 时填写，不能为 `[]` |
| `user_input.mention.skill` | 对象数组 | 有 skill 时填写基本信息，引用与 `skills` 相同的 skill |

**不使用 skill（普通任务）**：
```json
{
  "user_input": {
    "text": "生成日报"
  }
}
```

**使用 skill**：
1. 先调用 `GET_api_scheduled-tasks_installed_skills_{user_id}` 获取用户已安装 skill 列表
2. 展示给用户选择（≤10 个全展示；>10 个展示前10并提示还有 X 个）
3. `description` 中用 `/skill名` 标记 skill 位置，如 `/schedule-creator 汇总日报`
4. `user_input.text` 中将 `/skill名` 替换为 `/{index}` 占位符（index 从 0 开始）
5. `mention.skill` 写入选中的 skill 基本信息（无 version/downloadUrl）
6. `skills` 数组写入完整 skill 信息（含 version/downloadUrl）

```json
{
  "user_input": {
    "text": "/{0} 汇总日报",
    "skills": [
      {
        "skill_id": 824,
        "name": "schedule-creator",
        "skill_name": "schedule-creator",
        "source": "personal",
        "version": "1784538130874",
        "downloadUrl": "..."
      }
    ],
    "mention": {
      "skill": [
        {
          "skill_id": 824,
          "name": "schedule-creator",
          "skill_name": "schedule-creator",
          "source": "personal"
        }
      ]
    }
  }
}
```

#### 创建前强制校验

在任何创建调用（包括 dry-run）前，先校验最终完整 payload。**schema 可能列出尚未支持的参数；schema 中出现某个值不代表云端已支持，必须同时满足以下业务约束。**

- `trigger_type` 仅允许 `cron` / `date`，禁止 `interval`。**计划创建最小粒度为小时级，不支持每隔若干分钟或秒的计划**；每小时可用 `0 * * * *`。分钟级需求须说明暂不支持，不得改写为 cron 或创建多个任务绕过限制，也不得擅自改为小时级。
- `cron` 配置使用 `cron_expression`，不得使用 `seconds`、`minutes`、`hours`、`interval` 等间隔字段；表达式须为 5 字段，分钟字段必须为 0–59 的单个固定值（不允许 `*`、`*/30`、列表或范围），时区默认 `Asia/Shanghai`。
- `date` 配置使用有效的 `run_date`（`YYYY-MM-DD HH:mm:ss`），不得提交 `once`、`execute_at`；不要混入另一种触发类型的配置字段。
- 推送渠道仅支持 `message` / `wechat`，`delivery_config` 必须为非空数组，每项含 `type` 和对象 `config`。不得提交旧渠道名 `site_message` / `wecom`。
- 检查上述必填字段和类型；`name` 不超过 200 字符，`output_format` 仅支持 `message` / `report` / `table` / `alert`，`execution_context` 必须为对象。

创建参数必须经过 `scripts/validate_schedule.py` 的参数校验，通过后才能进入审批流程。脚本支持 `--payload` 直接传入 JSON、标准输入或 `--payload-file` 读取文件。校验失败时先修正参数并重新校验，不得继续请求。参数修改后必须重新校验，dry-run 与真实提交使用同一份已校验参数。

创建继续遵守 `moma-shared` 的 CLI 与审批规则。若 schema 与这些业务约束无法同时满足，停止创建并说明限制。

#### 步骤3：审批流程（high-risk-write）

按 `moma-shared` 审批协议执行：**dry-run 预览 → 展示影响 → 等待用户确认 → 追加 `--yes` 真实调用**

```bash
# 预览
moma moma-schedule api POST_api_scheduled-tasks -d '{
  "name": "生成日报",
  "description": "生成日报",
  "trigger_type": "cron",
  "trigger_config": { "cron_expression": "0 10 * * *", "timezone": "Asia/Shanghai" },
  "output_format": "message",
  "delivery_config": [{ "type": "message", "config": {} }],
  "execution_context": {"user_input":{"text":"生成日报"}},
  "source": "ob-chat"
}' --dry-run --json

# 用户确认后
moma moma-schedule api POST_api_scheduled-tasks -d '{
  "name": "生成日报",
  "description": "生成日报",
  "trigger_type": "cron",
  "trigger_config": { "cron_expression": "0 10 * * *", "timezone": "Asia/Shanghai" },
  "output_format": "message",
  "delivery_config": [{ "type": "message", "config": {} }],
  "execution_context": {"user_input":{"text":"生成日报"}},
  "source": "ob-chat"
}' --yes --json
```

**成功判断**：响应 `errno=0` 且 `data.id` 存在。每次只调用一次，不重试。

**成功展示**：任务ID、任务名称、触发配置的自然语言描述、下次执行时间。

---

### 5) 立即触发任务（high-risk-write，须审批）

**触发关键词**：立即执行、现在跑一下、手动触发

task_id 缺失时先调列表接口让用户选择。

```bash
# 预览
moma moma-schedule api POST_api_scheduled-tasks_{task_id}_trigger -p "task_id=<task_id>" --dry-run --json

# 用户确认后
moma moma-schedule api POST_api_scheduled-tasks_{task_id}_trigger -p "task_id=<task_id>" --yes --json
```

---

### 6) 查询任务执行记录

**触发关键词**：执行记录、执行历史、执行详情、跑了几次

```bash
moma moma-schedule api GET_api_scheduled-tasks_{task_id}_executions -p "task_id=<task_id>" --json

# 带分页
moma moma-schedule api GET_api_scheduled-tasks_{task_id}_executions -p "task_id=<task_id>" -q "page=1&page_size=10" --json
```

**结果展示**：触发时间、执行状态（pending/running/success/failed/timeout）、开始/结束时间、错误信息。

---

### 7) 修改任务（high-risk-write，须审批）

**触发关键词**：修改、更新、调整、改一下

task_id 缺失时先调列表接口让用户选择。只传需要修改的字段，未传字段保持不变。

修改前先展示当前配置与修改后配置的对比，再进入审批流程。

```bash
# 预览
moma moma-schedule api PUT_api_scheduled-tasks_{task_id} \
  -p "task_id=<task_id>" \
  -d '{ "trigger_type": "cron", "trigger_config": { "cron_expression": "0 15 * * *", "timezone": "Asia/Shanghai" } }' \
  --dry-run --json

# 用户确认后
moma moma-schedule api PUT_api_scheduled-tasks_{task_id} \
  -p "task_id=<task_id>" \
  -d '{ "trigger_type": "cron", "trigger_config": { "cron_expression": "0 15 * * *", "timezone": "Asia/Shanghai" } }' \
  --yes --json
```

**可修改字段**：`name`、`description`、`trigger_type`、`trigger_config`、`effective_start_date`、`effective_end_date`、`output_format`、`delivery_config`、`execution_context`

---

### 8) 暂停任务（high-risk-write，须审批）

**触发关键词**：暂停、停止、关闭、禁用

task_id 缺失时先调列表接口让用户选择。暂停后任务状态变为 `paused`，不再触发执行。

```bash
# 预览
moma moma-schedule api POST_api_scheduled-tasks_{task_id}_pause -p "task_id=<task_id>" --dry-run --json

# 用户确认后
moma moma-schedule api POST_api_scheduled-tasks_{task_id}_pause -p "task_id=<task_id>" --yes --json
```

---

## 实现提示

- **name 和 description 均不得包含定时/间隔信息**：禁止词汇包括每天、每周、每月、每小时、每隔、定时、周一、10点、早上、下午等
- **description 必须经用户确认**：不得直接使用用户原始输入，必须清洗 + 充分性检查 + 用户确认后才能写入
- **宁可多追问一次，不要提交模糊的 description**
- **cron 必须为标准 5 字段**，时区用 `Asia/Shanghai`
- **delivery_config 必须为数组**
- `-d` 传单个完整 JSON 字符串，不拆多个 `-d`
- `-p` 传 path 参数，`-q` 传 query 参数，`-q` 值含 `&` 时必须加引号
- 调用失败不输出敏感信息（URL、鉴权头、完整命令等）

---

## 示例

### 查看所有定时任务

```bash
moma moma-schedule api GET_api_scheduled-tasks --json
```

### 查看运行中的任务

```bash
moma moma-schedule api GET_api_scheduled-tasks -q "status=active" --json
```

### 创建每天10点的日报任务

```bash
# 预览
moma moma-schedule api POST_api_scheduled-tasks -d '{"name":"生成日报","description":"生成日报","trigger_type":"cron","trigger_config":{"cron_expression":"0 10 * * *","timezone":"Asia/Shanghai"},"output_format":"message","delivery_config":[{"type":"message","config":{}}],"execution_context":{"user_input":{"text":"生成日报"}},"source":"ob-chat"}' --dry-run --json

# 确认后
moma moma-schedule api POST_api_scheduled-tasks -d '{"name":"生成日报","description":"生成日报","trigger_type":"cron","trigger_config":{"cron_expression":"0 10 * * *","timezone":"Asia/Shanghai"},"output_format":"message","delivery_config":[{"type":"message","config":{}}],"execution_context":{"user_input":{"text":"生成日报"}},"source":"ob-chat"}' --yes --json
```

### 创建带 skill 的任务（每天9点用 schedule-creator 汇总日报）

```bash
# 预览
moma moma-schedule api POST_api_scheduled-tasks -d '{"name":"日报总结","description":"/schedule-creator 汇总日报","trigger_type":"cron","trigger_config":{"cron_expression":"0 9 * * *","timezone":"Asia/Shanghai"},"output_format":"message","delivery_config":[{"type":"message","config":{}}],"execution_context":{"user_input":{"text":"/{0} 汇总日报","skills":[{"skill_id":824,"name":"schedule-creator","skill_name":"schedule-creator","source":"personal","version":"1784538130874","downloadUrl":"..."}],"mention":{"skill":[{"skill_id":824,"name":"schedule-creator","skill_name":"schedule-creator","source":"personal"}]}}},"source":"ob-chat"}' --dry-run --json

# 确认后
moma moma-schedule api POST_api_scheduled-tasks -d '{"name":"日报总结","description":"/schedule-creator 汇总日报","trigger_type":"cron","trigger_config":{"cron_expression":"0 9 * * *","timezone":"Asia/Shanghai"},"output_format":"message","delivery_config":[{"type":"message","config":{}}],"execution_context":{"user_input":{"text":"/{0} 汇总日报","skills":[{"skill_id":824,"name":"schedule-creator","skill_name":"schedule-creator","source":"personal","version":"1784538130874","downloadUrl":"..."}],"mention":{"skill":[{"skill_id":824,"name":"schedule-creator","skill_name":"schedule-creator","source":"personal"}]}}},"source":"ob-chat"}' --yes --json
```

### 修改触发时间为每天15点

```bash
# 预览
moma moma-schedule api PUT_api_scheduled-tasks_{task_id} -p "task_id=abc123" -d '{"trigger_type":"cron","trigger_config":{"cron_expression":"0 15 * * *","timezone":"Asia/Shanghai"}}' --dry-run --json

# 确认后
moma moma-schedule api PUT_api_scheduled-tasks_{task_id} -p "task_id=abc123" -d '{"trigger_type":"cron","trigger_config":{"cron_expression":"0 15 * * *","timezone":"Asia/Shanghai"}}' --yes --json
```

### 查询任务执行记录

```bash
moma moma-schedule api GET_api_scheduled-tasks_{task_id}_executions -p "task_id=02f50f0a-2070-451f-9c50-451adacf7bdb" --json
```
