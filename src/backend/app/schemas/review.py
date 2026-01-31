"""
复习相关的 Pydantic Schemas
"""

from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel, Field


class ReviewRequest(BaseModel):
    """复习请求"""
    quality: int = Field(..., ge=0, le=5, description="复习质量评分 (0-5)")
    review_duration: int = Field(..., ge=0, description="复习时长（秒）")


class ReviewResponse(BaseModel):
    """复习响应"""
    node_id: str
    mastery_level: str
    next_review_at: str
    interval_days: int
    easiness: float
    repetitions: int


class ReviewQueueRequest(BaseModel):
    """复习队列请求"""
    graph_id: Optional[str] = Field(None, description="知识图谱 ID（可选）")
    mode: str = Field("spaced", description="复习模式：spaced, focused, random, graph_traversal")
    limit: int = Field(20, ge=1, le=100, description="返回数量限制")


class ReviewNodeInfo(BaseModel):
    """复习队列中的节点信息"""
    node_id: str
    title: str
    node_type: str
    mastery_level: str
    last_review_at: Optional[str]
    next_review_at: Optional[str]
    forgetting_index: float
    forgetting_color: str
    review_stats: Dict


class ReviewQueueResponse(BaseModel):
    """复习队列响应"""
    total: int
    nodes: list[ReviewNodeInfo]


class ReviewStatistics(BaseModel):
    """复习统计信息"""
    total_nodes: int
    mastery_distribution: Dict[str, int]
    mastery_rate: float
    due_today: int
    overdue: int
    total_reviews: int

