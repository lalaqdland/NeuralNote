"""
记忆节点相关的 API 端点
"""

from typing import List, Optional
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
from app.schemas.memory_node import (
    MemoryNodeCreate,
    MemoryNodeDetailResponse,
    MemoryNodeListItem,
    MemoryNodeResponse,
    MemoryNodeUpdate,
    NodeRelationCreate,
    NodeRelationResponse,
)

router = APIRouter()


@router.post("/", response_model=MemoryNodeResponse, status_code=status.HTTP_201_CREATED)
async def create_memory_node(
    node_data: MemoryNodeCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    创建记忆节点
    
    - **graph_id**: 所属知识图谱ID（必填）
    - **node_type**: 节点类型（必填）：QUESTION, CONCEPT, SNIPPET, INSIGHT
    - **title**: 节点标题（必填）
    - **summary**: 节点摘要（可选）
    - **content_data**: 节点内容数据（可选，JSONB格式）
    - **position_x**: X坐标（可选，默认0.0）
    - **position_y**: Y坐标（可选，默认0.0）
    - **position_z**: Z坐标（可选，默认0.0）
    """
    try:
        # 验证图谱所有权
        result = await db.execute(
            select(KnowledgeGraph).where(
                KnowledgeGraph.id == node_data.graph_id,
                KnowledgeGraph.user_id == current_user.id
            )
        )
        graph = result.scalar_one_or_none()
        
        if graph is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="知识图谱不存在"
            )
        
        # 验证父节点（如果提供）
        # if node_data.parent_node_id:
        #     parent_result = await db.execute(
        #         select(MemoryNode).where(
        #             MemoryNode.id == node_data.parent_node_id,
        #             MemoryNode.graph_id == node_data.graph_id
        #         )
        #     )
        #     if parent_result.scalar_one_or_none() is None:
        #         raise HTTPException(
        #             status_code=status.HTTP_404_NOT_FOUND,
        #             detail="父节点不存在"
        #         )
        
        # 创建新节点
        new_node = MemoryNode(
            graph_id=node_data.graph_id,
            user_id=current_user.id,
            created_by=current_user.id,
            node_type=node_data.node_type,
            title=node_data.title,
            summary=node_data.summary,
            content_data=node_data.content_data,
            position_x=node_data.position_x,
            position_y=node_data.position_y,
            position_z=node_data.position_z,
        )
        
        db.add(new_node)
        
        # 更新图谱节点计数
        graph.node_count += 1
        
        await db.commit()
        await db.refresh(new_node)
        
        return new_node
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建记忆节点失败: {str(e)}"
        )


@router.get("/", response_model=PaginatedResponse[MemoryNodeListItem])
async def list_memory_nodes(
    graph_id: Optional[UUID] = Query(None, description="知识图谱ID"),
    node_type: Optional[str] = Query(None, description="节点类型"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取记忆节点列表（分页）
    
    - **graph_id**: 知识图谱ID（可选，不提供则返回所有图谱的节点）
    - **node_type**: 节点类型过滤（可选）
    - **page**: 页码（默认 1）
    - **page_size**: 每页数量（默认 20，最大 100）
    """
    try:
        # 构建查询
        query = select(MemoryNode).join(
            KnowledgeGraph, MemoryNode.graph_id == KnowledgeGraph.id
        ).where(
            KnowledgeGraph.user_id == current_user.id
        )
        
        # 按图谱过滤
        if graph_id:
            query = query.where(MemoryNode.graph_id == graph_id)
        
        # 按节点类型过滤
        if node_type:
            query = query.where(MemoryNode.node_type == node_type)
        
        # 按更新时间倒序排列
        query = query.order_by(MemoryNode.updated_at.desc())
        
        # 获取总数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # 分页查询
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        result = await db.execute(query)
        nodes = result.scalars().all()
        
        return PaginatedResponse.create(
            items=nodes,
            total=total,
            page=page,
            page_size=page_size
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取记忆节点列表失败: {str(e)}"
        )


@router.get("/{node_id}", response_model=MemoryNodeDetailResponse)
async def get_memory_node(
    node_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取记忆节点详情
    
    - **node_id**: 节点ID
    """
    # 查询节点
    result = await db.execute(
        select(MemoryNode).join(
            KnowledgeGraph, MemoryNode.graph_id == KnowledgeGraph.id
        ).where(
            MemoryNode.id == node_id,
            KnowledgeGraph.user_id == current_user.id
        )
    )
    node = result.scalar_one_or_none()
    
    if node is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="记忆节点不存在"
        )
    
    return node


@router.put("/{node_id}", response_model=MemoryNodeResponse)
async def update_memory_node(
    node_id: UUID,
    node_data: MemoryNodeUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    更新记忆节点
    
    - **node_id**: 节点ID
    - **title**: 节点标题（可选）
    - **summary**: 节点摘要（可选）
    - **content_data**: 节点内容数据（可选）
    - **node_type**: 节点类型（可选）
    - **position_x/y/z**: 坐标（可选）
    """
    try:
        # 查询节点
        result = await db.execute(
            select(MemoryNode).join(
                KnowledgeGraph, MemoryNode.graph_id == KnowledgeGraph.id
            ).where(
                MemoryNode.id == node_id,
                KnowledgeGraph.user_id == current_user.id
            )
        )
        node = result.scalar_one_or_none()
        
        if node is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="记忆节点不存在"
            )
        
        # 验证父节点（如果提供）
        # if node_data.parent_node_id:
        #     parent_result = await db.execute(
        #         select(MemoryNode).where(
        #             MemoryNode.id == node_data.parent_node_id,
        #             MemoryNode.graph_id == node.graph_id
        #         )
        #     )
        #     if parent_result.scalar_one_or_none() is None:
        #         raise HTTPException(
        #             status_code=status.HTTP_404_NOT_FOUND,
        #             detail="父节点不存在"
        #         )
        
        # 更新字段
        update_data = node_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(node, field, value)
        
        await db.commit()
        await db.refresh(node)
        
        return node
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新记忆节点失败: {str(e)}"
        )


@router.delete("/{node_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_memory_node(
    node_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    删除记忆节点
    
    - **node_id**: 节点ID
    
    注意：删除节点会级联删除所有相关的关联和复习记录
    """
    try:
        # 查询节点
        result = await db.execute(
            select(MemoryNode).join(
                KnowledgeGraph, MemoryNode.graph_id == KnowledgeGraph.id
            ).where(
                MemoryNode.id == node_id,
                KnowledgeGraph.user_id == current_user.id
            )
        )
        node = result.scalar_one_or_none()
        
        if node is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="记忆节点不存在"
            )
        
        # 获取图谱ID用于更新计数
        graph_id = node.graph_id
        
        # 删除节点（级联删除相关数据）
        await db.delete(node)
        
        # 更新图谱节点计数
        graph_result = await db.execute(
            select(KnowledgeGraph).where(KnowledgeGraph.id == graph_id)
        )
        graph = graph_result.scalar_one_or_none()
        if graph:
            graph.node_count = max(0, graph.node_count - 1)
        
        await db.commit()
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除记忆节点失败: {str(e)}"
        )


# ==================== 节点关联相关接口 ====================

@router.post("/{node_id}/relations", response_model=NodeRelationResponse, status_code=status.HTTP_201_CREATED)
async def create_node_relation(
    node_id: UUID,
    relation_data: NodeRelationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    创建节点关联
    
    - **node_id**: 源节点ID（路径参数）
    - **source_node_id**: 源节点ID（请求体，应与路径参数一致）
    - **target_node_id**: 目标节点ID
    - **relation_type**: 关联类型：PREREQUISITE, VARIANT, RELATED
    - **strength**: 关联强度（0-100，默认 50）
    - **is_auto_generated**: 是否自动生成（默认 false）
    """
    try:
        # 验证路径参数与请求体一致
        if node_id != relation_data.source_node_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="路径参数中的节点ID与请求体不一致"
            )
        
        # 验证源节点
        source_result = await db.execute(
            select(MemoryNode).join(
                KnowledgeGraph, MemoryNode.graph_id == KnowledgeGraph.id
            ).where(
                MemoryNode.id == relation_data.source_node_id,
                KnowledgeGraph.user_id == current_user.id
            )
        )
        source_node = source_result.scalar_one_or_none()
        
        if source_node is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="源节点不存在"
            )
        
        # 验证目标节点
        target_result = await db.execute(
            select(MemoryNode).join(
                KnowledgeGraph, MemoryNode.graph_id == KnowledgeGraph.id
            ).where(
                MemoryNode.id == relation_data.target_node_id,
                KnowledgeGraph.user_id == current_user.id
            )
        )
        target_node = target_result.scalar_one_or_none()
        
        if target_node is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="目标节点不存在"
            )
        
        # 检查是否已存在相同的关联
        existing_result = await db.execute(
            select(NodeRelation).where(
                NodeRelation.source_id == relation_data.source_node_id,
                NodeRelation.target_id == relation_data.target_node_id,
                NodeRelation.relation_type == relation_data.relation_type
            )
        )
        if existing_result.scalar_one_or_none() is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该关联已存在"
            )
        
        # 创建新关联
        new_relation = NodeRelation(
            graph_id=source_node.graph_id,
            source_id=relation_data.source_node_id,
            target_id=relation_data.target_node_id,
            relation_type=relation_data.relation_type,
            strength=relation_data.strength,
            is_auto_generated=relation_data.is_auto_generated,
            created_by=current_user.id,
        )
        
        db.add(new_relation)
        await db.commit()
        await db.refresh(new_relation)
        
        return new_relation
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建节点关联失败: {str(e)}"
        )


@router.get("/{node_id}/relations", response_model=List[NodeRelationResponse])
async def get_node_relations(
    node_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取节点的所有关联
    
    - **node_id**: 节点ID
    
    返回该节点作为源节点或目标节点的所有关联
    """
    try:
        # 验证节点所有权
        node_result = await db.execute(
            select(MemoryNode).join(
                KnowledgeGraph, MemoryNode.graph_id == KnowledgeGraph.id
            ).where(
                MemoryNode.id == node_id,
                KnowledgeGraph.user_id == current_user.id
            )
        )
        node = node_result.scalar_one_or_none()
        
        if node is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="节点不存在"
            )
        
        # 查询所有相关的关联
        result = await db.execute(
            select(NodeRelation).where(
                (NodeRelation.source_id == node_id) |
                (NodeRelation.target_id == node_id)
            ).order_by(NodeRelation.created_at.desc())
        )
        relations = result.scalars().all()
        
        return relations
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取节点关联失败: {str(e)}"
        )


@router.delete("/relations/{relation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_node_relation(
    relation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    删除节点关联
    
    - **relation_id**: 关联ID
    """
    try:
        # 查询关联
        result = await db.execute(
            select(NodeRelation).join(
                KnowledgeGraph, NodeRelation.graph_id == KnowledgeGraph.id
            ).where(
                NodeRelation.id == relation_id,
                KnowledgeGraph.user_id == current_user.id
            )
        )
        relation = result.scalar_one_or_none()
        
        if relation is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="节点关联不存在"
            )
        
        # 删除关联
        await db.delete(relation)
        await db.commit()
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除节点关联失败: {str(e)}"
        )

