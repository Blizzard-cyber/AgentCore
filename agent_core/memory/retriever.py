"""记忆检索机制

提供高效的记忆检索能力：
- 向量检索（基于语义相似度）
- 关键词检索
- 混合检索（向量 + 关键词）
- 检索结果排序与过滤
"""

from typing import Dict, Any, Optional, List, Tuple
from .storage import MemoryStorage, VectorDBStorage
from .cache import MemoryCache


class MemoryRetriever:
    """记忆检索器
    
    功能：
    - 向量检索（基于语义相似度）
    - 关键词检索
    - 混合检索（向量 + 关键词）
    - 检索结果排序与过滤
    """
    
    def __init__(self, storage: Optional[MemoryStorage] = None):
        """初始化记忆检索器
        
        Args:
            storage: 存储后端，默认使用VectorDBStorage
        """
        self.storage = storage or VectorDBStorage()
        self.cache = MemoryCache(max_size=1000, default_ttl=3600)
    
    def semantic_search(self, query: str, top_k: int = 5, 
                       filters: Optional[Dict[str, Any]] = None) -> List[Tuple[float, Dict[str, Any]]]:
        """语义搜索（基于向量相似度）
        
        Args:
            query: 搜索查询
            top_k: 返回结果数量
            filters: 过滤条件（可选）
            
        Returns:
            搜索结果列表，每个元素为(相似度, 记忆数据)
        """
        # 检查缓存
        cache_key = f"semantic_{query}_{top_k}_{filters}"
        cached_results = self.cache.get(cache_key)
        if cached_results:
            return cached_results
        
        results = self.storage.search(query, top_k * 2)  # 获取更多结果用于过滤
        
        # 应用过滤条件
        if filters:
            results = self._apply_filters(results, filters)
        
        # 按相似度排序并限制数量
        results.sort(key=lambda x: x[0], reverse=True)
        final_results = results[:top_k]
        
        # 存入缓存
        self.cache.set(cache_key, final_results)
        
        return final_results
    
    def keyword_search(self, query: str, top_k: int = 5, 
                      filters: Optional[Dict[str, Any]] = None) -> List[Tuple[float, Dict[str, Any]]]:
        """关键词搜索
        
        Args:
            query: 搜索查询
            top_k: 返回结果数量
            filters: 过滤条件（可选）
            
        Returns:
            搜索结果列表，每个元素为(相似度, 记忆数据)
        """
        # 检查缓存
        cache_key = f"keyword_{query}_{top_k}_{filters}"
        cached_results = self.cache.get(cache_key)
        if cached_results:
            return cached_results
        
        # 获取所有记忆
        memories = self.storage.list(1000)  # 限制数量以提高性能
        
        # 计算关键词匹配相似度
        results = []
        for memory in memories:
            similarity = self._calculate_keyword_similarity(query, memory)
            if similarity > 0:
                results.append((similarity, memory))
        
        # 应用过滤条件
        if filters:
            results = self._apply_filters(results, filters)
        
        # 按相似度排序并限制数量
        results.sort(key=lambda x: x[0], reverse=True)
        final_results = results[:top_k]
        
        # 存入缓存
        self.cache.set(cache_key, final_results)
        
        return final_results
    
    def hybrid_search(self, query: str, top_k: int = 5, 
                     filters: Optional[Dict[str, Any]] = None, 
                     semantic_weight: float = 0.7) -> List[Tuple[float, Dict[str, Any]]]:
        """混合搜索（向量 + 关键词）
        
        Args:
            query: 搜索查询
            top_k: 返回结果数量
            filters: 过滤条件（可选）
            semantic_weight: 语义搜索权重（0-1）
            
        Returns:
            搜索结果列表，每个元素为(相似度, 记忆数据)
        """
        # 检查缓存
        cache_key = f"hybrid_{query}_{top_k}_{filters}_{semantic_weight}"
        cached_results = self.cache.get(cache_key)
        if cached_results:
            return cached_results
        
        # 执行语义搜索
        semantic_results = self.semantic_search(query, top_k * 2, filters)
        
        # 执行关键词搜索
        keyword_results = self.keyword_search(query, top_k * 2, filters)
        
        # 合并结果
        combined_results = self._combine_results(semantic_results, keyword_results, semantic_weight)
        
        # 按相似度排序并限制数量
        combined_results.sort(key=lambda x: x[0], reverse=True)
        final_results = combined_results[:top_k]
        
        # 存入缓存
        self.cache.set(cache_key, final_results)
        
        return final_results
    
    def _apply_filters(self, results: List[Tuple[float, Dict[str, Any]]], 
                      filters: Dict[str, Any]) -> List[Tuple[float, Dict[str, Any]]]:
        """应用过滤条件
        
        Args:
            results: 搜索结果
            filters: 过滤条件
            
        Returns:
            过滤后的结果
        """
        filtered_results = []
        
        for similarity, memory in results:
            # 检查所有过滤条件
            match = True
            
            # 分类过滤
            if "category" in filters:
                if memory.get("category") != filters["category"]:
                    match = False
            
            # 标签过滤
            if "tags" in filters:
                memory_tags = memory.get("tags", [])
                if not any(tag in memory_tags for tag in filters["tags"]):
                    match = False
            
            # 优先级过滤
            if "min_priority" in filters:
                if memory.get("priority", 0) < filters["min_priority"]:
                    match = False
            
            # 时间范围过滤
            if "start_date" in filters:
                memory_date = memory.get("created_at", "")
                if memory_date < filters["start_date"]:
                    match = False
            
            if "end_date" in filters:
                memory_date = memory.get("created_at", "")
                if memory_date > filters["end_date"]:
                    match = False
            
            if match:
                filtered_results.append((similarity, memory))
        
        return filtered_results
    
    def _calculate_keyword_similarity(self, query: str, memory: Dict[str, Any]) -> float:
        """计算关键词相似度
        
        Args:
            query: 查询文本
            memory: 记忆数据
            
        Returns:
            相似度（0-1）
        """
        # 提取记忆中的文本内容
        content = memory.get("content", "") + " " + memory.get("summary", "")
        
        # 分词
        query_words = set(query.lower().split())
        content_words = set(content.lower().split())
        
        if not query_words:
            return 0
        
        # 计算词集交集
        intersection = query_words & content_words
        
        # 计算相似度
        return len(intersection) / len(query_words)
    
    def _combine_results(self, semantic_results: List[Tuple[float, Dict[str, Any]]], 
                        keyword_results: List[Tuple[float, Dict[str, Any]]], 
                        semantic_weight: float) -> List[Tuple[float, Dict[str, Any]]]:
        """合并搜索结果
        
        Args:
            semantic_results: 语义搜索结果
            keyword_results: 关键词搜索结果
            semantic_weight: 语义搜索权重
            
        Returns:
            合并后的结果
        """
        # 创建记忆ID到结果的映射
        memory_map = {}
        
        # 添加语义搜索结果
        for similarity, memory in semantic_results:
            memory_id = memory.get("memory_id")
            if memory_id:
                memory_map[memory_id] = {
                    "memory": memory,
                    "semantic_score": similarity,
                    "keyword_score": 0
                }
        
        # 添加关键词搜索结果
        for similarity, memory in keyword_results:
            memory_id = memory.get("memory_id")
            if memory_id:
                if memory_id in memory_map:
                    memory_map[memory_id]["keyword_score"] = similarity
                else:
                    memory_map[memory_id] = {
                        "memory": memory,
                        "semantic_score": 0,
                        "keyword_score": similarity
                    }
        
        # 计算综合得分
        combined_results = []
        for memory_id, data in memory_map.items():
            # 加权计算综合得分
            total_score = (data["semantic_score"] * semantic_weight + 
                          data["keyword_score"] * (1 - semantic_weight))
            combined_results.append((total_score, data["memory"]))
        
        return combined_results
