"""
文件上传记录模型
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import UUIDMixin


class FileUpload(Base, UUIDMixin):
    """文件上传记录表模型"""

    __tablename__ = "file_uploads"
    __table_args__ = {"comment": "文件上传记录表"}

    # 所属用户
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="用户ID",
    )

    # 所属图谱（可选）
    graph_id = Column(
        UUID(as_uuid=True),
        ForeignKey("knowledge_graphs.id"),
        nullable=True,
        comment="知识图谱ID",
    )

    # 文件信息
    original_filename = Column(
        String(255),
        nullable=False,
        comment="原始文件名",
    )
    stored_filename = Column(
        String(255),
        nullable=False,
        comment="存储文件名",
    )
    file_url = Column(
        String(500),
        nullable=False,
        comment="文件URL",
    )
    file_size = Column(
        BigInteger,
        nullable=False,
        comment="文件大小（字节）",
    )
    mime_type = Column(
        String(100),
        nullable=False,
        comment="MIME类型",
    )

    # 处理状态
    status = Column(
        String(20),
        nullable=False,
        default="pending",
        index=True,
        comment="处理状态: pending, processing, completed, failed",
    )
    processing_result = Column(
        JSONB,
        nullable=True,
        comment="处理结果",
    )
    error_message = Column(
        Text,
        nullable=True,
        comment="错误信息",
    )

    # 元数据
    uploaded_ip = Column(
        String(45),
        nullable=True,
        comment="上传IP地址",
    )
    device_info = Column(
        JSONB,
        nullable=True,
        comment="设备信息",
    )

    # 时间戳
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="创建时间",
    )
    processed_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="处理完成时间",
    )

    # 关系
    user = relationship("User", back_populates="file_uploads")
    graph = relationship("KnowledgeGraph", back_populates="file_uploads")

    def __repr__(self) -> str:
        return f"<FileUpload(id={self.id}, filename={self.original_filename}, status={self.status})>"

