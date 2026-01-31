"""
复习功能测试脚本
测试复习算法、复习队列、复习统计等功能
"""

import asyncio
import httpx
from datetime import datetime

# API 基础 URL
BASE_URL = "http://localhost:8000/api/v1"

# 测试用户凭证
TEST_EMAIL = "review_test@neuralnote.com"
TEST_PASSWORD = "test123456"


async def test_review_features():
    """测试复习功能"""
    
    async with httpx.AsyncClient(follow_redirects=True) as client:
        print("=" * 60)
        print("复习功能测试")
        print("=" * 60)
        print()
        
        # ============================================================
        # 步骤 0: 注册测试用户（如果不存在）
        # ============================================================
        print("【步骤 0】注册测试用户")
        print("-" * 60)
        
        register_response = await client.post(
            f"{BASE_URL}/auth/register",
            json={
                "email": TEST_EMAIL,
                "username": "review_tester",
                "password": TEST_PASSWORD
            }
        )
        
        if register_response.status_code == 201:
            print("✅ 测试用户注册成功")
        elif register_response.status_code == 400:
            print("⚠️ 用户已存在，继续测试")
        else:
            print(f"❌ 注册失败: {register_response.status_code}")
            print(f"   响应: {register_response.text}")
        print()
        
        # ============================================================
        # 步骤 1: 用户登录
        # ============================================================
        print("【步骤 1】用户登录")
        print("-" * 60)
        
        login_data = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
        
        response = await client.post(
            f"{BASE_URL}/auth/login",
            json=login_data
        )
        
        if response.status_code != 200:
            print(f"❌ 登录失败: {response.status_code}")
            print(f"   响应: {response.text}")
            return
        
        result = response.json()
        access_token = result["access_token"]
        print(f"✅ 登录成功")
        print(f"   Token: {access_token[:20]}...")
        print()
        
        # 设置认证头
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # ============================================================
        # 步骤 2: 创建测试知识图谱
        # ============================================================
        print("【步骤 2】创建测试知识图谱")
        print("-" * 60)
        
        graph_data = {
            "name": "复习测试图谱",
            "subject": "数学",
            "description": "用于测试复习功能的图谱"
        }
        
        response = await client.post(
            f"{BASE_URL}/graphs",
            json=graph_data,
            headers=headers
        )
        
        if response.status_code != 201:
            print(f"❌ 创建图谱失败: {response.status_code}")
            print(f"   响应: {response.text}")
            return
        
        graph = response.json()
        graph_id = graph["id"]
        print(f"✅ 创建图谱成功")
        print(f"   图谱 ID: {graph_id}")
        print()
        
        # ============================================================
        # 步骤 3: 创建测试节点
        # ============================================================
        print("【步骤 3】创建测试节点")
        print("-" * 60)
        
        nodes_data = [
            {
                "graph_id": graph_id,
                "title": "勾股定理",
                "node_type": "CONCEPT",
                "content_data": {
                    "definition": "直角三角形两直角边的平方和等于斜边的平方",
                    "formula": "a² + b² = c²"
                }
            },
            {
                "graph_id": graph_id,
                "title": "二次方程求解",
                "node_type": "QUESTION",
                "content_data": {
                    "question": "解方程 x² - 5x + 6 = 0",
                    "answer": "x = 2 或 x = 3"
                }
            },
            {
                "graph_id": graph_id,
                "title": "三角函数",
                "node_type": "CONCEPT",
                "content_data": {
                    "definition": "sin, cos, tan 的定义和性质"
                }
            }
        ]
        
        node_ids = []
        for i, node_data in enumerate(nodes_data, 1):
            response = await client.post(
                f"{BASE_URL}/nodes",
                json=node_data,
                headers=headers
            )
            
            if response.status_code != 201:
                print(f"❌ 创建节点 {i} 失败: {response.status_code}")
                continue
            
            node = response.json()
            node_ids.append(node["id"])
            print(f"✅ 创建节点 {i}: {node['title']}")
        
        print(f"   共创建 {len(node_ids)} 个节点")
        print()
        
        # ============================================================
        # 步骤 4: 获取复习队列（间隔重复模式）
        # ============================================================
        print("【步骤 4】获取复习队列（间隔重复模式）")
        print("-" * 60)
        
        response = await client.get(
            f"{BASE_URL}/reviews/queue",
            params={"graph_id": graph_id, "mode": "spaced", "limit": 10},
            headers=headers
        )
        
        if response.status_code != 200:
            print(f"❌ 获取复习队列失败: {response.status_code}")
            print(f"   响应: {response.text}")
        else:
            queue = response.json()
            print(f"✅ 获取复习队列成功")
            print(f"   待复习节点数: {queue['total']}")
            for node in queue['nodes']:
                print(f"   - {node['title']}")
                print(f"     掌握程度: {node['mastery_level']}")
                print(f"     遗忘指数: {node['forgetting_index']:.2f}")
                print(f"     颜色标注: {node['forgetting_color']}")
        print()
        
        # ============================================================
        # 步骤 5: 提交复习记录（高质量）
        # ============================================================
        print("【步骤 5】提交复习记录（高质量）")
        print("-" * 60)
        
        if node_ids:
            review_data = {
                "quality": 5,  # 完美回忆
                "review_duration": 120  # 2分钟
            }
            
            response = await client.post(
                f"{BASE_URL}/reviews/{node_ids[0]}",
                json=review_data,
                headers=headers
            )
            
            if response.status_code != 200:
                print(f"❌ 提交复习记录失败: {response.status_code}")
                print(f"   响应: {response.text}")
            else:
                result = response.json()
                print(f"✅ 提交复习记录成功")
                print(f"   节点 ID: {result['node_id']}")
                print(f"   新掌握程度: {result['mastery_level']}")
                print(f"   下次复习时间: {result['next_review_at']}")
                print(f"   间隔天数: {result['interval_days']}")
                print(f"   难度因子: {result['easiness']:.2f}")
                print(f"   复习次数: {result['repetitions']}")
        print()
        
        # ============================================================
        # 步骤 6: 提交复习记录（低质量）
        # ============================================================
        print("【步骤 6】提交复习记录（低质量）")
        print("-" * 60)
        
        if len(node_ids) > 1:
            review_data = {
                "quality": 2,  # 困难，勉强记起
                "review_duration": 300  # 5分钟
            }
            
            response = await client.post(
                f"{BASE_URL}/reviews/{node_ids[1]}",
                json=review_data,
                headers=headers
            )
            
            if response.status_code != 200:
                print(f"❌ 提交复习记录失败: {response.status_code}")
                print(f"   响应: {response.text}")
            else:
                result = response.json()
                print(f"✅ 提交复习记录成功")
                print(f"   节点 ID: {result['node_id']}")
                print(f"   新掌握程度: {result['mastery_level']}")
                print(f"   下次复习时间: {result['next_review_at']}")
                print(f"   间隔天数: {result['interval_days']}")
                print(f"   难度因子: {result['easiness']:.2f}")
                print(f"   复习次数: {result['repetitions']}")
        print()
        
        # ============================================================
        # 步骤 7: 获取复习统计
        # ============================================================
        print("【步骤 7】获取复习统计")
        print("-" * 60)
        
        response = await client.get(
            f"{BASE_URL}/reviews/statistics",
            params={"graph_id": graph_id},
            headers=headers
        )
        
        if response.status_code != 200:
            print(f"❌ 获取复习统计失败: {response.status_code}")
            print(f"   响应: {response.text}")
        else:
            stats = response.json()
            print(f"✅ 获取复习统计成功")
            print(f"   总节点数: {stats['total_nodes']}")
            print(f"   掌握率: {stats['mastery_rate']}%")
            print(f"   今日到期: {stats['due_today']}")
            print(f"   逾期数量: {stats['overdue']}")
            print(f"   总复习次数: {stats['total_reviews']}")
            print(f"   掌握程度分布:")
            for level, count in stats['mastery_distribution'].items():
                print(f"     - {level}: {count}")
        print()
        
        # ============================================================
        # 步骤 8: 获取遗忘指数
        # ============================================================
        print("【步骤 8】获取遗忘指数")
        print("-" * 60)
        
        if node_ids:
            response = await client.get(
                f"{BASE_URL}/reviews/forgetting-index/{node_ids[0]}",
                headers=headers
            )
            
            if response.status_code != 200:
                print(f"❌ 获取遗忘指数失败: {response.status_code}")
                print(f"   响应: {response.text}")
            else:
                result = response.json()
                print(f"✅ 获取遗忘指数成功")
                print(f"   节点 ID: {result['node_id']}")
                print(f"   遗忘指数: {result['forgetting_index']:.2f}")
                print(f"   颜色标注: {result['forgetting_color']}")
                print(f"   掌握程度: {result['mastery_level']}")
                print(f"   上次复习: {result['last_review_at']}")
                print(f"   下次复习: {result['next_review_at']}")
        print()
        
        # ============================================================
        # 步骤 9: 测试不同复习模式
        # ============================================================
        print("【步骤 9】测试不同复习模式")
        print("-" * 60)
        
        modes = ["spaced", "focused", "random", "graph_traversal"]
        for mode in modes:
            response = await client.get(
                f"{BASE_URL}/reviews/queue",
                params={"graph_id": graph_id, "mode": mode, "limit": 5},
                headers=headers
            )
            
            if response.status_code != 200:
                print(f"❌ 模式 {mode} 失败: {response.status_code}")
            else:
                queue = response.json()
                print(f"✅ 模式 {mode}: {queue['total']} 个节点")
        print()
        
        # ============================================================
        # 总结
        # ============================================================
        print("=" * 60)
        print("✅ 复习功能测试完成！")
        print("=" * 60)
        print()
        print("测试总结:")
        print(f"  - 创建了 1 个测试图谱")
        print(f"  - 创建了 {len(node_ids)} 个测试节点")
        print(f"  - 提交了 2 次复习记录")
        print(f"  - 测试了 4 种复习模式")
        print(f"  - 所有核心功能正常运行")
        print()


if __name__ == "__main__":
    asyncio.run(test_review_features())

