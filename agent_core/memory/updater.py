"""记忆更新与修正

提供记忆的更新和修正能力：
- 记忆更新
- 记忆修正
- 过期记忆清理
- 记忆版本控制
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from .long_term_memory import LongTermMemory


class MemoryUpdater:
    """记忆更新器
    
    功能：
    - 记忆更新
    - 记忆修正
    - 过期记忆清理
    - 记忆版本控制
    """
    
    def __init__(self, long_term_memory: LongTermMemory):
        """初始化记忆更新器
        
        Args:
            long_term_memory: 长期记忆实例
        """
        self.long_term_memory = long_term_memory
    
    def update_memory(self, memory_id: str, **kwargs) -> Dict[str, Any]:
        """更新记忆
        
        Args:
            memory_id: 记忆ID
            **kwargs: 要更新的字段
            
        Returns:
            更新结果
        """
        # 检查记忆是否存在
        memory = self.long_term_memory.get_memory(memory_id)
        if not memory:
            return {
                "success": False,
                "message": "记忆不存在"
            }
        
        # 保存旧版本（版本控制）
        self._save_version(memory)
        
        # 更新字段
        for key, value in kwargs.items():
            memory[key] = value
        
        # 更新时间戳
        memory["updated_at"] = datetime.now().isoformat()
        
        # 保存更新后的记忆
        # 避免 memory_id 重复传参导致 TypeError
        memory_copy = memory.copy()
        memory_copy.pop("memory_id", None)
        success = self.long_term_memory.update_memory(memory_id, **memory_copy)
        
        return {
            "success": success,
            "memory_id": memory_id,
            "updated_fields": list(kwargs.keys())
        }
    
    def correct_memory(self, memory_id: str, correction: str, 
                      reason: Optional[str] = None) -> Dict[str, Any]:
        """修正记忆
        
        Args:
            memory_id: 记忆ID
            correction: 修正内容
            reason: 修正原因（可选）
            
        Returns:
            修正结果
        """
        # 检查记忆是否存在
        memory = self.long_term_memory.get_memory(memory_id)
        if not memory:
            return {
                "success": False,
                "message": "记忆不存在"
            }
        
        # 保存旧版本（版本控制）
        self._save_version(memory)
        
        # 添加修正记录
        corrections = memory.get("corrections", [])
        corrections.append({
            "correction": correction,
            "reason": reason,
            "corrected_at": datetime.now().isoformat()
        })
        
        # 更新记忆内容
        memory["content"] = correction
        memory["corrections"] = corrections
        memory["updated_at"] = datetime.now().isoformat()
        
        # 保存更新后的记忆
        # 从memory中移除memory_id，避免重复参数
        memory_copy = memory.copy()
        memory_copy.pop("memory_id", None)
        success = self.long_term_memory.update_memory(memory_id, **memory_copy)
        
        return {
            "success": success,
            "memory_id": memory_id,
            "correction": correction,
            "reason": reason
        }
    
    def clean_expired_memories(self, days: int = 30) -> Dict[str, Any]:
        """清理过期记忆
        
        Args:
            days: 过期天数
            
        Returns:
            清理结果
        """
        # 计算过期时间
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        # 获取所有记忆
        memories = self.long_term_memory.list_memories(limit=1000)
        
        # 查找过期记忆
        expired_memories = []
        for memory in memories:
            created_at = memory.get("created_at", "")
            if created_at and created_at < cutoff_date:
                # 检查是否有引用
                if not self._has_references(memory):
                    expired_memories.append(memory)
        
        # 删除过期记忆
        deleted_count = 0
        for memory in expired_memories:
            memory_id = memory.get("memory_id")
            if memory_id:
                if self.long_term_memory.delete_memory(memory_id):
                    deleted_count += 1
        
        return {
            "success": True,
            "total_expired": len(expired_memories),
            "deleted": deleted_count
        }
    
    def clean_unused_memories(self, days: int = 90, min_access_count: int = 1) -> Dict[str, Any]:
        """清理未使用的记忆
        
        Args:
            days: 未使用天数
            min_access_count: 最小访问次数
            
        Returns:
            清理结果
        """
        # 计算过期时间
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        # 获取所有记忆
        memories = self.long_term_memory.list_memories(limit=1000)
        
        # 查找未使用的记忆
        unused_memories = []
        for memory in memories:
            updated_at = memory.get("updated_at", memory.get("created_at", ""))
            access_count = memory.get("access_count", 0)
            
            if updated_at and updated_at < cutoff_date and access_count < min_access_count:
                # 检查是否有引用
                if not self._has_references(memory):
                    unused_memories.append(memory)
        
        # 删除未使用的记忆
        deleted_count = 0
        for memory in unused_memories:
            memory_id = memory.get("memory_id")
            if memory_id:
                if self.long_term_memory.delete_memory(memory_id):
                    deleted_count += 1
        
        return {
            "success": True,
            "total_unused": len(unused_memories),
            "deleted": deleted_count
        }
    
    def optimize_memory(self) -> Dict[str, Any]:
        """优化记忆存储
        
        Returns:
            优化结果
        """
        # 获取所有记忆
        memories = self.long_term_memory.list_memories(limit=1000)
        
        optimized_count = 0
        
        for memory in memories:
            memory_id = memory.get("memory_id")
            if not memory_id:
                continue
            
            # 优化步骤
            optimized = False
            
            # 1. 清理空字段
            cleaned_memory = self._clean_empty_fields(memory)
            if cleaned_memory != memory:
                optimized = True
                memory = cleaned_memory
            
            # 2. 压缩内容
            compressed_memory = self._compress_content(memory)
            if compressed_memory != memory:
                optimized = True
                memory = compressed_memory
            
            # 保存优化后的记忆
            if optimized:
                if self.long_term_memory.update_memory(memory_id, **memory):
                    optimized_count += 1
        
        return {
            "success": True,
            "optimized": optimized_count
        }
    
    def _save_version(self, memory: Dict[str, Any]) -> None:
        """保存记忆版本
        
        Args:
            memory: 记忆数据
        """
        # 获取版本历史
        versions = memory.get("versions", [])
        
        # 创建版本记录
        version = {
            "content": memory.get("content"),
            "summary": memory.get("summary"),
            "created_at": memory.get("created_at"),
            "saved_at": datetime.now().isoformat()
        }
        
        # 添加到版本历史（最多保存5个版本）
        versions.append(version)
        if len(versions) > 5:
            versions = versions[-5:]
        
        # 更新版本历史
        memory["versions"] = versions
    
    def _has_references(self, memory: Dict[str, Any]) -> bool:
        """检查记忆是否被引用
        
        Args:
            memory: 记忆数据
            
        Returns:
            是否被引用
        """
        # 检查是否有子记忆
        children = memory.get("children", [])
        if children:
            return True
        
        # 检查是否有父记忆
        parents = memory.get("parents", [])
        if parents:
            return True
        
        # 检查是否是系统记忆
        category = memory.get("category")
        if category == "system":
            return True
        
        return False
    
    def _clean_empty_fields(self, memory: Dict[str, Any]) -> Dict[str, Any]:
        """清理空字段
        
        Args:
            memory: 记忆数据
            
        Returns:
            清理后的记忆数据
        """
        cleaned = {}
        for key, value in memory.items():
            if value is not None and value != "" and value != [] and value != {}:
                cleaned[key] = value
        return cleaned
    
    def _compress_content(self, memory: Dict[str, Any]) -> Dict[str, Any]:
        """压缩内容
        
        Args:
            memory: 记忆数据
            
        Returns:
            压缩后的记忆数据
        """
        # 简单压缩，实际应用中可以使用更复杂的压缩算法
        content = memory.get("content")
        if content and len(content) > 1000:
            # 保留前500和后500字符
            compressed = content[:500] + "... [内容已压缩] ..." + content[-500:]
            memory["content"] = compressed
            memory["compressed"] = True
        return memory
