---
tags: [source-summary, AI, Agent, 面试]
type: source-summary
source: Agent Skills
date: 2026-06-09
---

# Agent Skills

## 基本概念

**Agent Skills（智能体技能）**：将专业知识、工作流规范固化为可复用资产的核心工具

本质：**模块化的Markdown文件**，教会AI工具执行特定任务，支持自动触发、团队共享与工程化管理

> Agent Skills = **行为规范 + 专业知识 + 使用时机** 的组合

核心是**Context工程**：Skills把垂直领域的知识、脚本调用方法等挂载到Agent的上下文窗口，一次任务可调用多个Skill

## 工作原理 — 渐进式披露（节省token）

| 层级 | 名称 | 说明 |
|------|------|------|
| 1 | 技能发现 | AI读取所有技能元数据（name+description），判断相关性，始终在系统提示中 |
| 2 | 加载核心指令 | 相关时自动读取 **SKILL.md** 正文，获取详细指导 |
| 3 | 加载资源文件 | 需要时读取额外文件（脚本、示例），或通过工具执行 |

## 基本结构

```
my-skill/
└── SKILL.md   （唯一必需文件）
```

### SKILL.md 模板

```markdown
---
name: your-skill-name
description: What it does and when Claude should use it
---

# Skill Title

## Instructions
Clear, concrete, actionable rules.

## Examples
- Example usage 1
- Example usage 2

## Guidelines
- Guideline 1
- Guideline 2
```

### 元数据字段

| 字段 | 必需 | 作用 |
|------|------|------|
| name | 是 | 唯一标识，小写+连字符 |
| description | 是 | **触发条件（最重要）** |
| allowed-tools | 否 | 限制可用工具 |
| model | 否 | 指定模型 |
| context | 否 | `fork` = 独立上下文 |
| agent | 否 | fork时使用的子代理 |
| hooks | 否 | Skill生命周期钩子 |
| user-invocable | 否 | 是否显示在 `/` 菜单 |

## 相关资源

- Skills市场：https://skillsmp.com/zh
- 官方标准：https://agentskills.io
- Anthropic工程文章：https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
- Agent Skills GitHub：https://github.com/anthropics/skills
- Claude技能列表：https://github.com/ComposioHQ/awesome-claude-skills
- 开发工作流skills：https://github.com/obra/superpowers
- 自动写skill的skill：https://github.com/anthropics/skills/tree/main/skills/skill-creator
