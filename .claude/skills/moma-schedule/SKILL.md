---
name: moma-schedule
version: 1.0.0
description: 管理定时任务，涵盖云端任务和本地任务两种模式。涉及定时"/计划/每天/每周/cron"等周期性任务、"立即执行/查看/修改/"等云端任务管理操作；或涉及"本地定时/本地 cron/本地计划任务/本地自动化"、"查看/添加/删除/触发本地任务"、"查看 daemon 状态/查看本地执行历史"等本地任务管理操作时使用本技能。不负责创建待办（todo）。"
metadata:
  requires:
    bins: ["moma"]
---

# MOMA 定时任务

本 Skill 覆盖两类定时任务：

| 任务类型 | 命令前缀 | 执行位置 |
|---|---|---|
| **云端任务** | `moma moma-schedule ...` | 服务器侧执行，结果推送给用户 |
| **本地任务** | `moma plan-local ...` | 本机 daemon 进程执行 |

**CRITICAL — 云端任务命令前缀固定为 `moma moma-schedule`；本地任务命令前缀固定为 `moma plan-local`。两者完全独立，不得混用。**
**CRITICAL — 创建云端任务前 MUST 按 [云端参数校验规则](references/moma-schedule-cloud.md#创建前强制校验) 校验完整 payload，通过后才能 dry-run 和提交。当前 `trigger_type` 仅支持 `cron` / `date`，即使 schema 列出 `interval` 等其它值也不得使用。**
**CRITICAL — 云端计划创建最小粒度为小时级，不支持分钟级或秒级计划；不得通过改写 cron 或创建多个任务绕过限制。**
**云端创建参数：`execution_context.user_input.text` 必填；有 skill 时再填 `skills` 与对象 `mention` 下的 `skill` 数组，不补齐无用空字段。字段结构及中文时间解析规则见 [云端创建流程](references/moma-schedule-cloud.md#4-创建定时任务high-risk-write须审批)。**
**CRITICAL — 云端任务：开始前 MUST 先读取 [`../moma-shared/SKILL.md`](../moma-shared/SKILL.md)，遵守其中的登录、权限、审批和安全规则。**
**CRITICAL — 本地任务：写操作无 `--dry-run`/`--yes` 机制，须展示操作摘要并获得用户口头确认后再执行。**

## 场景识别

**先判断是云端还是本地：**

- 用户提到"定时任务"但未说明是本地还是云端 → **询问用户**（本地 = 本机运行，云端 = 服务器运行）
- 用户提到"计划任务" + 有 cwd/工作目录/仓库等本地概念 → 优先识别为**本地任务**
- 含周期词（每天/每周/cron）且无本地概念 → 优先识别为**云端任务**
- 一次性提醒（无周期词）→ 告知本技能不支持

**确认类型后，根据意图路由：**

### 云端任务意图

| 用户意图特征 | 操作 |
|---|---|
| 含周期触发词 + 创建意图 | create |
| 查看/列出我的定时任务 | list |
| 查看某个任务详情 | get |
| 查看执行记录 | executions |
| 立即执行/手动触发 | trigger |
| 修改/更新/调整任务 | update |
| 暂停/停止/禁用任务 | pause |

### 本地任务意图

| 用户意图特征 | 操作 |
|---|---|
| 查看/列出所有本地任务 | list |
| 添加/创建本地任务 | add |
| 查看某个任务详情/配置 | detail |
| 修改/更新任务 | update |
| 删除任务 | delete |
| 启用/禁用/切换状态 | toggle |
| 立即执行/手动触发一次 | run |
| 查看执行历史 | history |
| 查看 daemon 状态/启停 daemon | status / restart / stop |

## References

- [云端定时任务详情](references/moma-schedule-cloud.md)
- [本地定时任务详情](references/moma-schedule-local.md)
