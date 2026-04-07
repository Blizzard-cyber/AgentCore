# 异步 Agent 指南

异步执行用于提升吞吐与响应体验，适合 I/O 密集和长链路任务。

## API

- `arun(input_text, ...) -> str`
- `arun_stream(input_text, ...) -> AsyncGenerator[AgentEvent]`

## 生命周期钩子

- on_start
- on_step
- on_finish
- on_error

## 示例

```python
import asyncio
from hello_agents import ReActAgent, HelloAgentsLLM

async def main():
    agent = ReActAgent("assistant", HelloAgentsLLM())
    result = await agent.arun("分析仓库并输出结论")
    print(result)

asyncio.run(main())
```

## 工程建议

1. 对外部工具设置超时
2. 钩子异常不应中断主流程
3. 流式输出与最终结果分离处理

