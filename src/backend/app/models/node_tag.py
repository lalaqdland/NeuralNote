"""
节点-标签关联模型
"""

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import UUIDMixin


class NodeTag(Base, UUIDMixin):
    """节点-标签关联表模型"""

    __tablename__ = "node_tags"
    __table_args__ = {"comment": "节点-标签关联表"}

    # 关联的节点
    node_id = Column(
        UUID(as_uuid=True),
        ForeignKey("memory_nodes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="节点ID",
    )

    # 关联的标签
    tag_id = Column(
        UUID(as_uuid=True),
        ForeignKey("knowledge_tags.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="标签ID",
    )

    # AI推荐的置信度
    confidence = Column(
        Float,
        nullable=False,
        default=1.0,
        comment="AI推荐的置信度 0-1",
    )

    # 是否用户手动添加
    is_manual = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="是否用户手动添加",
    )

    # 时间戳
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="创建时间",
    )

    # 关系
    node = relationship("MemoryNode", back_populates="node_tags")
    tag = relationship("KnowledgeTag", back_populates="node_tags")

    def __repr__(self) -> str:
        return f"<NodeTag(node_id={self.node_id}, tag_id={self.tag_id})>"

