"""
向量搜索 API 端点
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.vector_search import (
    VectorSearchRequest,
    VectorSearchResponse,
    SimilarNodeRequest,
    SimilarNodeResult,
    NodeRecommendationRequest,
    ClusterResponse,
    NodeClusterResult,
    EmbeddingUpdateRequest,
    EmbeddingUpdateResponse,
)
from app.services.vector_search_service import vector_search_service


router = APIRouter()


@router.post("/search", response_model=VectorSearchResponse)
async def search_similar_nodes(
    request: VectorSearchRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    基于文本查询搜索相似节点
    
    - **query_text**: 查询文本
    - **graph_id**: 限制在特定知识图谱（可选）
    - **node_type**: 限制节点类型（可选）
    - **limit**: 返回结果数量（1-50）
    - **similarity_threshold**: 相似度阈值（0-1）
    """
    try:
        results = await vector_search_service.search_similar_nodes(
            db=db,
            query_text=request.query_text,
            graph_id=request.graph_id,
            node_type=request.node_type,
            limit=request.limit,
            similarity_threshold=request.similarity_threshold,
        )
        
        # 转换为响应格式
        similar_nodes = [
            SimilarNodeResult(
                node_id=node.id,
                title=node.title,
                node_type=node.node_type,
                summary=node.summary,
                similarity_score=round(score, 4),
                graph_id=node.graph_id,
            )
            for node, score in results
        ]
        
        return VectorSearchResponse(
            query_text=request.query_text,
            total=len(similar_nodes),
            results=similar_nodes,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


@router.get("/similar/{node_id}", response_model=List[SimilarNodeResult])
async def find_similar_nodes(
    node_id: UUID,
    graph_id: UUID = Query(None, description="限制在特定知识图谱"),
    node_type: str = Query(None, description="限制节点类型"),
    limit: int = Query(10, ge=1, le=50, description="返回结果数量"),
    similarity_threshold: float = Query(0.7, ge=0.0, le=1.0, description="相似度阈值"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    查找与指定节点相似的其他节点
    
    - **node_id**: 参考节点ID
    - **graph_id**: 限制在特定知识图谱（可选）
    - **node_type**: 限制节点类型（可选）
    - **limit**: 返回结果数量（1-50）
    - **similarity_threshold**: 相似度阈值（0-1）
    """
    try:
        results = await vector_search_service.find_similar_nodes_by_id(
            db=db,
            node_id=node_id,
            graph_id=graph_id,
            node_type=node_type,
            limit=limit,
            similarity_threshold=similarity_threshold,
        )
        
        return [
            SimilarNodeResult(
                node_id=node.id,
                title=node.title,
                node_type=node.node_type,
                summary=node.summary,
                similarity_score=round(score, 4),
                graph_id=node.graph_id,
            )
            for node, score in results
        ]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查找相似节点失败: {str(e)}")


@router.get("/recommend/{node_id}", response_model=List[SimilarNodeResult])
async def recommend_related_nodes(
    node_id: UUID,
    limit: int = Query(5, ge=1, le=20, description="推荐数量"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    为指定节点推荐相关节点（用于学习路径推荐）
    
    - **node_id**: 节点ID
    - **limit**: 推荐数量（1-20）
    """
    try:
        results = await vector_search_service.recommend_related_nodes(
            db=db,
            node_id=node_id,
            limit=limit,
        )
        
        return [
            SimilarNodeResult(
                node_id=node.id,
                title=node.title,
                node_type=node.node_type,
                summary=node.summary,
                similarity_score=round(score, 4),
                graph_id=node.graph_id,
            )
            for node, score in results
        ]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"推荐节点失败: {str(e)}")


@router.get("/cluster/{graph_id}", response_model=ClusterResponse)
async def cluster_nodes(
    graph_id: UUID,
    similarity_threshold: float = Query(0.8, ge=0.0, le=1.0, description="相似度阈值"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    基于相似度对知识图谱中的节点进行聚类
    
    - **graph_id**: 知识图谱ID
    - **similarity_threshold**: 相似度阈值（0-1）
    """
    try:
        clusters = await vector_search_service.cluster_nodes_by_similarity(
            db=db,
            graph_id=graph_id,
            similarity_threshold=similarity_threshold,
        )
        
        cluster_results = [
            NodeClusterResult(
                cluster_id=idx,
                node_ids=cluster,
                size=len(cluster),
            )
            for idx, cluster in enumerate(clusters)
        ]
        
        return ClusterResponse(
            graph_id=graph_id,
            total_clusters=len(cluster_results),
            clusters=cluster_results,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"聚类失败: {str(e)}")


@router.post("/update-embedding", response_model=EmbeddingUpdateResponse)
async def update_node_embedding(
    request: EmbeddingUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    更新节点的向量嵌入
    
    - **node_id**: 单个节点ID（单个更新）
    - **graph_id**: 知识图谱ID（批量更新该图谱中所有未生成向量的节点）
    
    注意：至少提供 node_id 或 graph_id 之一
    """
    try:
        if request.node_id:
            # 单个节点更新
            await vector_search_service.update_node_embedding(
                db=db,
                node_id=request.node_id,
            )
            return EmbeddingUpdateResponse(
                success=True,
                updated_count=1,
                message=f"成功更新节点 {request.node_id} 的向量嵌入",
            )
        elif request.graph_id:
            # 批量更新
            updated_count = await vector_search_service.batch_update_embeddings(
                db=db,
                graph_id=request.graph_id,
            )
            return EmbeddingUpdateResponse(
                success=True,
                updated_count=updated_count,
                message=f"成功更新 {updated_count} 个节点的向量嵌入",
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="必须提供 node_id 或 graph_id 之一",
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新向量嵌入失败: {str(e)}")


@router.post("/batch-update-embedding", response_model=EmbeddingUpdateResponse)
async def batch_update_embeddings(
    graph_id: UUID = Query(None, description="知识图谱ID（可选，不提供则更新所有）"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    批量更新节点的向量嵌入
    
    - **graph_id**: 知识图谱ID（可选，不提供则更新所有未生成向量的节点）
    
    注意：此操作可能耗时较长，建议在后台任务中执行
    """
    try:
        updated_count = await vector_search_service.batch_update_embeddings(
            db=db,
            graph_id=graph_id,
        )
        
        message = f"成功更新 {updated_count} 个节点的向量嵌入"
        if graph_id:
            message += f"（知识图谱: {graph_id}）"
        
        return EmbeddingUpdateResponse(
            success=True,
            updated_count=updated_count,
            message=message,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量更新失败: {str(e)}")

