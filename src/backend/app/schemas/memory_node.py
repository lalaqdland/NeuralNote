"""
记忆节点相关的 Pydantic Schemas
"""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ==================== 记忆节点创建 ====================

class MemoryNodeCreate(BaseModel):
    """创建记忆节点请求"""
    
    graph_id: UUID = Field(..., description="所属知识图谱ID")
    node_type: str = Field(..., description="节点类型: QUESTION, CONCEPT, SNIPPET, INSIGHT")
    title: str = Field(..., min_length=1, max_length=200, description="节点标题")
    summary: Optional[str] = Field(None, description="节点摘要")
    content_data: dict[str, Any] = Field(default_factory=dict, description="节点内容数据（JSONB）")
    position_x: Optional[float] = Field(0.0, description="X坐标")
    position_y: Optional[float] = Field(0.0, description="Y坐标")
    position_z: Optional[float] = Field(0.0, description="Z坐标")


# ==================== 记忆节点更新 ====================

class MemoryNodeUpdate(BaseModel):
    """更新记忆节点请求"""
    
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="节点标题")
    summary: Optional[str] = Field(None, description="节点摘要")
    content_data: Optional[dict[str, Any]] = Field(None, description="节点内容数据（JSONB）")
    node_type: Optional[str] = Field(None, description="节点类型")
    position_x: Optional[float] = Field(None, description="X坐标")
    position_y: Optional[float] = Field(None, description="Y坐标")
    position_z: Optional[float] = Field(None, description="Z坐标")


# ==================== 记忆节点响应 ====================

class MemoryNodeBase(BaseModel):
    """记忆节点基础信息"""
    
    id: UUID
    graph_id: UUID
    node_type: str
    title: str
    summary: Optional[str] = None
    content_data: dict[str, Any]
    position_x: float
    position_y: float
    position_z: float
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class MemoryNodeResponse(MemoryNodeBase):
    """记忆节点响应"""
    
    pass


class MemoryNodeDetailResponse(MemoryNodeBase):
    """记忆节点详细信息响应"""
    
    created_by: Optional[UUID] = None
    review_stats: dict[str, Any]
    
    model_config = {"from_attributes": True}


# ==================== 记忆节点列表 ====================

class MemoryNodeListItem(BaseModel):
    """记忆节点列表项"""
    
    id: UUID
    graph_id: UUID
    node_type: str
    title: str
    summary: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


# ==================== 节点关联 ====================

class NodeRelationCreate(BaseModel):
    """创建节点关联请求"""
    
    source_node_id: UUID = Field(..., description="源节点ID")
    target_node_id: UUID = Field(..., description="目标节点ID")
    relation_type: str = Field(..., description="关联类型: PREREQUISITE, VARIANT, RELATED")
    strength: Optional[int] = Field(50, ge=0, le=100, description="关联强度 0-100")
    is_auto_generated: Optional[bool] = Field(False, description="是否自动生成")


class NodeRelationResponse(BaseModel):
    """节点关联响应"""
    
    id: UUID
    source_id: UUID
    target_id: UUID
    relation_type: str
    strength: int
    is_auto_generated: bool
    created_at: datetime
    
    model_config = {"from_attributes": True}


# ==================== 节点标签 ====================

class KnowledgeTagCreate(BaseModel):
    """创建知识标签请求"""
    
    name: str = Field(..., min_length=1, max_length=100, description="标签名称")
    category: Optional[str] = Field(None, max_length=50, description="标签分类")
    color: Optional[str] = Field("#1890ff", max_length=20, description="标签颜色")


class KnowledgeTagResponse(BaseModel):
    """知识标签响应"""
    
    id: UUID
    name: str
    category: Optional[str] = None
    color: str
    usage_count: int
    created_at: datetime
    
    model_config = {"from_attributes": True}


class NodeTagAssign(BaseModel):
    """节点标签分配请求"""
    
    node_id: UUID = Field(..., description="节点ID")
    tag_id: UUID = Field(..., description="标签ID")


# ==================== 复习相关 ====================

class ReviewLogCreate(BaseModel):
    """创建复习记录请求"""
    
    node_id: UUID = Field(..., description="节点ID")
    quality: int = Field(..., ge=0, le=5, description="复习质量评分 0-5")
    time_spent: Optional[int] = Field(None, ge=0, description="复习耗时（秒）")


class ReviewLogResponse(BaseModel):
    """复习记录响应"""
    
    id: UUID
    node_id: UUID
    quality: int
    time_spent: Optional[int] = None
    reviewed_at: datetime
    next_review_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}

