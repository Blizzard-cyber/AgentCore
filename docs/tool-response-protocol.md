# 工具响应协议

ToolResponse 是 HelloAgents 的统一工具返回结构。每个工具必须返回可解析、可观测、可编排的结果对象，而不是随意字符串。

## 设计原则

- 状态显式：成功、部分成功、失败可直接判断
- 错误标准化：统一错误码与上下文
- 数据结构化：业务数据和展示文本分离
- 可诊断：携带耗时、输入参数摘要、执行上下文

## 标准结构

```python
ToolResponse.success(
    text="查询完成",
    data={"items": [...]},
    stats={"time_ms": 23},
    context={"tool_name": "search"}
)
```

## 三种状态

- SUCCESS: 任务按预期完成
- PARTIAL: 任务部分完成，结果可用但有折损
- ERROR: 任务失败，无可用业务结果

## 错误模型

统一使用 `ToolErrorCode`，例如：

- NOT_FOUND
- INVALID_PARAM
- EXECUTION_ERROR
- TIMEOUT
- CONFLICT
- CIRCUIT_OPEN

## 工具实现建议

1. 参数校验尽早失败
2. 所有异常转为 ToolResponse.error
3. 长输出使用 PARTIAL + 全量落盘路径
4. 统计信息至少包含 `time_ms`

## 与 Agent 协作

Agent 只依赖结构化字段：

- `status`: 决策下一步
- `text`: 给模型阅读
- `data`: 给流程逻辑读取
- `error_info`: 失败分支处理

