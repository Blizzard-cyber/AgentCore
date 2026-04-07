# 日志系统指南

日志系统用于在线排障与离线分析，目标是“低噪声、可追踪、可检索”。

## 日志级别

- DEBUG: 开发调试
- INFO: 关键流程
- WARNING: 可恢复异常
- ERROR: 失败事件

## 字段建议

- request_id / session_id
- agent_name / tool_name
- duration_ms
- status

## 实施建议

1. 统一格式（JSON）
2. 明确采样策略
3. 日志与 trace 关联同一 id
4. 严禁打印密钥与原始敏感输入

