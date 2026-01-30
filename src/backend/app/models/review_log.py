"""
复习记录模型
"""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import UUIDMixin


class ReviewLog(Base, UUIDMixin):
    """复习记录表模型"""

    __tablename__ = "review_logs"
    __table_args__ = {"comment": "复习记录表"}

    # 关联的节点
    node_id = Column(
        UUID(as_uuid=True),
        ForeignKey("memory_nodes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="节点ID",
    )

    # 关联的用户
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="用户ID",
    )

    # 复习模式
    review_mode = Column(
        String(20),
        nullable=False,
        comment="复习模式: graph-traversal, random, focused, spaced",
    )

    # 复习结果
    mastery_feedback = Column(
        String(20),
        nullable=False,
        comment="掌握反馈: remembered, forgot, partial",
    )
    time_spent_seconds = Column(
        Integer,
        nullable=True,
        comment="花费时间（秒）",
    )

    # 复习时的状态快照
    node_state_snapshot = Column(
        JSONB,
        nullable=True,
        comment="节点状态快照",
    )

    # 上下文信息
    device_type = Column(
        String(20),
        nullable=True,
        comment="设备类型",
    )
    app_version = Column(
        String(20),
        nullable=True,
        comment="应用版本",
    )

    # 时间戳
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="创建时间",
    )

    # 关系
    node = relationship("MemoryNode", back_populates="review_logs")
    user = relationship("User", back_populates="review_logs")

    def __repr__(self) -> str:
        return f"<ReviewLog(id={self.id}, node_id={self.node_id}, feedback={self.mastery_feedback})>"

