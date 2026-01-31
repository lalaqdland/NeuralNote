"""
测试创建节点
"""

import asyncio
import httpx


async def test_create_node():
    """测试创建节点"""
    async with httpx.AsyncClient(follow_redirects=True) as client:
        # 登录
        login_response = await client.post(
            "http://localhost:8000/api/v1/auth/login",
            json={
                "email": "review_test@neuralnote.com",
                "password": "test123456"
            }
        )
        
        if login_response.status_code != 200:
            print(f"❌ 登录失败: {login_response.status_code}")
            print(f"   响应: {login_response.text}")
            return
        
        tokens = login_response.json()
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        
        # 创建图谱
        graph_response = await client.post(
            "http://localhost:8000/api/v1/graphs",
            json={
                "name": "测试图谱",
                "subject": "数学",
                "description": "测试用"
            },
            headers=headers
        )
        
        if graph_response.status_code != 201:
            print(f"❌ 创建图谱失败: {graph_response.status_code}")
            print(f"   响应: {graph_response.text}")
            return
        
        graph = graph_response.json()
        graph_id = graph["id"]
        print(f"✅ 创建图谱成功: {graph_id}")
        
        # 创建节点
        node_response = await client.post(
            "http://localhost:8000/api/v1/nodes",
            json={
                "graph_id": graph_id,
                "title": "测试节点",
                "node_type": "CONCEPT",
                "content_data": {
                    "definition": "这是一个测试"
                }
            },
            headers=headers
        )
        
        print(f"状态码: {node_response.status_code}")
        print(f"响应: {node_response.text}")
        
        if node_response.status_code == 201:
            print("✅ 创建节点成功")
        else:
            print("❌ 创建节点失败")


if __name__ == "__main__":
    asyncio.run(test_create_node())

