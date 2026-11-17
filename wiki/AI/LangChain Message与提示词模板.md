---
tags: [source-summary, AI, LangChain]
type: source-summary
source: 尚硅谷-04-Message与提示词模板
date: 2026-11-17
---

# LangChain Message与提示词模板

## 核心要点

### 消息（Message）：模型交互的基本单元

- **大模型没有记忆**，输出只与输入上下文有关；多数模型 API 服务端也**无状态**——要「记住」多轮对话，必须在程序中维护消息列表
- Message 是模型交互的最基本单元，既代表模型**输入**也代表**输出**；除文字内容外还携带元信息（metadata），让模型分清「谁在说话、说了什么、属于哪轮对话」
- LangChain 1.0 提供跨模型**统一的 Message 标准**（OpenAI / Anthropic / Gemini / 本地模型行为一致）：兼容性强、可扩展性高、为 LangSmith 等调试工具提供一致数据结构
- 内部结构三种字段：**Role**（角色/类型）、**Content**（内容）、**Metadata**（可选元数据：消息 ID、响应时间、token 消耗、标签等）

### 四种常用消息类型与两种格式

| 角色 | JSON 格式 | 对象格式 | 用途 |
|------|-----------|----------|------|
| System | `{"role": "system", ...}` | `SystemMessage(...)` | 开场设定角色、行为准则、领域范围（「工作说明书」） |
| User | `{"role": "user", ...}` | `HumanMessage(...)` | 用户输入，可为多模态（图片/音频/文档） |
| Assistant | `{"role": "assistant", ...}` | `AIMessage(...)` | 模型回复，含文本、tool_calls、元数据 |
| Tool | `{"role": "tool", ...}` | `ToolMessage(...)` | 工具执行结果回传模型继续生成 |

- 两种格式等价，`model.invoke(messages)` 都接受；**ToolMessage 的 `tool_call_id` 必须与 AIMessage 中 tool_calls 的 id 匹配**；分类型可明确角色、控制 AI 行为、构建多轮上下文、调试友好

### 消息对象关键字段

- **content**：弱类型，纯文本传字符串（参数名可省略）；多模态传**字典列表**（`{'type': 'text', 'text': ...}` + `{'type': 'image_url', ...}`，遵循供应商 API 规范）
- **name / id**（HumanMessage 元数据）：区分同名消息、多人对话场景有用；**是否生效取决于供应商**——OpenAI 支持，DeepSeek 文档支持但实测不识别，OpenRouter 不传递
- **AIMessage 特有**：`tool_calls`（工具调用列表，每项含 name/args/id/type）、`response_metadata`（响应元数据）、`usage_metadata`（token 用量）
- **ToolMessage**：`content`（工具输出）、`name`（工具名）、`tool_call_id`（匹配 AI 消息的调用 ID，需紧邻）

### 实战：对话历史管理

- **关键规则：每次调用必须传递完整对话历史**，在原有列表上**追加**新消息（不可重建列表、不可忘记保存 AI 回复）：`append(user) → invoke → append(assistant.content) → append(user) → invoke`
- **历史优化**：对话越长 token 消耗越大 → `keep_recent_messages()` 只保留**最近 N 轮**（一轮 = user + assistant 两条），**system 消息永远保留**（定义角色）；实现即「分离 system → 取非 system 尾部 `[-(N*2):]` → 拼回 system」
- **多轮聊天机器人**：消息列表拼接 + `model.stream()` 流式输出 + 历史优化控制发送长度，主循环「append 用户消息 → 流式回复 → append 回复」

### 拓展：content 与 content_blocks

- **content_blocks** 是 LangChain 1.x 消息对象的重大升级：`list[TypedDict]`，每个 block 有 **type** 字段统一区分内容类型（text / image / audio / video / tool_call / **reasoning**）
- 目标：终结不同供应商多模态格式各异的问题——一套标准代码无缝切换模型厂商
- **输入**：多模态推荐用 content_blocks 构造，替代供应商私有格式（如 OpenAI 的 image_url）：`HumanMessage(content_blocks=[{'type': 'text', 'text': ...}, {'type': 'image', 'base64': ..., 'mime_type': 'image/png'}])`
- **输出**：不同模型的思维链（如 DeepSeek `reasoning_content`）位置各异，content_blocks 提供统一输出格式；需要**思维链或引用（Citations）时优先读 `response.content_blocks` 而非 `response.content`**
- 注意：content_blocks 是**懒加载**的，调用时才解析

### 提示词模板：为什么不用字符串拼接

- 字符串拼接（f-string 等）优点是简单直接适合临时 demo；缺点：可读性差、不易维护、**无变量校验**（漏传/拼错难发现）、难支持多轮对话 / RAG / Few-shot
- 模板优点：结构清晰（变量占位）、易维护可复用、**自动变量校验**、支持复杂场景、与 LangChain 生态无缝集成、便于调试追踪；代价是学习成本
- 开发建议：小项目临时用 → 拼接；**正式 AI 应用 → 提示词模板必选**

### Prompt 机制演进：PromptTemplate → ChatPromptTemplate

- **旧时代 LLM + PromptTemplate**：面向早期文本补全模型，输入输出均为**字符串**；模拟多轮对话要在字符串里伪造 `Human: ...\nAI: ...`，结构混乱且易混淆上下文
- **新时代 ChatModel + ChatPromptTemplate**：现代聊天 API 原生支持角色概念，要求输入**结构化消息列表**；模板接收变量输出 `List[BaseMessage]` 直接传模型
- **对比**：PromptTemplate 输出字符串、不支持角色与对话历史；ChatPromptTemplate 三者全有——**已取代前者成为构建现代应用的首选**

### ChatPromptTemplate 基本用法

- **两种实例化**：`from_messages([...])`（推荐）与直接 `ChatPromptTemplate([...])`（前者底层即调后者 `__init__`）；列表元素常为 `(role, content)` 元组，角色字符串 system / human(=user) / ai(=assistant)
- **三种调用方式**：`invoke(vars)` → **ChatPromptValue**（可直接传模型）；`format(**vars)` → 纯字符串；`format_messages(**vars)` → 消息列表
- **结合 LLM**：`from_messages([("system", "你是数学家"), ("human", "{text}")])` → `invoke({"text": ...})` 得 prompt_value → `model.invoke(prompt_value)` 得输出

### 六种初始化参数类型

- **str**：默认角色为 human（不推荐）
- **tuple**：`("system", "你的名字是{role}.")`——最常用
- **dict**：`{"role": "system", "content": "..."}`——与 JSON 消息一致
- **Message 对象**：`SystemMessage(content="...")`——**注意其中占位符 `{word}` 不会被渲染**，需要变量就用元组
- **MessagePromptTemplate**：`SystemMessagePromptTemplate.from_template("你是一个{role}")` 等三类，模板化生成对应角色消息
- **嵌套 ChatPromptTemplate**（BaseChatPromptTemplate）：模板里再嵌模板，变量在 invoke 时统一填充

### 高级特性

- **partial() 部分预填充**：固定不变的变量提前填好，生成模板变体（如基础模板派生 IT 部门版 / 销售部门版），调用时只传剩余变量
- **消息占位符**：在固定位置**插入整段消息列表**——多轮对话历史、Agent 中间步骤必备；两种写法：`("placeholder", "{conversation}")` 或 `MessagesPlaceholder(variable_name="history")`
- **模板库**：把 TRANSLATOR / SUMMARIZER 等模板集中到 `templates.py` 的类属性或分模块文件，跨项目复用
- **模板组合**：字符串拼接各片段；或用 **`+` 运算符**直接相加两个 ChatPromptTemplate（1.0 支持）

## 相关链接

- [[LangChain概述]] - LangChain整体认知
- [[LangChain模型的创建与调用]] - 模型调用
- [[LangChain Tools]] - 工具与ToolMessage详解
- [[LangSmith的使用]] - 追踪调试消息链路
