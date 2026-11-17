---
tags: [source-summary, AI, LangChain]
type: source-summary
source: 尚硅谷-09-上下文与记忆
date: 2026-11-17
---

# LangChain上下文与记忆

## 核心要点

### 为什么需要记忆

- **LLM 本质无状态**：大模型不会记忆任何上下文，每次 `agent.invoke()` 都是全新开始——会话 1 说了「我叫小明」，会话 2 问「我叫什么」答不上来；只有把完整历史消息一起传入才能答对
- **记忆（Memory）**：专门「存储历史交互信息」的组件，核心作用是**保存上下文 + 提供上下文**
- **上下文工程（Context Engineering）**：负责「合理组织」记忆与任务信息，让响应更连贯——Agent 复杂多轮交互的核心基础
- 版本演进：v0.x 用专用 `xxxMemory` 类；v1.x 构建在 LangGraph 之上，用 **state + store** 统一管理

### 上下文工程与三种上下文类型

- LangGraph 按可变性 × 生命周期提供三种管理方法：
  - **动态运行时上下文** → `state` 对象（单次运行内演变的可变数据）
  - **动态跨会话上下文** → `store` 对象（跨对话共享的持久数据：用户偏好、历史洞察）
  - **静态运行时上下文** → `context` 对象（启动时传入的用户元数据、工具、数据库连接）
- 记忆两大类：**短期记忆**（thread-scoped，换 thread_id 即消失）、**长期记忆**（跨会话、任意命名空间共享）

### 短期记忆：State + Checkpointer + Thread ID

- 三者组合：**State**（会话状态，默认含 messages 列表）+ **Checkpointer**（把 State 作为快照持久化）+ **Thread ID**（唯一标识 State，运行时按 thread_id 读写快照）——类比 RPG 游戏的「自动存档」
- 最小可用代码：

```python
from langgraph.checkpoint.memory import InMemorySaver

agent = create_agent(model=model, checkpointer=InMemorySaver())
config = {"configurable": {"thread_id": "1"}}
agent.invoke({"messages": [HumanMessage("我叫张三")]}, config)
agent.invoke({"messages": [HumanMessage("我叫什么？")]}, config)  # 记得！
```

- **checkpointer 自动管理历史**：读旧历史 → 追加新消息 → 带完整历史调模型 → 保存新历史；调用时只传新消息即可
- **thread_id 是记忆开关**：同 id 共享记忆、不同 id 完全隔离（多用户 / 同用户多任务都靠它分开）
- 常见排查：不记得 = 没加 checkpointer / 没传 config / 两次 thread_id 不同
- **InMemorySaver**：进程结束即丢、不支持跨进程，仅适合测试；生产用 **PostgresSaver**（`setup()` 首次建表，幂等可重复执行），底层 4 张表：`checkpoints`（快照主表）、`checkpoint_blobs`（复杂 channel 值）、`checkpoint_writes`（中间写入）、`checkpoint_migrations`（迁移版本表）
- 关键对比：内存版重建 Saver 历史即丢；外部存储版**只要 thread_id 一致，历史可跨进程串联**

### 记忆治理策略（上下文管理）

- 动机：历史无限增长 → 超上下文窗口、长上下文注意力分散、token 成本高
- **消息裁剪**（调模型前，`@before_model`）：只保留首条 + 最近 N 条，控制模型可见范围；配 `RemoveMessage(id=REMOVE_ALL_MESSAGES)` 先清空再写入保留集
- **消息删除**（调模型后，`@after_model`）：超阈值就删最老的几条、总数恒定；**墓碑机制**——返回 `RemoveMessage(id=m.id)` 只是追加一条删除标记，内置 Reducer 在喂给模型前自动过滤被标记消息
- **摘要**（SummarizationMiddleware）：把旧历史压成摘要替换原文，保语义不保原文，最适合长会话；`trigger=[("tokens", 100)]` 触发、`keep=("messages", 2)` 保留近几条、摘要可交给便宜模型（如 gpt-4o-mini）做
- 阈值经验：按模型窗口的 3/4 设置（4k→3000、8k→6000、16k→12000），留余量给工具调用与系统提示
- 也可以在中间件里自定义任意过滤策略（消息列表随你改）

### 长期记忆：类型与四层存储架构

- 记录**用户/应用级**数据（喜欢简短回答、偏好 Python、是 VIP、某流程怎么做更好），任何会话随时可访问
- LangChain 参考 CoALA paper 分三类：**Semantic**（语义/事实：偏好、概念）、**Episodic**（情景/经验：过去任务怎么做成、常表现为 few-shot 示例）、**Procedural**（程序/规则：系统提示词、工作流程、工具调用规则）
- 存储四层架构 **store → namespace → key → value**：
  - **Store**：`BaseStore` 子类（LangGraph 提供）——`InMemoryStore` 测试 / `PostgresStore` 生产（新增 store、store_migrations 两张表）
  - **namespace**：任意长度字符串元组的层级路径，类似文件路径，用于分组隔离（如 `("users", "user_123", "preferences")`）
  - **key**：namespace 内唯一标识（str）；**value**：JSON-like 字典（dict）
- 多会话各自 State 互不干扰，但共享同一个 Store 实例，靠 namespace 区分用户/业务域

### 长期记忆基础 API 与运行时访问

- 三个 API：**put()** 写入（index 控制语义索引：None 用默认 / False 不建 / list[str] 指定字段；ttl 可选过期）；**get()** 按 namespace+key 精确读，返回 `Item`（带 value、created_at、updated_at）；**search()** 检索——支持 **filter 结构化过滤**（value 键值匹配）与 **query 语义检索**（向量相似度、按 score 降序），配 limit/offset
- 语义检索需初始化时配 `index={"embed": 嵌入函数或模型, "dims": 维度, "fields": ["$"]}`；fields 支持 `["$"]` 整体嵌入、指定一级字段、`["parent.child"]` 嵌套、`["array[*].field"]` 数组
- **Agent 内访问**：工具里 `runtime.store`（`ToolRuntime` 注入，可配 `CustomState` 扩展 AgentState 加 user_id 字段）；中间件里 Node-style 用 `runtime.store`，Wrap-style 用 `request.runtime.store`
- AgentState 三字段：`messages`（Required）、`jump_to`（跳转指定节点）、`structured_response`（结构化输出结果）
- **何时写入记忆**：**hot path** 主流程内边答边记（立即生效、透明，但加延迟）/ **background** 后台异步整理（主流程快，但不能立刻生效）——用户偏好、账号资料可热路径；对话摘要、经验沉淀适合后台写

### 静态运行时上下文（context）

- 运行开始时经 `invoke(..., context=UserContext(...))` 传入、运行期间不变；自定义 ContextSchema 用 `@dataclass` 修饰，创建 Agent 时传 `context_schema`
- 典型用法（配套长期记忆 store 一起读）：
  - **额度管控**：`before_model` 查额度不足就 `jump_to="end"` 提前结束；`after_model` 按 usage_metadata 扣 token 并写回 store
  - **工具权限**：`wrap_model_call` 里按用户开通情况过滤工具集，`request.override(tools=tools)` 仅本次生效
  - **工具计费**：`wrap_tool_call` 校验剩余额度、不足时返回 `Command(update={"messages": [ToolMessage(...)]})`，扣费后写回 store
  - **个性化提示词**：`@dynamic_prompt` 钩子按用户偏好动态生成系统提示词（只影响本次调用，不改消息列表）
- 工具里 `ToolRuntime[UserContext, Any]` 指定泛型，否则传 context 会告警；ToolRuntime 由运行时注入、不出现在工具 schema 中

## 相关链接

- [[LangChain概述]] - LangChain整体认知
- [[LangChain智能体]] - 智能体
- [[LangChain中间件]] - 中间件机制
- [[Agent Skills]] - 智能体技能体系
