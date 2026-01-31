"""
创建测试用户
"""

import asyncio
import httpx


async def create_test_user():
    """创建测试用户"""
    async with httpx.AsyncClient() as client:
        # 注册用户
        response = await client.post(
            "http://localhost:8000/api/v1/auth/register",
            json={
                "email": "test@neuralnote.com",
                "username": "testuser",
                "password": "test123456"
            }
        )
        
        if response.status_code == 201:
            print("✅ 测试用户创建成功")
            print(f"   邮箱: test@neuralnote.com")
            print(f"   密码: test123456")
        elif response.status_code == 400:
            print("⚠️ 用户已存在")
        else:
            print(f"❌ 创建失败: {response.status_code}")
            print(f"   响应: {response.text}")


if __name__ == "__main__":
    asyncio.run(create_test_user())

