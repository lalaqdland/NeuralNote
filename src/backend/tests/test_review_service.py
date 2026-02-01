"""
复习服务单元测试
测试 SM-2 算法、遗忘指数计算、复习队列等功能
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from app.services.review_service import ReviewService, ReviewMode
from app.models.memory_node import MemoryNode, MasteryLevel


class TestSM2Algorithm:
    """测试 SM-2 算法"""
    
    def test_calculate_next_review_quality_5(self):
        """测试质量评分为 5（完美）的情况"""
        interval, easiness, repetitions = ReviewService.calculate_next_review(
            quality=5,
            repetitions=0,
            easiness=2.5,
            interval=1
        )
        
        assert repetitions == 1
        assert interval == 1
        assert easiness == 2.6  # 2.5 + 0.1
    
    def test_calculate_next_review_quality_4(self):
        """测试质量评分为 4（容易）的情况"""
        interval, easiness, repetitions = ReviewService.calculate_next_review(
            quality=4,
            repetitions=0,
            easiness=2.5,
            interval=1
        )
        
        assert repetitions == 1
        assert interval == 1
        assert easiness == 2.5  # 2.5 + 0.0
    
    def test_calculate_next_review_quality_3(self):
        """测试质量评分为 3（犹豫）的情况"""
        interval, easiness, repetitions = ReviewService.calculate_next_review(
            quality=3,
            repetitions=0,
            easiness=2.5,
            interval=1
        )
        
        assert repetitions == 1
        assert interval == 1
        assert easiness == 2.36  # 2.5 - 0.14
    
    def test_calculate_next_review_quality_2(self):
        """测试质量评分为 2（困难）的情况 - 应该重置"""
        interval, easiness, repetitions = ReviewService.calculate_next_review(
            quality=2,
            repetitions=3,
            easiness=2.5,
            interval=10
        )
        
        assert repetitions == 0  # 重置
        assert interval == 1  # 重置为 1 天
        assert easiness < 2.5  # 难度因子降低
    
    def test_calculate_next_review_second_repetition(self):
        """测试第二次复习"""
        interval, easiness, repetitions = ReviewService.calculate_next_review(
            quality=4,
            repetitions=1,
            easiness=2.5,
            interval=1
        )
        
        assert repetitions == 2
        assert interval == 6  # 第二次固定为 6 天
    
    def test_calculate_next_review_third_repetition(self):
        """测试第三次及以后的复习"""
        interval, easiness, repetitions = ReviewService.calculate_next_review(
            quality=4,
            repetitions=2,
            easiness=2.5,
            interval=6
        )
        
        assert repetitions == 3
        assert interval == int(6 * 2.5)  # 15 天
    
    def test_easiness_minimum_limit(self):
        """测试难度因子的最小值限制"""
        interval, easiness, repetitions = ReviewService.calculate_next_review(
            quality=0,
            repetitions=0,
            easiness=1.3,
            interval=1
        )
        
        assert easiness >= ReviewService.MIN_EASINESS  # 不低于 1.3


class TestForgettingIndex:
    """测试遗忘指数计算"""
    
    def test_forgetting_index_before_due(self):
        """测试未到期的遗忘指数"""
        now = datetime.utcnow()
        last_review = now - timedelta(days=1)
        next_review = now + timedelta(days=1)
        
        index = ReviewService.calculate_forgetting_index(
            last_review_time=last_review,
            next_review_time=next_review,
            mastery_level=MasteryLevel.FAMILIAR
        )
        
        assert 0 <= index <= 0.5  # 未到期，遗忘指数较低
    
    def test_forgetting_index_just_due(self):
        """测试刚到期的遗忘指数"""
        now = datetime.utcnow()
        last_review = now - timedelta(days=2)
        next_review = now
        
        index = ReviewService.calculate_forgetting_index(
            last_review_time=last_review,
            next_review_time=next_review,
            mastery_level=MasteryLevel.FAMILIAR
        )
        
        assert 0.4 <= index <= 0.6  # 刚到期，遗忘指数中等
    
    def test_forgetting_index_overdue(self):
        """测试已过期的遗忘指数"""
        now = datetime.utcnow()
        last_review = now - timedelta(days=5)
        next_review = now - timedelta(days=2)
        
        index = ReviewService.calculate_forgetting_index(
            last_review_time=last_review,
            next_review_time=next_review,
            mastery_level=MasteryLevel.FAMILIAR
        )
        
        assert index > 0.5  # 已过期，遗忘指数较高
    
    def test_forgetting_index_mastery_level_impact(self):
        """测试掌握程度对遗忘指数的影响"""
        now = datetime.utcnow()
        last_review = now - timedelta(days=5)
        next_review = now - timedelta(days=2)
        
        # 未开始学习的节点遗忘更快
        index_not_started = ReviewService.calculate_forgetting_index(
            last_review_time=last_review,
            next_review_time=next_review,
            mastery_level=MasteryLevel.NOT_STARTED
        )
        
        # 已掌握的节点遗忘更慢
        index_mastered = ReviewService.calculate_forgetting_index(
            last_review_time=last_review,
            next_review_time=next_review,
            mastery_level=MasteryLevel.MASTERED
        )
        
        assert index_not_started > index_mastered
    
    def test_forgetting_index_max_value(self):
        """测试遗忘指数的最大值"""
        now = datetime.utcnow()
        last_review = now - timedelta(days=100)
        next_review = now - timedelta(days=50)
        
        index = ReviewService.calculate_forgetting_index(
            last_review_time=last_review,
            next_review_time=next_review,
            mastery_level=MasteryLevel.NOT_STARTED
        )
        
        assert index <= 1.0  # 最大值为 1.0


class TestForgettingColor:
    """测试遗忘颜色标注"""
    
    def test_forgetting_color_green(self):
        """测试绿色（记忆牢固）"""
        color = ReviewService.get_forgetting_color(0.1)
        assert color == "#4CAF50"
    
    def test_forgetting_color_light_green(self):
        """测试浅绿色（记忆良好）"""
        color = ReviewService.get_forgetting_color(0.3)
        assert color == "#8BC34A"
    
    def test_forgetting_color_yellow(self):
        """测试黄色（需要复习）"""
        color = ReviewService.get_forgetting_color(0.5)
        assert color == "#FFC107"
    
    def test_forgetting_color_orange(self):
        """测试橙色（急需复习）"""
        color = ReviewService.get_forgetting_color(0.7)
        assert color == "#FF9800"
    
    def test_forgetting_color_red(self):
        """测试红色（即将遗忘）"""
        color = ReviewService.get_forgetting_color(0.9)
        assert color == "#F44336"


class TestReviewService:
    """测试复习服务的集成功能"""
    
    @pytest.mark.asyncio
    async def test_update_review_stats(self, db_session, test_node):
        """测试更新复习统计"""
        result = await ReviewService.update_review_stats(
            db=db_session,
            node_id=str(test_node.id),
            quality=4,
            review_duration=60
        )
        
        assert result["node_id"] == str(test_node.id)
        assert result["mastery_level"] in ["familiar", "proficient", "mastered"]
        assert result["interval_days"] >= 1
        assert result["easiness"] >= ReviewService.MIN_EASINESS
        assert result["repetitions"] >= 1
    
    @pytest.mark.asyncio
    async def test_update_review_stats_quality_low(self, db_session, test_node):
        """测试低质量评分的复习统计更新"""
        result = await ReviewService.update_review_stats(
            db=db_session,
            node_id=str(test_node.id),
            quality=2,
            review_duration=120
        )
        
        assert result["mastery_level"] == "learning"
        assert result["interval_days"] == 1  # 重置为 1 天
        assert result["repetitions"] == 0  # 重置为 0
    
    @pytest.mark.asyncio
    async def test_update_review_stats_invalid_node(self, db_session):
        """测试无效节点 ID"""
        with pytest.raises(ValueError, match="节点不存在"):
            await ReviewService.update_review_stats(
                db=db_session,
                node_id=str(uuid4()),
                quality=4,
                review_duration=60
            )
    
    @pytest.mark.asyncio
    async def test_get_review_queue_spaced_mode(self, db_session, test_user, test_graph):
        """测试间隔重复模式的复习队列"""
        # 创建一些测试节点
        nodes = []
        for i in range(3):
            node = MemoryNode(
                graph_id=test_graph.id,
                user_id=test_user.id,
                node_type="CONCEPT",
                title=f"测试节点 {i}",
                content_data={"test": "data"},
                last_review_at=datetime.utcnow() - timedelta(days=i+1),
                next_review_at=datetime.utcnow() - timedelta(hours=i),
            )
            db_session.add(node)
            nodes.append(node)
        
        await db_session.commit()
        
        queue = await ReviewService.get_review_queue(
            db=db_session,
            user_id=str(test_user.id),
            graph_id=str(test_graph.id),
            mode=ReviewMode.SPACED,
            limit=10
        )
        
        assert len(queue) == 3
        assert all("forgetting_index" in item for item in queue)
        assert all("forgetting_color" in item for item in queue)
    
    @pytest.mark.asyncio
    async def test_get_review_queue_focused_mode(self, db_session, test_user, test_graph):
        """测试集中攻克模式的复习队列"""
        # 创建不同掌握程度的节点
        node1 = MemoryNode(
            graph_id=test_graph.id,
            user_id=test_user.id,
            node_type="CONCEPT",
            title="未开始节点",
            content_data={"test": "data"},
            mastery_level=MasteryLevel.NOT_STARTED.value,
        )
        node2 = MemoryNode(
            graph_id=test_graph.id,
            user_id=test_user.id,
            node_type="CONCEPT",
            title="已掌握节点",
            content_data={"test": "data"},
            mastery_level=MasteryLevel.MASTERED.value,
        )
        db_session.add_all([node1, node2])
        await db_session.commit()
        
        queue = await ReviewService.get_review_queue(
            db=db_session,
            user_id=str(test_user.id),
            graph_id=str(test_graph.id),
            mode=ReviewMode.FOCUSED,
            limit=10
        )
        
        # focused 模式只返回薄弱知识点
        assert len(queue) >= 1
        assert all(
            item["mastery_level"] in ["not_started", "learning", "familiar"]
            for item in queue
        )
    
    @pytest.mark.asyncio
    async def test_get_review_statistics(self, db_session, test_user, test_graph):
        """测试复习统计"""
        # 创建不同掌握程度的节点
        for mastery in [MasteryLevel.NOT_STARTED, MasteryLevel.LEARNING, MasteryLevel.MASTERED]:
            node = MemoryNode(
                graph_id=test_graph.id,
                user_id=test_user.id,
                node_type="CONCEPT",
                title=f"节点 {mastery.value}",
                content_data={"test": "data"},
                mastery_level=mastery.value,
                review_stats={"total_reviews": 5}
            )
            db_session.add(node)
        
        await db_session.commit()
        
        stats = await ReviewService.get_review_statistics(
            db=db_session,
            user_id=str(test_user.id),
            graph_id=str(test_graph.id)
        )
        
        assert stats["total_nodes"] == 3
        assert "mastery_distribution" in stats
        assert stats["mastery_distribution"]["not_started"] >= 1
        assert stats["mastery_distribution"]["learning"] >= 1
        assert stats["mastery_distribution"]["mastered"] >= 1
        assert stats["total_reviews"] == 15  # 3 nodes * 5 reviews
        assert 0 <= stats["mastery_rate"] <= 100


class TestHelperMethods:
    """测试辅助方法"""
    
    def test_normalize_datetime_with_timezone(self):
        """测试移除时区信息"""
        from datetime import timezone
        dt_with_tz = datetime.now(timezone.utc)
        dt_normalized = ReviewService._normalize_datetime(dt_with_tz)
        
        assert dt_normalized.tzinfo is None
    
    def test_normalize_datetime_without_timezone(self):
        """测试已经没有时区信息的时间"""
        dt_without_tz = datetime.utcnow()
        dt_normalized = ReviewService._normalize_datetime(dt_without_tz)
        
        assert dt_normalized.tzinfo is None
        assert dt_normalized == dt_without_tz
    
    def test_normalize_datetime_none(self):
        """测试 None 值"""
        result = ReviewService._normalize_datetime(None)
        assert result is None
    
    def test_get_utc_now(self):
        """测试获取当前 UTC 时间"""
        now = ReviewService._get_utc_now()
        
        assert isinstance(now, datetime)
        assert now.tzinfo is None  # 应该没有时区信息
        
        # 验证时间是合理的（在当前时间附近）
        current = datetime.utcnow()
        time_diff = abs((now - current).total_seconds())
        assert time_diff < 1  # 差异应该小于 1 秒




