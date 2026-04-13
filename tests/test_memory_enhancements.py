"""记忆系统增强功能测试

测试记忆系统的增强功能，包括：
- 短期记忆（工作记忆）
- 记忆系统与上下文构建器集成
- 记忆质量评估
- 记忆检索性能（缓存机制）
- 自适应上下文调整
- 多模态记忆支持
- 记忆版本控制
"""

import unittest
import time
from datetime import datetime, timedelta

from agent_core.memory import MemoryManager, ShortTermMemory
from agent_core.memory.cache import MemoryCache
from agent_core.memory.storage import VectorDBStorage
from agent_core.context.builder import ContextBuilder, ContextConfig
from agent_core.core.message import Message


class TestMemoryEnhancements(unittest.TestCase):
    """记忆系统增强功能测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.memory_manager = MemoryManager()
        self.short_term_memory = ShortTermMemory(max_size=100, default_ttl=60)
        self.context_builder = ContextBuilder(memory_manager=self.memory_manager)
    
    def test_short_term_memory(self):
        """测试短期记忆功能"""
        # 添加短期记忆
        session_id = "test_session"
        memory_id = self.short_term_memory.add_memory(
            content="测试短期记忆内容",
            session_id=session_id,
            summary="测试摘要",
            tags=["test", "short_term"],
            ttl=30
        )
        
        # 获取短期记忆
        memory = self.short_term_memory.get_memory(memory_id)
        self.assertIsNotNone(memory)
        self.assertEqual(memory["content"], "测试短期记忆内容")
        
        # 获取会话记忆
        session_memories = self.short_term_memory.get_session_memories(session_id)
        self.assertEqual(len(session_memories), 1)
        
        # 更新短期记忆
        updated = self.short_term_memory.update_memory(
            memory_id,
            content="更新后的内容"
        )
        self.assertTrue(updated)
        
        # 验证更新
        updated_memory = self.short_term_memory.get_memory(memory_id)
        self.assertEqual(updated_memory["content"], "更新后的内容")
        
        # 删除短期记忆
        deleted = self.short_term_memory.delete_memory(memory_id)
        self.assertTrue(deleted)
        
        # 验证删除
        deleted_memory = self.short_term_memory.get_memory(memory_id)
        self.assertIsNone(deleted_memory)
    
    def test_memory_context_integration(self):
        """测试记忆系统与上下文构建器集成"""
        # 添加长期记忆
        memory_id = self.memory_manager.add_memory(
            content="测试长期记忆内容",
            summary="测试长期记忆摘要",
            category="test",
            tags=["test", "long_term"]
        )
        
        # 添加短期记忆
        session_id = "test_session"
        self.memory_manager.add_short_term_memory(
            content="测试短期记忆内容",
            session_id=session_id,
            summary="测试短期记忆摘要"
        )
        
        # 构建上下文
        user_query = "测试记忆检索"
        context = self.context_builder.build(
            user_query=user_query,
            session_id=session_id
        )
        
        # 验证上下文包含记忆内容
        self.assertIn("测试长期记忆摘要", context)
        self.assertIn("测试短期记忆摘要", context)
    
    def test_memory_quality_evaluation(self):
        """测试记忆质量评估"""
        # 添加记忆
        memory_id = self.memory_manager.add_memory(
            content="测试记忆质量评估内容",
            summary="测试记忆质量评估摘要",
            category="test",
            tags=["test", "quality"]
        )
        
        # 评估记忆质量
        quality_eval = self.memory_manager.evaluate_memory_quality(memory_id)
        self.assertIn("quality_score", quality_eval)
        self.assertGreaterEqual(quality_eval["quality_score"], 0.0)
        self.assertLessEqual(quality_eval["quality_score"], 1.0)
        
        # 调整记忆优先级
        new_priority = self.memory_manager.adjust_memory_priority(memory_id)
        self.assertGreaterEqual(new_priority, 0)
        self.assertLessEqual(new_priority, 10)
        
        # 获取记忆维护建议
        suggestions = self.memory_manager.get_memory_maintenance_suggestions(memory_id)
        self.assertIsInstance(suggestions, dict)
    
    def test_memory_retrieval_performance(self):
        """测试记忆检索性能（缓存机制）"""
        # 添加多个记忆
        for i in range(5):
            self.memory_manager.add_memory(
                content=f"测试记忆内容 {i}",
                summary=f"测试记忆摘要 {i}",
                category="test",
                tags=["test", f"memory_{i}"]
            )
        
        # 第一次搜索（应该没有缓存）
        start_time = time.time()
        results1 = self.memory_manager.semantic_search("测试记忆", top_k=3)
        time1 = time.time() - start_time
        
        # 第二次搜索（应该使用缓存）
        start_time = time.time()
        results2 = self.memory_manager.semantic_search("测试记忆", top_k=3)
        time2 = time.time() - start_time
        
        # 验证结果一致
        self.assertEqual(len(results1), len(results2))
        
        # 验证缓存生效（第二次搜索应该更快）
        self.assertLess(time2, time1)
    
    def test_adaptive_context(self):
        """测试自适应上下文调整"""
        # 添加记忆
        self.memory_manager.add_memory(
            content="测试问答记忆内容",
            summary="测试问答记忆摘要",
            category="qa",
            tags=["test", "qa"]
        )
        
        # 测试问答类型任务
        qa_query = "什么是测试？"
        qa_context = self.context_builder.build(
            user_query=qa_query,
            task_type="qa"
        )
        
        # 测试创意写作类型任务
        creative_query = "写一个测试故事"
        creative_context = self.context_builder.build(
            user_query=creative_query,
            task_type="creative"
        )
        
        # 验证上下文构建成功
        self.assertIsInstance(qa_context, str)
        self.assertIsInstance(creative_context, str)
    
    def test_multimodal_memory(self):
        """测试多模态记忆支持"""
        # 测试文本内容
        text_memory_id = self.memory_manager.add_multimodal_memory(
            content="测试文本内容",
            content_type="text/plain",
            summary="测试文本摘要"
        )
        
        # 测试图像内容（使用base64编码的简单图像）
        # 这里使用一个简单的base64编码图像数据作为示例
        image_data = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        image_memory_id = self.memory_manager.add_multimodal_memory(
            content=image_data,
            content_type="image/png",
            summary="测试图像摘要"
        )
        
        # 获取多模态内容
        text_content = self.memory_manager.get_multimodal_content(text_memory_id)
        image_content = self.memory_manager.get_multimodal_content(image_memory_id)
        
        # 验证多模态内容
        self.assertIsNotNone(text_content)
        self.assertIsNotNone(image_content)
        self.assertEqual(text_content["type"], "text/plain")
        self.assertEqual(image_content["type"], "image/png")
    
    def test_memory_versioning(self):
        """测试记忆版本控制"""
        # 添加记忆
        memory_id = self.memory_manager.add_memory(
            content="初始记忆内容",
            summary="初始记忆摘要"
        )
        
        # 创建版本
        version1_id = self.memory_manager.create_memory_version(
            memory_id, 
            reason="初始版本"
        )
        
        # 更新记忆
        self.memory_manager.update_memory(
            memory_id, 
            content="更新后的记忆内容"
        )
        
        # 创建第二个版本
        version2_id = self.memory_manager.create_memory_version(
            memory_id, 
            reason="更新版本"
        )
        
        # 获取所有版本
        versions = self.memory_manager.get_all_memory_versions(memory_id)
        self.assertEqual(len(versions), 2)
        
        # 比较版本
        diff = self.memory_manager.compare_memory_versions(
            memory_id, 
            version1_id, 
            version2_id
        )
        self.assertIn("modified", diff)
        
        # 回滚到第一个版本
        rolled_back = self.memory_manager.rollback_memory_version(
            memory_id, 
            version1_id
        )
        self.assertEqual(rolled_back["content"], "初始记忆内容")
        
        # 为版本添加标签
        tagged = self.memory_manager.tag_memory_version(
            memory_id, 
            version1_id, 
            "initial", 
            "初始版本"
        )
        self.assertTrue(tagged)
        
        # 通过标签获取版本
        version_by_tag = self.memory_manager.get_memory_version_by_tag(
            memory_id, 
            "initial"
        )
        self.assertIsNotNone(version_by_tag)
    
    def test_memory_migration(self):
        """测试短期记忆到长期记忆的迁移"""
        # 添加短期记忆
        session_id = "test_session"
        short_term_id = self.memory_manager.add_short_term_memory(
            content="测试迁移内容",
            session_id=session_id,
            summary="测试迁移摘要"
        )
        
        # 迁移到长期记忆
        long_term_id = self.memory_manager.migrate_to_long_term(
            short_term_id, 
            category="migrated",
            priority=5
        )
        
        # 验证迁移成功
        self.assertIsNotNone(long_term_id)
        
        # 验证短期记忆已删除
        short_term_memory = self.memory_manager.get_short_term_memory(short_term_id)
        self.assertIsNone(short_term_memory)
        
        # 验证长期记忆存在
        long_term_memory = self.memory_manager.get_memory(long_term_id)
        self.assertIsNotNone(long_term_memory)
        self.assertEqual(long_term_memory["content"], "[会话记忆] 测试迁移摘要")

    def test_updater_update_memory_no_duplicate_memory_id_error(self):
        """测试更新器不会因 memory_id 重复传参报错"""
        memory_id = self.memory_manager.add_memory(
            content="原始内容",
            summary="原始摘要"
        )

        result = self.memory_manager.updater.update_memory(
            memory_id,
            content="更新后的内容"
        )

        self.assertTrue(result["success"])
        updated_memory = self.memory_manager.get_memory(memory_id)
        self.assertEqual(updated_memory["content"], "更新后的内容")

    def test_memory_cache_stats_no_runtime_error(self):
        """测试缓存统计接口可正常返回"""
        cache = MemoryCache(max_size=10, default_ttl=60)
        cache.set("q1", {"ok": True})

        stats = cache.get_stats()
        self.assertIn("total_items", stats)
        self.assertIn("oldest_item_age", stats)
        self.assertIn("newest_item_age", stats)
        self.assertGreaterEqual(stats["total_items"], 1)

    def test_vector_fallback_generates_non_collinear_vectors(self):
        """测试无嵌入模型时的回退向量不会退化为共线向量"""
        storage = VectorDBStorage(dim=16)
        storage.embedding_model = None

        vec1 = storage._generate_vector("apple")
        vec2 = storage._generate_vector("banana")
        similarity = storage._calculate_cosine_similarity(vec1, vec2)

        # 对不同文本，回退向量相似度不应退化为完全相同
        self.assertLess(similarity, 0.9999)


if __name__ == "__main__":
    unittest.main()