"""记忆缓存模块

用于缓存记忆检索结果，提高检索性能。
"""

from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
import hashlib
import threading


class MemoryCache:
    """记忆缓存
    
    功能：
    - 缓存记忆检索结果
    - 自动过期机制
    - 缓存大小限制
    - 线程安全
    """
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        """初始化记忆缓存
        
        Args:
            max_size: 最大缓存项数量
            default_ttl: 默认过期时间（秒）
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.RLock()
        
        # 启动过期清理线程
        self._start_cleanup_thread()
    
    def _generate_key(self, query: str, **kwargs) -> str:
        """生成缓存键
        
        Args:
            query: 查询文本
            **kwargs: 其他参数
            
        Returns:
            缓存键
        """
        # 构建键的内容
        key_parts = [query]
        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}:{v}")
        
        # 生成哈希值作为键
        key_str = "|".join(key_parts)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, query: str, **kwargs) -> Optional[Any]:
        """获取缓存
        
        Args:
            query: 查询文本
            **kwargs: 其他参数
            
        Returns:
            缓存的结果，不存在或已过期返回None
        """
        key = self._generate_key(query, **kwargs)
        
        with self.lock:
            if key not in self.cache:
                return None
            
            item = self.cache[key]
            
            # 检查是否过期
            if datetime.now() > item["expiry_time"]:
                del self.cache[key]
                return None
            
            # 更新访问时间
            item["last_accessed"] = datetime.now()
            item["access_count"] += 1
            
            return item["value"]
    
    def set(self, query: str, value: Any, **kwargs) -> None:
        """设置缓存
        
        Args:
            query: 查询文本
            value: 缓存值
            **kwargs: 其他参数，可包含ttl
        """
        ttl = kwargs.pop("ttl", self.default_ttl)
        key = self._generate_key(query, **kwargs)
        
        item = {
            "value": value,
            "created_at": datetime.now(),
            "expiry_time": datetime.now() + timedelta(seconds=ttl),
            "last_accessed": datetime.now(),
            "access_count": 0
        }
        
        with self.lock:
            # 检查是否达到最大容量
            if len(self.cache) >= self.max_size:
                # 删除最旧的或最少使用的项
                self._evict_oldest()
            
            self.cache[key] = item
    
    def delete(self, query: str, **kwargs) -> bool:
        """删除缓存
        
        Args:
            query: 查询文本
            **kwargs: 其他参数
            
        Returns:
            是否删除成功
        """
        key = self._generate_key(query, **kwargs)
        
        with self.lock:
            if key not in self.cache:
                return False
            
            del self.cache[key]
            return True
    
    def clear(self) -> None:
        """清空缓存"""
        with self.lock:
            self.cache.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息
        
        Returns:
            统计信息
        """
        with self.lock:
            # 清理过期项
            self._cleanup_expired()
            
            total_items = len(self.cache)
            total_accesses = sum(item["access_count"] for item in self.cache.values())
            
            if total_items > 0:
                oldest_item = min(self.cache.values(), key=lambda x: x["created_at"])
                newest_item = max(self.cache.values(), key=lambda x: x["created_at"])
            else:
                oldest_item = None
                newest_item = None
            
            return {
                "total_items": total_items,
                "max_size": self.max_size,
                "total_accesses": total_accesses,
                "oldest_item_age": (datetime.now() - oldest_item["created_at"]).total_seconds() if oldest_item else 0,
                "newest_item_age": (datetime.now() - newest_item["created_at"]).total_seconds() if newest_item else 0
            }
    
    def _cleanup_expired(self):
        """清理过期缓存项"""
        with self.lock:
            expired_keys = []
            for key, item in self.cache.items():
                if datetime.now() > item["expiry_time"]:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.cache[key]
    
    def _evict_oldest(self):
        """删除最旧的缓存项"""
        with self.lock:
            if not self.cache:
                return
            
            # 优先删除过期项
            self._cleanup_expired()
            
            if len(self.cache) >= self.max_size:
                # 删除最少使用的项
                least_used_key = min(
                    self.cache.keys(),
                    key=lambda k: (self.cache[k]["access_count"], self.cache[k]["last_accessed"])
                )
                del self.cache[least_used_key]
    
    def _start_cleanup_thread(self):
        """启动过期清理线程"""
        import time
        
        def cleanup_task():
            while True:
                time.sleep(60)  # 每分钟清理一次
                self._cleanup_expired()
        
        thread = threading.Thread(target=cleanup_task, daemon=True)
        thread.start()
    
    def __len__(self) -> int:
        """返回当前缓存项数量"""
        with self.lock:
            self._cleanup_expired()
            return len(self.cache)