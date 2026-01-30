"""
节点关联模型
"""

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import UUIDMixin


class NodeRelation(Base, UUIDMixin):
    """节点关联表模型"""

    __tablename__ = "node_relations"
    __table_args__ = {"comment": "节点关联表"}

    # 所属图谱
    graph_id = Column(
        UUID(as_uuid=True),
        ForeignKey("knowledge_graphs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="知识图谱ID",
    )

    # 源节点
    source_id = Column(
        UUID(as_uuid=True),
        ForeignKey("memory_nodes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="源节点ID",
    )

    # 目标节点
    target_id = Column(
        UUID(as_uuid=True),
        ForeignKey("memory_nodes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="目标节点ID",
    )

    # 关联类型
    relation_type = Column(
        String(20),
        nullable=False,
        index=True,
        comment="关联类型: PREREQUISITE, VARIANT, RELATED",
    )

    # 关联强度
    strength = Column(
        Integer,
        nullable=False,
        default=50,
        comment="关联强度 0-100",
    )

    # 是否自动生成
    is_auto_generated = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="是否自动生成",
    )

    # 创建者
    created_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
        comment="创建者ID",
    )

    # 时间戳
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="创建时间",
    )

    # 关系
    graph = relationship("KnowledgeGraph", back_populates="node_relations")
    source_node = relationship(
        "MemoryNode",
        back_populates="outgoing_relations",
        foreign_keys=[source_id],
    )
    target_node = relationship(
        "MemoryNode",
        back_populates="incoming_relations",
        foreign_keys=[target_id],
    )

    def __repr__(self) -> str:
        return f"<NodeRelation(source={self.source_id}, target={self.target_id}, type={self.relation_type})>"

