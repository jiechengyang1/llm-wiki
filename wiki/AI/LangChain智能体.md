---
tags: [source-summary, AI, LangChain]
type: source-summary
source: 尚硅谷-07-智能体
date: 2026-11-17
---

# LangChain 智能体

## 核心要点

### 1. Agent 是什么

- **定义**：以 LLM 为推理决策核心，配合记忆、工具调用与环境交互，自主规划、执行复杂任务的软件系统
- **组件必要性排序**：Action 必须有；Tool 几乎总要有；Planning 视任务而定；Memory 最容易被省略

### 2. 从 0.x 碎片化到 1.x 统一 create_agent

- **0.x 之痛**：create_react_agent / create_structured_chat_agent / create_tool_calling_agent 三套入口并存——心智负担高、可组合性差、生态碎片化
- **1.x 统一**：唯一入口 `create_agent()`，底层基于 LangGraph，返回对象本质是 CompiledStateGraph 实例
- **关键参数**：model（传字符串自动走 init_chat_model，或直接传模型对象）、tools、system_prompt、middleware、response_format、checkpointer、interrupt_before/after、name、debug
- **最小用法**：

```python
agent = create_agent(
    model="openai:gpt-4o",             # 字符串或模型对象均可
    tools=[search, calculator],
    system_prompt="你是一个严谨的助手",
)
result = agent.invoke({"messages": [{"role": "user", "content": "帮我查天气"}]})
print(result["messages"][-1].content)  # 最终答案 = 最后一条 AI 消息
```

### 3. invoke 消息协议与 Function Calling 流

- **输入固定** `{"messages": [{"role", "content"}]}`；输出 dict 含完整 messages，最终答案取 `response["messages"][-1].content`
- **标准 4 消息流**：HumanMessage → AIMessage(tool_calls) → ToolMessage → AIMessage(最终回答)
- **并行调用**：一条 AIMessage 可携带多个 tool_calls，对应多个 ToolMessage 同步返回

### 4. 工具与 ReAct 循环

- **工具定义**：`@tool(parse_docstring=True)` + Google 风格 docstring，Args 段自动转参数 schema；模型选工具全靠 docstring 描述质量
- **内置工具**：TavilySearch(max_results=N) 网络搜索开箱即用
- **工具数量**：2-5 个最佳；docstring 不清晰、问题不明确、模型认为不需要时都不会调用工具
- **ReAct 循环**：思考 → 行动（调工具）→ 观察（工具结果）→ 再思考，直到 AIMessage 不再带 tool_calls
- **失控防护**：工具调用次数默认无限制，`config={"recursion_limit": 5}` 可限；SystemMessage 指导模型失败时最多自主重试 3 次

### 5. 高级用法

- **name 参数**：流式输出归因、消息身份标记、调试 trace、组件化封装的运行时身份 ID
- **结构化输出 response_format 四策略**：
    - ProviderStrategy：模型原生结构化输出（OpenAI/Claude/Grok）
    - ToolStrategy：伪装成工具调用，兼容绝大多数模型，**官方推荐**；结果存 `result["structured_response"]`
    - 直接传类型：AutoStrategy 自动选择，1.0+ 官方不再支持（1.2 仍可用）
    - None：不结构化
- **ToolStrategy 三参数**：schema（Pydantic 优先；支持 Union[A, B] 多 schema 但只输出一种）、tool_message_content（自定义成功消息省 token）、handle_errors（默认 True 自动重试；两类默认异常 MultipleStructuredOutputsError / StructuredOutputValidationError）
- **流式 7 模式**：values（每步全量）/ updates（默认增量）/ messages（Token 级打字机）/ tasks / debug（加时间戳与 task 类型）/ checkpoints（需 checkpointer）/ custom（get_stream_writer 业务进度）；可组合 `stream_mode=["tasks", "updates"]`

### 6. 实战模式

- **SmartAssistant**：类封装 5 个工具（天气/计算/时间/汇率/搜索），chat() 维护 self.messages 实现多轮对话；回复取最后一条有 content 的 AI 消息，跳过中间 tool_calls 消息

## 相关链接

- [[LangChain概述]] - LangChain整体认知
- [[LangChain Tools]] - 工具调用
- [[Agent Skills]] - 智能体技能体系
