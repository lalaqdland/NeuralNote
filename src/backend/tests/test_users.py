"""
用户管理接口测试
测试用户信息的查询和更新
"""

import pytest
from httpx import AsyncClient

from app.models import User


class TestUserProfile:
    """用户信息测试"""

    @pytest.mark.asyncio
    async def test_get_user_profile(self, client: AsyncClient, auth_headers: dict, test_user: User):
        """测试获取用户信息"""
        response = await client.get(
            "/api/v1/users/me",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email
        assert data["username"] == test_user.username
        assert "id" in data

    @pytest.mark.asyncio
    async def test_get_user_profile_no_auth(self, client: AsyncClient):
        """测试未认证获取用户信息"""
        response = await client.get("/api/v1/users/me")
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_update_user_profile(self, client: AsyncClient, auth_headers: dict):
        """测试更新用户信息"""
        update_data = {
            "username": "updated_username",
            "timezone": "Asia/Shanghai",
            "language": "zh-CN"
        }
        
        response = await client.put(
            "/api/v1/users/me",
            headers=auth_headers,
            json=update_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == update_data["username"]
        assert data["timezone"] == update_data["timezone"]
        assert data["language"] == update_data["language"]

    @pytest.mark.asyncio
    async def test_update_user_partial(self, client: AsyncClient, auth_headers: dict, test_user: User):
        """测试部分更新用户信息"""
        response = await client.put(
            "/api/v1/users/me",
            headers=auth_headers,
            json={"username": "new_username"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "new_username"
        assert data["email"] == test_user.email  # 保持不变


class TestUserDeletion:
    """用户删除测试"""

    @pytest.mark.asyncio
    async def test_delete_user_account(self, client: AsyncClient, auth_headers: dict):
        """测试删除用户账号"""
        response = await client.delete(
            "/api/v1/users/me",
            headers=auth_headers
        )
        
        assert response.status_code == 204
        
        # 验证用户已被删除（无法再获取信息）
        get_response = await client.get(
            "/api/v1/users/me",
            headers=auth_headers
        )
        assert get_response.status_code == 401  # Token 失效


class TestUserStatistics:
    """用户统计测试"""

    @pytest.mark.asyncio
    async def test_get_user_stats(self, client: AsyncClient, auth_headers: dict):
        """测试获取用户统计信息"""
        response = await client.get(
            "/api/v1/users/me/stats",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "total_graphs" in data
        assert "total_nodes" in data
        assert "total_reviews" in data

