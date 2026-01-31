"""
测试所有复习模式
"""

import asyncio
import sys
from datetime import datetime, timedelta
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

import httpx

# API 配置
BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}/api/v1"

# 测试用户凭证
TEST_EMAIL = "test@neuralnote.com"
TEST_PASSWORD = "test123456"


class ReviewModeTester:
    """复习模式测试器"""
    
    def __init__(self):
        self.token = None
        self.user_id = None
        self.graph_id = None
        self.node_ids = []
    
    async def login(self):
        """登录获取 Token"""
        print("\n" + "="*60)
        print("1. 用户登录")
        print("="*60)
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            # 登录获取 Token
            response = await client.post(
                f"{API_V1}/auth/login",
                json={
                    "email": TEST_EMAIL,
                    "password": TEST_PASSWORD
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data["access_token"]
                print(f"✅ 登录成功")
                print(f"   Token: {self.token[:20]}...")
                
                # 获取用户信息
                response = await client.get(
                    f"{API_V1}/auth/me",
                    headers={"Authorization": f"Bearer {self.token}"}
                )
                
                if response.status_code == 200:
                    user_data = response.json()
                    self.user_id = user_data["id"]
                    print(f"   用户ID: {self.user_id}")
                    return True
                else:
                    print(f"❌ 获取用户信息失败: {response.status_code}")
                    return False
            else:
                print(f"❌ 登录失败: {response.status_code}")
                print(f"   响应: {response.text}")
                return False
    
    def get_headers(self):
        """获取请求头"""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    async def create_test_graph(self):
        """创建测试知识图谱"""
        print("\n" + "="*60)
        print("2. 创建测试知识图谱")
        print("="*60)
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.post(
                f"{API_V1}/graphs/",
                headers=self.get_headers(),
                json={
                    "name": "复习模式测试图谱",
                    "subject": "数学",
                    "description": "用于测试各种复习模式"
                }
            )
            
            if response.status_code == 201:
                data = response.json()
                self.graph_id = data["id"]
                print(f"✅ 创建成功")
                print(f"   图谱ID: {self.graph_id}")
                print(f"   图谱名称: {data['name']}")
                return True
            else:
                print(f"❌ 创建失败: {response.status_code}")
                print(f"   响应: {response.text}")
                return False
    
    async def create_test_nodes(self):
        """创建测试节点（不同掌握程度）"""
        print("\n" + "="*60)
        print("3. 创建测试节点")
        print("="*60)
        
        # 创建不同掌握程度的节点
        test_nodes = [
            {
                "title": "未开始学习的节点",
                "node_type": "CONCEPT",
                "mastery_level": "NOT_STARTED",
                "content_data": {"text": "这是一个未开始学习的概念"}
            },
            {
                "title": "学习中的节点1",
                "node_type": "QUESTION",
                "mastery_level": "LEARNING",
                "content_data": {"text": "这是一个正在学习的题目"}
            },
            {
                "title": "学习中的节点2",
                "node_type": "CONCEPT",
                "mastery_level": "LEARNING",
                "content_data": {"text": "这是另一个正在学习的概念"}
            },
            {
                "title": "熟悉的节点",
                "node_type": "QUESTION",
                "mastery_level": "FAMILIAR",
                "content_data": {"text": "这是一个熟悉的题目"}
            },
            {
                "title": "精通的节点",
                "node_type": "CONCEPT",
                "mastery_level": "PROFICIENT",
                "content_data": {"text": "这是一个精通的概念"}
            },
            {
                "title": "已掌握的节点",
                "node_type": "QUESTION",
                "mastery_level": "MASTERED",
                "content_data": {"text": "这是一个已掌握的题目"}
            }
        ]
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            for i, node_data in enumerate(test_nodes, 1):
                response = await client.post(
                    f"{API_V1}/nodes/",
                    headers=self.get_headers(),
                    json={
                        **node_data,
                        "graph_id": self.graph_id,
                        "user_id": self.user_id
                    }
                )
                
                if response.status_code == 201:
                    data = response.json()
                    self.node_ids.append(data["id"])
                    print(f"✅ 节点 {i}: {node_data['title']}")
                    print(f"   ID: {data['id']}")
                    print(f"   类型: {data['node_type']}")
                else:
                    print(f"❌ 创建失败: {response.status_code}")
                    print(f"   响应: {response.text}")
                    return False
        
        print(f"\n✅ 共创建 {len(self.node_ids)} 个测试节点")
        return True
    
    async def set_review_times(self):
        """设置节点的复习时间（模拟不同的复习状态）"""
        print("\n" + "="*60)
        print("4. 设置节点复习时间")
        print("="*60)
        
        now = datetime.utcnow()
        
        # 为不同节点设置不同的复习时间
        review_configs = [
            {"last": now - timedelta(days=5), "next": now - timedelta(days=2)},  # 已过期2天
            {"last": now - timedelta(days=3), "next": now - timedelta(hours=1)},  # 已过期1小时
            {"last": now - timedelta(days=1), "next": now},  # 今天到期
            {"last": now - timedelta(hours=12), "next": now + timedelta(hours=12)},  # 今天到期
            {"last": now - timedelta(days=2), "next": now + timedelta(days=1)},  # 明天到期
            {"last": now - timedelta(days=7), "next": now + timedelta(days=7)}  # 一周后到期
        ]
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            for i, (node_id, config) in enumerate(zip(self.node_ids, review_configs), 1):
                response = await client.put(
                    f"{API_V1}/nodes/{node_id}",
                    headers=self.get_headers(),
                    json={
                        "last_review_at": config["last"].isoformat(),
                        "next_review_at": config["next"].isoformat(),
                        "review_stats": {
                            "repetitions": i,
                            "easiness": 2.5,
                            "interval": i,
                            "total_reviews": i
                        }
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ 节点 {i}: 复习时间已设置")
                    print(f"   上次复习: {config['last'].strftime('%Y-%m-%d %H:%M')}")
                    print(f"   下次复习: {config['next'].strftime('%Y-%m-%d %H:%M')}")
                else:
                    print(f"❌ 更新失败: {response.status_code}")
                    print(f"   响应: {response.text}")
        
        print(f"\n✅ 复习时间设置完成")
        return True
    
    async def test_review_statistics(self):
        """测试复习统计"""
        print("\n" + "="*60)
        print("5. 测试复习统计")
        print("="*60)
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(
                f"{API_V1}/reviews/statistics",
                headers=self.get_headers(),
                params={"graph_id": self.graph_id}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 统计查询成功")
                print(f"\n📊 统计数据:")
                print(f"   总节点数: {data['total_nodes']}")
                print(f"   掌握率: {data['mastery_rate']}%")
                print(f"   今日到期: {data['due_today']}")
                print(f"   已过期: {data['overdue']}")
                print(f"   总复习次数: {data['total_reviews']}")
                print(f"\n📈 掌握程度分布:")
                for level, count in data['mastery_distribution'].items():
                    print(f"   {level}: {count}")
                return True
            else:
                print(f"❌ 查询失败: {response.status_code}")
                print(f"   响应: {response.text}")
                return False
    
    async def test_review_mode(self, mode: str, mode_name: str):
        """测试指定的复习模式"""
        print("\n" + "="*60)
        print(f"测试复习模式: {mode_name} ({mode})")
        print("="*60)
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(
                f"{API_V1}/reviews/queue",
                headers=self.get_headers(),
                params={
                    "graph_id": self.graph_id,
                    "mode": mode,
                    "limit": 10
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                nodes = data.get("nodes", [])
                print(f"✅ 查询成功，返回 {len(nodes)} 个节点")
                
                if len(nodes) > 0:
                    print(f"\n📋 复习队列:")
                    for i, node in enumerate(nodes, 1):
                        print(f"\n   {i}. {node['title']}")
                        print(f"      节点ID: {node['node_id']}")
                        print(f"      类型: {node['node_type']}")
                        print(f"      掌握程度: {node['mastery_level']}")
                        print(f"      遗忘指数: {node['forgetting_index']:.2f}")
                        print(f"      遗忘颜色: {node['forgetting_color']}")
                        if node['last_review_at']:
                            print(f"      上次复习: {node['last_review_at']}")
                        if node['next_review_at']:
                            print(f"      下次复习: {node['next_review_at']}")
                else:
                    print(f"\n⚠️  复习队列为空")
                
                return True
            else:
                print(f"❌ 查询失败: {response.status_code}")
                print(f"   响应: {response.text}")
                return False
    
    async def test_all_modes(self):
        """测试所有复习模式"""
        modes = [
            ("spaced", "间隔重复模式"),
            ("focused", "集中攻克模式"),
            ("random", "随机抽查模式"),
            ("graph_traversal", "图谱遍历模式")
        ]
        
        results = {}
        for mode, mode_name in modes:
            success = await self.test_review_mode(mode, mode_name)
            results[mode] = success
            await asyncio.sleep(0.5)  # 避免请求过快
        
        return results
    
    async def test_review_submission(self):
        """测试提交复习结果"""
        print("\n" + "="*60)
        print("6. 测试提交复习结果")
        print("="*60)
        
        if not self.node_ids:
            print("❌ 没有可用的测试节点")
            return False
        
        # 选择第一个节点进行复习
        node_id = self.node_ids[0]
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            # 提交复习结果（质量评分：4 - 容易）
            response = await client.post(
                f"{API_V1}/reviews/{node_id}",
                headers=self.get_headers(),
                json={
                    "quality": 4,
                    "review_duration": 60
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 复习提交成功")
                print(f"\n📝 复习结果:")
                print(f"   节点ID: {data['node_id']}")
                print(f"   新掌握程度: {data['mastery_level']}")
                print(f"   下次复习时间: {data['next_review_at']}")
                print(f"   间隔天数: {data['interval_days']}")
                print(f"   难度因子: {data['easiness']}")
                print(f"   复习次数: {data['repetitions']}")
                return True
            else:
                print(f"❌ 提交失败: {response.status_code}")
                print(f"   响应: {response.text}")
                return False
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("\n" + "🚀"*30)
        print("开始测试所有复习模式")
        print("🚀"*30)
        
        # 1. 登录
        if not await self.login():
            return False
        
        # 2. 创建测试图谱
        if not await self.create_test_graph():
            return False
        
        # 3. 创建测试节点
        if not await self.create_test_nodes():
            return False
        
        # 4. 设置复习时间
        if not await self.set_review_times():
            return False
        
        # 5. 测试复习统计
        if not await self.test_review_statistics():
            return False
        
        # 6. 测试所有复习模式
        results = await self.test_all_modes()
        
        # 7. 测试提交复习结果
        await self.test_review_submission()
        
        # 8. 再次查看统计（验证更新）
        print("\n" + "="*60)
        print("7. 验证统计数据更新")
        print("="*60)
        await self.test_review_statistics()
        
        # 总结
        print("\n" + "="*60)
        print("测试总结")
        print("="*60)
        
        all_passed = all(results.values())
        
        for mode, success in results.items():
            status = "✅ 通过" if success else "❌ 失败"
            print(f"{status} - {mode}")
        
        if all_passed:
            print("\n🎉 所有测试通过！")
        else:
            print("\n⚠️  部分测试失败，请检查日志")
        
        return all_passed


async def main():
    """主函数"""
    tester = ReviewModeTester()
    success = await tester.run_all_tests()
    
    if success:
        print("\n✅ 测试完成")
        return 0
    else:
        print("\n❌ 测试失败")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

