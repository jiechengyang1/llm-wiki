---
tags: [source-summary, AI, LangChain]
type: source-summary
source: 尚硅谷-01-LangChain概述
date: 2026-11-17
---

# LangChain概述

## 核心要点

### 为什么需要 LangChain
- 单一 LLM 有局限：知识滞后、有幻觉、无法直接执行任务、无跨轮记忆
- 实用 AI 应用必须把 LLM 与**外部工具、数据源、记忆机制**有机结合 → LangChain 的设计理念

### 定位：大模型与应用间的中间层
- **打通大模型与外部资源**：统一接口对接数据库、检索引擎、API、文件系统
- **封装底层复杂逻辑**：抽象工具调用、记忆等能力，降低智能体开发门槛
- **支撑多智能体协作**：依托 LangGraph 等生态，从单智能体拓展到多智能体

### 典型应用场景
- **RAG**：解决知识滞后与幻觉——检索外部知识库向量化后供模型作答
- **Agent**：模型作为"推理引擎"自主规划并动态调用工具（订票/查报告/写 SQL）
- **对话系统**：记忆管理记住用户偏好与历史交互
- **多模态 / 自动化写作 / 数据连接**：图文音视频推理、模板+解析器规范输出、PDF/Excel/自然语言转 SQL

### 发展时间线
- 2022.10 哈里森·蔡斯创建开源框架，名字 = **Language + Chain**（链式连接大模型与计算资源）
- 2023：引入 Tool / Agent / Retrieval，推出 LangChain Hub 与 LangSmith，形成开发-调试-部署生态闭环
- 2024：LangGraph、LangServe 发布；旧链式 API 被弃用转向 LangGraph，v0.3 因 API 频繁变动被称"版本碎钞机"，开发者大量流失
- 2025.10.20：**LangChain v1.0 + LangGraph v1.0 正式发布**，官方承诺 2.0 前无破坏性变更；同期融资 1.2 亿美元、估值超 12 亿美元

### v0.3 vs v1.2（关键差异速记）
| 维度 | v0.3 | v1.2 |
|------|------|------|
| 理念 | 以链 Chain 为核心的过渡版本 | 智能体框架范式 |
| Agent 构建 | initialize_agent + AgentExecutor 硬编码 | **create_agent**（底层 LangGraph） |
| 工具定义 | @tool / Tool 类，类型安全弱 | **Pydantic Schema**，类型安全 |
| 结构化输出 | JSON Parser + 正则，不稳 | 一等公民，直接绑定 Pydantic 类 |
| 输出解析 | 纯文本需手动正则解析 | 标准 **content_blocks** 统一对象 |
| 扩展机制 | 改源码/提示词 | **Middleware 中间件**拦截各生命周期 |
| Python 要求 | ≥3.9 | **≥3.10** |

### v1.2 包结构
- `langchain-core`：官方推荐核心 API（Runnable、BaseMessage 等）
- `langchain-classic`：0.x 弃用经典 API 迁移地
- `langchain-community`：第三方集成（langchain-openai、langchain-anthropic 按需装）
- `langgraph`：图形化编排增强版，支持循环调用
### 生态四大支柱（截至 2025.11）
| 支柱 | 层次 | 核心价值 |
|------|------|----------|
| **LangChain** | 基础能力层 | 统一模型抽象（屏蔽 OpenAI/Anthropic/Ollama 接口差异）、Message/Tool/Middleware 模块化——"智能体操作系统内核" |
| **LangGraph** | 运行时编排层 | 复杂工作流 = **有向图**（Node 节点 + Edge 边 + State 共享状态）；显式、可控、可观测 |
| **Deep Agent** | 智能体抽象层 | Agent Harness：显式规划、虚拟文件系统、子智能体、长期记忆、可扩展中间件 |
| **LangSmith** | 监控与评估层 | 全链路可视化追踪（模型调用/提示词/工具使用）、调试优化、评测与团队协作 |

- 三者关系非竞争互斥：**LangChain = 能力抽象层（有什么能力）；LangGraph = 执行编排层（怎么跑）**；快速起步用 LangChain，复杂控制用 LangGraph，Deep Agents 赋予更强自主能力
- 选型建议：简单智能体应用 → LangChain；多步骤有状态复杂工作流 → LangGraph

### 学习心法
- **不要试图学完所有 API**——搞懂核心逻辑与核心模块，其余用到再查；把它当工具箱，不是教科书
### 环境与安装
- 前置：Python 基础（装饰器、协程、JSON 处理）+ LLM 基础概念（Token、Prompt、Embedding）
- 虚拟环境三选：**conda**（能管 CUDA/编译器等非 Python 依赖，AI/深度学习首选，本课程用）/ **uv**（纯 Python 项目，快）/ **venv**（自带轻量，只基于已有解释器）
- 安装：`conda install langchain==1.2.12` 或 `pip install langchain==1.2.12`（conda 依赖检查严，pip 宽松；优先 conda，没有再 pip）

### 大模型应用 4 个场景（成本从低到高）
| 场景 | 适用 | 类比 |
|------|------|------|
| 纯 Prompt | 唯一接口，你说一句它答一句 | 日常问答 |
| Agent + Function Calling | AI 主动要求执行外部函数 | "先看天气预报，再告诉你带不带伞" |
| RAG + Embeddings | 补充领域知识，向量检索找相似内容 | 开卷考试翻书 |
| Fine-tuning | 以上都不行时的最后手段，成本最高 | 提前背熟活学活用 |

### Agent 核心公式（Lilian Weng, 2023）
- **Agent = LLM（大脑）+ Planning（规划/思维链分解）+ Tools（外部工具）+ Memory（短期=上下文窗口 / 长期=微调·知识图谱·向量库）+ Action（执行）**

## 相关链接

- [[LangChain智能体]] - 智能体构建
- [[LangChain RAG]] - 检索增强生成
- [[LangChain模型的创建与调用]] - 模型调用
- [[Agent Skills]] - 智能体技能体系
