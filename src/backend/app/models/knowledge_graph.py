"""
知识图谱模型
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class KnowledgeGraph(Base, UUIDMixin, TimestampMixin):
    """知识图谱表模型"""

    __tablename__ = "knowledge_graphs"
    __table_args__ = {"comment": "知识图谱表"}

    # 所属用户
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="用户ID",
    )

    # 基本信息
    name = Column(
        String(100),
        nullable=False,
        comment="图谱名称",
    )
    description = Column(
        Text,
        nullable=True,
        comment="图谱描述",
    )
    subject = Column(
        String(50),
        nullable=True,
        index=True,
        comment="学科分类: math, physics, cs, etc.",
    )
    cover_image_url = Column(
        String(500),
        nullable=True,
        comment="封面图片URL",
    )

    # 公开设置
    is_public = Column(
        Boolean,
        nullable=False,
        default=False,
        index=True,
        comment="是否公开",
    )
    is_preset = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="是否为公有云预设图谱",
    )

    # 统计信息
    node_count = Column(
        Integer,
        nullable=False,
        default=0,
        comment="节点数量",
    )
    edge_count = Column(
        Integer,
        nullable=False,
        default=0,
        comment="边数量",
    )
    total_review_count = Column(
        Integer,
        nullable=False,
        default=0,
        comment="总复习次数",
    )

    # 访问时间
    last_accessed_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="最后访问时间",
    )

    # 关系
    user = relationship("User", back_populates="knowledge_graphs")
    memory_nodes = relationship(
        "MemoryNode",
        back_populates="graph",
        cascade="all, delete-orphan",
    )
    knowledge_tags = relationship(
        "KnowledgeTag",
        back_populates="graph",
        cascade="all, delete-orphan",
    )
    node_relations = relationship(
        "NodeRelation",
        back_populates="graph",
        cascade="all, delete-orphan",
    )
    view_configs = relationship(
        "ViewConfig",
        back_populates="graph",
        cascade="all, delete-orphan",
    )
    file_uploads = relationship(
        "FileUpload",
        back_populates="graph",
    )

    def __repr__(self) -> str:
        return f"<KnowledgeGraph(id={self.id}, name={self.name}, user_id={self.user_id})>"

