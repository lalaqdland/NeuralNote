"""
成就系统 API 端点
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.services.achievement_service import AchievementService

router = APIRouter()


@router.get("/stats")
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取用户统计数据
    
    返回：
    - total_nodes: 总节点数
    - mastered_nodes: 已掌握节点数
    - total_reviews: 总复习次数
    - total_graphs: 知识图谱数
    - current_streak: 连续学习天数
    - night_reviews: 深夜复习次数
    - morning_reviews: 清晨复习次数
    - perfect_week: 是否完美一周
    """
    service = AchievementService(db)
    stats = await service.get_user_stats(current_user.id)
    
    return {
        "code": 200,
        "message": "获取统计数据成功",
        "data": stats
    }


@router.get("/level")
async def get_user_level(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取用户等级信息
    
    返回：
    - level: 当前等级
    - total_exp: 总经验值
    - current_level_exp: 当前等级起始经验
    - next_level_exp: 下一等级所需经验
    - exp_in_level: 当前等级内的经验
    - exp_to_next: 距离下一等级的经验
    - progress: 当前等级进度（百分比）
    """
    service = AchievementService(db)
    level_info = await service.calculate_level_and_exp(current_user.id)
    
    return {
        "code": 200,
        "message": "获取等级信息成功",
        "data": level_info
    }


@router.get("/achievements")
async def get_user_achievements(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取用户成就列表
    
    返回：
    - unlocked: 已解锁的成就列表
    - locked: 未解锁的成就列表
    - total: 总成就数
    - unlocked_count: 已解锁数量
    - progress: 成就完成度（百分比）
    """
    service = AchievementService(db)
    achievements = await service.get_achievements(current_user.id)
    
    return {
        "code": 200,
        "message": "获取成就列表成功",
        "data": achievements
    }


@router.get("/profile")
async def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取用户完整档案
    
    包含：统计数据 + 等级信息 + 成就列表
    """
    service = AchievementService(db)
    profile = await service.get_user_profile(current_user.id)
    
    return {
        "code": 200,
        "message": "获取用户档案成功",
        "data": profile
    }

