"""
视图配置模型
"""

from sqlalchemy import Boolean, Column, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class ViewConfig(Base, UUIDMixin, TimestampMixin):
    """视图配置表模型"""

    __tablename__ = "view_configs"
    __table_args__ = {"comment": "视图配置表"}

    # 所属用户
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="用户ID",
    )

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
        comment="视图名称",
    )
    description = Column(
        Text,
        nullable=True,
        comment="视图描述",
    )

    # 视图类型
    view_type = Column(
        String(20),
        nullable=False,
        default="custom",
        comment="视图类型: preset, custom",
    )

    # 过滤配置
    filter_config = Column(
        JSONB,
        nullable=False,
        default={},
        comment="过滤配置",
    )

    # 布局配置
    layout_engine = Column(
        String(50),
        nullable=False,
        default="force-directed",
        comment="布局引擎",
    )
    layout_params = Column(
        JSONB,
        nullable=True,
        default={},
        comment="布局参数",
    )

    # 视觉配置
    color_scheme = Column(
        String(50),
        nullable=False,
        default="fresh-modern",
        comment="配色方案",
    )
    node_size_mode = Column(
        String(20),
        nullable=False,
        default="fixed",
        comment="节点大小模式",
    )
    show_labels = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="是否显示标签",
    )
    animation_enabled = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="是否启用动画",
    )

    # 是否默认视图
    is_default = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="是否为默认视图",
    )

    # 关系
    user = relationship("User", back_populates="view_configs")
    graph = relationship("KnowledgeGraph", back_populates="view_configs")

    def __repr__(self) -> str:
        return f"<ViewConfig(id={self.id}, name={self.name}, user_id={self.user_id})>"

