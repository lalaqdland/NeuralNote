"""
测试用户认证接口
"""

import asyncio
import httpx

BASE_URL = "http://localhost:8000/api/v1"


async def test_register():
    """测试用户注册"""
    print("=" * 50)
    print("测试用户注册")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/auth/register",
            json={
                "email": "testuser3@example.com",
                "username": "testuser3",
                "password": "password123"
            }
        )
        
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200 or response.status_code == 201:
            return response.json()
        else:
            print(f"❌ 注册失败")
            return None


async def test_login(email: str, password: str):
    """测试用户登录"""
    print("\n" + "=" * 50)
    print("测试用户登录")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": email,
                "password": password
            }
        )
        
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        
        return response.json()


async def test_get_current_user(access_token: str):
    """测试获取当前用户信息"""
    print("\n" + "=" * 50)
    print("测试获取当前用户信息")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/auth/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        
        return response.json()


async def test_refresh_token(refresh_token: str):
    """测试刷新令牌"""
    print("\n" + "=" * 50)
    print("测试刷新令牌")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        
        return response.json()


async def main():
    """主测试流程"""
    try:
        # 1. 测试注册
        user = await test_register()
        
        if user is None:
            print("\n❌ 注册失败，停止测试")
            return
        
        # 2. 测试登录
        tokens = await test_login(user["email"], "password123")
        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]
        
        # 3. 测试获取当前用户信息
        await test_get_current_user(access_token)
        
        # 4. 测试刷新令牌
        await test_refresh_token(refresh_token)
        
        print("\n" + "=" * 50)
        print("✅ 所有测试通过！")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

