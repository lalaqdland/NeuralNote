"""
知识图谱相关的 API 端点
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.knowledge_graph import KnowledgeGraph
from app.models.memory_node import MemoryNode
from app.models.node_relation import NodeRelation
from app.models.user import User
from app.schemas.common import PaginatedResponse
from app.schemas.knowledge_graph import (
    KnowledgeGraphCreate,
    KnowledgeGraphDetailResponse,
    KnowledgeGraphListItem,
    KnowledgeGraphResponse,
    KnowledgeGraphStats,
    KnowledgeGraphUpdate,
)

router = APIRouter()


@router.post("/", response_model=KnowledgeGraphResponse, status_code=status.HTTP_201_CREATED)
async def create_knowledge_graph(
    graph_data: KnowledgeGraphCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    创建知识图谱
    
    - **name**: 图谱名称（必填）
    - **description**: 图谱描述（可选）
    - **subject**: 学科分类（可选）
    - **cover_image_url**: 封面图片URL（可选）
    - **is_public**: 是否公开（可选，默认 false）
    """
    try:
        # 创建新图谱
        new_graph = KnowledgeGraph(
            user_id=current_user.id,
            name=graph_data.name,
            description=graph_data.description,
            subject=graph_data.subject,
            cover_image_url=graph_data.cover_image_url,
            is_public=graph_data.is_public or False,
            node_count=0,
            edge_count=0,
            total_review_count=0,
        )
        
        db.add(new_graph)
        await db.commit()
        await db.refresh(new_graph)
        
        return new_graph
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建知识图谱失败: {str(e)}"
        )


@router.get("/", response_model=PaginatedResponse[KnowledgeGraphListItem])
async def list_knowledge_graphs(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    include_archived: bool = Query(False, description="是否包含已归档的图谱"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取知识图谱列表（分页）
    
    - **page**: 页码（默认 1）
    - **page_size**: 每页数量（默认 20，最大 100）
    - **include_archived**: 是否包含已归档的图谱（默认 false）
    """
    try:
        # 构建查询
        query = select(KnowledgeGraph).where(
            KnowledgeGraph.user_id == current_user.id
        )
        
        # 不显示预设图谱（除非是自己的）
        # query = query.where(KnowledgeGraph.is_preset == False)
        
        # 按更新时间倒序排列
        query = query.order_by(KnowledgeGraph.updated_at.desc())
        
        # 获取总数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # 分页查询
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        result = await db.execute(query)
        graphs = result.scalars().all()
        
        return PaginatedResponse.create(
            items=graphs,
            total=total,
            page=page,
            page_size=page_size
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取知识图谱列表失败: {str(e)}"
        )


@router.get("/{graph_id}", response_model=KnowledgeGraphDetailResponse)
async def get_knowledge_graph(
    graph_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取知识图谱详情
    
    - **graph_id**: 图谱ID
    """
    # 查询图谱
    result = await db.execute(
        select(KnowledgeGraph).where(
            KnowledgeGraph.id == graph_id,
            KnowledgeGraph.user_id == current_user.id
        )
    )
    graph = result.scalar_one_or_none()
    
    if graph is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="知识图谱不存在"
        )
    
    return graph


@router.put("/{graph_id}", response_model=KnowledgeGraphResponse)
async def update_knowledge_graph(
    graph_id: UUID,
    graph_data: KnowledgeGraphUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    更新知识图谱
    
    - **graph_id**: 图谱ID
    - **name**: 图谱名称（可选）
    - **description**: 图谱描述（可选）
    - **subject**: 学科分类（可选）
    - **cover_image_url**: 封面图片URL（可选）
    - **is_public**: 是否公开（可选）
    """
    try:
        # 查询图谱
        result = await db.execute(
            select(KnowledgeGraph).where(
                KnowledgeGraph.id == graph_id,
                KnowledgeGraph.user_id == current_user.id
            )
        )
        graph = result.scalar_one_or_none()
        
        if graph is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="知识图谱不存在"
            )
        
        # 更新字段
        update_data = graph_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(graph, field, value)
        
        await db.commit()
        await db.refresh(graph)
        
        return graph
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新知识图谱失败: {str(e)}"
        )


@router.delete("/{graph_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_knowledge_graph(
    graph_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    删除知识图谱
    
    - **graph_id**: 图谱ID
    
    注意：删除图谱会级联删除所有相关的节点、关联和复习记录
    """
    try:
        # 查询图谱
        result = await db.execute(
            select(KnowledgeGraph).where(
                KnowledgeGraph.id == graph_id,
                KnowledgeGraph.user_id == current_user.id
            )
        )
        graph = result.scalar_one_or_none()
        
        if graph is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="知识图谱不存在"
            )
        
        # 删除图谱（级联删除相关数据）
        await db.delete(graph)
        await db.commit()
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除知识图谱失败: {str(e)}"
        )


@router.get("/{graph_id}/stats", response_model=KnowledgeGraphStats)
async def get_knowledge_graph_stats(
    graph_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取知识图谱统计信息
    
    - **graph_id**: 图谱ID
    
    返回节点数、关联数、标签数等统计信息
    """
    try:
        # 验证图谱所有权
        result = await db.execute(
            select(KnowledgeGraph).where(
                KnowledgeGraph.id == graph_id,
                KnowledgeGraph.user_id == current_user.id
            )
        )
        graph = result.scalar_one_or_none()
        
        if graph is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="知识图谱不存在"
            )
        
        # 统计节点数
        nodes_count_result = await db.execute(
            select(func.count()).select_from(MemoryNode).where(
                MemoryNode.graph_id == graph_id
            )
        )
        total_nodes = nodes_count_result.scalar()
        
        # 统计关联数
        relations_count_result = await db.execute(
            select(func.count()).select_from(NodeRelation).where(
                NodeRelation.graph_id == graph_id
            )
        )
        total_relations = relations_count_result.scalar()
        
        # 统计标签数（通过节点标签关联）
        from app.models.node_tag import NodeTag
        tags_count_result = await db.execute(
            select(func.count(func.distinct(NodeTag.tag_id)))
            .select_from(NodeTag)
            .join(MemoryNode, MemoryNode.id == NodeTag.node_id)
            .where(MemoryNode.graph_id == graph_id)
        )
        total_tags = tags_count_result.scalar() or 0
        
        # TODO: 统计待复习节点数（需要实现复习算法）
        review_due_count = 0
        
        # TODO: 获取最后复习时间
        last_review_at = None
        
        return KnowledgeGraphStats(
            total_nodes=total_nodes,
            total_relations=total_relations,
            total_tags=total_tags,
            review_due_count=review_due_count,
            last_review_at=last_review_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取统计信息失败: {str(e)}"
        )

