# HelloAgents

生产级多智能体框架（二次开发版本）。

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-sa/4.0/)

本仓库为持续迭代的工程化版本，面向真实项目落地，重点在稳定性、可观测性、工具协作与扩展能力。

## 项目定位

- 当前仓库是独立维护的二次开发分支，不再使用旧的学习分支说明与教程版本映射。
- 所有功能、文档与测试以本仓库 `main` 分支为准。
- 近期新增并集成了完整记忆系统（长期/短期记忆、检索、质量评估、版本控制、多模态与安全模块）。

## 核心能力

- 多 Agent 范式：Simple / ReAct / Reflection / Plan&Solve
- 工具系统：ToolRegistry、ToolResponse 协议、内置文件工具与任务管理工具
- 上下文工程：HistoryManager、TokenCounter、ContextBuilder
- 会话持久化与可观测性：SessionStore、TraceLogger
- 健壮性：熔断器、乐观锁、工具过滤、子代理机制
- 记忆系统：MemoryManager 统一编排长期/短期记忆与检索更新能力

## 快速开始

### 安装

```bash
pip install hello-agents
```

### 环境变量

创建 `.env`：

```bash
LLM_MODEL_ID=your-model-name
LLM_API_KEY=your-api-key
LLM_BASE_URL=your-api-base-url
```

### 基本示例

```python
from hello_agents import ReActAgent, HelloAgentsLLM, ToolRegistry
from hello_agents.tools.builtin import ReadTool, WriteTool, TodoWriteTool

llm = HelloAgentsLLM()
registry = ToolRegistry()
registry.register_tool(ReadTool())
registry.register_tool(WriteTool())
registry.register_tool(TodoWriteTool())

agent = ReActAgent("assistant", llm, tool_registry=registry)
result = agent.run("分析项目结构并生成报告")
print(result)
```

## 项目结构

```text
hello-agents/
├── hello_agents/
│   ├── agents/          # 多种 Agent 实现
│   ├── core/            # LLM/Agent 基础设施
│   ├── tools/           # 工具协议与工具系统
│   ├── context/         # 上下文构建与压缩
│   ├── memory/          # 记忆系统
│   ├── observability/   # 可观测性
│   └── skills/          # Skills 加载与管理
├── docs/
├── examples/
└── tests/
```

## 文档导航

- [工具响应协议](./docs/tool-response-protocol.md)
- [上下文工程](./docs/context-engineering-guide.md)
- [会话持久化](./docs/session-persistence-guide.md)
- [可观测性](./docs/observability-guide.md)
- [子代理机制](./docs/subagent-guide.md)
- [记忆系统](./docs/memory-system-guide.md)
- [自定义工具扩展](./docs/custom_tools_guide.md)

## 开发与测试

```bash
# 运行全部测试
pytest -q

# 运行记忆系统相关测试
pytest -q tests/test_memory_system.py tests/test_memory_enhancements.py
```

## 贡献

欢迎通过 Issue 和 Pull Request 参与改进。

建议流程：

1. 创建功能分支
2. 补充或更新测试
3. 更新相关文档
4. 提交 PR

## 许可证

本项目采用 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)。
详情见 [LICENSE](LICENSE)。

