# HelloAgents

HelloAgents 是一个从零设计的多智能体工程框架，面向真实生产任务：可控执行、可观测运行、可扩展工具、可持续会话。

## 项目目标

- 提供统一 Agent 执行模型（同步、异步、流式）
- 提供标准工具协议，避免“字符串猜测”
- 提供上下文与会话治理，控制成本与稳定性
- 提供可观测与日志体系，支持排障与复盘
- 提供子代理、技能与记忆能力，支持复杂任务编排

## 快速开始

### 1. 安装

```bash
pip install -e .
```

### 2. 配置环境变量

```bash
LLM_MODEL_ID=your-model
LLM_API_KEY=your-api-key
LLM_BASE_URL=your-base-url
```

### 3. 运行最小示例

```python
from hello_agents import ReActAgent, HelloAgentsLLM, ToolRegistry
from hello_agents.tools.builtin.calculator import CalculatorTool

llm = HelloAgentsLLM()
registry = ToolRegistry()
registry.register_tool(CalculatorTool())

agent = ReActAgent(name="assistant", llm=llm, tool_registry=registry)
print(agent.run("计算 256 * 789"))
```

## 核心模块

- `hello_agents/agents`: Agent 范式实现（Simple/ReAct/Reflection/PlanSolve）
- `hello_agents/core`: 基础抽象、LLM 适配、生命周期与会话组件
- `hello_agents/tools`: 工具协议、注册器、内置工具、错误模型
- `hello_agents/context`: 历史管理、Token 计数、上下文构建、截断策略
- `hello_agents/memory`: 长短期记忆与存储实现
- `hello_agents/observability`: Trace、事件与诊断输出

## 文档目录

- docs/tool-response-protocol.md
- docs/function-calling-architecture.md
- docs/context-engineering-guide.md
- docs/async-agent-guide.md
- docs/subagent-guide.md
- docs/memory-system-guide.md
- docs/observability-guide.md
- docs/session-persistence-guide.md
- docs/skills-quickstart.md

## 开发命令

```bash
# 推荐：确保测试使用当前工作区源码
PYTHONPATH=. pytest -q

# 运行关键模块测试
PYTHONPATH=. pytest -q tests/test_tool_response_protocol.py tests/test_custom_tools.py
```

## 许可证

CC BY-NC-SA 4.0，见 LICENSE。
