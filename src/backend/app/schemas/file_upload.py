"""
文件上传相关的 Pydantic Schemas
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class FileUploadBase(BaseModel):
    """文件上传基础 Schema"""
    
    graph_id: Optional[UUID] = Field(None, description="所属知识图谱ID")


class FileUploadCreate(FileUploadBase):
    """创建文件上传记录"""
    
    original_filename: str = Field(..., description="原始文件名")
    stored_filename: str = Field(..., description="存储文件名")
    file_url: str = Field(..., description="文件URL")
    file_size: int = Field(..., description="文件大小（字节）")
    mime_type: str = Field(..., description="MIME类型")
    uploaded_ip: Optional[str] = Field(None, description="上传IP地址")


class FileUploadUpdate(BaseModel):
    """更新文件上传记录"""
    
    status: Optional[str] = Field(None, description="处理状态")
    processing_result: Optional[dict] = Field(None, description="处理结果")
    error_message: Optional[str] = Field(None, description="错误信息")


class FileUploadResponse(FileUploadBase):
    """文件上传响应"""
    
    id: UUID
    user_id: UUID
    original_filename: str
    stored_filename: str
    file_url: str
    file_size: int
    mime_type: str
    status: str
    processing_result: Optional[dict] = None
    error_message: Optional[str] = None
    uploaded_ip: Optional[str] = None
    created_at: datetime
    processed_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}


class FileUploadInfo(BaseModel):
    """文件上传信息（简化版）"""
    
    id: UUID
    original_filename: str
    file_url: str
    file_size: int
    mime_type: str
    status: str
    created_at: datetime
    
    model_config = {"from_attributes": True}


class UploadResponse(BaseModel):
    """上传成功响应"""
    
    file_id: UUID = Field(..., description="文件ID")
    file_url: str = Field(..., description="文件访问URL")
    original_filename: str = Field(..., description="原始文件名")
    file_size: int = Field(..., description="文件大小（字节）")
    mime_type: str = Field(..., description="文件类型")
    message: str = Field(default="文件上传成功", description="提示信息")


class OCRRequest(BaseModel):
    """OCR 识别请求"""
    
    file_id: UUID = Field(..., description="文件ID")
    ocr_engine: Optional[str] = Field("baidu", description="OCR引擎: baidu, tencent, auto")
    
    @field_validator("ocr_engine")
    @classmethod
    def validate_ocr_engine(cls, v: str) -> str:
        """验证 OCR 引擎"""
        allowed = ["baidu", "tencent", "auto"]
        if v not in allowed:
            raise ValueError(f"OCR引擎必须是以下之一: {', '.join(allowed)}")
        return v


class OCRResponse(BaseModel):
    """OCR 识别响应"""
    
    file_id: UUID = Field(..., description="文件ID")
    text: str = Field(..., description="识别的文本")
    confidence: float = Field(..., description="置信度 (0-1)")
    engine: str = Field(..., description="使用的OCR引擎")
    raw_result: Optional[dict] = Field(None, description="原始识别结果")
    processing_time: float = Field(..., description="处理时间（秒）")

