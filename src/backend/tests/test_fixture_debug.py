"""
调试 fixture 问题
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User


class TestFixtureDebug:
    """调试 fixture"""
    
    @pytest.mark.asyncio
    async def test_user_creation(self, db_session: AsyncSession, test_user: User):
        """测试用户是否正确创建"""
        print(f"\n测试用户 ID: {test_user.id}")
        print(f"测试用户邮箱: {test_user.email}")
        assert test_user.id is not None
        assert test_user.email == "test@example.com"
    
    @pytest.mark.asyncio
    async def test_auth_headers(self, client: AsyncClient, auth_headers: dict, test_user: User):
        """测试认证头是否正确"""
        print(f"\n测试用户 ID: {test_user.id}")
        print(f"认证头: {auth_headers}")
        
        # 尝试访问需要认证的接口
        response = await client.get(
            "/api/v1/users/me",
            headers=auth_headers
        )
        
        print(f"响应状态码: {response.status_code}")
        if response.status_code != 200:
            print(f"响应内容: {response.text}")
        
        assert response.status_code == 200
        data = response.json()
        print(f"返回的用户 ID: {data.get('id')}")
        assert data["email"] == "test@example.com"

