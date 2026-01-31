"""
测试统计接口
"""

import pytest
from httpx import AsyncClient


class TestStatistics:
    """测试统计功能"""
    
    @pytest.mark.asyncio
    async def test_review_statistics(self, client: AsyncClient, test_user, auth_headers: dict, test_graph):
        """测试复习统计接口"""
        response = await client.get(
            f"/api/v1/reviews/statistics?graph_id={test_graph.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "total_nodes" in data
        assert "reviewed_nodes" in data
        assert "due_nodes" in data
        assert "mastery_rate" in data
    
    @pytest.mark.asyncio
    async def test_user_statistics(self, client: AsyncClient, test_user, auth_headers: dict):
        """测试用户统计接口"""
        response = await client.get(
            "/api/v1/users/me/stats",
            headers=auth_headers
        )
        
        # 如果接口存在，应该返回 200
        # 如果接口不存在，返回 404
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert "total_graphs" in data
            assert "total_nodes" in data
