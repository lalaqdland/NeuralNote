"""
复习算法服务
实现基于 SM-2 算法的遗忘曲线计算
"""

from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Dict, List, Optional, Tuple

from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.memory_node import MemoryNode, MasteryLevel
from app.models.review_log import ReviewLog


class ReviewQuality(Enum):
    """复习质量评分（SM-2 算法）"""
    BLACKOUT = 0  # 完全不记得
    INCORRECT = 1  # 错误，但有印象
    DIFFICULT = 2  # 困难，勉强记起
    HESITANT = 3  # 犹豫，但最终正确
    EASY = 4  # 容易，有些犹豫
    PERFECT = 5  # 完美，立即回忆


class ReviewMode(Enum):
    """复习模式"""
    GRAPH_TRAVERSAL = "graph_traversal"  # 图谱遍历模式
    RANDOM = "random"  # 随机抽查模式
    FOCUSED = "focused"  # 集中攻克模式（针对薄弱知识点）
    SPACED = "spaced"  # 间隔重复模式（基于遗忘曲线）


class ReviewService:
    """复习算法服务"""
    
    # SM-2 算法默认参数
    DEFAULT_EASINESS = 2.5  # 默认难度因子
    MIN_EASINESS = 1.3  # 最小难度因子
    
    @staticmethod
    def calculate_next_review(
        quality: int,
        repetitions: int,
        easiness: float,
        interval: int
    ) -> Tuple[int, float, int]:
        """
        计算下次复习时间（SM-2 算法）
        
        Args:
            quality: 复习质量评分 (0-5)
            repetitions: 已复习次数
            easiness: 难度因子 (>= 1.3)
            interval: 当前间隔天数
            
        Returns:
            (新间隔天数, 新难度因子, 新复习次数)
        """
        # 更新难度因子
        new_easiness = easiness + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        new_easiness = max(new_easiness, ReviewService.MIN_EASINESS)
        
        # 如果质量评分 < 3，重置复习次数
        if quality < 3:
            new_repetitions = 0
            new_interval = 1
        else:
            new_repetitions = repetitions + 1
            
            # 计算新间隔
            if new_repetitions == 1:
                new_interval = 1
            elif new_repetitions == 2:
                new_interval = 6
            else:
                new_interval = int(interval * new_easiness)
        
        return new_interval, new_easiness, new_repetitions
    
    @staticmethod
    def _get_utc_now() -> datetime:
        """
        获取当前 UTC 时间（不带时区信息，用于数据库存储）
        
        Returns:
            当前 UTC 时间（不带时区）
        """
        return datetime.utcnow()
    
    @staticmethod
    def _normalize_datetime(dt: datetime) -> datetime:
        """
        标准化 datetime 对象，移除时区信息
        
        Args:
            dt: datetime 对象
            
        Returns:
            移除时区信息的 datetime 对象
        """
        if dt is None:
            return None
        if dt.tzinfo is not None:
            # 转换为 UTC 并移除时区信息
            return dt.replace(tzinfo=None)
        return dt
    
    @staticmethod
    def calculate_forgetting_index(
        last_review_time: datetime,
        next_review_time: datetime,
        mastery_level: MasteryLevel
    ) -> float:
        """
        计算遗忘指数（0-1，越大越容易遗忘）
        
        Args:
            last_review_time: 上次复习时间
            next_review_time: 下次复习时间
            mastery_level: 掌握程度
            
        Returns:
            遗忘指数 (0-1)
        """
        # 统一移除时区信息
        now = ReviewService._normalize_datetime(ReviewService._get_utc_now())
        last_review_time = ReviewService._normalize_datetime(last_review_time)
        next_review_time = ReviewService._normalize_datetime(next_review_time)
        
        # 如果还没到复习时间，遗忘指数较低
        if now < next_review_time:
            time_passed = (now - last_review_time).total_seconds()
            total_interval = (next_review_time - last_review_time).total_seconds()
            
            if total_interval == 0:
                return 0.0
            
            # 线性增长，但不超过 0.5
            forgetting_index = min(0.5, time_passed / total_interval * 0.5)
        else:
            # 超过复习时间，遗忘指数快速增长
            overdue_seconds = (now - next_review_time).total_seconds()
            overdue_days = overdue_seconds / 86400
            
            # 根据掌握程度调整遗忘速度
            mastery_factor = {
                MasteryLevel.NOT_STARTED: 1.5,
                MasteryLevel.LEARNING: 1.2,
                MasteryLevel.FAMILIAR: 1.0,
                MasteryLevel.PROFICIENT: 0.8,
                MasteryLevel.MASTERED: 0.5
            }.get(mastery_level, 1.0)
            
            # 遗忘指数 = 0.5 + 超期天数 * 遗忘速度因子
            forgetting_index = min(1.0, 0.5 + overdue_days * 0.1 * mastery_factor)
        
        return forgetting_index
    
    @staticmethod
    def get_forgetting_color(forgetting_index: float) -> str:
        """
        根据遗忘指数获取颜色标注
        
        Args:
            forgetting_index: 遗忘指数 (0-1)
            
        Returns:
            颜色代码（十六进制）
        """
        if forgetting_index < 0.2:
            return "#4CAF50"  # 绿色 - 记忆牢固
        elif forgetting_index < 0.4:
            return "#8BC34A"  # 浅绿色 - 记忆良好
        elif forgetting_index < 0.6:
            return "#FFC107"  # 黄色 - 需要复习
        elif forgetting_index < 0.8:
            return "#FF9800"  # 橙色 - 急需复习
        else:
            return "#F44336"  # 红色 - 即将遗忘
    
    @staticmethod
    async def update_review_stats(
        db: AsyncSession,
        node_id: str,
        quality: int,
        review_duration: int
    ) -> Dict:
        """
        更新节点的复习统计数据
        
        Args:
            db: 数据库会话
            node_id: 节点 ID
            quality: 复习质量评分 (0-5)
            review_duration: 复习时长（秒）
            
        Returns:
            更新后的复习统计数据
        """
        # 查询节点
        result = await db.execute(
            select(MemoryNode).where(MemoryNode.id == node_id)
        )
        node = result.scalar_one_or_none()
        
        if not node:
            raise ValueError(f"节点不存在: {node_id}")
        
        # 获取当前复习统计
        review_stats = node.review_stats or {}
        
        # 获取当前参数
        repetitions = review_stats.get("repetitions", 0)
        easiness = review_stats.get("easiness", ReviewService.DEFAULT_EASINESS)
        interval = review_stats.get("interval", 1)
        
        # 计算新参数
        new_interval, new_easiness, new_repetitions = ReviewService.calculate_next_review(
            quality=quality,
            repetitions=repetitions,
            easiness=easiness,
            interval=interval
        )
        
        # 更新掌握程度
        if quality >= 4:
            if new_repetitions >= 5:
                new_mastery = MasteryLevel.MASTERED
            elif new_repetitions >= 3:
                new_mastery = MasteryLevel.PROFICIENT
            else:
                new_mastery = MasteryLevel.FAMILIAR
        elif quality >= 3:
            new_mastery = MasteryLevel.FAMILIAR
        else:
            new_mastery = MasteryLevel.LEARNING
        
        # 计算下次复习时间
        next_review_time = ReviewService._get_utc_now() + timedelta(days=new_interval)
        
        # 更新节点
        node.mastery_level = new_mastery.value  # 存储为字符串
        node.last_review_at = ReviewService._get_utc_now()
        node.next_review_at = next_review_time
        node.review_stats = {
            "repetitions": new_repetitions,
            "easiness": new_easiness,
            "interval": new_interval,
            "total_reviews": review_stats.get("total_reviews", 0) + 1,
            "last_quality": quality,
            "last_duration": review_duration
        }
        
        # 创建复习记录
        review_log = ReviewLog(
            user_id=node.user_id,
            node_id=node.id,
            review_mode="manual",
            mastery_feedback="remembered" if quality >= 3 else "forgot",
            time_spent_seconds=review_duration,
            node_state_snapshot={
                "mastery_before": node.mastery_level,
                "mastery_after": new_mastery.value,
                "quality": quality
            }
        )
        db.add(review_log)
        
        await db.commit()
        await db.refresh(node)
        
        return {
            "node_id": str(node.id),
            "mastery_level": new_mastery.value,
            "next_review_at": next_review_time.isoformat(),
            "interval_days": new_interval,
            "easiness": new_easiness,
            "repetitions": new_repetitions
        }
    
    @staticmethod
    async def get_review_queue(
        db: AsyncSession,
        user_id: str,
        graph_id: Optional[str] = None,
        mode: ReviewMode = ReviewMode.SPACED,
        limit: int = 20
    ) -> List[Dict]:
        """
        获取复习队列
        
        Args:
            db: 数据库会话
            user_id: 用户 ID
            graph_id: 知识图谱 ID（可选）
            mode: 复习模式
            limit: 返回数量限制
            
        Returns:
            待复习节点列表
        """
        now = ReviewService._normalize_datetime(ReviewService._get_utc_now())
        
        # 基础查询条件
        conditions = [MemoryNode.user_id == user_id]
        if graph_id:
            conditions.append(MemoryNode.graph_id == graph_id)
        
        # 根据模式选择节点
        if mode == ReviewMode.SPACED:
            # 间隔重复：选择到期的节点
            conditions.append(
                or_(
                    MemoryNode.next_review_at <= now,
                    MemoryNode.next_review_at.is_(None)
                )
            )
            order_by = MemoryNode.next_review_at.asc()
            
        elif mode == ReviewMode.FOCUSED:
            # 集中攻克：选择掌握程度低的节点
            conditions.append(
                MemoryNode.mastery_level.in_([
                    MasteryLevel.NOT_STARTED.value,
                    MasteryLevel.LEARNING.value,
                    MasteryLevel.FAMILIAR.value
                ])
            )
            order_by = MemoryNode.mastery_level.asc()
            
        elif mode == ReviewMode.RANDOM:
            # 随机抽查：随机排序
            order_by = None  # 后续使用 func.random()
            
        else:  # GRAPH_TRAVERSAL
            # 图谱遍历：按创建时间排序
            order_by = MemoryNode.created_at.asc()
        
        # 构建查询
        query = select(MemoryNode).where(and_(*conditions))
        
        if order_by is not None:
            query = query.order_by(order_by)
        
        query = query.limit(limit)
        
        # 执行查询
        result = await db.execute(query)
        nodes = result.scalars().all()
        
        # 构建返回数据
        review_queue = []
        for node in nodes:
            # 转换 mastery_level 为枚举（如果是字符串）
            try:
                if isinstance(node.mastery_level, str):
                    mastery_level_enum = MasteryLevel(node.mastery_level)
                else:
                    mastery_level_enum = node.mastery_level
            except (ValueError, AttributeError):
                mastery_level_enum = MasteryLevel.NOT_STARTED
            
            # 计算遗忘指数
            if node.last_review_at and node.next_review_at:
                try:
                    forgetting_index = ReviewService.calculate_forgetting_index(
                        last_review_time=node.last_review_at,
                        next_review_time=node.next_review_at,
                        mastery_level=mastery_level_enum
                    )
                except Exception as e:
                    print(f"Warning: Failed to calculate forgetting index for node {node.id}: {e}")
                    forgetting_index = 0.8  # 默认值
            else:
                forgetting_index = 0.8  # 未复习过的节点，默认较高
            
            review_queue.append({
                "node_id": str(node.id),
                "title": node.title,
                "node_type": node.node_type,
                "mastery_level": node.mastery_level if isinstance(node.mastery_level, str) else node.mastery_level.value,
                "last_review_at": node.last_review_at.isoformat() if node.last_review_at else None,
                "next_review_at": node.next_review_at.isoformat() if node.next_review_at else None,
                "forgetting_index": forgetting_index,
                "forgetting_color": ReviewService.get_forgetting_color(forgetting_index),
                "review_stats": node.review_stats or {}
            })
        
        return review_queue
    
    @staticmethod
    async def get_review_statistics(
        db: AsyncSession,
        user_id: str,
        graph_id: Optional[str] = None
    ) -> Dict:
        """
        获取复习统计信息
        
        Args:
            db: 数据库会话
            user_id: 用户 ID
            graph_id: 知识图谱 ID（可选）
            
        Returns:
            复习统计数据
        """
        try:
            # 基础查询条件
            conditions = [MemoryNode.user_id == user_id]
            if graph_id:
                conditions.append(MemoryNode.graph_id == graph_id)
            
            # 查询所有节点
            result = await db.execute(
                select(MemoryNode).where(and_(*conditions))
            )
            nodes = result.scalars().all()
            
            # 统计数据
            total_nodes = len(nodes)
            mastery_distribution = {
                "not_started": 0,
                "learning": 0,
                "familiar": 0,
                "proficient": 0,
                "mastered": 0
            }
            
            due_today = 0
            overdue = 0
            total_reviews = 0
            
            now = ReviewService._normalize_datetime(ReviewService._get_utc_now())
            
            for node in nodes:
                try:
                    # 掌握程度分布（处理字符串类型）
                    if isinstance(node.mastery_level, str):
                        mastery_key = node.mastery_level.lower()
                    else:
                        mastery_key = node.mastery_level.value.lower()
                    mastery_distribution[mastery_key] = mastery_distribution.get(mastery_key, 0) + 1
                    
                    # 复习次数
                    review_stats = node.review_stats or {}
                    total_reviews += review_stats.get("total_reviews", 0)
                    
                    # 到期统计
                    if node.next_review_at:
                        try:
                            # 统一移除时区信息
                            next_review_date = ReviewService._normalize_datetime(node.next_review_at)
                            now_date = now  # now 已经是不带时区的
                            
                            if next_review_date.date() == now_date.date():
                                due_today += 1
                            elif next_review_date < now_date:
                                overdue += 1
                        except Exception as e:
                            # 跳过有问题的节点
                            print(f"Warning: Failed to compare dates for node {node.id}: {e}")
                            print(f"  next_review_at type: {type(node.next_review_at)}, value: {node.next_review_at}")
                            print(f"  now type: {type(now)}, value: {now}")
                            continue
                except Exception as e:
                    print(f"Error processing node {node.id}: {e}")
                    import traceback
                    traceback.print_exc()
                    continue
            
            # 计算掌握率
            mastery_rate = 0
            if total_nodes > 0:
                mastered_count = mastery_distribution["proficient"] + mastery_distribution["mastered"]
                mastery_rate = round(mastered_count / total_nodes * 100, 2)
            
            return {
                "total_nodes": total_nodes,
                "mastery_distribution": mastery_distribution,
                "mastery_rate": mastery_rate,
                "due_today": due_today,
                "overdue": overdue,
                "total_reviews": total_reviews
            }
        except Exception as e:
            print(f"Error in get_review_statistics: {e}")
            import traceback
            traceback.print_exc()
            raise

