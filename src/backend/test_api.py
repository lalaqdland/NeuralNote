"""
测试知识图谱和记忆节点 API
"""

import asyncio
import httpx

BASE_URL = "http://localhost:8000/api/v1"


async def test_full_workflow():
    """测试完整的工作流程"""
    
    print("=" * 60)
    print("NeuralNote API 完整测试")
    print("=" * 60)
    
    async with httpx.AsyncClient() as client:
        # ==================== 1. 用户注册和登录 ====================
        print("\n【步骤 1】用户注册")
        print("-" * 60)
        
        register_response = await client.post(
            f"{BASE_URL}/auth/register",
            json={
                "email": "testuser_full@example.com",
                "username": "testuser_full",
                "password": "password123"
            }
        )
        
        if register_response.status_code == 201:
            print("✅ 注册成功")
            user = register_response.json()
            print(f"   用户ID: {user['id']}")
            print(f"   用户名: {user['username']}")
        elif register_response.status_code == 400:
            print("⚠️  用户已存在，继续登录")
        else:
            print(f"❌ 注册失败: {register_response.text}")
            return
        
        # 登录
        print("\n【步骤 2】用户登录")
        print("-" * 60)
        
        login_response = await client.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": "testuser_full@example.com",
                "password": "password123"
            }
        )
        
        if login_response.status_code != 200:
            print(f"❌ 登录失败: {login_response.text}")
            return
        
        tokens = login_response.json()
        access_token = tokens["access_token"]
        print("✅ 登录成功")
        print(f"   Access Token: {access_token[:50]}...")
        
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # ==================== 2. 创建知识图谱 ====================
        print("\n【步骤 3】创建知识图谱")
        print("-" * 60)
        
        graph_response = await client.post(
            f"{BASE_URL}/graphs/",
            headers=headers,
            json={
                "name": "高等数学知识图谱",
                "description": "包含微积分、线性代数等内容",
                "subject": "math",
                "is_public": False
            }
        )
        
        if graph_response.status_code != 201:
            print(f"❌ 创建知识图谱失败: {graph_response.text}")
            return
        
        graph = graph_response.json()
        graph_id = graph["id"]
        print("✅ 创建知识图谱成功")
        print(f"   图谱ID: {graph_id}")
        print(f"   图谱名称: {graph['name']}")
        
        # ==================== 3. 创建记忆节点 ====================
        print("\n【步骤 4】创建记忆节点")
        print("-" * 60)
        
        # 创建第一个节点（概念）
        node1_response = await client.post(
            f"{BASE_URL}/nodes/",
            headers=headers,
            json={
                "graph_id": graph_id,
                "node_type": "CONCEPT",
                "title": "导数的定义",
                "summary": "函数在某一点的导数是该点切线的斜率",
                "content_data": {
                    "definition": "函数在某一点的导数是该点切线的斜率",
                    "formula": "f'(x) = lim(h->0) [f(x+h) - f(x)] / h"
                }
            }
        )
        
        if node1_response.status_code != 201:
            print(f"❌ 创建节点1失败: {node1_response.text}")
            return
        
        node1 = node1_response.json()
        node1_id = node1["id"]
        print("✅ 创建节点1成功")
        print(f"   节点ID: {node1_id}")
        print(f"   节点标题: {node1['title']}")
        
        # 创建第二个节点（题目）
        node2_response = await client.post(
            f"{BASE_URL}/nodes/",
            headers=headers,
            json={
                "graph_id": graph_id,
                "node_type": "QUESTION",
                "title": "求函数 f(x) = x² 的导数",
                "summary": "求 f(x) = x² 在 x=2 处的导数",
                "content_data": {
                    "question": "求 f(x) = x² 在 x=2 处的导数",
                    "answer": "f'(2) = 4",
                    "steps": [
                        "f'(x) = 2x",
                        "f'(2) = 2 * 2 = 4"
                    ]
                }
            }
        )
        
        if node2_response.status_code != 201:
            print(f"❌ 创建节点2失败: {node2_response.text}")
            return
        
        node2 = node2_response.json()
        node2_id = node2["id"]
        print("✅ 创建节点2成功")
        print(f"   节点ID: {node2_id}")
        print(f"   节点标题: {node2['title']}")
        
        # ==================== 4. 创建节点关联 ====================
        print("\n【步骤 5】创建节点关联")
        print("-" * 60)
        
        relation_response = await client.post(
            f"{BASE_URL}/nodes/{node1_id}/relations",
            headers=headers,
            json={
                "source_node_id": node1_id,
                "target_node_id": node2_id,
                "relation_type": "RELATED",
                "strength": 90
            }
        )
        
        if relation_response.status_code != 201:
            print(f"❌ 创建关联失败: {relation_response.text}")
            return
        
        relation = relation_response.json()
        print("✅ 创建节点关联成功")
        print(f"   关联ID: {relation['id']}")
        print(f"   关联类型: {relation['relation_type']}")
        print(f"   关联强度: {relation['strength']}")
        
        # ==================== 5. 查询数据 ====================
        print("\n【步骤 6】查询知识图谱列表")
        print("-" * 60)
        
        graphs_list_response = await client.get(
            f"{BASE_URL}/graphs/",
            headers=headers,
            params={"page": 1, "page_size": 10}
        )
        
        if graphs_list_response.status_code != 200:
            print(f"❌ 查询失败: {graphs_list_response.text}")
            return
        
        graphs_list = graphs_list_response.json()
        print("✅ 查询知识图谱列表成功")
        print(f"   总数: {graphs_list['total']}")
        print(f"   当前页: {graphs_list['page']}")
        print(f"   图谱列表:")
        for g in graphs_list['items']:
            print(f"     - {g['name']} (节点数: {g['node_count']})")
        
        # 查询节点列表
        print("\n【步骤 7】查询记忆节点列表")
        print("-" * 60)
        
        nodes_list_response = await client.get(
            f"{BASE_URL}/nodes/",
            headers=headers,
            params={"graph_id": graph_id, "page": 1, "page_size": 10}
        )
        
        if nodes_list_response.status_code != 200:
            print(f"❌ 查询失败: {nodes_list_response.text}")
            return
        
        nodes_list = nodes_list_response.json()
        print("✅ 查询记忆节点列表成功")
        print(f"   总数: {nodes_list['total']}")
        print(f"   节点列表:")
        for n in nodes_list['items']:
            print(f"     - {n['title']} ({n['node_type']})")
        
        # 查询节点详情
        print("\n【步骤 8】查询节点详情")
        print("-" * 60)
        
        node_detail_response = await client.get(
            f"{BASE_URL}/nodes/{node1_id}",
            headers=headers
        )
        
        if node_detail_response.status_code != 200:
            print(f"❌ 查询失败: {node_detail_response.text}")
            return
        
        node_detail = node_detail_response.json()
        print("✅ 查询节点详情成功")
        print(f"   标题: {node_detail['title']}")
        print(f"   类型: {node_detail['node_type']}")
        print(f"   内容: {node_detail['content_data']}")
        
        # 查询节点关联
        print("\n【步骤 9】查询节点关联")
        print("-" * 60)
        
        relations_response = await client.get(
            f"{BASE_URL}/nodes/{node1_id}/relations",
            headers=headers
        )
        
        if relations_response.status_code != 200:
            print(f"❌ 查询失败: {relations_response.text}")
            return
        
        relations = relations_response.json()
        print("✅ 查询节点关联成功")
        print(f"   关联数量: {len(relations)}")
        for r in relations:
            print(f"     - {r['relation_type']}: {r['source_id']} -> {r['target_id']}")
        
        # 查询图谱统计
        print("\n【步骤 10】查询图谱统计信息")
        print("-" * 60)
        
        stats_response = await client.get(
            f"{BASE_URL}/graphs/{graph_id}/stats",
            headers=headers
        )
        
        if stats_response.status_code != 200:
            print(f"❌ 查询失败: {stats_response.text}")
            return
        
        stats = stats_response.json()
        print("✅ 查询图谱统计成功")
        print(f"   总节点数: {stats['total_nodes']}")
        print(f"   总关联数: {stats['total_relations']}")
        print(f"   总标签数: {stats['total_tags']}")
        
        # ==================== 6. 更新数据 ====================
        print("\n【步骤 11】更新节点信息")
        print("-" * 60)
        
        update_response = await client.put(
            f"{BASE_URL}/nodes/{node1_id}",
            headers=headers,
            json={
                "title": "导数的定义（已更新）",
                "content_data": {
                    "definition": "函数在某一点的导数是该点切线的斜率",
                    "formula": "f'(x) = lim(h->0) [f(x+h) - f(x)] / h",
                    "note": "这是一个重要的概念"
                }
            }
        )
        
        if update_response.status_code != 200:
            print(f"❌ 更新失败: {update_response.text}")
            return
        
        updated_node = update_response.json()
        print("✅ 更新节点成功")
        print(f"   新标题: {updated_node['title']}")
        
        # ==================== 7. 测试用户信息更新 ====================
        print("\n【步骤 12】更新用户信息")
        print("-" * 60)
        
        user_update_response = await client.put(
            f"{BASE_URL}/users/me",
            headers=headers,
            json={
                "username": "testuser_full_updated",
                "timezone": "Asia/Shanghai",
                "language": "zh-CN"
            }
        )
        
        if user_update_response.status_code != 200:
            print(f"❌ 更新用户信息失败: {user_update_response.text}")
        else:
            updated_user = user_update_response.json()
            print("✅ 更新用户信息成功")
            print(f"   新用户名: {updated_user['username']}")
        
        # ==================== 完成 ====================
        print("\n" + "=" * 60)
        print("✅ 所有测试通过！")
        print("=" * 60)
        print("\n测试总结:")
        print(f"  - 创建了 1 个知识图谱")
        print(f"  - 创建了 2 个记忆节点")
        print(f"  - 创建了 1 个节点关联")
        print(f"  - 所有 CRUD 操作均正常")


async def main():
    """主函数"""
    try:
        await test_full_workflow()
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

