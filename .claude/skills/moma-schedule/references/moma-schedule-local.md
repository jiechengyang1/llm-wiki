# 本地定时任务（moma plan-local）

> 本地任务由本机 daemon 进程管理和执行，与工作目录/代码仓库绑定。通过 `moma plan-local` 命令调用。

**CRITICAL — 本 Skill 的命令前缀固定为 `moma plan-local`。所有命令必须使用 `moma plan-local ...`。**
**CRITICAL — 本地任务与云端定时任务（moma-schedule或者moma-schedul(旧版)）完全独立，不得混用。**
**CRITICAL — 写操作（add/update/delete/toggle/run 等）无 `--dry-run`/`--yes` 机制，须在执行前向用户展示操作摘要并获得确认后再执行。**

## 场景识别

| 用户意图特征 | 操作 | CLI 命令 |
|---|---|---|
| 查看/列出所有本地任务 | list | `plan-local list` |
| 添加/创建本地定时任务 | add | `plan-local add` |
| 查看某个任务详情/配置 | detail | `plan-local detail <id>` |
| 修改/更新/调整任务 | update | `plan-local update <id>` |
| 删除任务 | delete | `plan-local delete <id>` |
| 启用/禁用/切换任务状态 | toggle | `plan-local toggle <id>` |
| 立即执行/手动触发一次 | run | `plan-local run <id>` |
| 查看执行历史/执行记录 | history | `plan-local history <id>` |
| 删除历史记录 | history-delete | `plan-local history-delete <id>` |
| 查看 daemon 状态/进程状态 | status | `plan-local status` |
| 停止 daemon | stop | `plan-local stop` |
| 启动/重启 daemon | restart | `plan-local restart` |

**歧义处理**：
- 用户提到"定时任务"但未说明是"本地"还是"云端" → 询问用户区分（本地 = 本机运行，云端 = 服务器运行）
- 用户提到"计划任务" + 有 cwd/工作目录/仓库等本地概念 → 优先识别为**本地任务**
- 一次性提醒（无周期且无手动模式意图）→ 告知本技能不支持

---

## 命令速查

| 动作 | 命令 | risk |
|---|---|---|
| 查看任务列表 | `plan-local list` | read |
| 查看任务详情 | `plan-local detail <id>` | read |
| 查看执行历史 | `plan-local history <id>` | read |
| 查看 daemon 状态 | `plan-local status` | read |
| 添加任务 | `plan-local add` | high-risk-write |
| 更新任务 | `plan-local update <id>` | high-risk-write |
| 删除任务 | `plan-local delete <id>` | high-risk-write |
| 切换启用/禁用 | `plan-local toggle <id>` | high-risk-write |
| 手动立即触发 | `plan-local run <id>` | high-risk-write |
| 删除历史记录 | `plan-local history-delete <id>` | high-risk-write |
| 停止 daemon | `plan-local stop` | high-risk-write |
| 启动/重启 daemon | `plan-local restart` | high-risk-write |

---

## 操作详情

### 1) 查看任务列表

**触发关键词**：查看、列出、有哪些、我的本地任务

```bash
# 列表形式
moma plan-local list

# JSON 格式（需要原始数据时）
moma plan-local list --json
```

**结果展示**：以列表形式展示任务编号、任务名称、触发方式（scheduled/manual）、cron 表达式、启用状态、最近执行状态。

---

### 2) 添加本地定时任务（high-risk-write，须确认）

**触发关键词**：添加、创建、新建、设置 + 本地定时/本地任务

#### 步骤1：收集必要参数

从用户描述中提取或追问：

| 参数 | 说明 | 是否必填 |
|---|---|---|
| `--description` | 任务描述，即执行时发送给 Claude 的指令，最长 500 字符 | 必填 |
| `--trigger` | `scheduled`（定时，默认）或 `manual`（仅手动触发） | 选填 |
| `--cron` | 标准 5 字段 cron 表达式（trigger=scheduled 时必填） | 条件必填 |
| `--trigger-description` | 触发规则的自然语言描述，如"每个工作日上午9点" | 选填（建议填写） |
| `--name` | 任务名称；不传则自动取 --description 前 10 个字符 | 选填 |
| `--cwd` | 任务执行的工作目录，**不能为空**；正常情况下由上下文自动传入，若上下文中找不到则必须询问用户 | 必填 |
| `--work-repo-id` | 关联 **Obsidian 仓库** ID（非 git 仓库），**从上下文中读取，不向用户询问** | 自动 |
| `--work-repo-name` | 关联 **Obsidian 仓库**名称（非 git 仓库），**从上下文中读取，不向用户询问** | 自动 |
| `--output-format` | 输出格式，**由上下文自动传入，不向用户询问** | 自动 |

**description 处理规则**：
- description 是任务执行时 Agent 的唯一指令，必须具体清晰
- 若用户描述过于模糊（如"提醒我"、"发一下"），必须追问具体内容
- 提醒类任务 → 加 `提醒用户：` 前缀
- 操作类任务（生成/查询/汇总/发送等）→ 保持原文

**cron 规则**：
- 标准 5 字段，时区为本地时间（不需要额外 timezone 参数）
- 示例：`"0 9 * * 1-5"`（工作日9点）、`"0 10 * * *"`（每天10点）、`"30 18 * * 5"`（每周五18:30）

#### 步骤2：展示操作摘要并确认

向用户展示将要创建的任务信息，待确认后再执行：

```
即将创建本地定时任务：
- 名称：生成日报
- 触发方式：scheduled（每天上午10点）
- 描述：生成今日工作日报
确认创建？
```

#### 步骤3：执行（用户确认后）

预览命令必须填入 `--cwd`、`--work-repo-id`、`--work-repo-name`，从上下文自动获取，不向用户询问。

```bash
# 定时任务（scheduled）
moma plan-local add \
  --description "生成今日工作日报" \
  --name "生成日报" \
  --trigger scheduled \
  --cron "0 10 * * *" \
  --trigger-description "每天上午10点" \
  --cwd "<cwd>" \
  --work-repo-id "<repo_id>" \
  --work-repo-name "<repo_name>"

# 手动触发任务（manual）
moma plan-local add \
  --description "汇总本周代码改动并生成周报" \
  --name "生成周报" \
  --trigger manual \
  --cwd "<cwd>" \
  --work-repo-id "<repo_id>" \
  --work-repo-name "<repo_name>"
```

**成功判断**：命令正常退出，输出包含任务 ID。展示：任务 ID（取前 8 位即可）、名称、触发规则描述。

**创建成功后**：询问用户是否需要立即执行一次（`moma plan-local run <id>`），若用户确认则执行。

---

### 3) 查看任务详情

**触发关键词**：详情、配置、第X个任务

```bash
moma plan-local detail <id>

# JSON 格式
moma plan-local detail <id> --json
```

**id 缺失时**：先调用 `list` 让用户选择目标任务。id 支持前缀（至少 4 个字符）。

---

### 4) 更新任务（high-risk-write，须确认）

**触发关键词**：修改、更新、调整、改一下

id 缺失时先调用 `list` 让用户选择目标任务。更新前先通过 `detail` 获取当前配置，展示变更对比后等待用户确认。

```bash
# 只传需要修改的字段，未传字段保持不变
moma plan-local update <id> \
  --cron "0 15 * * *" \
  --trigger-description "每天下午3点"

# 修改名称和描述
moma plan-local update <id> \
  --name "新任务名称" \
  --description "新任务描述"
```

**可更新字段（用户可指定）**：`--name`、`--description`、`--cron`、`--trigger`、`--trigger-description`

**从上下文中读取、不向用户询问**：`--cwd`（传空字符串清除）、`--work-repo-id`（传空字符串清除，指 Obsidian 仓库 ID，非 git）、`--work-repo-name`（传空字符串清除，指 Obsidian 仓库名称，非 git）

---

### 5) 删除任务（high-risk-write，须确认）

**触发关键词**：删除、移除、清除

id 缺失时先调用 `list` 让用户选择目标任务。删除操作**不可恢复**，须明确告知用户并等待确认。

```bash
moma plan-local delete <id>
```

---

### 6) 切换启用/禁用状态（high-risk-write，须确认）

**触发关键词**：启用、禁用、暂停、恢复、开启、关闭

操作前先通过 `detail` 查询当前状态，告知用户"当前状态为 XX，操作后将切换为 YY"，确认后执行。

```bash
moma plan-local toggle <id>
```

---

### 7) 手动立即触发（high-risk-write，须确认）

**触发关键词**：立即执行、现在跑一下、手动触发、触发一次

id 缺失时先调用 `list` 让用户选择目标任务。告知用户将立即在本机执行该任务，确认后执行。

```bash
moma plan-local run <id>
```

---

### 8) 查看执行历史

**触发关键词**：执行历史、历史记录、跑了几次、执行结果

```bash
# 查看最近 20 条记录
moma plan-local history <id>

# 查看最近 N 条
moma plan-local history <id> --limit 10

# 查看第 N 条完整响应（1 = 最新）
moma plan-local history <id> --index 1

# JSON 格式
moma plan-local history <id> --json
```

**结果展示**：触发时间、触发方式（scheduled/manual）、执行状态（running/ok/error/skipped）、耗时。若用户要查看某次完整响应，使用 `--index N`。

---

### 9) 删除历史记录（high-risk-write，须确认）

**触发关键词**：清空历史、删除历史记录

`--all` 为删除全部，操作**不可恢复**，须明确告知用户影响。

```bash
# 删除第 N 条（1 = 最新）
moma plan-local history-delete <id> --index 1

# 删除全部历史记录
moma plan-local history-delete <id> --all
```

---

### 10) 查看 Daemon 状态

**触发关键词**：daemon 状态、进程状态、后台进程

```bash
moma plan-local status

# JSON 格式
moma plan-local status --json
```

**结果展示**：daemon 是否存活（alive）、本地任务总数。

---

### 11) 启动/重启 Daemon

**触发关键词**：启动 daemon、重启 daemon、启动后台进程

```bash
moma plan-local restart
```

---

## 实现提示

- **id 缺失时先调用 list**：所有需要 `<id>` 的命令，若用户未提供，先 `moma plan-local list` 列出任务让用户选择
- **id 支持前缀**：至少 4 个字符的 ID 前缀即可，无需完整 ID
- **写操作无 dry-run**：plan-local 命令没有 `--dry-run`/`--yes` 机制，改为"展示操作摘要 → 用户口头确认 → 直接执行"
- **daemon 自动启动**：执行 `add` 创建任务时 daemon 会自动启动，无需手动 `restart`；`status`/`stop`/`restart` 仅在用户主动管理进程时使用
- **cron 为标准 5 字段**：如 `"0 9 * * 1-5"`，不含秒字段，不含 timezone（使用本地时区）
- **--name 选填**：不传时自动取 --description 前 10 个字符作为任务名
- **`--cwd` 不能为空**：正常情况下从上下文（当前工作目录、打开的仓库等）自动获取；若上下文中找不到，必须询问用户"请问您希望在哪个工作目录下执行该任务？"，不得省略或留空
- **以下参数从上下文中读取，不向用户询问**：`--work-repo-id`（Obsidian 仓库 ID，非 git）、`--work-repo-name`（Obsidian 仓库名称，非 git）、`--output-format`
- 调用失败不输出敏感信息

---

## 示例

### 示例1：查看所有本地任务

```bash
moma plan-local list
```

### 示例2：查看 daemon 状态

```bash
moma plan-local status --json
```

### 示例3：创建每天10点的日报任务

```bash
moma plan-local add \
  --description "生成今日工作日报，包含完成事项、进行中工作和明日计划" \
  --name "生成日报" \
  --trigger scheduled \
  --cron "0 10 * * *" \
  --trigger-description "每天上午10点" \
  --cwd "<cwd>" \
  --work-repo-id "<repo_id>" \
  --work-repo-name "<repo_name>"
```

### 示例4：创建每周五下午的周报任务

```bash
moma plan-local add \
  --description "汇总本周工作内容，整理成周报格式，包含主要成果和下周计划" \
  --name "生成周报" \
  --trigger scheduled \
  --cron "0 17 * * 5" \
  --trigger-description "每周五下午5点" \
  --cwd "<cwd>" \
  --work-repo-id "<repo_id>" \
  --work-repo-name "<repo_name>"
```

### 示例5：创建仅手动触发的任务

```bash
moma plan-local add \
  --description "分析当前代码库中的潜在问题，生成代码质量报告" \
  --name "代码质量分析" \
  --trigger manual \
  --cwd "<cwd>" \
  --work-repo-id "<repo_id>" \
  --work-repo-name "<repo_name>"
```

### 示例6：查看某任务详情

```bash
moma plan-local detail abcd1234
```

### 示例7：修改触发时间为每天下午3点

```bash
moma plan-local update abcd1234 \
  --cron "0 15 * * *" \
  --trigger-description "每天下午3点"
```

### 示例8：手动立即触发一次任务

```bash
moma plan-local run abcd1234
```

### 示例9：查看任务执行历史并查看最新一条完整响应

```bash
# 查看历史列表
moma plan-local history abcd1234 --limit 10

# 查看最新一条完整响应
moma plan-local history abcd1234 --index 1
```

### 示例10：切换任务启用/禁用状态

```bash
# 先查当前状态
moma plan-local detail abcd1234

# 确认后切换
moma plan-local toggle abcd1234
```