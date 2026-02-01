"""
学习成就系统服务

功能：
1. 计算用户等级和经验值
2. 检查和解锁成就徽章
3. 统计学习数据
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy import func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.memory_node import MemoryNode, MasteryLevel
from app.models.review_log import ReviewLog
from app.models.knowledge_graph import KnowledgeGraph


class AchievementService:
    """成就系统服务"""
    
    # 等级经验值配置（每级所需总经验）
    LEVEL_EXP = {
        1: 0,
        2: 100,
        3: 300,
        4: 600,
        5: 1000,
        6: 1500,
        7: 2100,
        8: 2800,
        9: 3600,
        10: 4500,
        11: 5500,
        12: 6600,
        13: 7800,
        14: 9100,
        15: 10500,
        16: 12000,
        17: 13600,
        18: 15300,
        19: 17100,
        20: 19000,
    }
    
    # 经验值获取规则
    EXP_RULES = {
        "create_node": 10,          # 创建节点
        "review_again": 5,          # 复习（重来）
        "review_hard": 10,          # 复习（困难）
        "review_good": 15,          # 复习（良好）
        "review_easy": 20,          # 复习（简单）
        "master_node": 50,          # 完全掌握节点
        "create_graph": 30,         # 创建知识图谱
        "continuous_days": 20,      # 连续学习（每天）
    }
    
    # 成就徽章定义
    ACHIEVEMENTS = {
        # 学习里程碑
        "first_node": {
            "id": "first_node",
            "name": "初学者",
            "description": "创建第一个记忆节点",
            "icon": "🌱",
            "category": "milestone",
            "condition": lambda stats: stats["total_nodes"] >= 1,
        },
        "node_10": {
            "id": "node_10",
            "name": "勤奋学习",
            "description": "创建10个记忆节点",
            "icon": "📚",
            "category": "milestone",
            "condition": lambda stats: stats["total_nodes"] >= 10,
        },
        "node_50": {
            "id": "node_50",
            "name": "知识探索者",
            "description": "创建50个记忆节点",
            "icon": "🔍",
            "category": "milestone",
            "condition": lambda stats: stats["total_nodes"] >= 50,
        },
        "node_100": {
            "id": "node_100",
            "name": "知识大师",
            "description": "创建100个记忆节点",
            "icon": "🎓",
            "category": "milestone",
            "condition": lambda stats: stats["total_nodes"] >= 100,
        },
        "node_500": {
            "id": "node_500",
            "name": "知识巨匠",
            "description": "创建500个记忆节点",
            "icon": "👑",
            "category": "milestone",
            "condition": lambda stats: stats["total_nodes"] >= 500,
        },
        
        # 复习成就
        "review_10": {
            "id": "review_10",
            "name": "复习新手",
            "description": "完成10次复习",
            "icon": "✏️",
            "category": "review",
            "condition": lambda stats: stats["total_reviews"] >= 10,
        },
        "review_50": {
            "id": "review_50",
            "name": "复习达人",
            "description": "完成50次复习",
            "icon": "📝",
            "category": "review",
            "condition": lambda stats: stats["total_reviews"] >= 50,
        },
        "review_100": {
            "id": "review_100",
            "name": "复习专家",
            "description": "完成100次复习",
            "icon": "🏆",
            "category": "review",
            "condition": lambda stats: stats["total_reviews"] >= 100,
        },
        
        # 掌握成就
        "master_10": {
            "id": "master_10",
            "name": "初窥门径",
            "description": "完全掌握10个节点",
            "icon": "⭐",
            "category": "mastery",
            "condition": lambda stats: stats["mastered_nodes"] >= 10,
        },
        "master_30": {
            "id": "master_30",
            "name": "融会贯通",
            "description": "完全掌握30个节点",
            "icon": "🌟",
            "category": "mastery",
            "condition": lambda stats: stats["mastered_nodes"] >= 30,
        },
        "master_50": {
            "id": "master_50",
            "name": "登峰造极",
            "description": "完全掌握50个节点",
            "icon": "💫",
            "category": "mastery",
            "condition": lambda stats: stats["mastered_nodes"] >= 50,
        },
        
        # 连续学习
        "streak_3": {
            "id": "streak_3",
            "name": "三日之功",
            "description": "连续学习3天",
            "icon": "🔥",
            "category": "streak",
            "condition": lambda stats: stats["current_streak"] >= 3,
        },
        "streak_7": {
            "id": "streak_7",
            "name": "一周坚持",
            "description": "连续学习7天",
            "icon": "🔥🔥",
            "category": "streak",
            "condition": lambda stats: stats["current_streak"] >= 7,
        },
        "streak_30": {
            "id": "streak_30",
            "name": "月度冠军",
            "description": "连续学习30天",
            "icon": "🔥🔥🔥",
            "category": "streak",
            "condition": lambda stats: stats["current_streak"] >= 30,
        },
        
        # 知识图谱
        "graph_3": {
            "id": "graph_3",
            "name": "图谱构建者",
            "description": "创建3个知识图谱",
            "icon": "🗺️",
            "category": "graph",
            "condition": lambda stats: stats["total_graphs"] >= 3,
        },
        "graph_10": {
            "id": "graph_10",
            "name": "知识架构师",
            "description": "创建10个知识图谱",
            "icon": "🏗️",
            "category": "graph",
            "condition": lambda stats: stats["total_graphs"] >= 10,
        },
        
        # 特殊成就
        "perfect_week": {
            "id": "perfect_week",
            "name": "完美一周",
            "description": "一周内每天都完成复习",
            "icon": "💯",
            "category": "special",
            "condition": lambda stats: stats.get("perfect_week", False),
        },
        "night_owl": {
            "id": "night_owl",
            "name": "夜猫子",
            "description": "在深夜（22:00-02:00）完成50次复习",
            "icon": "🦉",
            "category": "special",
            "condition": lambda stats: stats.get("night_reviews", 0) >= 50,
        },
        "early_bird": {
            "id": "early_bird",
            "name": "早起鸟",
            "description": "在清晨（05:00-08:00）完成50次复习",
            "icon": "🐦",
            "category": "special",
            "condition": lambda stats: stats.get("morning_reviews", 0) >= 50,
        },
    }
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_user_stats(self, user_id: int) -> Dict:
        """获取用户统计数据"""
        
        # 节点统计
        total_nodes = await self.db.scalar(
            func.count(MemoryNode.id).filter(MemoryNode.user_id == user_id)
        )
        
        mastered_nodes = await self.db.scalar(
            func.count(MemoryNode.id).filter(
                and_(
                    MemoryNode.user_id == user_id,
                    MemoryNode.mastery_level == MasteryLevel.MASTERED
                )
            )
        )
        
        # 复习统计
        total_reviews = await self.db.scalar(
            func.count(ReviewLog.id).filter(ReviewLog.user_id == user_id)
        )
        
        # 知识图谱统计
        total_graphs = await self.db.scalar(
            func.count(KnowledgeGraph.id).filter(KnowledgeGraph.user_id == user_id)
        )
        
        # 连续学习天数
        current_streak = await self._calculate_streak(user_id)
        
        # 特殊统计
        night_reviews = await self._count_time_reviews(user_id, 22, 2)
        morning_reviews = await self._count_time_reviews(user_id, 5, 8)
        perfect_week = await self._check_perfect_week(user_id)
        
        return {
            "total_nodes": total_nodes or 0,
            "mastered_nodes": mastered_nodes or 0,
            "total_reviews": total_reviews or 0,
            "total_graphs": total_graphs or 0,
            "current_streak": current_streak,
            "night_reviews": night_reviews,
            "morning_reviews": morning_reviews,
            "perfect_week": perfect_week,
        }
    
    async def _calculate_streak(self, user_id: int) -> int:
        """计算连续学习天数"""
        from sqlalchemy import select, distinct, cast, Date
        
        # 获取所有复习日期（去重）
        stmt = select(distinct(cast(ReviewLog.reviewed_at, Date))).where(
            ReviewLog.user_id == user_id
        ).order_by(cast(ReviewLog.reviewed_at, Date).desc())
        
        result = await self.db.execute(stmt)
        review_dates = [row[0] for row in result.fetchall()]
        
        if not review_dates:
            return 0
        
        # 计算连续天数
        today = datetime.now().date()
        streak = 0
        
        # 如果今天没有复习，从昨天开始算
        check_date = today if review_dates[0] == today else today - timedelta(days=1)
        
        for date in review_dates:
            if date == check_date:
                streak += 1
                check_date -= timedelta(days=1)
            else:
                break
        
        return streak
    
    async def _count_time_reviews(self, user_id: int, start_hour: int, end_hour: int) -> int:
        """统计特定时间段的复习次数"""
        from sqlalchemy import select, extract
        
        if start_hour < end_hour:
            # 正常时间段（如 5-8）
            stmt = select(func.count(ReviewLog.id)).where(
                and_(
                    ReviewLog.user_id == user_id,
                    extract('hour', ReviewLog.reviewed_at) >= start_hour,
                    extract('hour', ReviewLog.reviewed_at) < end_hour
                )
            )
        else:
            # 跨天时间段（如 22-2）
            stmt = select(func.count(ReviewLog.id)).where(
                and_(
                    ReviewLog.user_id == user_id,
                    or_(
                        extract('hour', ReviewLog.reviewed_at) >= start_hour,
                        extract('hour', ReviewLog.reviewed_at) < end_hour
                    )
                )
            )
        
        result = await self.db.scalar(stmt)
        return result or 0
    
    async def _check_perfect_week(self, user_id: int) -> bool:
        """检查是否有完美一周（连续7天每天都复习）"""
        from sqlalchemy import select, distinct, cast, Date
        
        # 获取最近7天的复习日期
        seven_days_ago = datetime.now().date() - timedelta(days=6)
        
        stmt = select(distinct(cast(ReviewLog.reviewed_at, Date))).where(
            and_(
                ReviewLog.user_id == user_id,
                cast(ReviewLog.reviewed_at, Date) >= seven_days_ago
            )
        )
        
        result = await self.db.execute(stmt)
        review_dates = set(row[0] for row in result.fetchall())
        
        # 检查最近7天是否每天都有复习
        for i in range(7):
            check_date = datetime.now().date() - timedelta(days=i)
            if check_date not in review_dates:
                return False
        
        return True
    
    async def calculate_level_and_exp(self, user_id: int) -> Dict:
        """计算用户等级和经验值"""
        
        # 获取统计数据
        stats = await self.get_user_stats(user_id)
        
        # 计算总经验值
        total_exp = 0
        
        # 节点创建经验
        total_exp += stats["total_nodes"] * self.EXP_RULES["create_node"]
        
        # 掌握节点经验
        total_exp += stats["mastered_nodes"] * self.EXP_RULES["master_node"]
        
        # 知识图谱经验
        total_exp += stats["total_graphs"] * self.EXP_RULES["create_graph"]
        
        # 连续学习经验
        total_exp += stats["current_streak"] * self.EXP_RULES["continuous_days"]
        
        # 复习经验（简化计算，假设平均每次15经验）
        total_exp += stats["total_reviews"] * 15
        
        # 计算等级
        level = 1
        for lv in range(20, 0, -1):
            if total_exp >= self.LEVEL_EXP[lv]:
                level = lv
                break
        
        # 计算当前等级经验和下一等级所需经验
        current_level_exp = self.LEVEL_EXP[level]
        next_level = min(level + 1, 20)
        next_level_exp = self.LEVEL_EXP[next_level]
        
        # 当前等级进度
        exp_in_level = total_exp - current_level_exp
        exp_to_next = next_level_exp - current_level_exp
        progress = (exp_in_level / exp_to_next * 100) if exp_to_next > 0 else 100
        
        return {
            "level": level,
            "total_exp": total_exp,
            "current_level_exp": current_level_exp,
            "next_level_exp": next_level_exp,
            "exp_in_level": exp_in_level,
            "exp_to_next": exp_to_next,
            "progress": round(progress, 2),
        }
    
    async def get_achievements(self, user_id: int) -> Dict:
        """获取用户成就"""
        
        # 获取统计数据
        stats = await self.get_user_stats(user_id)
        
        # 检查所有成就
        unlocked = []
        locked = []
        
        for achievement_id, achievement in self.ACHIEVEMENTS.items():
            is_unlocked = achievement["condition"](stats)
            
            achievement_data = {
                "id": achievement["id"],
                "name": achievement["name"],
                "description": achievement["description"],
                "icon": achievement["icon"],
                "category": achievement["category"],
                "unlocked": is_unlocked,
            }
            
            if is_unlocked:
                unlocked.append(achievement_data)
            else:
                locked.append(achievement_data)
        
        return {
            "unlocked": unlocked,
            "locked": locked,
            "total": len(self.ACHIEVEMENTS),
            "unlocked_count": len(unlocked),
            "progress": round(len(unlocked) / len(self.ACHIEVEMENTS) * 100, 2),
        }
    
    async def get_user_profile(self, user_id: int) -> Dict:
        """获取用户完整档案（等级 + 成就 + 统计）"""
        
        stats = await self.get_user_stats(user_id)
        level_info = await self.calculate_level_and_exp(user_id)
        achievements = await self.get_achievements(user_id)
        
        return {
            "stats": stats,
            "level": level_info,
            "achievements": achievements,
        }

