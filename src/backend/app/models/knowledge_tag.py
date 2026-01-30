"""
知识点标签模型
"""

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import UUIDMixin


class KnowledgeTag(Base, UUIDMixin):
    """知识点标签表模型"""

    __tablename__ = "knowledge_tags"
    __table_args__ = {"comment": "知识点标签表"}

    # 所属图谱
    graph_id = Column(
        UUID(as_uuid=True),
        ForeignKey("knowledge_graphs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="知识图谱ID",
    )

    # 基本信息
    name = Column(
        String(100),
        nullable=False,
        comment="标签名称",
    )
    description = Column(
        Text,
        nullable=True,
        comment="标签描述",
    )

    # 父标签（支持层级结构）
    parent_id = Column(
        UUID(as_uuid=True),
        ForeignKey("knowledge_tags.id"),
        nullable=True,
        index=True,
        comment="父标签ID",
    )

    # 视觉配置
    color = Column(
        String(20),
        nullable=False,
        default="#1890FF",
        comment="标签颜色",
    )
    icon = Column(
        String(50),
        nullable=True,
        comment="标签图标",
    )

    # 统计信息
    importance_score = Column(
        Float,
        nullable=False,
        default=50.0,
        comment="重要性评分 0-100",
    )
    mastery_rate = Column(
        Float,
        nullable=False,
        default=0.0,
        comment="该知识点的整体掌握率",
    )
    node_count = Column(
        Integer,
        nullable=False,
        default=0,
        comment="关联的节点数量",
    )

    # 时间戳
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="创建时间",
    )

    # 关系
    graph = relationship("KnowledgeGraph", back_populates="knowledge_tags")
    parent = relationship(
        "KnowledgeTag",
        remote_side="KnowledgeTag.id",
        backref="children",
    )
    node_tags = relationship(
        "NodeTag",
        back_populates="tag",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<KnowledgeTag(id={self.id}, name={self.name}, graph_id={self.graph_id})>"

