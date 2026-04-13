# 上下文工程指南

上下文工程负责控制对话成本、保证长期任务稳定性、减少模型上下文噪声。

## 目标

- 控制 token 增长
- 保留关键任务记忆
- 限制工具输出污染上下文
- 支持会话恢复

## 关键组件

- HistoryManager: 维护消息历史和压缩边界
- TokenCounter: 统计历史 token 使用量
- ObservationTruncator: 截断工具超长输出
- ContextBuilder: 组装最终模型输入

## 推荐配置

```python
from agent_core import Config

config = Config(
    context_window=128000,
    compression_threshold=0.8,
    min_retain_rounds=10,
    tool_output_max_lines=2000,
    tool_output_max_bytes=51200,
)
```

## 压缩策略

- 简单摘要：基于历史统计，成本低
- 智能摘要：通过专用模型提炼任务状态

## 实战建议

1. 先用简单摘要上线
2. 关键业务再开启智能摘要
3. 对读取类工具启用严格截断
4. 对生成类工具落盘全量输出并回传路径

