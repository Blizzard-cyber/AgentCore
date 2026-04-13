"""存储接口与实现

提供不同的存储后端支持：
- MemoryStorage: 存储接口基类
- LocalStorage: 本地文件存储
- VectorDBStorage: 向量数据库存储（支持向量检索）
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple
import json
import os
import hashlib
from pathlib import Path
import uuid
from datetime import datetime


class MemoryStorage(ABC):
    """存储接口基类"""
    
    @abstractmethod
    def save(self, data: Dict[str, Any], memory_id: Optional[str] = None) -> str:
        """保存记忆数据
        
        Args:
            data: 记忆数据
            memory_id: 记忆ID（可选）
            
        Returns:
            记忆ID
        """
        pass
    
    @abstractmethod
    def load(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """加载记忆数据
        
        Args:
            memory_id: 记忆ID
            
        Returns:
            记忆数据，不存在返回None
        """
        pass
    
    @abstractmethod
    def delete(self, memory_id: str) -> bool:
        """删除记忆数据
        
        Args:
            memory_id: 记忆ID
            
        Returns:
            是否删除成功
        """
        pass
    
    @abstractmethod
    def list(self, limit: int = 100) -> List[Dict[str, Any]]:
        """列出所有记忆
        
        Args:
            limit: 限制数量
            
        Returns:
            记忆列表
        """
        pass
    
    @abstractmethod
    def search(self, query: str, top_k: int = 5) -> List[Tuple[float, Dict[str, Any]]]:
        """搜索记忆
        
        Args:
            query: 搜索查询
            top_k: 返回结果数量
            
        Returns:
            搜索结果列表，每个元素为(相似度, 记忆数据)
        """
        pass


class LocalStorage(MemoryStorage):
    """本地文件存储"""
    
    def __init__(self, storage_dir: str = "memory/long_term"):
        """初始化本地存储
        
        Args:
            storage_dir: 存储目录
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
    
    def save(self, data: Dict[str, Any], memory_id: Optional[str] = None) -> str:
        """保存记忆数据
        
        Args:
            data: 记忆数据
            memory_id: 记忆ID（可选）
            
        Returns:
            记忆ID
        """
        if memory_id is None:
            memory_id = self._generate_memory_id()
        
        # 确保数据包含必要字段
        if "memory_id" not in data:
            data["memory_id"] = memory_id
        if "created_at" not in data:
            data["created_at"] = datetime.now().isoformat()
        if "updated_at" not in data:
            data["updated_at"] = datetime.now().isoformat()
        
        # 原子写入
        filepath = self.storage_dir / f"{memory_id}.json"
        temp_path = str(filepath) + ".tmp"
        
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        os.replace(temp_path, filepath)
        return memory_id
    
    def load(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """加载记忆数据
        
        Args:
            memory_id: 记忆ID
            
        Returns:
            记忆数据，不存在返回None
        """
        filepath = self.storage_dir / f"{memory_id}.json"
        if not filepath.exists():
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None
    
    def delete(self, memory_id: str) -> bool:
        """删除记忆数据
        
        Args:
            memory_id: 记忆ID
            
        Returns:
            是否删除成功
        """
        filepath = self.storage_dir / f"{memory_id}.json"
        if filepath.exists():
            os.remove(filepath)
            return True
        return False
    
    def list(self, limit: int = 100) -> List[Dict[str, Any]]:
        """列出所有记忆
        
        Args:
            limit: 限制数量
            
        Returns:
            记忆列表
        """
        memories = []
        
        for filepath in self.storage_dir.glob("*.json"):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    memories.append(data)
            except Exception:
                pass
        
        # 按更新时间倒序排序
        memories.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
        return memories[:limit]
    
    def search(self, query: str, top_k: int = 5) -> List[Tuple[float, Dict[str, Any]]]:
        """搜索记忆（简单文本匹配）
        
        Args:
            query: 搜索查询
            top_k: 返回结果数量
            
        Returns:
            搜索结果列表，每个元素为(相似度, 记忆数据)
        """
        results = []
        
        for filepath in self.storage_dir.glob("*.json"):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # 简单文本匹配
                    content = data.get("content", "") + " " + data.get("summary", "")
                    similarity = self._calculate_similarity(query, content)
                    
                    if similarity > 0:
                        results.append((similarity, data))
            except Exception:
                pass
        
        # 按相似度排序
        results.sort(key=lambda x: x[0], reverse=True)
        return results[:top_k]
    
    def _generate_memory_id(self) -> str:
        """生成记忆ID
        
        Returns:
            记忆ID
        """
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        unique_suffix = uuid.uuid4().hex[:8]
        return f"m-{timestamp}-{unique_suffix}"
    
    def _calculate_similarity(self, query: str, content: str) -> float:
        """计算文本相似度（简单实现）
        
        Args:
            query: 查询文本
            content: 内容文本
            
        Returns:
            相似度（0-1）
        """
        query_words = set(query.lower().split())
        content_words = set(content.lower().split())
        
        if not query_words:
            return 0
        
        intersection = query_words & content_words
        return len(intersection) / len(query_words)


class VectorDBStorage(MemoryStorage):
    """向量数据库存储
    
    注：本实现使用内存向量存储，实际生产环境应使用专业向量数据库
    """
    
    def __init__(self, dim: int = 768):
        """初始化向量存储
        
        Args:
            dim: 向量维度
        """
        self.dim = dim
        self.memories = {}
        self.vectors = {}
        
        # 模拟向量生成（实际应使用真实的嵌入模型）
        try:
            from sentence_transformers import SentenceTransformer
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        except ImportError:
            self.embedding_model = None
    
    def save(self, data: Dict[str, Any], memory_id: Optional[str] = None) -> str:
        """保存记忆数据
        
        Args:
            data: 记忆数据
            memory_id: 记忆ID（可选）
            
        Returns:
            记忆ID
        """
        if memory_id is None:
            memory_id = self._generate_memory_id()
        
        # 确保数据包含必要字段
        if "memory_id" not in data:
            data["memory_id"] = memory_id
        if "created_at" not in data:
            data["created_at"] = datetime.now().isoformat()
        if "updated_at" not in data:
            data["updated_at"] = datetime.now().isoformat()
        
        # 生成向量
        content = data.get("content", "") + " " + data.get("summary", "")
        vector = self._generate_vector(content)
        
        # 存储
        self.memories[memory_id] = data
        self.vectors[memory_id] = vector
        
        return memory_id
    
    def load(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """加载记忆数据
        
        Args:
            memory_id: 记忆ID
            
        Returns:
            记忆数据，不存在返回None
        """
        return self.memories.get(memory_id)
    
    def delete(self, memory_id: str) -> bool:
        """删除记忆数据
        
        Args:
            memory_id: 记忆ID
            
        Returns:
            是否删除成功
        """
        if memory_id in self.memories:
            del self.memories[memory_id]
            del self.vectors[memory_id]
            return True
        return False
    
    def list(self, limit: int = 100) -> List[Dict[str, Any]]:
        """列出所有记忆
        
        Args:
            limit: 限制数量
            
        Returns:
            记忆列表
        """
        memories = list(self.memories.values())
        memories.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
        return memories[:limit]
    
    def search(self, query: str, top_k: int = 5) -> List[Tuple[float, Dict[str, Any]]]:
        """搜索记忆（向量相似度）
        
        Args:
            query: 搜索查询
            top_k: 返回结果数量
            
        Returns:
            搜索结果列表，每个元素为(相似度, 记忆数据)
        """
        if not self.vectors:
            return []

        # 无嵌入模型时降级到关键词匹配，避免回退向量导致检索质量失真
        if self.embedding_model is None:
            results: List[Tuple[float, Dict[str, Any]]] = []
            for memory in self.memories.values():
                content = memory.get("content", "") + " " + memory.get("summary", "")
                similarity = self._calculate_text_similarity(query, content)
                if similarity > 0:
                    results.append((similarity, memory))
            results.sort(key=lambda x: x[0], reverse=True)
            return results[:top_k]
        
        # 生成查询向量
        query_vector = self._generate_vector(query)
        
        # 计算相似度
        results = []
        for memory_id, vector in self.vectors.items():
            cosine_similarity = self._calculate_cosine_similarity(query_vector, vector)
            similarity = (cosine_similarity + 1.0) / 2.0
            results.append((similarity, self.memories[memory_id]))
        
        # 按相似度排序
        results.sort(key=lambda x: x[0], reverse=True)
        return results[:top_k]

    def _calculate_text_similarity(self, query: str, content: str) -> float:
        """计算简单关键词相似度（用于无模型降级检索）"""
        query_norm = query.lower().strip()
        content_norm = content.lower().strip()
        if not query_norm:
            return 0.0

        # 子串命中直接给高分，兼容中文无空格文本
        if query_norm in content_norm:
            return 1.0

        query_words = set(query_norm.split())
        content_words = set(content_norm.split())
        word_score = 0.0
        if query_words:
            word_score = len(query_words & content_words) / len(query_words)

        # 字符级重叠作为回退，提升中文场景可检索性
        query_chars = {ch for ch in query_norm if not ch.isspace()}
        content_chars = {ch for ch in content_norm if not ch.isspace()}
        char_score = 0.0
        if query_chars:
            char_score = len(query_chars & content_chars) / len(query_chars)

        return max(word_score, char_score)
    
    def _generate_memory_id(self) -> str:
        """生成记忆ID
        
        Returns:
            记忆ID
        """
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        unique_suffix = uuid.uuid4().hex[:8]
        return f"m-{timestamp}-{unique_suffix}"
    
    def _generate_vector(self, text: str) -> List[float]:
        """生成文本向量
        
        Args:
            text: 文本
            
        Returns:
            向量
        """
        if self.embedding_model:
            return self.embedding_model.encode(text).tolist()
        else:
            # 基于文本哈希生成稳定伪随机向量，避免所有向量共线
            # 该回退方案仅用于无嵌入模型时的基础可用性
            values: List[float] = []
            counter = 0
            while len(values) < self.dim:
                digest = hashlib.sha256(f"{text}|{counter}".encode("utf-8")).digest()
                for i in range(0, len(digest), 4):
                    if len(values) >= self.dim:
                        break
                    chunk = int.from_bytes(digest[i:i + 4], "big", signed=False)
                    # 映射到 [-1, 1] 区间
                    values.append((chunk / 0xFFFFFFFF) * 2.0 - 1.0)
                counter += 1
            return values
    
    def _calculate_cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """计算余弦相似度
        
        Args:
            vec1: 向量1
            vec2: 向量2
            
        Returns:
            相似度（0-1）
        """
        import math
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(a * a for a in vec2))
        
        if norm1 == 0 or norm2 == 0:
            return 0
        
        return dot_product / (norm1 * norm2)
