"""长期记忆存储与管理

提供跨会话的长期记忆能力：
- 支持记忆的添加、查询、更新、删除
- 支持记忆的分类和标签
- 支持记忆的优先级管理
"""

from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from .storage import MemoryStorage, LocalStorage


class LongTermMemory:
    """长期记忆管理
    
    功能：
    - 添加记忆
    - 查询记忆
    - 更新记忆
    - 删除记忆
    - 记忆分类和标签管理
    - 记忆优先级管理
    """
    
    def __init__(self, storage: Optional[MemoryStorage] = None):
        """初始化长期记忆
        
        Args:
            storage: 存储后端，默认使用LocalStorage
        """
        self.storage = storage or LocalStorage()
    
    def add_memory(self, content: str, summary: Optional[str] = None, 
                   category: Optional[str] = None, tags: Optional[List[str]] = None, 
                   priority: int = 0, metadata: Optional[Dict[str, Any]] = None) -> str:
        """添加记忆
        
        Args:
            content: 记忆内容
            summary: 记忆摘要（可选）
            category: 记忆分类（可选）
            tags: 记忆标签（可选）
            priority: 记忆优先级（0-10，默认0）
            metadata: 记忆元数据（可选）
            
        Returns:
            记忆ID
        """
        memory_data = {
            "content": content,
            "summary": summary or self._generate_summary(content),
            "category": category,
            "tags": tags or [],
            "priority": priority,
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "access_count": 0
        }
        
        return self.storage.save(memory_data)
    
    def get_memory(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """获取记忆
        
        Args:
            memory_id: 记忆ID
            
        Returns:
            记忆数据，不存在返回None
        """
        memory = self.storage.load(memory_id)
        if memory:
            # 更新访问次数
            memory["access_count"] = memory.get("access_count", 0) + 1
            memory["updated_at"] = datetime.now().isoformat()
            self.storage.save(memory, memory_id)
        return memory
    
    def update_memory(self, memory_id: str, **kwargs) -> bool:
        """更新记忆
        
        Args:
            memory_id: 记忆ID
            **kwargs: 要更新的字段
            
        Returns:
            是否更新成功
        """
        memory = self.storage.load(memory_id)
        if not memory:
            return False
        
        # 更新字段
        for key, value in kwargs.items():
            memory[key] = value
        
        # 更新时间戳
        memory["updated_at"] = datetime.now().isoformat()
        
        self.storage.save(memory, memory_id)
        return True
    
    def delete_memory(self, memory_id: str) -> bool:
        """删除记忆
        
        Args:
            memory_id: 记忆ID
            
        Returns:
            是否删除成功
        """
        return self.storage.delete(memory_id)
    
    def search_memories(self, query: str, top_k: int = 5, 
                       category: Optional[str] = None, 
                       tags: Optional[List[str]] = None) -> List[Tuple[float, Dict[str, Any]]]:
        """搜索记忆
        
        Args:
            query: 搜索查询
            top_k: 返回结果数量
            category: 分类过滤（可选）
            tags: 标签过滤（可选）
            
        Returns:
            搜索结果列表，每个元素为(相似度, 记忆数据)
        """
        results = self.storage.search(query, top_k * 2)  # 获取更多结果用于过滤
        
        # 过滤结果
        filtered_results = []
        for similarity, memory in results:
            # 分类过滤
            if category and memory.get("category") != category:
                continue
            
            # 标签过滤
            if tags:
                memory_tags = memory.get("tags", [])
                if not any(tag in memory_tags for tag in tags):
                    continue
            
            filtered_results.append((similarity, memory))
        
        # 按相似度排序并限制数量
        filtered_results.sort(key=lambda x: x[0], reverse=True)
        return filtered_results[:top_k]
    
    def list_memories(self, limit: int = 100, 
                     category: Optional[str] = None, 
                     tags: Optional[List[str]] = None, 
                     min_priority: Optional[int] = None) -> List[Dict[str, Any]]:
        """列出记忆
        
        Args:
            limit: 限制数量
            category: 分类过滤（可选）
            tags: 标签过滤（可选）
            min_priority: 最小优先级过滤（可选）
            
        Returns:
            记忆列表
        """
        memories = self.storage.list(limit * 2)  # 获取更多结果用于过滤
        
        # 过滤结果
        filtered_memories = []
        for memory in memories:
            # 分类过滤
            if category and memory.get("category") != category:
                continue
            
            # 标签过滤
            if tags:
                memory_tags = memory.get("tags", [])
                if not any(tag in memory_tags for tag in tags):
                    continue
            
            # 优先级过滤
            if min_priority is not None and memory.get("priority", 0) < min_priority:
                continue
            
            filtered_memories.append(memory)
        
        # 按更新时间倒序排序并限制数量
        filtered_memories.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
        return filtered_memories[:limit]
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """获取记忆统计信息
        
        Returns:
            统计信息
        """
        memories = self.storage.list(1000)  # 获取所有记忆
        
        total_memories = len(memories)
        category_stats = {}
        tag_stats = {}
        priority_stats = {}
        
        for memory in memories:
            # 分类统计
            category = memory.get("category")
            if category:
                category_stats[category] = category_stats.get(category, 0) + 1
            
            # 标签统计
            tags = memory.get("tags", [])
            for tag in tags:
                tag_stats[tag] = tag_stats.get(tag, 0) + 1
            
            # 优先级统计
            priority = memory.get("priority", 0)
            priority_stats[priority] = priority_stats.get(priority, 0) + 1
        
        return {
            "total_memories": total_memories,
            "category_stats": category_stats,
            "tag_stats": tag_stats,
            "priority_stats": priority_stats
        }
    
    def _generate_summary(self, content: str) -> str:
        """生成记忆摘要
        
        Args:
            content: 记忆内容
            
        Returns:
            摘要
        """
        # 简单摘要生成
        if len(content) <= 100:
            return content
        
        # 提取前100个字符作为摘要
        summary = content[:100].strip()
        if summary[-1] not in ['.', '!', '?', ',', ';', ':']:
            summary += '...'
        
        return summary
