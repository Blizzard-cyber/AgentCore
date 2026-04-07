# Function Calling 架构

HelloAgents 统一采用 Function Calling 作为工具调用主通道，减少解析歧义并提升执行稳定性。

## 架构目标

- 工具调用从“文本解析”转为“结构化调用”
- 所有 Agent 使用同一调用语义
- 输出协议统一接入 ToolResponse

## 调用链路

1. Agent 构建工具 schema
2. LLM 产出 tool_calls
3. ToolRegistry 执行工具
4. ToolResponse 回填对话
5. Agent 决策下一轮或结束

## 统一接口

- `invoke_with_tools(messages, tools, ...)`
- `LLMToolResponse(content, tool_calls, usage, latency_ms)`

## 落地收益

- 工具名与参数解析失败率显著下降
- 错误处理与重试路径清晰
- 易于观测与调试（调用链完整）

