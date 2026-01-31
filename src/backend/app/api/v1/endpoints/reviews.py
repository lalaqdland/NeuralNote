"""
复习管理 API 端点
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.review import (
    ReviewRequest,
    ReviewResponse,
    ReviewQueueRequest,
    ReviewQueueResponse,
    ReviewStatistics,
    ReviewNodeInfo
)
from app.services.review_service import ReviewService, ReviewMode

router = APIRouter()


@router.post("/{node_id}", response_model=ReviewResponse)
async def submit_review(
    node_id: str,
    review_data: ReviewRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    提交复习记录
    
    - **node_id**: 节点 ID
    - **quality**: 复习质量评分 (0-5)
      - 0: 完全不记得
      - 1: 错误，但有印象
      - 2: 困难，勉强记起
      - 3: 犹豫，但最终正确
      - 4: 容易，有些犹豫
      - 5: 完美，立即回忆
    - **review_duration**: 复习时长（秒）
    """
    try:
        result = await ReviewService.update_review_stats(
            db=db,
            node_id=node_id,
            quality=review_data.quality,
            review_duration=review_data.review_duration
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"提交复习记录失败: {str(e)}")


@router.get("/queue", response_model=ReviewQueueResponse)
async def get_review_queue(
    graph_id: Optional[str] = Query(None, description="知识图谱 ID（可选）"),
    mode: str = Query("spaced", description="复习模式：spaced, focused, random, graph_traversal"),
    limit: int = Query(20, ge=1, le=100, description="返回数量限制"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取复习队列
    
    **复习模式说明**：
    - **spaced**: 间隔重复模式（基于遗忘曲线，推荐）
    - **focused**: 集中攻克模式（针对薄弱知识点）
    - **random**: 随机抽查模式
    - **graph_traversal**: 图谱遍历模式（按创建时间顺序）
    """
    try:
        # 验证复习模式
        try:
            review_mode = ReviewMode(mode)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的复习模式: {mode}。支持的模式: spaced, focused, random, graph_traversal"
            )
        
        # 获取复习队列
        nodes = await ReviewService.get_review_queue(
            db=db,
            user_id=str(current_user.id),
            graph_id=graph_id,
            mode=review_mode,
            limit=limit
        )
        
        return {
            "total": len(nodes),
            "nodes": nodes
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取复习队列失败: {str(e)}")


@router.get("/statistics", response_model=ReviewStatistics)
async def get_review_statistics(
    graph_id: Optional[str] = Query(None, description="知识图谱 ID（可选）"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取复习统计信息
    
    返回用户的复习统计数据，包括：
    - 总节点数
    - 掌握程度分布
    - 掌握率
    - 今日到期数量
    - 逾期数量
    - 总复习次数
    """
    try:
        stats = await ReviewService.get_review_statistics(
            db=db,
            user_id=str(current_user.id),
            graph_id=graph_id
        )
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取复习统计失败: {str(e)}")


@router.get("/forgetting-index/{node_id}")
async def get_forgetting_index(
    node_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取节点的遗忘指数
    
    返回节点的遗忘指数和对应的颜色标注：
    - 0.0-0.2: 绿色 - 记忆牢固
    - 0.2-0.4: 浅绿色 - 记忆良好
    - 0.4-0.6: 黄色 - 需要复习
    - 0.6-0.8: 橙色 - 急需复习
    - 0.8-1.0: 红色 - 即将遗忘
    """
    from sqlalchemy import select
    from app.models.memory_node import MemoryNode
    
    try:
        # 查询节点
        result = await db.execute(
            select(MemoryNode).where(MemoryNode.id == node_id)
        )
        node = result.scalar_one_or_none()
        
        if not node:
            raise HTTPException(status_code=404, detail="节点不存在")
        
        # 验证权限
        if str(node.user_id) != str(current_user.id):
            raise HTTPException(status_code=403, detail="无权访问此节点")
        
        # 计算遗忘指数
        if node.last_review_at and node.next_review_at:
            # 转换 mastery_level 为枚举
            from app.models.memory_node import MasteryLevel
            try:
                if isinstance(node.mastery_level, str):
                    mastery_level_enum = MasteryLevel(node.mastery_level)
                else:
                    mastery_level_enum = node.mastery_level
            except (ValueError, AttributeError):
                mastery_level_enum = MasteryLevel.NOT_STARTED
            
            forgetting_index = ReviewService.calculate_forgetting_index(
                last_review_time=node.last_review_at,
                next_review_time=node.next_review_at,
                mastery_level=mastery_level_enum
            )
        else:
            forgetting_index = 0.8  # 未复习过的节点
        
        return {
            "node_id": str(node.id),
            "forgetting_index": forgetting_index,
            "forgetting_color": ReviewService.get_forgetting_color(forgetting_index),
            "last_review_at": node.last_review_at.isoformat() if node.last_review_at else None,
            "next_review_at": node.next_review_at.isoformat() if node.next_review_at else None,
            "mastery_level": node.mastery_level if isinstance(node.mastery_level, str) else node.mastery_level.value
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取遗忘指数失败: {str(e)}")

