"""ContextBuilder - GSSC流水线实现

实现 Gather-Select-Structure-Compress 上下文构建流程：
1. Gather: 从多源收集候选信息（历史、工具结果、记忆）
2. Select: 基于优先级、相关性、多样性筛选
3. Structure: 组织成结构化上下文模板
4. Compress: 在预算内压缩与规范化
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import tiktoken
import math

from ..core.message import Message
from ..memory import MemoryManager


@dataclass
class ContextPacket:
    """上下文信息包"""
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    token_count: int = 0
    relevance_score: float = 0.0  # 0.0-1.0
    
    def __post_init__(self):
        """自动计算token数"""
        if self.token_count == 0:
            self.token_count = count_tokens(self.content)


@dataclass
class ContextConfig:
    """上下文构建配置"""
    max_tokens: int = 8000  # 总预算
    reserve_ratio: float = 0.15  # 生成余量（10-20%）
    min_relevance: float = 0.3  # 最小相关性阈值
    enable_mmr: bool = True  # 启用最大边际相关性（多样性）
    mmr_lambda: float = 0.7  # MMR平衡参数（0=纯多样性, 1=纯相关性）
    system_prompt_template: str = ""  # 系统提示模板
    enable_compression: bool = True  # 启用压缩
    enable_memory: bool = True  # 启用记忆检索
    memory_top_k: int = 3  # 记忆检索返回数量
    memory_weight: float = 0.8  # 记忆在相关性计算中的权重
    enable_adaptive: bool = True  # 启用自适应调整
    task_type_weights: Dict[str, Dict[str, float]] = field(default_factory=lambda: {
        "qa": {"memory": 0.8, "history": 0.2, "tool_result": 0.9},
        "creative": {"memory": 0.4, "history": 0.3, "tool_result": 0.3},
        "analysis": {"memory": 0.7, "history": 0.2, "tool_result": 0.8},
        "conversation": {"memory": 0.5, "history": 0.8, "tool_result": 0.4}
    })
    
    def get_available_tokens(self) -> int:
        """获取可用token预算（扣除余量）"""
        return int(self.max_tokens * (1 - self.reserve_ratio))


class ContextBuilder:
    """上下文构建器 - GSSC流水线

    用法示例：
    ```python
    from agent_core.memory import MemoryManager
    
    memory_manager = MemoryManager()
    builder = ContextBuilder(
        config=ContextConfig(max_tokens=8000),
        memory_manager=memory_manager
    )

    context = builder.build(
        user_query="用户问题",
        conversation_history=[...],
        system_instructions="系统指令",
        session_id="会话ID"
    )
    ```
    """

    def __init__(
        self,
        config: Optional[ContextConfig] = None,
        memory_manager: Optional[MemoryManager] = None
    ):
        self.config = config or ContextConfig()
        self.memory_manager = memory_manager
        self._encoding = tiktoken.get_encoding("cl100k_base")
    
    def build(
        self,
        user_query: str,
        conversation_history: Optional[List[Message]] = None,
        system_instructions: Optional[str] = None,
        additional_packets: Optional[List[ContextPacket]] = None,
        session_id: Optional[str] = None,
        task_type: Optional[str] = None
    ) -> str:
        """构建完整上下文
        
        Args:
            user_query: 用户查询
            conversation_history: 对话历史
            system_instructions: 系统指令
            additional_packets: 额外的上下文包
            session_id: 会话ID（用于记忆检索）
            task_type: 任务类型（可选，自动识别）
            
        Returns:
            结构化上下文字符串
        """
        # 识别任务类型
        if task_type is None and self.config.enable_adaptive:
            task_type = self._identify_task_type(user_query)
        
        # 1. Gather: 收集候选信息
        packets = self._gather(
            user_query=user_query,
            conversation_history=conversation_history or [],
            system_instructions=system_instructions,
            additional_packets=additional_packets or [],
            session_id=session_id
        )
        
        # 2. Select: 筛选与排序
        selected_packets = self._select(packets, user_query, task_type)
        
        # 3. Structure: 组织成结构化模板
        structured_context = self._structure(
            selected_packets=selected_packets,
            user_query=user_query,
            system_instructions=system_instructions
        )
        
        # 4. Compress: 压缩与规范化（如果超预算）
        final_context = self._compress(structured_context)
        
        return final_context
    
    def _gather(
        self,
        user_query: str,
        conversation_history: List[Message],
        system_instructions: Optional[str],
        additional_packets: List[ContextPacket],
        session_id: Optional[str]
    ) -> List[ContextPacket]:
        """Gather: 收集候选信息"""
        packets = []
        
        # P0: 系统指令（强约束）
        if system_instructions:
            packets.append(ContextPacket(
                content=system_instructions,
                metadata={"type": "instructions"}
            ))

        # P1: 记忆检索（相关事实）
        if self.config.enable_memory and self.memory_manager:
            # 检索长期记忆
            long_term_results = self.memory_manager.semantic_search(
                query=user_query,
                top_k=self.config.memory_top_k
            )
            
            for score, memory in long_term_results:
                    packets.append(ContextPacket(
                        content=f"[长期记忆] {memory.get('summary', memory.get('content', ''))}",
                        metadata={"type": "related_memory", "score": score, "memory_id": memory.get("memory_id")}
                    ))
            
            # 检索短期记忆（会话记忆）
            if session_id:
                session_memories = self.memory_manager.get_session_memories(session_id)
                for memory in session_memories:
                    # 确保记忆有id字段
                    memory_id = memory.get("id") or memory.get("memory_id")
                    # 直接添加短期记忆，不进行相关性过滤
                    packets.append(ContextPacket(
                        content=f"[会话记忆] {memory.get('summary', memory.get('content', ''))}",
                        metadata={"type": "session_memory", "memory_id": memory_id},
                        relevance_score=0.9  # 设置高相关性得分，确保被包含
                    ))

        # P3: 对话历史（辅助材料）
        if conversation_history:
            # 只保留最近N条
            recent_history = conversation_history[-10:]
            history_text = "\n".join([
                f"[{msg.role}] {msg.content}"
                for msg in recent_history
            ])
            packets.append(ContextPacket(
                content=history_text,
                metadata={"type": "history", "count": len(recent_history)}
            ))

        # 添加额外包
        packets.extend(additional_packets)

        return packets
    
    def _select(
        self,
        packets: List[ContextPacket],
        user_query: str,
        task_type: Optional[str] = None
    ) -> List[ContextPacket]:
        """Select: 基于分数与预算的筛选"""
        # 1) 计算相关性
        query_tokens = set(user_query.lower().split())
        for packet in packets:
            # 如果是记忆包，使用记忆系统返回的相似度得分
            if packet.metadata.get("type") in {"related_memory", "session_memory"}:
                if "score" in packet.metadata:
                    packet.relevance_score = packet.metadata["score"]
                else:
                    # 降级到关键词重叠计算
                    content_tokens = set(packet.content.lower().split())
                    if len(query_tokens) > 0:
                        overlap = len(query_tokens & content_tokens)
                        packet.relevance_score = overlap / len(query_tokens)
                    else:
                        packet.relevance_score = 0.0
            else:
                # 其他类型的包使用关键词重叠计算
                content_tokens = set(packet.content.lower().split())
                if len(query_tokens) > 0:
                    overlap = len(query_tokens & content_tokens)
                    packet.relevance_score = overlap / len(query_tokens)
                else:
                    packet.relevance_score = 0.0
        
        # 2) 计算新近性（指数衰减）
        def recency_score(ts: datetime) -> float:
            delta = max((datetime.now() - ts).total_seconds(), 0)
            tau = 3600  # 1小时时间尺度，可暴露到配置
            return math.exp(-delta / tau)
        
        # 3) 根据任务类型获取权重
        weights = {"memory": 0.7, "history": 0.3, "tool_result": 0.6}
        if task_type and self.config.enable_adaptive:
            task_weights = self.config.task_type_weights.get(task_type, {})
            if task_weights:
                weights.update(task_weights)
        
        # 4) 计算复合分
        scored_packets: List[Tuple[float, ContextPacket]] = []
        for p in packets:
            rec = recency_score(p.timestamp)
            
            # 根据包类型调整权重
            packet_type = p.metadata.get("type")
            if packet_type in {"related_memory", "session_memory"}:
                score = weights["memory"] * p.relevance_score + (1 - weights["memory"]) * rec
            elif packet_type == "history":
                score = weights["history"] * p.relevance_score + (1 - weights["history"]) * rec
            elif packet_type in {"tool_result", "retrieval", "knowledge_base"}:
                score = weights["tool_result"] * p.relevance_score + (1 - weights["tool_result"]) * rec
            else:
                # 默认权重
                score = 0.7 * p.relevance_score + 0.3 * rec
            
            scored_packets.append((score, p))
        
        # 4) 系统指令单独拿出，固定纳入
        system_packets = [p for (_, p) in scored_packets if p.metadata.get("type") == "instructions"]
        # 会话记忆单独拿出，优先纳入
        session_memory_packets = [p for (_, p) in scored_packets if p.metadata.get("type") == "session_memory"]
        # 其余包
        remaining = [p for (s, p) in sorted(scored_packets, key=lambda x: x[0], reverse=True)
                     if p.metadata.get("type") not in ["instructions", "session_memory"]]
        
        # 5) 依据 min_relevance 过滤（对非系统、非会话记忆包）
        filtered = [p for p in remaining if p.relevance_score >= self.config.min_relevance]
        
        # 6) 按预算填充
        available_tokens = self.config.get_available_tokens()
        selected: List[ContextPacket] = []
        used_tokens = 0
        
        # 先放入系统指令（不排序）
        for p in system_packets:
            if used_tokens + p.token_count <= available_tokens:
                selected.append(p)
                used_tokens += p.token_count
        
        # 再放入会话记忆（优先纳入）
        for p in session_memory_packets:
            if used_tokens + p.token_count <= available_tokens:
                selected.append(p)
                used_tokens += p.token_count
        
        # 最后按分数加入其余
        for p in filtered:
            if used_tokens + p.token_count > available_tokens:
                continue
            selected.append(p)
            used_tokens += p.token_count
        
        return selected
    
    def _structure(
        self,
        selected_packets: List[ContextPacket],
        user_query: str,
        system_instructions: Optional[str]
    ) -> str:
        """Structure: 组织成结构化上下文模板"""
        sections = []
        
        # [Role & Policies] - 系统指令
        p0_packets = [p for p in selected_packets if p.metadata.get("type") == "instructions"]
        if p0_packets:
            role_section = "[Role & Policies]\n"
            role_section += "\n".join([p.content for p in p0_packets])
            sections.append(role_section)
        
        # [Task] - 当前任务
        sections.append(f"[Task]\n用户问题：{user_query}")
        
        # [State] - 任务状态
        p1_packets = [p for p in selected_packets if p.metadata.get("type") == "task_state"]
        if p1_packets:
            state_section = "[State]\n关键进展与未决问题：\n"
            state_section += "\n".join([p.content for p in p1_packets])
            sections.append(state_section)
        
        # [Evidence] - 事实证据
        p2_packets = [
            p for p in selected_packets
            if p.metadata.get("type") in {"related_memory", "session_memory", "knowledge_base", "retrieval", "tool_result"}
        ]
        if p2_packets:
            evidence_section = "[Evidence]\n事实与引用：\n"
            for p in p2_packets:
                evidence_section += f"\n{p.content}\n"
            sections.append(evidence_section)
        
        # [Context] - 辅助材料（历史等）
        p3_packets = [p for p in selected_packets if p.metadata.get("type") == "history"]
        if p3_packets:
            context_section = "[Context]\n对话历史与背景：\n"
            context_section += "\n".join([p.content for p in p3_packets])
            sections.append(context_section)
        
        # [Output] - 输出约束
        output_section = """[Output]
                            请按以下格式回答：
                            1. 结论（简洁明确）
                            2. 依据（列出支撑证据及来源）
                            3. 风险与假设（如有）
                            4. 下一步行动建议（如适用）"""
        sections.append(output_section)
        
        return "\n\n".join(sections)
    
    def _compress(self, context: str) -> str:
        """Compress: 压缩与规范化"""
        if not self.config.enable_compression:
            return context
        
        current_tokens = count_tokens(context)
        available_tokens = self.config.get_available_tokens()
        
        if current_tokens <= available_tokens:
            return context
        
        # 简单截断策略（保留前N个token）
        # 实际应用中可用LLM做高保真摘要
        print(f"⚠️ 上下文超预算 ({current_tokens} > {available_tokens})，执行截断")
        
        # 按段落截断，保留结构
        lines = context.split("\n")
        compressed_lines = []
        used_tokens = 0
        
        for line in lines:
            line_tokens = count_tokens(line)
            if used_tokens + line_tokens > available_tokens:
                break
            compressed_lines.append(line)
            used_tokens += line_tokens
        
        return "\n".join(compressed_lines)
    
    def _identify_task_type(self, user_query: str) -> str:
        """识别任务类型
        
        Args:
            user_query: 用户查询
            
        Returns:
            任务类型
        """
        query_lower = user_query.lower()
        
        # 问答类型
        qa_keywords = ["what", "when", "where", "who", "why", "how", "which", "is", "are", "was", "were", "do", "does", "did", "can", "could", "would", "should", "will", "may", "might", "?", "吗", "呢", "什么", "怎么", "为什么", "哪里", "何时", "谁", "哪个"]
        if any(keyword in query_lower for keyword in qa_keywords):
            return "qa"
        
        # 创意写作类型
        creative_keywords = ["write", "create", "generate", "compose", "design", "invent", "imagine", "story", "poem", "essay", "letter", "email", "report", "article", "创作", "写", "生成", "设计", "想象", "故事", "诗歌", "文章", "邮件", "报告"]
        if any(keyword in query_lower for keyword in creative_keywords):
            return "creative"
        
        # 分析类型
        analysis_keywords = ["analyze", "analys", "evaluate", "assess", "examine", "review", "study", "inspect", "investigate", "analyze", "分析", "评估", "审查", "研究", "检查", "调查"]
        if any(keyword in query_lower for keyword in analysis_keywords):
            return "analysis"
        
        # 默认对话类型
        return "conversation"


def count_tokens(text: str) -> int:
    """计算文本token数（使用tiktoken）"""
    try:
        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
    except Exception:
        # 降级方案：粗略估算（1 token ≈ 4 字符）
        return len(text) // 4

