# 子代理机制指南

子代理用于拆分复杂任务，让主代理专注编排与验收。

## 适用场景

- 大规模代码检索
- 多阶段数据处理
- 文档生成与校对分离
- 并行执行多个子任务

## 工厂创建

```python
from hello_agents.agents.factory import create_agent
sub = create_agent("react", "sub-search", llm, tool_registry=registry)
```

## 设计要点

- 子代理职责单一
- 明确输入输出契约
- 限制最大步骤和超时
- 主代理统一做结果收敛

## 失败治理

- 子代理失败不阻断总流程（可配置）
- 失败结果结构化回传
- 支持重试与降级模型

