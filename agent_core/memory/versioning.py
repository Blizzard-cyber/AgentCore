"""记忆版本控制模块

用于管理记忆的版本历史，支持版本记录和回滚。
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid


class MemoryVersionManager:
    """记忆版本管理器
    
    功能：
    - 记录记忆的版本历史
    - 支持版本回滚
    - 版本比较
    - 版本标签管理
    """
    
    def __init__(self, storage: Any):
        """初始化版本管理器
        
        Args:
            storage: 存储后端，用于存储版本历史
        """
        self.storage = storage
        self.version_prefix = "version_"
    
    def create_version(self, memory_id: str, 
                      memory_data: Dict[str, Any], 
                      reason: Optional[str] = None) -> str:
        """创建记忆版本
        
        Args:
            memory_id: 记忆ID
            memory_data: 记忆数据
            reason: 版本创建原因
            
        Returns:
            版本ID
        """
        # 生成版本ID
        version_id = str(uuid.uuid4())
        
        # 创建版本数据，存储记忆数据的副本
        import copy
        version_data = {
            "version_id": version_id,
            "memory_id": memory_id,
            "data": copy.deepcopy(memory_data),
            "created_at": datetime.now().isoformat(),
            "reason": reason,
            "version_number": self._get_next_version_number(memory_id),
            "original_memory_id": memory_id
        }
        
        # 存储版本
        version_key = f"{self.version_prefix}{memory_id}_{version_id}"
        self.storage.save(version_data, version_key)
        
        # 由于我们不再使用索引，不需要更新索引
        
        return version_id
    
    def get_version(self, memory_id: str, version_id: str) -> Optional[Dict[str, Any]]:
        """获取指定版本
        
        Args:
            memory_id: 记忆ID
            version_id: 版本ID
            
        Returns:
            版本数据，不存在返回None
        """
        version_key = f"{self.version_prefix}{memory_id}_{version_id}"
        return self.storage.load(version_key)
    
    def get_all_versions(self, memory_id: str) -> List[Dict[str, Any]]:
        """获取记忆的所有版本
        
        Args:
            memory_id: 记忆ID
            
        Returns:
            版本列表，按版本号降序排序
        """
        # 列出所有记忆
        all_memories = self.storage.list(1000)
        
        # 过滤出该记忆的版本
        versions = []
        for memory in all_memories:
            if memory.get("original_memory_id") == memory_id:
                versions.append(memory)
        
        # 按版本号降序排序
        versions.sort(key=lambda x: x.get("version_number", 0), reverse=True)
        
        return versions
    
    def rollback_to_version(self, memory_id: str, version_id: str) -> Dict[str, Any]:
        """回滚到指定版本
        
        Args:
            memory_id: 记忆ID
            version_id: 版本ID
            
        Returns:
            回滚后的记忆数据
        """
        # 获取指定版本
        version = self.get_version(memory_id, version_id)
        if not version:
            raise ValueError(f"Version {version_id} not found for memory {memory_id}")
        
        # 获取版本数据
        version_data = version.get("data", {})
        
        # 保存当前版本（作为回滚前的版本）
        current_memory = self.storage.load(memory_id)
        if current_memory:
            self.create_version(memory_id, current_memory, "Before rollback")
        
        # 确保版本数据包含必要的字段
        if "memory_id" not in version_data:
            version_data["memory_id"] = memory_id
        if "created_at" not in version_data:
            version_data["created_at"] = current_memory.get("created_at", datetime.now().isoformat())
        if "updated_at" not in version_data:
            version_data["updated_at"] = datetime.now().isoformat()
        if "access_count" not in version_data:
            version_data["access_count"] = 0
        
        # 恢复到指定版本
        self.storage.save(version_data, memory_id)
        
        # 验证回滚是否成功
        rolled_back_memory = self.storage.load(memory_id)
        if rolled_back_memory:
            return rolled_back_memory
        
        return version_data
    
    def compare_versions(self, memory_id: str, 
                        version_id1: str, 
                        version_id2: str) -> Dict[str, Any]:
        """比较两个版本
        
        Args:
            memory_id: 记忆ID
            version_id1: 版本1 ID
            version_id2: 版本2 ID
            
        Returns:
            版本差异
        """
        # 获取两个版本
        version1 = self.get_version(memory_id, version_id1)
        version2 = self.get_version(memory_id, version_id2)
        
        if not version1 or not version2:
            raise ValueError("One or both versions not found")
        
        # 提取数据
        data1 = version1.get("data", {})
        data2 = version2.get("data", {})
        
        # 计算差异
        added = {k: v for k, v in data2.items() if k not in data1}
        removed = {k: v for k, v in data1.items() if k not in data2}
        modified = {k: {"old": data1[k], "new": data2[k]} 
                   for k in data1 if k in data2 and data1[k] != data2[k]}
        
        return {
            "version1": version_id1,
            "version2": version_id2,
            "added": added,
            "removed": removed,
            "modified": modified
        }
    
    def tag_version(self, memory_id: str, 
                   version_id: str, 
                   tag: str, 
                   description: Optional[str] = None) -> bool:
        """为版本添加标签
        
        Args:
            memory_id: 记忆ID
            version_id: 版本ID
            tag: 标签名
            description: 标签描述
            
        Returns:
            是否成功
        """
        # 获取版本
        version = self.get_version(memory_id, version_id)
        if not version:
            return False
        
        # 添加标签
        if "tags" not in version:
            version["tags"] = []
        
        # 检查标签是否已存在
        existing_tags = [t.get("name") for t in version["tags"]]
        if tag in existing_tags:
            return False
        
        # 添加新标签
        version["tags"].append({
            "name": tag,
            "description": description,
            "created_at": datetime.now().isoformat()
        })
        
        # 保存版本
        version_key = f"{self.version_prefix}{memory_id}_{version_id}"
        self.storage.save(version, version_key)
        
        # 由于我们不再使用索引，不需要更新标签索引
        
        return True
    
    def get_version_by_tag(self, memory_id: str, tag: str) -> Optional[Dict[str, Any]]:
        """通过标签获取版本
        
        Args:
            memory_id: 记忆ID
            tag: 标签名
            
        Returns:
            版本数据，不存在返回None
        """
        # 列出所有版本
        versions = self.get_all_versions(memory_id)
        
        # 查找带有指定标签的版本
        for version in versions:
            tags = version.get("tags", [])
            for t in tags:
                if t.get("name") == tag:
                    return version
        
        return None
    
    def delete_version(self, memory_id: str, version_id: str) -> bool:
        """删除版本
        
        Args:
            memory_id: 记忆ID
            version_id: 版本ID
            
        Returns:
            是否成功
        """
        # 检查版本是否存在
        version_key = f"{self.version_prefix}{memory_id}_{version_id}"
        if not self.storage.load(version_key):
            return False
        
        # 删除版本
        self.storage.delete(version_key)
        
        # 由于我们不再使用索引，不需要更新索引
        
        return True
    
    def _get_next_version_number(self, memory_id: str) -> int:
        """获取下一个版本号
        
        Args:
            memory_id: 记忆ID
            
        Returns:
            下一个版本号
        """
        # 列出所有版本
        versions = self.get_all_versions(memory_id)
        
        # 计算下一个版本号
        if not versions:
            return 1
        
        max_version = max(v.get("version_number", 0) for v in versions)
        return max_version + 1
    
    # 由于我们不再使用索引来管理版本，删除所有索引相关方法
    
    def get_version_stats(self, memory_id: str) -> Dict[str, Any]:
        """获取版本统计信息
        
        Args:
            memory_id: 记忆ID
            
        Returns:
            统计信息
        """
        versions = self.get_all_versions(memory_id)
        
        return {
            "total_versions": len(versions),
            "latest_version": versions[0] if versions else None,
            "oldest_version": versions[-1] if versions else None
        }