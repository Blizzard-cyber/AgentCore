# Streaming SSE 指南

SSE 让前端实时接收 Agent 运行事件，适合对话、代码生成、执行监控场景。

## 事件类型

- token
- tool_call
- tool_result
- status
- done
- error

## 服务端建议

1. 事件格式保持稳定
2. 心跳机制防止连接假死
3. 对异常统一输出 error 事件

## 客户端建议

- 使用增量渲染
- 支持断线重连
- done 事件后再确认最终态

