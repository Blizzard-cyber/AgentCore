# 会话持久化指南

会话持久化用于保存执行状态，支持断点恢复、复盘审计和跨进程协作。

## 存储内容

- 消息历史
- 执行元数据
- token 统计
- 关键事件时间线

## 基本流程

1. 启动会话时创建 session id
2. 周期性保存快照
3. 任务结束写入最终状态
4. 恢复时加载并校验版本

## 配置建议

```python
Config(
    session_enabled=True,
    session_dir="memory/sessions",
    auto_save_enabled=True,
    auto_save_interval=10,
)
```

