---
name: moma
description: 安全使用 moma CLI 查询会议、会议转写、会议纪要、指标数据、Hive 数据和数据模型。
user-invocable: true
---

<!-- MOMA CLI 管理的 MOMA Skill，请勿手动编辑。 -->

# MOMA CLI

执行任何 `moma` 命令前，先完整读取 [`../moma-shared/SKILL.md`](../moma-shared/SKILL.md)。

## 使用流程

1. 执行 `moma service list --json`。
2. 根据返回的 `service` 和 `description` 选择能力；存在多个候选时，让用户选择。
3. 选定 service 后，在当前 Agent 提供的可用 Skills 中查找名称与 service 完全相同的 `moma-*` 业务 Skill：
   - 找到时，按当前 Agent 的 Skill 加载机制读取并执行该 Skill。
   - 未找到时，不扫描本地目录或猜测 Skill 路径；执行 `moma <service> list --json`，按 `moma-shared` 的规则发现并调用 API。


## 恢复

- CLI 明确提示 MOMA Skills 未安装时，执行 `moma skills install -y --json`；安装或更新成功后，按当前 Agent 的机制重新加载 Skills，再重新开始能力发现。
