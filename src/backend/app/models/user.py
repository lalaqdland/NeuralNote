"""
用户模型
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, String
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class User(Base, UUIDMixin, TimestampMixin):
    """用户表模型"""

    __tablename__ = "users"
    __table_args__ = {"comment": "用户表"}

    # 基本信息
    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="邮箱地址",
    )
    phone = Column(
        String(20),
        unique=True,
        nullable=True,
        comment="手机号码",
    )
    username = Column(
        String(50),
        unique=True,
        nullable=False,
        comment="用户名",
    )
    password_hash = Column(
        String(255),
        nullable=False,
        comment="密码哈希",
    )
    avatar_url = Column(
        String(500),
        nullable=True,
        comment="头像URL",
    )

    # 偏好设置
    timezone = Column(
        String(50),
        nullable=False,
        default="Asia/Shanghai",
        comment="时区",
    )
    language = Column(
        String(10),
        nullable=False,
        default="zh-CN",
        comment="语言",
    )

    # 订阅信息
    subscription_plan = Column(
        String(20),
        nullable=False,
        default="free",
        index=True,
        comment="订阅计划: free, pro_monthly, pro_yearly, team",
    )
    subscription_expires_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="订阅过期时间",
    )

    # 状态信息
    last_login_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="最后登录时间",
    )
    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="是否激活",
    )
    is_verified = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="是否已验证邮箱",
    )

    # 关系
    knowledge_graphs = relationship(
        "KnowledgeGraph",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    memory_nodes = relationship(
        "MemoryNode",
        back_populates="creator",
        foreign_keys="MemoryNode.created_by",
    )
    view_configs = relationship(
        "ViewConfig",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    review_logs = relationship(
        "ReviewLog",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    file_uploads = relationship(
        "FileUpload",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"

