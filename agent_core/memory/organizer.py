"""记忆组织与管理

提供记忆的组织和管理能力：
- 记忆分类管理
- 标签管理
- 层次化组织结构
- 记忆关联管理
"""

from typing import Dict, Any, Optional, List, Set
from .long_term_memory import LongTermMemory


class MemoryOrganizer:
    """记忆组织器
    
    功能：
    - 记忆分类管理
    - 标签管理
    - 层次化组织结构
    - 记忆关联管理
    """
    
    def __init__(self, long_term_memory: LongTermMemory):
        """初始化记忆组织器
        
        Args:
            long_term_memory: 长期记忆实例
        """
        self.long_term_memory = long_term_memory
    
    def create_category(self, category_name: str, description: Optional[str] = None) -> Dict[str, Any]:
        """创建分类
        
        Args:
            category_name: 分类名称
            description: 分类描述（可选）
            
        Returns:
            分类信息
        """
        # 检查分类是否已存在（分类元数据存储在 system/category 记忆中）
        existing_categories = self.list_categories()
        if any(cat.get("name") == category_name for cat in existing_categories):
            return {
                "success": False,
                "message": f"分类 '{category_name}' 已存在"
            }
        
        # 创建分类标记记忆
        memory_id = self.long_term_memory.add_memory(
            content=f"分类: {category_name}",
            summary=description or f"分类 '{category_name}'",
            category="system",
            tags=["category", category_name],
            priority=10
        )
        
        return {
            "success": True,
            "category_name": category_name,
            "description": description,
            "memory_id": memory_id
        }
    
    def list_categories(self) -> List[Dict[str, Any]]:
        """列出所有分类
        
        Returns:
            分类列表
        """
        # 搜索系统标记的分类记忆
        memories = self.long_term_memory.list_memories(
            category="system",
            tags=["category"]
        )
        
        categories = []
        for memory in memories:
            # 提取分类名称
            content = memory.get("content", "")
            if content.startswith("分类: "):
                category_name = content[4:].strip()
                categories.append({
                    "name": category_name,
                    "description": memory.get("summary", ""),
                    "memory_id": memory.get("memory_id"),
                    "created_at": memory.get("created_at")
                })
        
        return categories
    
    def add_tag(self, memory_id: str, tag: str) -> bool:
        """为记忆添加标签
        
        Args:
            memory_id: 记忆ID
            tag: 标签
            
        Returns:
            是否添加成功
        """
        memory = self.long_term_memory.get_memory(memory_id)
        if not memory:
            return False
        
        # 获取现有标签
        tags = memory.get("tags", [])
        if tag not in tags:
            tags.append(tag)
            return self.long_term_memory.update_memory(memory_id, tags=tags)
        
        return True
    
    def remove_tag(self, memory_id: str, tag: str) -> bool:
        """从记忆中移除标签
        
        Args:
            memory_id: 记忆ID
            tag: 标签
            
        Returns:
            是否移除成功
        """
        memory = self.long_term_memory.get_memory(memory_id)
        if not memory:
            return False
        
        # 获取现有标签
        tags = memory.get("tags", [])
        if tag in tags:
            tags.remove(tag)
            return self.long_term_memory.update_memory(memory_id, tags=tags)
        
        return True
    
    def list_tags(self) -> List[str]:
        """列出所有标签
        
        Returns:
            标签列表
        """
        # 获取所有记忆
        memories = self.long_term_memory.list_memories(limit=1000)
        
        # 收集所有标签
        tags = set()
        for memory in memories:
            memory_tags = memory.get("tags", [])
            tags.update(memory_tags)
        
        # 过滤系统标签
        system_tags = {"category", "system"}
        filtered_tags = [tag for tag in tags if tag not in system_tags]
        
        return sorted(filtered_tags)
    
    def organize_by_category(self) -> Dict[str, List[Dict[str, Any]]]:
        """按分类组织记忆
        
        Returns:
            分类到记忆的映射
        """
        # 获取所有记忆
        memories = self.long_term_memory.list_memories(limit=1000)
        
        # 按分类组织
        organized = {}
        for memory in memories:
            category = memory.get("category", "uncategorized")
            if category not in organized:
                organized[category] = []
            organized[category].append(memory)
        
        return organized
    
    def organize_by_tags(self) -> Dict[str, List[Dict[str, Any]]]:
        """按标签组织记忆
        
        Returns:
            标签到记忆的映射
        """
        # 获取所有记忆
        memories = self.long_term_memory.list_memories(limit=1000)
        
        # 按标签组织
        organized = {}
        for memory in memories:
            tags = memory.get("tags", [])
            for tag in tags:
                if tag not in organized:
                    organized[tag] = []
                organized[tag].append(memory)
        
        return organized
    
    def create_hierarchy(self, parent_memory_id: str, child_memory_id: str) -> bool:
        """创建记忆层次关系
        
        Args:
            parent_memory_id: 父记忆ID
            child_memory_id: 子记忆ID
            
        Returns:
            是否创建成功
        """
        # 检查两个记忆是否存在
        parent = self.long_term_memory.get_memory(parent_memory_id)
        child = self.long_term_memory.get_memory(child_memory_id)
        
        if not parent or not child:
            return False
        
        # 更新父记忆，添加子记忆引用
        parent_children = parent.get("children", [])
        if child_memory_id not in parent_children:
            parent_children.append(child_memory_id)
            if not self.long_term_memory.update_memory(parent_memory_id, children=parent_children):
                return False
        
        # 更新子记忆，添加父记忆引用
        child_parents = child.get("parents", [])
        if parent_memory_id not in child_parents:
            child_parents.append(parent_memory_id)
            if not self.long_term_memory.update_memory(child_memory_id, parents=child_parents):
                return False
        
        return True
    
    def get_hierarchy(self, memory_id: str, depth: int = 2) -> Dict[str, Any]:
        """获取记忆的层次结构
        
        Args:
            memory_id: 记忆ID
            depth: 深度限制
            
        Returns:
            层次结构
        """
        memory = self.long_term_memory.get_memory(memory_id)
        if not memory:
            return {"error": "记忆不存在"}
        
        # 构建层次结构
        hierarchy = {
            "memory": memory,
            "children": []
        }
        
        if depth > 0:
            children = memory.get("children", [])
            for child_id in children:
                child_hierarchy = self.get_hierarchy(child_id, depth - 1)
                hierarchy["children"].append(child_hierarchy)
        
        return hierarchy
    
    def find_related_memories(self, memory_id: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """查找相关记忆
        
        Args:
            memory_id: 记忆ID
            top_k: 返回结果数量
            
        Returns:
            相关记忆列表
        """
        memory = self.long_term_memory.get_memory(memory_id)
        if not memory:
            return []
        
        # 基于标签查找相关记忆
        tags = memory.get("tags", [])
        if not tags:
            return []
        
        # 查找具有相同标签的记忆
        related_memories = []
        for tag in tags:
            memories = self.long_term_memory.list_memories(tags=[tag], limit=top_k)
            for mem in memories:
                if mem.get("memory_id") != memory_id:
                    related_memories.append(mem)
        
        # 去重并限制数量
        seen_ids = set()
        unique_memories = []
        for mem in related_memories:
            mem_id = mem.get("memory_id")
            if mem_id not in seen_ids:
                seen_ids.add(mem_id)
                unique_memories.append(mem)
                if len(unique_memories) >= top_k:
                    break
        
        return unique_memories
