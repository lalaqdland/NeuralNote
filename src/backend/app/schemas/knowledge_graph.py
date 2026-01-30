"""
知识图谱相关的 Pydantic Schemas
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ==================== 知识图谱创建 ====================

class KnowledgeGraphCreate(BaseModel):
    """创建知识图谱请求"""
    
    name: str = Field(..., min_length=1, max_length=100, description="图谱名称")
    description: Optional[str] = Field(None, description="图谱描述")
    subject: Optional[str] = Field(None, max_length=50, description="学科分类")
    cover_image_url: Optional[str] = Field(None, max_length=500, description="封面图片URL")
    is_public: Optional[bool] = Field(False, description="是否公开")


# ==================== 知识图谱更新 ====================

class KnowledgeGraphUpdate(BaseModel):
    """更新知识图谱请求"""
    
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="图谱名称")
    description: Optional[str] = Field(None, description="图谱描述")
    subject: Optional[str] = Field(None, max_length=50, description="学科分类")
    cover_image_url: Optional[str] = Field(None, max_length=500, description="封面图片URL")
    is_public: Optional[bool] = Field(None, description="是否公开")


# ==================== 知识图谱响应 ====================

class KnowledgeGraphBase(BaseModel):
    """知识图谱基础信息"""
    
    id: UUID
    name: str
    description: Optional[str] = None
    subject: Optional[str] = None
    cover_image_url: Optional[str] = None
    is_public: bool
    node_count: int
    edge_count: int
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class KnowledgeGraphResponse(KnowledgeGraphBase):
    """知识图谱响应"""
    
    pass


class KnowledgeGraphDetailResponse(KnowledgeGraphBase):
    """知识图谱详细信息响应"""
    
    user_id: UUID
    total_review_count: int
    last_accessed_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}


# ==================== 知识图谱列表 ====================

class KnowledgeGraphListItem(BaseModel):
    """知识图谱列表项"""
    
    id: UUID
    name: str
    description: Optional[str] = None
    subject: Optional[str] = None
    cover_image_url: Optional[str] = None
    node_count: int
    is_public: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


# ==================== 知识图谱统计 ====================

class KnowledgeGraphStats(BaseModel):
    """知识图谱统计信息"""
    
    total_nodes: int = Field(..., description="总节点数")
    total_relations: int = Field(..., description="总关联数")
    total_tags: int = Field(..., description="总标签数")
    review_due_count: int = Field(..., description="待复习节点数")
    last_review_at: Optional[datetime] = Field(None, description="最后复习时间")

