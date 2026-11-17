---
tags: [source-summary, AI, LangChain]
type: source-summary
source: 尚硅谷-08-中间件
date: 2026-11-17
---

# LangChain 中间件

## 核心要点

### 1. 中间件是什么

- **定义**：Agent 执行过程中的钩子函数，LangChain 1.x「王牌」工程化能力
- **create_agent 四组件**：Model 大脑、Tools 手脚、System Prompt 角色、Middleware 中枢
- **解决什么**：日志/鉴权/重试/风控/审计等横切逻辑从主流程剥离，避免主流程臃肿、不可复用、粒度不够、维护成本高

### 2. 16 个内置中间件 · 6 大类

- **成本资源控制**：ModelCallLimit / ToolCallLimit / Summarization / ContextEditing
- **稳定性容错**：ModelFallback / ModelRetry / ToolRetry
- **安全合规**：HumanInTheLoop / PIIMiddleware
- **决策增强**：TodoList / LLMToolSelector / Subagent（源自 deepagents）
- **执行能力扩展**：Shell / FileSearch / Filesystem（源自 deepagents，4 工具：看目录/读/写/改）
- **开发调试**：LLMToolEmulator

### 3. 高频内置详解

- **SummarizationMiddleware**：trigger（tokens/messages/fraction 任一满足即触发；fraction 依赖 model profile 含 max_input_tokens，DeepSeek 需 custom_profile 手动补）；keep 单一条件保留最新消息；summary_prompt 含 {messages} 占位符；trim_token_to_summarize 默认 4000。摘要结果以 HumanMessage 形式放消息列表头部
- **HumanInTheLoopMiddleware**：interrupt_on 映射工具名 → True / False / InterruptOnConfig(allowed_decisions=approve/edit/reject)；invoke 返回 `__interrupt__`（含 action_requests + review_configs）；必须配 checkpointer，同 thread_id 用 `Command(resume={"decisions": [...]})` 续跑，决策顺序须与中断请求顺序一致；edit 决策可改参数
- **PIIMiddleware**：pii_type 支持 email/credit_card/url/mac_address/ip；strategy 四选一——redact 替换占位 / mask 局部打码 / hash 哈希 / block 抛异常；apply_to_input 默认 True、apply_to_output 与 apply_to_tool_results 默认 False（核心目的：避免敏感信息发给模型服务）
- **TodoListMiddleware**：模型通过 write_todos 工具维护任务清单注入 state，每项 {content, status: pending/in_progress/completed}；决策树——任务无需拆解→不用；步骤固定→LangGraph 线性；步骤多变需边做边调→用它

### 4. 其它内置速览

- **限流**：ModelCallLimit / ToolCallLimit——thread_limit 需 checkpointer；exit_behavior：end（AIMessage 提示超限）/ error（抛异常）/ continue（默认，超限信息交给模型自主决定，可能死循环）
- **回退与重试**：ModelFallbackMiddleware 主模型失败切备用；ModelRetry / ToolRetry 指数退避（max_retries / backoff_factor / initial_delay / max_delay / jitter——jitter=True 生产防惊群削峰，False 便于本地精确调试；on_failure="continue" 把错误包装塞回对话历史）
- **选工具与模拟**：LLMToolSelectorMiddleware（子模型筛选工具，max_tools 上限，always_include 不计入）；LLMToolEmulator 用子 LLM 模拟未开发完成的工具返回
- **上下文与文件**：ContextEditingMiddleware（ClearToolUsesEdit 清历史工具调用痕迹，降 input_tokens，需 checkpointer）；FilesystemFileSearchMiddleware（自动注入 Glob 按路径 + Grep 按内容两个工具）

### 5. 组合与执行顺序（洋葱模型）

- **三类钩子三种序**：before_* 正序（1→2→3）→ 模型调用 → after_* 逆序（3→2→1）；wrap_* 洋葱架构，先传的包最外层
- **顺序只看 create_agent 的传参列表**，与函数定义顺序无关
- **书写即执行**：例 PII 检查 → 限流 → 摘要 → 重试，按安全优先级排列

### 6. 自定义中间件

- **6 个钩子分两类**：Node-style（before_agent / before_model / after_model / after_agent，适合顺序逻辑如日志验证）；Wrap-style（wrap_model_call / wrap_tool_call，适合控制流如重试/回退/缓存）
- **两种写法**：装饰器（@before_model 等，单钩子快速挂载）与类（继承 AgentMiddleware，方法名固定）；多钩子、复杂配置、跨项目复用推荐类——可实例化、可自省、可测试；底层统一：装饰器也构造 AgentMiddleware 子类实例；类写法传 can_jump_to 用 @hook_config 装饰方法
- **Node-style 签名** `(state: AgentState, runtime: Runtime)`：返回 None 放行 / dict 更新状态 / `{"jump_to": ...}` 控流（跳转目标需 can_jump_to 授权，可选 end/tools/model）。三个经典模式：
    - `@before_model(can_jump_to=["tools"])`：构造 fake AIMessage(tool_calls=[...]) 注入并 jump_to="tools"，跳过模型首轮思考直调工具
    - `@after_model(can_jump_to=["model"])`：注入 SystemMessage 强制「二次回答」后跳回模型；须检查是否已注入，防死循环
    - `@before_model(can_jump_to=["end"])`：上下文溢出熔断，AIMessage 兜底直接终止
- **Wrap-style 签名** `(request, handler)`：改 request → `handler(request)` 真实调用 → 改 response.result；ModelRequest 含 model/messages/system_message/tools（`request.override(system_message=...)` 动态改系统提示）；ToolCallRequest 可读写 `tool_call["args"]`；场景——统一追加提示词、敏感词过滤、指数退避重试、md5 响应缓存、工具监控计时与改参重调

## 相关链接

- [[LangChain智能体]] - create_agent 与智能体循环
- [[LangChain Tools]] - 工具定义与调用
- [[LangChain上下文与记忆]] - checkpointer 与短期记忆
