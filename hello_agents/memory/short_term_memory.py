"""短期记忆（工作记忆）模块

用于存储临时会话信息，具有自动过期机制和快速访问特性。
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import threading
import time


class ShortTermMemory:
    """短期记忆（工作记忆）
    
    功能：
    - 存储临时会话信息
    - 自动过期机制
    - 快速访问
    - 与长期记忆的交互
    """
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        """初始化短期记忆
        
        Args:
            max_size: 最大记忆数量
            default_ttl: 默认过期时间（秒）
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.memories: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.RLock()
        
        # 启动过期清理线程
        self._start_cleanup_thread()
    
    def add_memory(self, content: str, session_id: str, 
                   summary: Optional[str] = None, 
                   tags: Optional[List[str]] = None, 
                   ttl: Optional[int] = None) -> str:
        """添加短期记忆
        
        Args:
            content: 记忆内容
            session_id: 会话ID
            summary: 记忆摘要（可选）
            tags: 记忆标签（可选）
            ttl: 过期时间（秒，可选）
            
        Returns:
            记忆ID
        """
        import uuid
        memory_id = str(uuid.uuid4())
        
        ttl = ttl or self.default_ttl
        expiry_time = datetime.now() + timedelta(seconds=ttl)
        
        memory = {
            "id": memory_id,
            "content": content,
            "session_id": session_id,
            "summary": summary,
            "tags": tags or [],
            "created_at": datetime.now(),
            "expiry_time": expiry_time,
            "access_count": 0,
            "last_accessed": datetime.now()
        }
        
        with self.lock:
            # 检查是否达到最大容量
            if len(self.memories) >= self.max_size:
                # 删除最旧的记忆
                oldest_id = min(self.memories.keys(), 
                              key=lambda k: self.memories[k]["created_at"])
                del self.memories[oldest_id]
            
            self.memories[memory_id] = memory
        
        return memory_id
    
    def get_memory(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """获取短期记忆
        
        Args:
            memory_id: 记忆ID
            
        Returns:
            记忆数据，不存在或已过期返回None
        """
        with self.lock:
            if memory_id not in self.memories:
                return None
            
            memory = self.memories[memory_id]
            
            # 检查是否过期
            if datetime.now() > memory["expiry_time"]:
                del self.memories[memory_id]
                return None
            
            # 更新访问信息
            memory["access_count"] += 1
            memory["last_accessed"] = datetime.now()
            
            return memory.copy()
    
    def get_session_memories(self, session_id: str) -> List[Dict[str, Any]]:
        """获取指定会话的所有记忆
        
        Args:
            session_id: 会话ID
            
        Returns:
            记忆列表
        """
        with self.lock:
            # 过滤出未过期且属于指定会话的记忆
            valid_memories = []
            expired_ids = []
            
            for memory_id, memory in self.memories.items():
                if datetime.now() > memory["expiry_time"]:
                    expired_ids.append(memory_id)
                elif memory["session_id"] == session_id:
                    # 更新访问信息
                    memory["access_count"] += 1
                    memory["last_accessed"] = datetime.now()
                    valid_memories.append(memory.copy())
            
            # 清理过期记忆
            for memory_id in expired_ids:
                del self.memories[memory_id]
            
            # 按创建时间排序
            valid_memories.sort(key=lambda x: x["created_at"])
            
            return valid_memories
    
    def update_memory(self, memory_id: str, **kwargs) -> bool:
        """更新短期记忆
        
        Args:
            memory_id: 记忆ID
            **kwargs: 要更新的字段
            
        Returns:
            是否更新成功
        """
        with self.lock:
            if memory_id not in self.memories:
                return False
            
            memory = self.memories[memory_id]
            
            # 检查是否过期
            if datetime.now() > memory["expiry_time"]:
                del self.memories[memory_id]
                return False
            
            # 更新字段
            for key, value in kwargs.items():
                if key in memory:
                    memory[key] = value
            
            # 更新访问信息
            memory["last_accessed"] = datetime.now()
            
            return True
    
    def delete_memory(self, memory_id: str) -> bool:
        """删除短期记忆
        
        Args:
            memory_id: 记忆ID
            
        Returns:
            是否删除成功
        """
        with self.lock:
            if memory_id not in self.memories:
                return False
            
            del self.memories[memory_id]
            return True
    
    def delete_session_memories(self, session_id: str) -> int:
        """删除指定会话的所有记忆
        
        Args:
            session_id: 会话ID
            
        Returns:
            删除的记忆数量
        """
        with self.lock:
            to_delete = [
                memory_id for memory_id, memory in self.memories.items()
                if memory["session_id"] == session_id
            ]
            
            for memory_id in to_delete:
                del self.memories[memory_id]
            
            return len(to_delete)
    
    def get_memory_stats(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """获取记忆统计信息
        
        Args:
            session_id: 会话ID（可选）
            
        Returns:
            统计信息
        """
        with self.lock:
            # 先清理过期记忆
            self._cleanup_expired()
            
            if session_id:
                session_memories = [
                    memory for memory in self.memories.values()
                    if memory["session_id"] == session_id
                ]
                total_count = len(session_memories)
                access_count = sum(memory["access_count"] for memory in session_memories)
            else:
                total_count = len(self.memories)
                access_count = sum(memory["access_count"] for memory in self.memories.values())
            
            return {
                "total_count": total_count,
                "access_count": access_count,
                "max_size": self.max_size,
                "default_ttl": self.default_ttl
            }
    
    def _cleanup_expired(self):
        """清理过期记忆"""
        with self.lock:
            expired_ids = [
                memory_id for memory_id, memory in self.memories.items()
                if datetime.now() > memory["expiry_time"]
            ]
            
            for memory_id in expired_ids:
                del self.memories[memory_id]
    
    def _start_cleanup_thread(self):
        """启动过期清理线程"""
        def cleanup_task():
            while True:
                time.sleep(60)  # 每分钟清理一次
                self._cleanup_expired()
        
        thread = threading.Thread(target=cleanup_task, daemon=True)
        thread.start()
    
    def clear(self):
        """清空所有短期记忆"""
        with self.lock:
            self.memories.clear()
    
    def __len__(self) -> int:
        """返回当前记忆数量"""
        with self.lock:
            self._cleanup_expired()
            return len(self.memories)