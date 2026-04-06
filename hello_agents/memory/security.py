"""安全性与隐私保护

提供记忆的安全性和隐私保护能力：
- 访问控制
- 权限管理
- 敏感信息过滤
- 数据加密
"""

from typing import Dict, Any, Optional, List
import re
import hashlib
import json
from datetime import datetime
from .long_term_memory import LongTermMemory


class MemorySecurity:
    """记忆安全管理器
    
    功能：
    - 访问控制
    - 权限管理
    - 敏感信息过滤
    - 数据加密
    """
    
    def __init__(self, long_term_memory: LongTermMemory):
        """初始化记忆安全管理器
        
        Args:
            long_term_memory: 长期记忆实例
        """
        self.long_term_memory = long_term_memory
        self._access_control = {}
        self._sensitive_patterns = [
            # 邮箱地址
            r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            # 手机号（中国）
            r'1[3-9]\d{9}',
            # 身份证号（中国）
            r'[1-9]\d{5}(18|19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx]',
            # 银行卡号
            r'\d{16,19}',
            # 密码
            r'password[:\s]*[:=][\s]*[\w\d!@#$%^&*()_+]+',
            # API密钥
            r'(api[_\s-]?key|api[_\s-]?token)[:\s]*[:=][\s]*[\w\d!@#$%^&*()_+]+'
        ]
    
    def set_access_control(self, memory_id: str, allowed_roles: List[str]) -> bool:
        """设置记忆的访问控制
        
        Args:
            memory_id: 记忆ID
            allowed_roles: 允许访问的角色列表
            
        Returns:
            是否设置成功
        """
        # 检查记忆是否存在
        memory = self.long_term_memory.get_memory(memory_id)
        if not memory:
            return False
        
        # 设置访问控制
        self._access_control[memory_id] = allowed_roles
        
        # 更新记忆的访问控制信息
        return self.long_term_memory.update_memory(
            memory_id, 
            access_control={"allowed_roles": allowed_roles}
        )
    
    def check_access(self, memory_id: str, user_roles: List[str]) -> bool:
        """检查用户是否有权访问记忆
        
        Args:
            memory_id: 记忆ID
            user_roles: 用户角色列表
            
        Returns:
            是否有权访问
        """
        # 检查记忆是否存在
        memory = self.long_term_memory.get_memory(memory_id)
        if not memory:
            return False
        
        # 获取访问控制信息
        access_control = memory.get("access_control", {})
        allowed_roles = access_control.get("allowed_roles", [])
        
        # 如果没有设置访问控制，则默认允许访问
        if not allowed_roles:
            return True
        
        # 检查用户角色是否在允许列表中
        for role in user_roles:
            if role in allowed_roles:
                return True
        
        return False
    
    def filter_sensitive_info(self, memory_id: str) -> Dict[str, Any]:
        """过滤记忆中的敏感信息
        
        Args:
            memory_id: 记忆ID
            
        Returns:
            过滤结果
        """
        # 检查记忆是否存在
        memory = self.long_term_memory.get_memory(memory_id)
        if not memory:
            return {
                "success": False,
                "message": "记忆不存在"
            }
        
        # 过滤敏感信息
        filtered_content = self._filter_sensitive_text(memory.get("content", ""))
        filtered_summary = self._filter_sensitive_text(memory.get("summary", ""))
        
        # 更新记忆
        success = self.long_term_memory.update_memory(
            memory_id,
            content=filtered_content,
            summary=filtered_summary,
            sensitive_filtered=True,
            filtered_at=datetime.now().isoformat()
        )
        
        return {
            "success": success,
            "memory_id": memory_id,
            "filtered_content": filtered_content,
            "filtered_summary": filtered_summary
        }
    
    def encrypt_memory(self, memory_id: str, encryption_key: str) -> Dict[str, Any]:
        """加密记忆
        
        Args:
            memory_id: 记忆ID
            encryption_key: 加密密钥
            
        Returns:
            加密结果
        """
        # 检查记忆是否存在
        memory = self.long_term_memory.get_memory(memory_id)
        if not memory:
            return {
                "success": False,
                "message": "记忆不存在"
            }
        
        # 加密内容
        encrypted_content = self._encrypt_text(memory.get("content", ""), encryption_key)
        encrypted_summary = self._encrypt_text(memory.get("summary", ""), encryption_key)
        
        # 更新记忆
        success = self.long_term_memory.update_memory(
            memory_id,
            content=encrypted_content,
            summary=encrypted_summary,
            encrypted=True,
            encrypted_at=datetime.now().isoformat()
        )
        
        return {
            "success": success,
            "memory_id": memory_id,
            "encrypted": True
        }
    
    def decrypt_memory(self, memory_id: str, encryption_key: str) -> Dict[str, Any]:
        """解密记忆
        
        Args:
            memory_id: 记忆ID
            encryption_key: 解密密钥
            
        Returns:
            解密结果
        """
        # 检查记忆是否存在
        memory = self.long_term_memory.get_memory(memory_id)
        if not memory:
            return {
                "success": False,
                "message": "记忆不存在"
            }
        
        # 检查记忆是否已加密
        if not memory.get("encrypted", False):
            return {
                "success": False,
                "message": "记忆未加密"
            }
        
        # 解密内容
        decrypted_content = self._decrypt_text(memory.get("content", ""), encryption_key)
        decrypted_summary = self._decrypt_text(memory.get("summary", ""), encryption_key)
        
        # 更新记忆
        success = self.long_term_memory.update_memory(
            memory_id,
            content=decrypted_content,
            summary=decrypted_summary,
            encrypted=False,
            decrypted_at=datetime.now().isoformat()
        )
        
        return {
            "success": success,
            "memory_id": memory_id,
            "decrypted": True
        }
    
    def audit_memory_access(self, memory_id: str, user_id: str, action: str) -> bool:
        """审计记忆访问
        
        Args:
            memory_id: 记忆ID
            user_id: 用户ID
            action: 操作类型（read, write, delete）
            
        Returns:
            是否审计成功
        """
        # 创建审计记录
        audit_record = {
            "memory_id": memory_id,
            "user_id": user_id,
            "action": action,
            "timestamp": datetime.now().isoformat(),
            "ip_address": "127.0.0.1"  # 实际应用中应获取真实IP
        }
        
        # 保存审计记录
        audit_id = self.long_term_memory.add_memory(
            content=json.dumps(audit_record),
            summary=f"审计记录: {action} - {user_id}",
            category="system",
            tags=["audit", action],
            priority=5
        )
        
        return bool(audit_id)
    
    def _filter_sensitive_text(self, text: str) -> str:
        """过滤文本中的敏感信息
        
        Args:
            text: 文本
            
        Returns:
            过滤后的文本
        """
        filtered_text = text
        
        for pattern in self._sensitive_patterns:
            # 替换敏感信息为占位符
            filtered_text = re.sub(pattern, "[敏感信息]", filtered_text)
        
        return filtered_text
    
    def _encrypt_text(self, text: str, key: str) -> str:
        """加密文本
        
        Args:
            text: 文本
            key: 加密密钥
            
        Returns:
            加密后的文本
        """
        # 简单的加密实现，实际应用中应使用更安全的加密算法
        key_hash = hashlib.sha256(key.encode()).digest()
        encrypted = []
        for i, char in enumerate(text):
            key_char = key_hash[i % len(key_hash)]
            encrypted_char = chr(ord(char) ^ key_char)
            encrypted.append(encrypted_char)
        
        return "".join(encrypted)
    
    def _decrypt_text(self, text: str, key: str) -> str:
        """解密文本
        
        Args:
            text: 加密文本
            key: 解密密钥
            
        Returns:
            解密后的文本
        """
        # 对应加密的解密实现
        key_hash = hashlib.sha256(key.encode()).digest()
        decrypted = []
        for i, char in enumerate(text):
            key_char = key_hash[i % len(key_hash)]
            decrypted_char = chr(ord(char) ^ key_char)
            decrypted.append(decrypted_char)
        
        return "".join(decrypted)
