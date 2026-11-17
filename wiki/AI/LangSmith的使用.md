---
tags: [source-summary, AI, LangChain]
type: source-summary
source: 尚硅谷-03-LangSmith的使用
date: 2026-11-17
---

# LangSmith的使用

## 核心要点

### LangSmith 是什么

- **定位**：LangChain 生态中专门用于 LLM 应用**调试、监控、评估和管理**的平台
- 四大能力：**追踪** tracing（记录每次 LLM 调用详情）、**监控** monitoring（实时查看性能）、**调试** debug（排查问题优化性能）、**评估** evaluate（系统化测试 LLM 应用）

### 核心应用与开发功能

- **Tracing（追踪）**：最核心功能。完整记录每次调用链路（Trace）——每步 Prompt、模型返回、Token 消耗、各节点耗时；Agent 或 RAG 变慢/报错时逐节点排查
- **Monitoring（监控）**：生产级可视化看板——Token 消耗趋势、QPS、错误率、平均延迟、成本预估，适合上线后观察稳定性与开销
- **Datasets & Experiments（数据集与实验）**：把真实输入和边界情况存为数据集；改 Prompt 或换模型时跑自动化对比实验，直观看到新旧版本差异
- **Evaluators（评估器）**：LLM 输出难以用传统断言测试，支持**基于规则**（关键词匹配）或**基于模型**（LLM-as-a-judge）的指标自动打分（相关性、幻觉等）
- **Annotation Queues（标注队列）**：把部分 Traces 发给业务专家人工打分、纠正、贴标签，产出数据可用于微调或充当测试集
- **学习路径建议**：现阶段重点 **Tracing**（看调用细节）+ **Playground**（快速调优提示词）；应用复杂后（复杂 RAG、多 Agent 协同）再引入 **Datasets** 量化评估 + **Studio** 可视化调试

### 提示词与调试工具

- **Prompts（提示词管理）**：「提示词版的 GitHub」——把 Prompt 从代码解耦，云端统一管理与**版本控制**（v1/v2），代码中通过 API 动态拉取，支持团队协作分享
- **Playground（演练场）**：网页端模型交互界面，零代码选不同模型微调测试 Prompt，一键保存回 Prompts 仓库
- **Studio（工作室）**：与 **LangGraph** 深度集成，可视化查看图结构 Agent 的状态（State）在节点间流转；支持在节点**暂停**、手动修改数据后继续执行
- **Context Hub（上下文中心）**：存放跨项目复用的公共上下文模板、全局变量、系统预设提示

### 部署与沙盒

- **Deployments（部署）**：一键把 LangChain 应用 / LangGraph Agent 部署为线上 API 服务（依托 LangGraph Cloud）；开箱即用的生产端点，代管高并发、队列、状态持久化
- **Sandboxes（沙盒）**：轻量级在线试运行环境，不污染生产环境地测试新部署的 Agent 或自动化脚本

### 接入准备：账号与环境变量

- 注册/登录：官网 https://smith.langchain.com ，自由选择注册方式
- **获取 API_KEY**：Settings → 创建后**只在弹窗中出现一次**，关闭后官网无法再查看，务必妥善保存（可按需删除）
- `.env` 中添加四个环境变量：

```bash
LANGSMITH_TRACING=true                          # 启用监控
LANGSMITH_ENDPOINT=https://api.smith.langchain.com  # WebUI 服务地址
LANGSMITH_API_KEY=<YOUR_API_KEY>                # API 密钥
LANGSMITH_PROJECT="pr-clear-harmony-32"         # 项目名（WebUI 按名查看）
```

### 查看监控指标

- 程序中 `load_dotenv()` 加载后，运行**任意** LangChain 代码即自动记录运行指标并同步后台——**无需改业务代码**
- 通过 `invoke()` 的 `config` 参数定制运行的元信息：

```python
config = {
    "run_name": "joke_generation",        # 本次运行的显示名
    "tags": ["my_tag1", "my_tag2"],       # 标签，便于分类查找
    "metadata": {"user_id": "shkstart"},  # 用户/会话等元数据
    "configurable": {"temperature": 0.7},  # 运行时调整模型参数
}
response = model.invoke("1 + 2 = ？", config=config)
```

- WebUI 流程：Tracing 界面按 `LANGSMITH_PROJECT` 名找到项目 → 点击运行条目进详情（每步 Prompt、返回、Token、耗时）→ 报表页切换查看各类指标

## 相关链接

- [[LangChain概述]] - LangChain整体认知
- [[LangChain模型的创建与调用]] - 模型调用
- [[Agent Skills]] - 智能体技能体系
