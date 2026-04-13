"""异常体系"""

class AgentCoreException(Exception):
    """AgentCore基础异常类"""
    pass

class LLMException(AgentCoreException):
    """LLM相关异常"""
    pass

class AgentException(AgentCoreException):
    """Agent相关异常"""
    pass

class ConfigException(AgentCoreException):
    """配置相关异常"""
    pass

class ToolException(AgentCoreException):
    """工具相关异常"""
    pass
