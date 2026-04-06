# 记忆系统使用指南

## 1. 概述

HelloAgents 企业级记忆系统是一个功能强大的记忆管理框架，为智能体提供长期记忆能力。它支持跨会话的记忆存储、智能检索、记忆组织、更新与修正、以及安全性与隐私保护等功能。

## 2. 核心组件

### 2.1 存储层

- **MemoryStorage**：存储接口基类，定义了存储操作的标准接口
- **LocalStorage**：本地文件存储，将记忆保存为本地JSON文件
- **VectorDBStorage**：向量数据库存储，支持基于向量的语义检索

### 2.2 核心功能

- **LongTermMemory**：长期记忆管理，支持记忆的添加、查询、更新、删除
- **MemoryRetriever**：记忆检索，支持向量检索、关键词检索和混合检索
- **MemoryOrganizer**：记忆组织，支持分类管理、标签管理、层次化组织结构
- **MemoryUpdater**：记忆更新与修正，支持记忆更新、修正、过期清理、版本控制
- **MemorySecurity**：安全性与隐私保护，支持访问控制、权限管理、敏感信息过滤、数据加密

### 2.3 统一管理

- **MemoryManager**：整合所有记忆组件，提供统一的接口

## 3. 快速开始

### 3.1 安装依赖

记忆系统需要 `sentence-transformers` 库来支持向量检索功能：

```bash
pip install hello-agents
```

或者手动安装：

```bash
pip install sentence-transformers>=2.0.0,<3.0.0
```

### 3.2 基本使用

```python
from hello_agents import MemoryManager

# 初始化记忆管理器
memory_manager = MemoryManager()

# 添加记忆
memory_id = memory_manager.add_memory(
    content="这是一个测试记忆",
    summary="测试记忆摘要",
    category="测试",
    tags=["测试", "示例"],
    priority=5
)

# 获取记忆
memory = memory_manager.get_memory(memory_id)
print(f"记忆内容: {memory['content']}")

# 更新记忆
memory_manager.update_memory(
    memory_id,
    content="更新后的测试记忆",
    summary="更新后的摘要"
)

# 搜索记忆
results = memory_manager.semantic_search("测试记忆", top_k=5)
for similarity, memory in results:
    print(f"相似度: {similarity:.2f}, 内容: {memory['content']}")

# 删除记忆
memory_manager.delete_memory(memory_id)
```

## 4. 功能详解

### 4.1 长期记忆管理

#### 添加记忆

```python
memory_id = memory_manager.add_memory(
    content="记忆内容",
    summary="记忆摘要",  # 可选
    category="分类",  # 可选
    tags=["标签1", "标签2"],  # 可选
    priority=5  # 可选，0-10
)
```

#### 获取记忆

```python
memory = memory_manager.get_memory(memory_id)
if memory:
    print(memory["content"])
```

#### 更新记忆

```python
success = memory_manager.update_memory(
    memory_id,
    content="新内容",
    summary="新摘要",
    # 其他字段...
)
```

#### 删除记忆

```python
success = memory_manager.delete_memory(memory_id)
```

#### 列出记忆

```python
# 列出所有记忆
memories = memory_manager.list_memories(limit=100)

# 按分类过滤
memories = memory_manager.list_memories(
    category="技术",
    limit=50
)

# 按标签过滤
memories = memory_manager.list_memories(
    tags=["Python", "编程"],
    limit=50
)

# 按优先级过滤
memories = memory_manager.list_memories(
    min_priority=5,
    limit=50
)
```

### 4.2 记忆检索

#### 语义搜索（基于向量相似度）

```python
results = memory_manager.semantic_search(
    query="编程语言",
    top_k=5,
    filters={"category": "技术"}  # 可选过滤条件
)

for similarity, memory in results:
    print(f"相似度: {similarity:.2f}, 内容: {memory['content']}")
```

#### 关键词搜索

```python
results = memory_manager.keyword_search(
    query="Python",
    top_k=5,
    filters={"tags": ["编程"]}  # 可选过滤条件
)
```

#### 混合搜索

```python
results = memory_manager.hybrid_search(
    query="Python编程",
    top_k=5,
    filters={"category": "技术"},  # 可选过滤条件
    semantic_weight=0.7  # 语义搜索权重
)
```

### 4.3 记忆组织

#### 创建分类

```python
result = memory_manager.create_category(
    category_name="技术",
    description="技术相关的记忆"
)

if result["success"]:
    print(f"分类创建成功: {result['category_name']}")
```

#### 列出分类

```python
categories = memory_manager.list_categories()
for category in categories:
    print(f"分类: {category['name']}, 描述: {category['description']}")
```

#### 添加标签

```python
success = memory_manager.add_tag(memory_id, "Python")
```

#### 移除标签

```python
success = memory_manager.remove_tag(memory_id, "Python")
```

#### 列出标签

```python
tags = memory_manager.list_tags()
print("所有标签:", tags)
```

#### 创建层次关系

```python
success = memory_manager.create_hierarchy(
    parent_memory_id=parent_id,
    child_memory_id=child_id
)
```

#### 获取层次结构

```python
hierarchy = memory_manager.get_hierarchy(memory_id, depth=2)
print(hierarchy)
```

#### 查找相关记忆

```python
related_memories = memory_manager.find_related_memories(memory_id, top_k=5)
for memory in related_memories:
    print(memory["content"])
```

### 4.4 记忆更新与修正

#### 修正记忆

```python
result = memory_manager.correct_memory(
    memory_id,
    correction="修正后的内容",
    reason="修正错误信息"
)

if result["success"]:
    print("记忆修正成功")
```

#### 清理过期记忆

```python
result = memory_manager.clean_expired_memories(days=30)
print(f"清理了 {result['deleted']} 个过期记忆")
```

#### 清理未使用的记忆

```python
result = memory_manager.clean_unused_memories(
    days=90,  # 90天未使用
    min_access_count=1  # 访问次数小于1
)
print(f"清理了 {result['deleted']} 个未使用的记忆")
```

#### 优化记忆存储

```python
result = memory_manager.optimize_memory()
print(f"优化了 {result['optimized']} 个记忆")
```

### 4.5 安全性与隐私保护

#### 设置访问控制

```python
success = memory_manager.set_access_control(
    memory_id,
    allowed_roles=["admin", "user"]
)
```

#### 检查访问权限

```python
has_access = memory_manager.check_access(
    memory_id,
    user_roles=["admin"]
)
if has_access:
    print("有权访问")
else:
    print("无权访问")
```

#### 过滤敏感信息

```python
result = memory_manager.filter_sensitive_info(memory_id)
if result["success"]:
    print("敏感信息已过滤")
    print(f"过滤后的内容: {result['filtered_content']}")
```

#### 加密记忆

```python
result = memory_manager.encrypt_memory(memory_id, "encryption_key")
if result["success"]:
    print("记忆已加密")
```

#### 解密记忆

```python
result = memory_manager.decrypt_memory(memory_id, "encryption_key")
if result["success"]:
    print("记忆已解密")
```

#### 审计记忆访问

```python
success = memory_manager.audit_memory_access(
    memory_id,
    user_id="user1",
    action="read"
)
if success:
    print("访问已审计")
```

## 5. 高级配置

### 5.1 自定义存储后端

```python
from hello_agents import MemoryManager, LocalStorage

# 使用本地存储
local_storage = LocalStorage(storage_dir="custom_memory_dir")
memory_manager = MemoryManager(storage=local_storage)
```

### 5.2 性能优化

- **向量检索性能**：对于大量记忆，建议使用专业的向量数据库，如 Pinecone、Qdrant 等
- **内存使用**：对于内存受限的环境，可以调整向量维度和批处理大小
- **检索速度**：可以通过设置合适的 `top_k` 值来平衡检索速度和结果质量

## 6. 最佳实践

1. **记忆分类**：合理使用分类和标签，便于记忆管理和检索
2. **记忆优先级**：为重要记忆设置较高的优先级，确保它们在检索时被优先考虑
3. **定期清理**：定期清理过期和未使用的记忆，保持系统性能
4. **安全管理**：对敏感记忆设置访问控制，保护隐私信息
5. **记忆优化**：定期运行 `optimize_memory()` 方法，优化记忆存储

## 7. 故障排除

### 7.1 常见问题

1. **向量检索失败**：确保已安装 `sentence-transformers` 库
2. **记忆存储失败**：检查存储目录权限
3. **访问控制不生效**：确保用户角色正确设置
4. **敏感信息过滤不完整**：可以自定义敏感信息模式

### 7.2 日志与监控

记忆系统会记录关键操作的日志，可通过配置日志级别来控制日志详细程度。

## 8. 示例场景

### 8.1 知识库管理

```python
# 创建知识库分类
memory_manager.create_category("知识库", "公司知识库")

# 添加知识库条目
memory_id = memory_manager.add_memory(
    content="公司产品介绍...",
    summary="产品介绍",
    category="知识库",
    tags=["产品", "介绍"],
    priority=8
)

# 搜索知识库
results = memory_manager.semantic_search("产品功能", top_k=3)
for similarity, memory in results:
    print(f"相似度: {similarity:.2f}, 标题: {memory['summary']}")
```

### 8.2 客户服务

```python
# 添加客户信息
customer_id = memory_manager.add_memory(
    content="客户姓名: 张三, 电话: 13800138000, 需求: 咨询产品功能",
    summary="客户张三",
    category="客户",
    tags=["潜在客户", "咨询"],
    priority=7
)

# 过滤敏感信息
memory_manager.filter_sensitive_info(customer_id)

# 查找相关客户
related_customers = memory_manager.find_related_memories(customer_id, top_k=5)
```

## 9. 总结

HelloAgents 企业级记忆系统为智能体提供了强大的记忆管理能力，支持长期记忆存储、智能检索、记忆组织、更新与修正、以及安全性与隐私保护等功能。通过合理使用这些功能，可以构建更加智能、高效的智能体应用。