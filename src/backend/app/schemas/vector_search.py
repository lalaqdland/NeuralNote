"""
向量搜索相关的 Pydantic Schemas
"""

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class VectorSearchRequest(BaseModel):
    """向量搜索请求"""
    
    query_text: str = Field(..., description="查询文本", min_length=1, max_length=1000)
    graph_id: Optional[UUID] = Field(None, description="限制在特定知识图谱")
    node_type: Optional[str] = Field(None, description="限制节点类型")
    limit: int = Field(10, description="返回结果数量", ge=1, le=50)
    similarity_threshold: float = Field(0.7, description="相似度阈值", ge=0.0, le=1.0)


class SimilarNodeRequest(BaseModel):
    """相似节点查询请求"""
    
    node_id: UUID = Field(..., description="参考节点ID")
    graph_id: Optional[UUID] = Field(None, description="限制在特定知识图谱")
    node_type: Optional[str] = Field(None, description="限制节点类型")
    limit: int = Field(10, description="返回结果数量", ge=1, le=50)
    similarity_threshold: float = Field(0.7, description="相似度阈值", ge=0.0, le=1.0)


class NodeRecommendationRequest(BaseModel):
    """节点推荐请求"""
    
    node_id: UUID = Field(..., description="节点ID")
    limit: int = Field(5, description="推荐数量", ge=1, le=20)


class SimilarNodeResult(BaseModel):
    """相似节点结果"""
    
    node_id: UUID = Field(..., description="节点ID")
    title: str = Field(..., description="节点标题")
    node_type: str = Field(..., description="节点类型")
    summary: Optional[str] = Field(None, description="节点摘要")
    similarity_score: float = Field(..., description="相似度分数", ge=0.0, le=1.0)
    graph_id: UUID = Field(..., description="所属知识图谱ID")
    
    class Config:
        from_attributes = True


class VectorSearchResponse(BaseModel):
    """向量搜索响应"""
    
    query_text: str = Field(..., description="查询文本")
    total: int = Field(..., description="结果总数")
    results: List[SimilarNodeResult] = Field(..., description="搜索结果列表")


class NodeClusterResult(BaseModel):
    """节点聚类结果"""
    
    cluster_id: int = Field(..., description="簇ID")
    node_ids: List[UUID] = Field(..., description="节点ID列表")
    size: int = Field(..., description="簇大小")


class ClusterResponse(BaseModel):
    """聚类响应"""
    
    graph_id: UUID = Field(..., description="知识图谱ID")
    total_clusters: int = Field(..., description="簇总数")
    clusters: List[NodeClusterResult] = Field(..., description="聚类结果")


class EmbeddingUpdateRequest(BaseModel):
    """向量嵌入更新请求"""
    
    node_id: Optional[UUID] = Field(None, description="节点ID（单个更新）")
    graph_id: Optional[UUID] = Field(None, description="知识图谱ID（批量更新）")


class EmbeddingUpdateResponse(BaseModel):
    """向量嵌入更新响应"""
    
    success: bool = Field(..., description="是否成功")
    updated_count: int = Field(..., description="更新的节点数量")
    message: str = Field(..., description="响应消息")

