"""
用户认证接口测试
测试用户注册、登录、Token 刷新等功能
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from tests.conftest import TEST_USER_DATA


class TestUserRegistration:
    """用户注册测试"""

    @pytest.mark.asyncio
    async def test_register_success(self, client: AsyncClient):
        """测试成功注册"""
        response = await client.post(
            "/api/v1/auth/register",
            json=TEST_USER_DATA
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == TEST_USER_DATA["email"]
        assert data["username"] == TEST_USER_DATA["username"]
        assert "id" in data
        assert "hashed_password" not in data  # 不应返回密码

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client: AsyncClient, test_user: User):
        """测试重复邮箱注册"""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": test_user.email,
                "username": "anotheruser",
                "password": "password123"
            }
        )
        
        assert response.status_code == 400
        detail = response.json()["detail"]
        # 支持中英文错误消息
        assert "already registered" in detail.lower() or "已被注册" in detail or "已注册" in detail

    @pytest.mark.asyncio
    async def test_register_duplicate_username(self, client: AsyncClient, test_user: User):
        """测试重复用户名注册"""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "another@example.com",
                "username": test_user.username,
                "password": "password123"
            }
        )
        
        assert response.status_code == 400
        detail = response.json()["detail"]
        # 支持中英文错误消息
        assert "already taken" in detail.lower() or "已被使用" in detail or "已使用" in detail

    @pytest.mark.asyncio
    async def test_register_invalid_email(self, client: AsyncClient):
        """测试无效邮箱格式"""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "invalid-email",
                "username": "testuser",
                "password": "password123"
            }
        )
        
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_register_short_password(self, client: AsyncClient):
        """测试密码过短"""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "username": "testuser",
                "password": "123"  # 少于6位
            }
        )
        
        assert response.status_code == 422


class TestUserLogin:
    """用户登录测试"""

    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient, test_user: User):
        """测试成功登录"""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": "password123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client: AsyncClient, test_user: User):
        """测试错误密码"""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == 401
        detail = response.json()["detail"]
        # 支持中英文错误消息
        assert "incorrect" in detail.lower() or "错误" in detail or "不正确" in detail

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client: AsyncClient):
        """测试不存在的用户"""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "password123"
            }
        )
        
        assert response.status_code == 401


class TestTokenOperations:
    """Token 操作测试"""

    @pytest.mark.asyncio
    async def test_get_current_user(self, client: AsyncClient, auth_headers: dict, test_user: User):
        """测试获取当前用户信息"""
        response = await client.get(
            "/api/v1/auth/me",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email
        assert data["username"] == test_user.username

    @pytest.mark.asyncio
    async def test_get_current_user_no_token(self, client: AsyncClient):
        """测试未提供 Token"""
        response = await client.get("/api/v1/auth/me")
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self, client: AsyncClient):
        """测试无效 Token"""
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_refresh_token(self, client: AsyncClient, test_user: User):
        """测试刷新 Token"""
        # 先登录获取 refresh_token
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": "password123"
            }
        )
        refresh_token = login_response.json()["refresh_token"]
        
        # 使用 refresh_token 获取新的 access_token
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    @pytest.mark.asyncio
    async def test_refresh_token_invalid(self, client: AsyncClient):
        """测试无效的 refresh_token"""
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid_token"}
        )
        
        assert response.status_code == 401


class TestPasswordOperations:
    """密码操作测试"""

    @pytest.mark.asyncio
    async def test_change_password(self, client: AsyncClient, auth_headers: dict, test_user: User):
        """测试修改密码"""
        response = await client.post(
            "/api/v1/auth/change-password",
            headers=auth_headers,
            json={
                "old_password": "password123",
                "new_password": "newpassword123"
            }
        )
        
        assert response.status_code == 200
        
        # 验证新密码可以登录
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": "newpassword123"
            }
        )
        assert login_response.status_code == 200

    @pytest.mark.asyncio
    async def test_change_password_wrong_old_password(self, client: AsyncClient, auth_headers: dict):
        """测试旧密码错误"""
        response = await client.post(
            "/api/v1/auth/change-password",
            headers=auth_headers,
            json={
                "old_password": "wrongpassword",
                "new_password": "newpassword123"
            }
        )
        
        assert response.status_code == 400

