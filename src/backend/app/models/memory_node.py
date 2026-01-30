"""
记忆节点模型（核心实体）
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class MemoryNode(Base, UUIDMixin, TimestampMixin):
    """记忆节点表模型（核心实体）"""

    __tablename__ = "memory_nodes"
    __table_args__ = {"comment": "记忆节点表（核心实体）"}

    # 所属图谱
    graph_id = Column(
        UUID(as_uuid=True),
        ForeignKey("knowledge_graphs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="知识图谱ID",
    )

    # 节点类型
    node_type = Column(
        String(20),
        nullable=False,
        default="QUESTION",
        index=True,
        comment="节点类型: QUESTION, CONCEPT, SNIPPET, INSIGHT",
    )

    # 基本信息
    title = Column(
        String(200),
        nullable=False,
        comment="节点标题",
    )
    summary = Column(
        Text,
        nullable=True,
        comment="节点摘要",
    )

    # 灵活的内容数据 (JSONB)
    content_data = Column(
        JSONB,
        nullable=False,
        default={},
        comment="灵活的内容数据，不同类型节点存储不同结构",
    )

    # 向量嵌入 (用于语义搜索)
    content_embedding = Column(
        Vector(1536),
        nullable=True,
        comment="1536维向量，用于语义搜索",
    )

    # 图谱位置信息
    position_x = Column(
        Float,
        nullable=False,
        default=0.0,
        comment="X坐标",
    )
    position_y = Column(
        Float,
        nullable=False,
        default=0.0,
        comment="Y坐标",
    )
    position_z = Column(
        Float,
        nullable=False,
        default=0.0,
        comment="Z坐标（3D视图）",
    )

    # 复习状态
    review_stats = Column(
        JSONB,
        nullable=False,
        default={
            "last_reviewed_at": None,
            "next_review_due": None,
            "review_count": 0,
            "forgetting_curve_index": 100,
            "mastery_status": "FRESH",
        },
        comment="复习状态数据",
    )

    # 创建者
    created_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
        comment="创建者ID",
    )

    # 软删除
    deleted_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="删除时间（软删除）",
    )

    # 关系
    graph = relationship("KnowledgeGraph", back_populates="memory_nodes")
    creator = relationship(
        "User",
        back_populates="memory_nodes",
        foreign_keys=[created_by],
    )
    node_tags = relationship(
        "NodeTag",
        back_populates="node",
        cascade="all, delete-orphan",
    )
    outgoing_relations = relationship(
        "NodeRelation",
        back_populates="source_node",
        foreign_keys="NodeRelation.source_id",
        cascade="all, delete-orphan",
    )
    incoming_relations = relationship(
        "NodeRelation",
        back_populates="target_node",
        foreign_keys="NodeRelation.target_id",
        cascade="all, delete-orphan",
    )
    review_logs = relationship(
        "ReviewLog",
        back_populates="node",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<MemoryNode(id={self.id}, title={self.title}, type={self.node_type})>"

