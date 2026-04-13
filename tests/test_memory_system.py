"""测试记忆系统

测试企业级记忆系统的核心功能：
- 长期记忆管理
- 记忆检索
- 记忆组织
- 记忆更新
- 记忆安全
"""

import pytest
from agent_core import MemoryManager


class TestMemorySystem:
    """测试记忆系统"""
    
    def setup_method(self):
        """设置测试环境"""
        self.memory_manager = MemoryManager()
    
    def test_add_memory(self):
        """测试添加记忆"""
        # 添加记忆
        memory_id = self.memory_manager.add_memory(
            content="测试记忆内容",
            summary="测试记忆摘要",
            category="测试",
            tags=["测试", "示例"],
            priority=5
        )
        
        # 验证记忆是否添加成功
        assert memory_id is not None
        assert isinstance(memory_id, str)
        
        # 获取记忆
        memory = self.memory_manager.get_memory(memory_id)
        assert memory is not None
        assert memory.get("content") == "测试记忆内容"
        assert memory.get("summary") == "测试记忆摘要"
        assert memory.get("category") == "测试"
        assert set(memory.get("tags", [])) == {"测试", "示例"}
        assert memory.get("priority") == 5
    
    def test_update_memory(self):
        """测试更新记忆"""
        # 添加记忆
        memory_id = self.memory_manager.add_memory(
            content="原始内容",
            summary="原始摘要"
        )
        
        # 更新记忆
        success = self.memory_manager.update_memory(
            memory_id,
            content="更新后的内容",
            summary="更新后的摘要"
        )
        
        # 验证更新是否成功
        assert success
        
        # 获取更新后的记忆
        memory = self.memory_manager.get_memory(memory_id)
        assert memory.get("content") == "更新后的内容"
        assert memory.get("summary") == "更新后的摘要"
    
    def test_delete_memory(self):
        """测试删除记忆"""
        # 添加记忆
        memory_id = self.memory_manager.add_memory(
            content="测试内容",
            summary="测试摘要"
        )
        
        # 验证记忆存在
        memory = self.memory_manager.get_memory(memory_id)
        assert memory is not None
        
        # 删除记忆
        success = self.memory_manager.delete_memory(memory_id)
        assert success
        
        # 验证记忆已删除
        memory = self.memory_manager.get_memory(memory_id)
        assert memory is None
    
    def test_list_memories(self):
        """测试列出记忆"""
        # 清空现有记忆
        # 注意：这里简化处理，实际测试中可能需要更复杂的清理
        
        # 添加多个记忆
        for i in range(5):
            self.memory_manager.add_memory(
                content=f"记忆{i}",
                summary=f"摘要{i}",
                category=f"分类{i % 2}"
            )
        
        # 列出所有记忆
        memories = self.memory_manager.list_memories(limit=10)
        assert len(memories) >= 5
        
        # 按分类过滤
        category_0_memories = self.memory_manager.list_memories(
            category="分类0",
            limit=10
        )
        assert len(category_0_memories) >= 2
    
    def test_semantic_search(self):
        """测试语义搜索"""
        # 添加相关记忆
        self.memory_manager.add_memory(
            content="Python是一种编程语言",
            summary="Python语言"
        )
        self.memory_manager.add_memory(
            content="Java是一种编程语言",
            summary="Java语言"
        )
        self.memory_manager.add_memory(
            content="猫是一种动物",
            summary="猫"
        )
        
        # 搜索与编程语言相关的记忆
        results = self.memory_manager.semantic_search("编程语言", top_k=2)
        assert len(results) >= 2
        
        # 验证搜索结果相关性
        for similarity, memory in results:
            content = memory.get("content", "")
            assert "编程语言" in content
    
    def test_keyword_search(self):
        """测试关键词搜索"""
        # 添加记忆
        self.memory_manager.add_memory(
            content="Python是一种流行的编程语言",
            summary="Python"
        )
        self.memory_manager.add_memory(
            content="Java也是一种流行的编程语言",
            summary="Java"
        )
        
        # 搜索关键词
        results = self.memory_manager.keyword_search("Python", top_k=1)
        assert len(results) >= 1
        assert "Python" in results[0][1].get("content", "")
    
    def test_hybrid_search(self):
        """测试混合搜索"""
        # 添加记忆
        self.memory_manager.add_memory(
            content="Python是一种高级编程语言",
            summary="Python"
        )
        
        # 混合搜索
        results = self.memory_manager.hybrid_search("Python编程", top_k=1)
        assert len(results) >= 1
        assert "Python" in results[0][1].get("content", "")
    
    def test_create_category(self):
        """测试创建分类"""
        # 创建分类
        result = self.memory_manager.create_category(
            category_name="技术",
            description="技术相关的记忆"
        )
        
        # 验证分类创建成功
        assert result.get("success") is True
        assert result.get("category_name") == "技术"
        
        # 列出分类
        categories = self.memory_manager.list_categories()
        category_names = [cat.get("name") for cat in categories]
        assert "技术" in category_names
    
    def test_add_remove_tag(self):
        """测试添加和移除标签"""
        # 添加记忆
        memory_id = self.memory_manager.add_memory(
            content="测试内容",
            summary="测试摘要"
        )
        
        # 添加标签
        success = self.memory_manager.add_tag(memory_id, "标签1")
        assert success
        
        # 验证标签添加成功
        memory = self.memory_manager.get_memory(memory_id)
        assert "标签1" in memory.get("tags", [])
        
        # 移除标签
        success = self.memory_manager.remove_tag(memory_id, "标签1")
        assert success
        
        # 验证标签移除成功
        memory = self.memory_manager.get_memory(memory_id)
        assert "标签1" not in memory.get("tags", [])
    
    def test_correct_memory(self):
        """测试修正记忆"""
        # 添加记忆
        memory_id = self.memory_manager.add_memory(
            content="错误内容",
            summary="错误摘要"
        )
        
        # 修正记忆
        result = self.memory_manager.correct_memory(
            memory_id,
            correction="正确内容",
            reason="修正错误"
        )
        
        # 验证修正成功
        assert result.get("success") is True
        
        # 获取修正后的记忆
        memory = self.memory_manager.get_memory(memory_id)
        assert memory.get("content") == "正确内容"
        assert "corrections" in memory
    
    def test_set_access_control(self):
        """测试设置访问控制"""
        # 添加记忆
        memory_id = self.memory_manager.add_memory(
            content="敏感内容",
            summary="敏感摘要"
        )
        
        # 设置访问控制
        success = self.memory_manager.set_access_control(
            memory_id,
            allowed_roles=["admin", "user"]
        )
        
        # 验证设置成功
        assert success
        
        # 检查访问权限
        assert self.memory_manager.check_access(memory_id, ["admin"])
        assert self.memory_manager.check_access(memory_id, ["user"])
        assert not self.memory_manager.check_access(memory_id, ["guest"])
    
    def test_filter_sensitive_info(self):
        """测试过滤敏感信息"""
        # 添加包含敏感信息的记忆
        memory_id = self.memory_manager.add_memory(
            content="我的邮箱是 test@example.com，手机号是 13800138000",
            summary="个人信息"
        )
        
        # 过滤敏感信息
        result = self.memory_manager.filter_sensitive_info(memory_id)
        
        # 验证过滤成功
        assert result.get("success") is True
        filtered_content = result.get("filtered_content")
        assert "[敏感信息]" in filtered_content
        assert "test@example.com" not in filtered_content
        assert "13800138000" not in filtered_content
    
    def test_audit_memory_access(self):
        """测试审计记忆访问"""
        # 添加记忆
        memory_id = self.memory_manager.add_memory(
            content="测试内容",
            summary="测试摘要"
        )
        
        # 审计访问
        success = self.memory_manager.audit_memory_access(
            memory_id,
            user_id="test_user",
            action="read"
        )
        
        # 验证审计成功
        assert success
