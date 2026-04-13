"""记忆系统核心管理器

整合所有记忆组件，提供统一的接口：
- 长期记忆管理
- 记忆检索
- 记忆组织
- 记忆更新
- 记忆安全
"""

from typing import Dict, Any, Optional, List, Tuple
from .long_term_memory import LongTermMemory
from .short_term_memory import ShortTermMemory
from .retriever import MemoryRetriever
from .organizer import MemoryOrganizer
from .updater import MemoryUpdater
from .security import MemorySecurity
from .quality import MemoryQualityEvaluator
from .multimodal import MultimodalProcessor
from .versioning import MemoryVersionManager
from .storage import MemoryStorage, LocalStorage, VectorDBStorage


class MemoryManager:
    """记忆系统核心管理器
    
    功能：
    - 整合所有记忆组件
    - 提供统一的记忆管理接口
    - 协调各组件之间的交互
    """
    
    def __init__(self, storage: Optional[MemoryStorage] = None):
        """初始化记忆管理器
        
        Args:
            storage: 存储后端，默认使用VectorDBStorage
        """
        # 初始化存储
        self.storage = storage or VectorDBStorage()
        
        # 初始化各组件
        self.long_term_memory = LongTermMemory(self.storage)
        self.short_term_memory = ShortTermMemory()
        self.retriever = MemoryRetriever(self.storage)
        self.organizer = MemoryOrganizer(self.long_term_memory)
        self.updater = MemoryUpdater(self.long_term_memory)
        self.security = MemorySecurity(self.long_term_memory)
        self.quality_evaluator = MemoryQualityEvaluator()
        self.multimodal_processor = MultimodalProcessor()
        self.version_manager = MemoryVersionManager(self.storage)
    
    # ==================== 长期记忆管理 ====================
    
    def add_memory(self, content: str, summary: Optional[str] = None, 
                   category: Optional[str] = None, tags: Optional[List[str]] = None, 
                   priority: int = 0) -> str:
        """添加记忆
        
        Args:
            content: 记忆内容
            summary: 记忆摘要（可选）
            category: 记忆分类（可选）
            tags: 记忆标签（可选）
            priority: 记忆优先级（0-10，默认0）
            
        Returns:
            记忆ID
        """
        return self.long_term_memory.add_memory(
            content=content,
            summary=summary,
            category=category,
            tags=tags,
            priority=priority
        )
    
    def get_memory(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """获取记忆
        
        Args:
            memory_id: 记忆ID
            
        Returns:
            记忆数据，不存在返回None
        """
        return self.long_term_memory.get_memory(memory_id)
    
    def update_memory(self, memory_id: str, **kwargs) -> bool:
        """更新记忆
        
        Args:
            memory_id: 记忆ID
            **kwargs: 要更新的字段
            
        Returns:
            是否更新成功
        """
        return self.long_term_memory.update_memory(memory_id, **kwargs)
    
    def delete_memory(self, memory_id: str) -> bool:
        """删除记忆
        
        Args:
            memory_id: 记忆ID
            
        Returns:
            是否删除成功
        """
        return self.long_term_memory.delete_memory(memory_id)
    
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
        return self.long_term_memory.list_memories(
            limit=limit,
            category=category,
            tags=tags,
            min_priority=min_priority
        )
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """获取记忆统计信息
        
        Returns:
            统计信息
        """
        return self.long_term_memory.get_memory_stats()
    
    # ==================== 记忆检索 ====================
    
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
        return self.retriever.semantic_search(
            query=query,
            top_k=top_k,
            filters=filters
        )
    
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
        return self.retriever.keyword_search(
            query=query,
            top_k=top_k,
            filters=filters
        )
    
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
        return self.retriever.hybrid_search(
            query=query,
            top_k=top_k,
            filters=filters,
            semantic_weight=semantic_weight
        )
    
    # ==================== 记忆组织 ====================
    
    def create_category(self, category_name: str, description: Optional[str] = None) -> Dict[str, Any]:
        """创建分类
        
        Args:
            category_name: 分类名称
            description: 分类描述（可选）
            
        Returns:
            分类信息
        """
        return self.organizer.create_category(
            category_name=category_name,
            description=description
        )
    
    def list_categories(self) -> List[Dict[str, Any]]:
        """列出所有分类
        
        Returns:
            分类列表
        """
        return self.organizer.list_categories()
    
    def add_tag(self, memory_id: str, tag: str) -> bool:
        """为记忆添加标签
        
        Args:
            memory_id: 记忆ID
            tag: 标签
            
        Returns:
            是否添加成功
        """
        return self.organizer.add_tag(memory_id, tag)
    
    def remove_tag(self, memory_id: str, tag: str) -> bool:
        """从记忆中移除标签
        
        Args:
            memory_id: 记忆ID
            tag: 标签
            
        Returns:
            是否移除成功
        """
        return self.organizer.remove_tag(memory_id, tag)
    
    def list_tags(self) -> List[str]:
        """列出所有标签
        
        Returns:
            标签列表
        """
        return self.organizer.list_tags()
    
    def create_hierarchy(self, parent_memory_id: str, child_memory_id: str) -> bool:
        """创建记忆层次关系
        
        Args:
            parent_memory_id: 父记忆ID
            child_memory_id: 子记忆ID
            
        Returns:
            是否创建成功
        """
        return self.organizer.create_hierarchy(parent_memory_id, child_memory_id)
    
    def get_hierarchy(self, memory_id: str, depth: int = 2) -> Dict[str, Any]:
        """获取记忆的层次结构
        
        Args:
            memory_id: 记忆ID
            depth: 深度限制
            
        Returns:
            层次结构
        """
        return self.organizer.get_hierarchy(memory_id, depth)
    
    def find_related_memories(self, memory_id: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """查找相关记忆
        
        Args:
            memory_id: 记忆ID
            top_k: 返回结果数量
            
        Returns:
            相关记忆列表
        """
        return self.organizer.find_related_memories(memory_id, top_k)
    
    # ==================== 记忆更新与修正 ====================
    
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
        return self.updater.correct_memory(
            memory_id=memory_id,
            correction=correction,
            reason=reason
        )
    
    def clean_expired_memories(self, days: int = 30) -> Dict[str, Any]:
        """清理过期记忆
        
        Args:
            days: 过期天数
            
        Returns:
            清理结果
        """
        return self.updater.clean_expired_memories(days=days)
    
    def clean_unused_memories(self, days: int = 90, min_access_count: int = 1) -> Dict[str, Any]:
        """清理未使用的记忆
        
        Args:
            days: 未使用天数
            min_access_count: 最小访问次数
            
        Returns:
            清理结果
        """
        return self.updater.clean_unused_memories(
            days=days,
            min_access_count=min_access_count
        )
    
    def optimize_memory(self) -> Dict[str, Any]:
        """优化记忆存储
        
        Returns:
            优化结果
        """
        return self.updater.optimize_memory()
    
    # ==================== 安全性与隐私保护 ====================
    
    def set_access_control(self, memory_id: str, allowed_roles: List[str]) -> bool:
        """设置记忆的访问控制
        
        Args:
            memory_id: 记忆ID
            allowed_roles: 允许访问的角色列表
            
        Returns:
            是否设置成功
        """
        return self.security.set_access_control(memory_id, allowed_roles)
    
    def check_access(self, memory_id: str, user_roles: List[str]) -> bool:
        """检查用户是否有权访问记忆
        
        Args:
            memory_id: 记忆ID
            user_roles: 用户角色列表
            
        Returns:
            是否有权访问
        """
        return self.security.check_access(memory_id, user_roles)
    
    def filter_sensitive_info(self, memory_id: str) -> Dict[str, Any]:
        """过滤记忆中的敏感信息
        
        Args:
            memory_id: 记忆ID
            
        Returns:
            过滤结果
        """
        return self.security.filter_sensitive_info(memory_id)
    
    def encrypt_memory(self, memory_id: str, encryption_key: str) -> Dict[str, Any]:
        """加密记忆
        
        Args:
            memory_id: 记忆ID
            encryption_key: 加密密钥
            
        Returns:
            加密结果
        """
        return self.security.encrypt_memory(memory_id, encryption_key)
    
    def decrypt_memory(self, memory_id: str, encryption_key: str) -> Dict[str, Any]:
        """解密记忆
        
        Args:
            memory_id: 记忆ID
            encryption_key: 解密密钥
            
        Returns:
            解密结果
        """
        return self.security.decrypt_memory(memory_id, encryption_key)
    
    def audit_memory_access(self, memory_id: str, user_id: str, action: str) -> bool:
        """审计记忆访问
        
        Args:
            memory_id: 记忆ID
            user_id: 用户ID
            action: 操作类型（read, write, delete）
            
        Returns:
            是否审计成功
        """
        return self.security.audit_memory_access(memory_id, user_id, action)
    
    # ==================== 短期记忆管理 ====================
    
    def add_short_term_memory(self, content: str, session_id: str, 
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
        return self.short_term_memory.add_memory(
            content=content,
            session_id=session_id,
            summary=summary,
            tags=tags,
            ttl=ttl
        )
    
    def get_short_term_memory(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """获取短期记忆
        
        Args:
            memory_id: 记忆ID
            
        Returns:
            记忆数据，不存在或已过期返回None
        """
        return self.short_term_memory.get_memory(memory_id)
    
    def get_session_memories(self, session_id: str) -> List[Dict[str, Any]]:
        """获取指定会话的所有短期记忆
        
        Args:
            session_id: 会话ID
            
        Returns:
            记忆列表
        """
        return self.short_term_memory.get_session_memories(session_id)
    
    def update_short_term_memory(self, memory_id: str, **kwargs) -> bool:
        """更新短期记忆
        
        Args:
            memory_id: 记忆ID
            **kwargs: 要更新的字段
            
        Returns:
            是否更新成功
        """
        return self.short_term_memory.update_memory(memory_id, **kwargs)
    
    def delete_short_term_memory(self, memory_id: str) -> bool:
        """删除短期记忆
        
        Args:
            memory_id: 记忆ID
            
        Returns:
            是否删除成功
        """
        return self.short_term_memory.delete_memory(memory_id)
    
    def delete_session_memories(self, session_id: str) -> int:
        """删除指定会话的所有短期记忆
        
        Args:
            session_id: 会话ID
            
        Returns:
            删除的记忆数量
        """
        return self.short_term_memory.delete_session_memories(session_id)
    
    def get_short_term_memory_stats(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """获取短期记忆统计信息
        
        Args:
            session_id: 会话ID（可选）
            
        Returns:
            统计信息
        """
        return self.short_term_memory.get_memory_stats(session_id)
    
    def migrate_to_long_term(self, memory_id: str, 
                            category: Optional[str] = None, 
                            priority: int = 0) -> Optional[str]:
        """将短期记忆迁移到长期记忆
        
        Args:
            memory_id: 短期记忆ID
            category: 长期记忆分类（可选）
            priority: 长期记忆优先级
            
        Returns:
            长期记忆ID，迁移失败返回None
        """
        # 获取短期记忆
        memory = self.short_term_memory.get_memory(memory_id)
        if not memory:
            return None
        
        # 添加到长期记忆
        long_term_id = self.long_term_memory.add_memory(
            content=f"[会话记忆] {memory.get('summary', memory['content'])}",
            summary=memory.get("summary"),
            category=category,
            tags=memory.get("tags"),
            priority=priority
        )
        
        # 删除短期记忆
        self.short_term_memory.delete_memory(memory_id)
        
        return long_term_id
    
    def migrate_session_to_long_term(self, session_id: str, 
                                    category: Optional[str] = None, 
                                    priority: int = 0) -> List[str]:
        """将整个会话的短期记忆迁移到长期记忆
        
        Args:
            session_id: 会话ID
            category: 长期记忆分类（可选）
            priority: 长期记忆优先级
            
        Returns:
            长期记忆ID列表
        """
        # 获取会话的所有短期记忆
        session_memories = self.short_term_memory.get_session_memories(session_id)
        
        # 迁移到长期记忆
        long_term_ids = []
        for memory in session_memories:
            long_term_id = self.long_term_memory.add_memory(
                content=memory["content"],
                summary=memory.get("summary"),
                category=category,
                tags=memory.get("tags"),
                priority=priority
            )
            long_term_ids.append(long_term_id)
        
        # 删除会话的短期记忆
        self.short_term_memory.delete_session_memories(session_id)
        
        return long_term_ids
    
    # ==================== 记忆质量评估 ====================
    
    def evaluate_memory_quality(self, memory_id: str, 
                               query: Optional[str] = None, 
                               relevance_score: Optional[float] = None) -> Optional[Dict[str, Any]]:
        """评估记忆质量
        
        Args:
            memory_id: 记忆ID
            query: 查询文本（可选，用于计算相关性）
            relevance_score: 相关性得分（可选）
            
        Returns:
            质量评估结果，记忆不存在返回None
        """
        # 先尝试从长期记忆中获取
        memory = self.long_term_memory.get_memory(memory_id)
        if not memory:
            # 再尝试从短期记忆中获取
            memory = self.short_term_memory.get_memory(memory_id)
            if not memory:
                return None
        
        # 评估质量
        return self.quality_evaluator.evaluate_quality(
            memory=memory,
            query=query,
            relevance_score=relevance_score
        )
    
    def adjust_memory_priority(self, memory_id: str, 
                              quality_score: Optional[float] = None) -> Optional[int]:
        """调整记忆优先级
        
        Args:
            memory_id: 记忆ID
            quality_score: 质量得分（可选，不提供则自动计算）
            
        Returns:
            新的优先级，记忆不存在返回None
        """
        # 先尝试从长期记忆中获取
        memory = self.long_term_memory.get_memory(memory_id)
        if memory:
            # 计算质量得分（如果未提供）
            if quality_score is None:
                quality_eval = self.quality_evaluator.evaluate_quality(memory)
                quality_score = quality_eval["quality_score"]
            
            # 调整优先级
            current_priority = memory.get("priority", 0)
            new_priority = self.quality_evaluator.adjust_priority(
                memory=memory,
                quality_score=quality_score,
                current_priority=current_priority
            )
            
            # 更新记忆
            if new_priority != current_priority:
                self.long_term_memory.update_memory(memory_id, priority=new_priority)
            
            return new_priority
        
        return None
    
    def optimize_memory_priorities(self, limit: int = 100) -> Dict[str, Any]:
        """批量优化记忆优先级
        
        Args:
            limit: 处理的记忆数量限制
            
        Returns:
            优化结果
        """
        # 获取记忆列表
        memories = self.long_term_memory.list_memories(limit=limit)
        
        optimized_count = 0
        promoted_count = 0
        demoted_count = 0
        
        for memory in memories:
            memory_id = memory.get("id")
            if not memory_id:
                continue
            
            # 评估质量
            quality_eval = self.quality_evaluator.evaluate_quality(memory)
            quality_score = quality_eval["quality_score"]
            
            # 调整优先级
            current_priority = memory.get("priority", 0)
            new_priority = self.quality_evaluator.adjust_priority(
                memory=memory,
                quality_score=quality_score,
                current_priority=current_priority
            )
            
            # 更新记忆
            if new_priority != current_priority:
                self.long_term_memory.update_memory(memory_id, priority=new_priority)
                optimized_count += 1
                
                if new_priority > current_priority:
                    promoted_count += 1
                else:
                    demoted_count += 1
        
        return {
            "total_processed": len(memories),
            "optimized_count": optimized_count,
            "promoted_count": promoted_count,
            "demoted_count": demoted_count
        }
    
    def get_memory_maintenance_suggestions(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """获取记忆维护建议
        
        Args:
            memory_id: 记忆ID
            
        Returns:
            维护建议，记忆不存在返回None
        """
        # 先尝试从长期记忆中获取
        memory = self.long_term_memory.get_memory(memory_id)
        if not memory:
            # 再尝试从短期记忆中获取
            memory = self.short_term_memory.get_memory(memory_id)
            if not memory:
                return None
        
        # 获取维护建议
        return self.quality_evaluator.get_maintenance_suggestions(memory)
    
    # ==================== 多模态记忆支持 ====================
    
    def add_multimodal_memory(self, content: Any, 
                             content_type: Optional[str] = None, 
                             summary: Optional[str] = None, 
                             category: Optional[str] = None, 
                             tags: Optional[List[str]] = None, 
                             priority: int = 0) -> str:
        """添加多模态记忆
        
        Args:
            content: 多模态内容（文本、图像、音频、视频等）
            content_type: 内容类型（可选，自动检测）
            summary: 记忆摘要（可选）
            category: 记忆分类（可选）
            tags: 记忆标签（可选）
            priority: 记忆优先级
            
        Returns:
            记忆ID
        """
        # 处理多模态内容
        if isinstance(content, str) and content.startswith("data:"):
            # 检测内容类型
            if not content_type:
                content_type = self.multimodal_processor.get_content_type(content)
            
            # 根据内容类型处理
            if content_type and content_type.startswith("image/"):
                multimodal_data = self.multimodal_processor.process_image(content)
            elif content_type and content_type.startswith("audio/"):
                multimodal_data = self.multimodal_processor.process_audio(content)
            elif content_type and content_type.startswith("video/"):
                multimodal_data = self.multimodal_processor.process_video(content)
            else:
                multimodal_data = self.multimodal_processor.process_text(content)
        elif isinstance(content, bytes):
            # 检测内容类型
            if not content_type:
                content_type = self.multimodal_processor.get_content_type(content)
            
            # 根据内容类型处理
            if content_type and content_type.startswith("image/"):
                multimodal_data = self.multimodal_processor.process_image(content)
            elif content_type and content_type.startswith("audio/"):
                multimodal_data = self.multimodal_processor.process_audio(content)
            elif content_type and content_type.startswith("video/"):
                multimodal_data = self.multimodal_processor.process_video(content)
            else:
                multimodal_data = self.multimodal_processor.process_text(content.decode())
        else:
            # 默认为文本
            multimodal_data = self.multimodal_processor.process_text(str(content))
        
        # 提取文本表示用于检索
        text_representation = self.multimodal_processor.extract_text_representation(multimodal_data)
        
        # 添加到长期记忆
        memory_id = self.long_term_memory.add_memory(
            content=text_representation,
            summary=summary or text_representation,
            category=category,
            tags=tags,
            priority=priority,
            metadata={"multimodal": multimodal_data}
        )
        
        return memory_id
    
    def get_multimodal_content(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """获取多模态内容
        
        Args:
            memory_id: 记忆ID
            
        Returns:
            多模态内容，不存在返回None
        """
        # 获取记忆
        memory = self.long_term_memory.get_memory(memory_id)
        if not memory:
            return None
        
        # 获取多模态数据
        multimodal_data = memory.get("metadata", {}).get("multimodal")
        if not multimodal_data:
            return None
        
        # 验证多模态数据
        if not self.multimodal_processor.validate_multimodal_data(multimodal_data):
            return None
        
        return multimodal_data
    
    def process_multimodal_content(self, content: Any, content_type: Optional[str] = None) -> Dict[str, Any]:
        """处理多模态内容
        
        Args:
            content: 多模态内容
            content_type: 内容类型（可选）
            
        Returns:
            处理后的多模态数据
        """
        # 检测内容类型
        if not content_type:
            content_type = self.multimodal_processor.get_content_type(content)
        
        # 根据内容类型处理
        if content_type == "image" or (content_type and content_type.startswith("image/")):
            return self.multimodal_processor.process_image(content)
        elif content_type == "audio" or (content_type and content_type.startswith("audio/")):
            return self.multimodal_processor.process_audio(content)
        elif content_type == "video" or (content_type and content_type.startswith("video/")):
            return self.multimodal_processor.process_video(content)
        elif content_type == "text" or (content_type and content_type == "text/plain"):
            return self.multimodal_processor.process_text(content)
        else:
            # 通用处理
            return self.multimodal_processor.process_generic(content, content_type or "application/octet-stream")
    
    def extract_text_representation(self, multimodal_data: Dict[str, Any]) -> str:
        """提取多模态内容的文本表示
        
        Args:
            multimodal_data: 多模态数据
            
        Returns:
            文本表示
        """
        return self.multimodal_processor.extract_text_representation(multimodal_data)
    
    # ==================== 记忆版本控制 ====================
    
    def create_memory_version(self, memory_id: str, reason: Optional[str] = None) -> str:
        """创建记忆版本
        
        Args:
            memory_id: 记忆ID
            reason: 版本创建原因
            
        Returns:
            版本ID
        """
        # 获取记忆数据
        memory = self.long_term_memory.get_memory(memory_id)
        if not memory:
            raise ValueError(f"Memory {memory_id} not found")
        
        # 创建版本
        return self.version_manager.create_version(memory_id, memory, reason)
    
    def get_memory_version(self, memory_id: str, version_id: str) -> Optional[Dict[str, Any]]:
        """获取指定版本
        
        Args:
            memory_id: 记忆ID
            version_id: 版本ID
            
        Returns:
            版本数据，不存在返回None
        """
        return self.version_manager.get_version(memory_id, version_id)
    
    def get_all_memory_versions(self, memory_id: str) -> List[Dict[str, Any]]:
        """获取记忆的所有版本
        
        Args:
            memory_id: 记忆ID
            
        Returns:
            版本列表，按版本号降序排序
        """
        return self.version_manager.get_all_versions(memory_id)
    
    def rollback_memory_version(self, memory_id: str, version_id: str) -> Dict[str, Any]:
        """回滚到指定版本
        
        Args:
            memory_id: 记忆ID
            version_id: 版本ID
            
        Returns:
            回滚后的记忆数据
        """
        return self.version_manager.rollback_to_version(memory_id, version_id)
    
    def compare_memory_versions(self, memory_id: str, 
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
        return self.version_manager.compare_versions(memory_id, version_id1, version_id2)
    
    def tag_memory_version(self, memory_id: str, 
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
        return self.version_manager.tag_version(memory_id, version_id, tag, description)
    
    def get_memory_version_by_tag(self, memory_id: str, tag: str) -> Optional[Dict[str, Any]]:
        """通过标签获取版本
        
        Args:
            memory_id: 记忆ID
            tag: 标签名
            
        Returns:
            版本数据，不存在返回None
        """
        return self.version_manager.get_version_by_tag(memory_id, tag)
    
    def delete_memory_version(self, memory_id: str, version_id: str) -> bool:
        """删除版本
        
        Args:
            memory_id: 记忆ID
            version_id: 版本ID
            
        Returns:
            是否成功
        """
        return self.version_manager.delete_version(memory_id, version_id)
    
    def get_memory_version_stats(self, memory_id: str) -> Dict[str, Any]:
        """获取版本统计信息
        
        Args:
            memory_id: 记忆ID
            
        Returns:
            统计信息
        """
        return self.version_manager.get_version_stats(memory_id)
