# 自定义工具开发指南

本指南说明如何在 HelloAgents 中实现、注册、测试一个新工具。

## 最小工具

```python
from hello_agents.tools.base import Tool
from hello_agents.tools.response import ToolResponse

class EchoTool(Tool):
    name = "echo"
    description = "回显输入文本"

    def run(self, parameters):
        text = parameters.get("input", "")
        if not text:
            return ToolResponse.error(code="INVALID_PARAM", message="input 不能为空")
        return ToolResponse.success(text=text, data={"echo": text})
```

## 注册与调用

```python
registry.register_tool(EchoTool())
resp = registry.execute_tool("echo", "hello")
```

## 开发规范

- 工具名称应稳定且可读
- 参数定义要明确
- 所有分支都返回 ToolResponse
- 错误信息要可诊断

## 测试清单

1. 正常输入
2. 空参数/非法参数
3. 异常路径
4. 性能统计字段

