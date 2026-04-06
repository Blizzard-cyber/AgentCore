"""记忆质量评估模块

用于评估记忆的质量，并根据评估结果动态调整记忆的优先级。
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import math


class MemoryQualityEvaluator:
    """记忆质量评估器
    
    功能：
    - 评估记忆的质量得分
    - 基于质量得分调整记忆优先级
    - 监控记忆的使用情况
    """
    
    def __init__(self, 
                 relevance_weight: float = 0.3, 
                 recency_weight: float = 0.2, 
                 access_count_weight: float = 0.2, 
                 length_weight: float = 0.1, 
                 completeness_weight: float = 0.2):
        """初始化记忆质量评估器
        
        Args:
            relevance_weight: 相关性权重
            recency_weight: 新近性权重
            access_count_weight: 访问次数权重
            length_weight: 长度权重
            completeness_weight: 完整性权重
        """
        self.relevance_weight = relevance_weight
        self.recency_weight = recency_weight
        self.access_count_weight = access_count_weight
        self.length_weight = length_weight
        self.completeness_weight = completeness_weight
    
    def evaluate_quality(self, memory: Dict[str, Any], 
                         query: Optional[str] = None, 
                         relevance_score: Optional[float] = None) -> Dict[str, Any]:
        """评估记忆质量
        
        Args:
            memory: 记忆数据
            query: 查询文本（可选，用于计算相关性）
            relevance_score: 相关性得分（可选）
            
        Returns:
            包含质量得分和各项指标的字典
        """
        # 1. 计算相关性得分
        if relevance_score is not None:
            relevance = relevance_score
        else:
            relevance = 0.5  # 默认值
        
        # 2. 计算新近性得分（指数衰减）
        created_at = memory.get("created_at", datetime.now())
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        
        delta = (datetime.now() - created_at).total_seconds()
        recency = math.exp(-delta / 86400)  # 1天的时间尺度
        
        # 3. 计算访问频率得分
        access_count = memory.get("access_count", 0)
        access_score = min(1.0, math.log(access_count + 1) / math.log(10))
        
        # 4. 计算长度得分（适中长度最佳）
        content = memory.get("content", "")
        length = len(content)
        # 长度得分：适中长度（100-1000字符）最佳
        if 100 <= length <= 1000:
            length_score = 1.0
        elif length < 100:
            length_score = length / 100
        else:
            length_score = 1.0 - min(0.9, (length - 1000) / 9000)
        
        # 5. 计算完整性得分
        completeness = 1.0
        if not memory.get("summary"):
            completeness -= 0.2
        if not memory.get("tags"):
            completeness -= 0.1
        if not memory.get("category"):
            completeness -= 0.1
        completeness = max(0.0, completeness)
        
        # 6. 计算综合质量得分
        quality_score = (
            relevance * self.relevance_weight +
            recency * self.recency_weight +
            access_score * self.access_count_weight +
            length_score * self.length_weight +
            completeness * self.completeness_weight
        )
        
        return {
            "quality_score": quality_score,
            "relevance": relevance,
            "recency": recency,
            "access_score": access_score,
            "length_score": length_score,
            "completeness": completeness
        }
    
    def adjust_priority(self, memory: Dict[str, Any], 
                        quality_score: float, 
                        current_priority: int) -> int:
        """根据质量得分调整记忆优先级
        
        Args:
            memory: 记忆数据
            quality_score: 质量得分
            current_priority: 当前优先级
            
        Returns:
            新的优先级（0-10）
        """
        # 基于质量得分计算新的优先级
        new_priority = min(10, max(0, int(quality_score * 10)))
        
        # 平滑过渡，避免优先级突变
        priority_diff = new_priority - current_priority
        if abs(priority_diff) <= 1:
            return new_priority
        else:
            # 逐步调整，每次最多变化1
            return current_priority + (1 if priority_diff > 0 else -1)
    
    def should_promote(self, memory: Dict[str, Any]) -> bool:
        """判断记忆是否应该被提升优先级
        
        Args:
            memory: 记忆数据
            
        Returns:
            是否应该提升优先级
        """
        # 检查访问频率
        access_count = memory.get("access_count", 0)
        last_accessed = memory.get("last_accessed", memory.get("created_at"))
        
        if isinstance(last_accessed, str):
            last_accessed = datetime.fromisoformat(last_accessed)
        
        # 如果最近24小时内访问次数超过5次，考虑提升
        if (datetime.now() - last_accessed).total_seconds() < 86400:
            if access_count >= 5:
                return True
        
        return False
    
    def should_demote(self, memory: Dict[str, Any]) -> bool:
        """判断记忆是否应该被降低优先级
        
        Args:
            memory: 记忆数据
            
        Returns:
            是否应该降低优先级
        """
        # 检查最后访问时间
        last_accessed = memory.get("last_accessed", memory.get("created_at"))
        
        if isinstance(last_accessed, str):
            last_accessed = datetime.fromisoformat(last_accessed)
        
        # 如果超过30天未访问，考虑降低
        if (datetime.now() - last_accessed).total_seconds() > 30 * 86400:
            return True
        
        return False
    
    def get_maintenance_suggestions(self, memory: Dict[str, Any]) -> Dict[str, Any]:
        """获取记忆维护建议
        
        Args:
            memory: 记忆数据
            
        Returns:
            维护建议
        """
        suggestions = {}
        
        # 检查摘要
        if not memory.get("summary"):
            suggestions["add_summary"] = "建议添加记忆摘要，提高记忆的可理解性"
        
        # 检查标签
        if not memory.get("tags"):
            suggestions["add_tags"] = "建议添加标签，提高记忆的可检索性"
        
        # 检查分类
        if not memory.get("category"):
            suggestions["add_category"] = "建议添加分类，提高记忆的组织性"
        
        # 检查长度
        content = memory.get("content", "")
        if len(content) < 50:
            suggestions["expand_content"] = "建议扩展记忆内容，提供更多详细信息"
        elif len(content) > 5000:
            suggestions["split_content"] = "建议将记忆拆分为多个小块，提高管理效率"
        
        return suggestions