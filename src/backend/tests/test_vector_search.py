"""
向量搜索功能测试脚本
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

import httpx


BASE_URL = "http://localhost:8000/api/v1"
TOKEN = None


async def register_and_login():
    """注册并登录获取 Token"""
    global TOKEN
    
    async with httpx.AsyncClient() as client:
        # 注册
        register_data = {
            "email": "vector_test@example.com",
            "username": "向量测试用户",
            "password": "test123456"
        }
        
        try:
            response = await client.post(f"{BASE_URL}/auth/register", json=register_data)
            if response.status_code == 201:
                print("✅ 用户注册成功")
            elif response.status_code == 400:
                print("ℹ️  用户已存在，直接登录")
        except Exception as e:
            print(f"⚠️  注册失败: {e}")
        
        # 登录
        login_data = {
            "email": "vector_test@example.com",
            "password": "test123456"
        }
        
        response = await client.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            TOKEN = response.json()["access_token"]
            print(f"✅ 登录成功，Token: {TOKEN[:20]}...")
            return True
        else:
            print(f"❌ 登录失败: {response.text}")
            return False


async def create_test_graph():
    """创建测试知识图谱"""
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    async with httpx.AsyncClient() as client:
        graph_data = {
            "name": "向量搜索测试图谱",
            "description": "用于测试向量相似度搜索功能",
            "subject": "数学"
        }
        
        response = await client.post(
            f"{BASE_URL}/graphs/",
            json=graph_data,
            headers=headers
        )
        
        if response.status_code == 201:
            graph = response.json()
            print(f"✅ 创建知识图谱成功: {graph['id']}")
            return graph["id"]
        else:
            print(f"❌ 创建知识图谱失败: {response.text}")
            return None


async def create_test_nodes(graph_id: str):
    """创建测试节点"""
    headers = {"Authorization": f"Bearer {TOKEN}"}
    node_ids = []
    
    # 创建多个相关的数学题目节点
    test_nodes = [
        {
            "title": "二次函数求导",
            "summary": "求函数 f(x) = x^2 + 2x + 1 的导数",
            "node_type": "QUESTION",
            "content_data": {
                "question": "求函数 f(x) = x^2 + 2x + 1 的导数",
                "answer": "f'(x) = 2x + 2",
                "difficulty": "简单"
            }
        },
        {
            "title": "三次函数求导",
            "summary": "求函数 g(x) = x^3 + 3x^2 + 3x + 1 的导数",
            "node_type": "QUESTION",
            "content_data": {
                "question": "求函数 g(x) = x^3 + 3x^2 + 3x + 1 的导数",
                "answer": "g'(x) = 3x^2 + 6x + 3",
                "difficulty": "简单"
            }
        },
        {
            "title": "导数的定义",
            "summary": "导数是函数在某一点的瞬时变化率",
            "node_type": "CONCEPT",
            "content_data": {
                "content": "导数的定义：f'(x) = lim(h->0) [f(x+h) - f(x)] / h",
                "category": "微积分基础"
            }
        },
        {
            "title": "积分计算",
            "summary": "求函数 f(x) = 2x 的不定积分",
            "node_type": "QUESTION",
            "content_data": {
                "question": "求函数 f(x) = 2x 的不定积分",
                "answer": "∫2x dx = x^2 + C",
                "difficulty": "简单"
            }
        },
        {
            "title": "三角函数求导",
            "summary": "求 sin(x) 的导数",
            "node_type": "QUESTION",
            "content_data": {
                "question": "求 sin(x) 的导数",
                "answer": "d/dx[sin(x)] = cos(x)",
                "difficulty": "中等"
            }
        }
    ]
    
    async with httpx.AsyncClient() as client:
        for node_data in test_nodes:
            node_data["graph_id"] = graph_id
            
            response = await client.post(
                f"{BASE_URL}/nodes/",
                json=node_data,
                headers=headers
            )
            
            if response.status_code == 201:
                node = response.json()
                node_ids.append(node["id"])
                print(f"✅ 创建节点成功: {node['title']}")
            else:
                print(f"❌ 创建节点失败: {response.text}")
    
    return node_ids


async def update_embeddings(graph_id: str):
    """更新节点的向量嵌入"""
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{BASE_URL}/vector-search/batch-update-embedding",
            params={"graph_id": graph_id},
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 批量更新向量嵌入成功: {result['message']}")
            return True
        else:
            print(f"❌ 更新向量嵌入失败: {response.text}")
            return False


async def test_vector_search():
    """测试向量搜索"""
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    print("\n" + "="*50)
    print("测试 1: 基于文本查询搜索相似节点")
    print("="*50)
    
    async with httpx.AsyncClient() as client:
        search_data = {
            "query_text": "如何求函数的导数",
            "limit": 5,
            "similarity_threshold": 0.5
        }
        
        response = await client.post(
            f"{BASE_URL}/vector-search/search",
            json=search_data,
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 搜索成功，找到 {result['total']} 个相似节点:")
            for node in result["results"]:
                print(f"  - {node['title']} (相似度: {node['similarity_score']:.4f})")
        else:
            print(f"❌ 搜索失败: {response.text}")


async def test_similar_nodes(node_id: str):
    """测试查找相似节点"""
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    print("\n" + "="*50)
    print("测试 2: 查找与指定节点相似的其他节点")
    print("="*50)
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/vector-search/similar/{node_id}",
            params={"limit": 5, "similarity_threshold": 0.5},
            headers=headers
        )
        
        if response.status_code == 200:
            results = response.json()
            print(f"✅ 找到 {len(results)} 个相似节点:")
            for node in results:
                print(f"  - {node['title']} (相似度: {node['similarity_score']:.4f})")
        else:
            print(f"❌ 查找失败: {response.text}")


async def test_recommendations(node_id: str):
    """测试节点推荐"""
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    print("\n" + "="*50)
    print("测试 3: 节点推荐（学习路径）")
    print("="*50)
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/vector-search/recommend/{node_id}",
            params={"limit": 3},
            headers=headers
        )
        
        if response.status_code == 200:
            results = response.json()
            print(f"✅ 推荐 {len(results)} 个相关节点:")
            for node in results:
                print(f"  - {node['title']} (相似度: {node['similarity_score']:.4f})")
        else:
            print(f"❌ 推荐失败: {response.text}")


async def test_clustering(graph_id: str):
    """测试节点聚类"""
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    print("\n" + "="*50)
    print("测试 4: 节点聚类")
    print("="*50)
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/vector-search/cluster/{graph_id}",
            params={"similarity_threshold": 0.7},
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 聚类成功，共 {result['total_clusters']} 个簇:")
            for cluster in result["clusters"]:
                print(f"  - 簇 {cluster['cluster_id']}: {cluster['size']} 个节点")
        else:
            print(f"❌ 聚类失败: {response.text}")


async def main():
    """主测试流程"""
    print("🚀 开始向量搜索功能测试\n")
    
    # 1. 登录
    if not await register_and_login():
        return
    
    # 2. 创建测试图谱
    graph_id = await create_test_graph()
    if not graph_id:
        return
    
    # 3. 创建测试节点
    node_ids = await create_test_nodes(graph_id)
    if not node_ids:
        return
    
    print(f"\n✅ 共创建 {len(node_ids)} 个测试节点")
    
    # 4. 更新向量嵌入
    print("\n⏳ 正在生成向量嵌入（可能需要一些时间）...")
    if not await update_embeddings(graph_id):
        print("⚠️  向量嵌入更新失败，可能是因为未配置 OpenAI API Key")
        print("请在 .env 文件中配置 OPENAI_API_KEY")
        return
    
    # 5. 测试向量搜索
    await test_vector_search()
    
    # 6. 测试相似节点查找
    await test_similar_nodes(node_ids[0])
    
    # 7. 测试节点推荐
    await test_recommendations(node_ids[0])
    
    # 8. 测试节点聚类
    await test_clustering(graph_id)
    
    print("\n" + "="*50)
    print("✅ 所有测试完成！")
    print("="*50)


if __name__ == "__main__":
    asyncio.run(main())

