"""
测试登录功能
"""

import asyncio
import httpx


async def test_login():
    """测试登录"""
    async with httpx.AsyncClient() as client:
        # 先尝试注册
        print("1. 尝试注册新用户...")
        response = await client.post(
            "http://localhost:8000/api/v1/auth/register",
            json={
                "email": "test2@neuralnote.com",
                "username": "testuser2",
                "password": "test123456"
            }
        )
        print(f"   注册响应: {response.status_code}")
        if response.status_code == 201:
            print(f"   ✅ 注册成功")
            data = response.json()
            print(f"   用户ID: {data['id']}")
        else:
            print(f"   响应: {response.text}")
        
        # 测试登录
        print("\n2. 测试登录...")
        response = await client.post(
            "http://localhost:8000/api/v1/auth/login",
            json={
                "email": "test2@neuralnote.com",
                "password": "test123456"
            }
        )
        print(f"   登录响应: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ 登录成功")
            data = response.json()
            print(f"   Token: {data['access_token'][:20]}...")
        else:
            print(f"   ❌ 登录失败")
            print(f"   响应: {response.text}")
        
        # 测试原用户登录
        print("\n3. 测试原用户登录...")
        response = await client.post(
            "http://localhost:8000/api/v1/auth/login",
            json={
                "email": "test@neuralnote.com",
                "password": "test123456"
            }
        )
        print(f"   登录响应: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ 登录成功")
            data = response.json()
            print(f"   Token: {data['access_token'][:20]}...")
        else:
            print(f"   ❌ 登录失败")
            print(f"   响应: {response.text}")


if __name__ == "__main__":
    asyncio.run(test_login())

