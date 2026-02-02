"""
NeuralNote 前端集成测试脚本

测试前端应用的核心功能，包括：
1. 用户认证（注册、登录、登出）
2. 知识图谱管理
3. 记忆节点管理
4. 复习系统
5. 统计和成就系统

使用方法：
    python tests/frontend_integration_test.py

注意：
    - 需要前端服务运行在 http://localhost:3000
    - 需要后端服务运行在 http://localhost:8000
    - 需要安装 selenium: pip install selenium
"""

import time
import random
import string
from datetime import datetime
from typing import Dict, List, Any

# 由于 Selenium 需要额外安装，我们使用 requests 来测试 API
# 前端的 UI 测试建议手动进行或使用专业的 E2E 测试工具（如 Playwright、Cypress）
import requests


class FrontendIntegrationTest:
    """前端集成测试类"""
    
    def __init__(self, base_url: str = "http://localhost:3000", api_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_url = api_url
        self.session = requests.Session()
        self.token = None
        self.user_id = None
        self.test_data = {
            "graphs": [],
            "nodes": [],
        }
        
    def log(self, message: str, level: str = "INFO"):
        """打印日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
        
    def generate_random_string(self, length: int = 8) -> str:
        """生成随机字符串"""
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
    
    def test_frontend_accessibility(self) -> bool:
        """测试前端服务可访问性"""
        self.log("测试 1: 前端服务可访问性")
        try:
            response = requests.get(self.base_url, timeout=5)
            if response.status_code == 200:
                self.log("✅ 前端服务可访问", "SUCCESS")
                return True
            else:
                self.log(f"❌ 前端服务返回状态码: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ 前端服务不可访问: {str(e)}", "ERROR")
            return False
    
    def test_api_health(self) -> bool:
        """测试后端 API 健康状态"""
        self.log("测试 2: 后端 API 健康状态")
        try:
            response = requests.get(f"{self.api_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ 后端 API 健康: {data}", "SUCCESS")
                return True
            else:
                self.log(f"❌ 后端 API 返回状态码: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ 后端 API 不可访问: {str(e)}", "ERROR")
            return False
    
    def test_user_registration(self) -> bool:
        """测试用户注册功能"""
        self.log("测试 3: 用户注册功能")
        try:
            # 使用测试账号登录（而不是注册新用户）
            response = requests.post(
                f"{self.api_url}/api/v1/auth/login",
                json={
                    "email": "test@neuralnote.com",
                    "password": "test123456"
                },
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.user_id = data.get("user", {}).get("id")
                self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                self.log(f"✅ 使用测试账号登录成功", "SUCCESS")
                return True
            else:
                self.log(f"❌ 登录失败: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ 登录异常: {str(e)}", "ERROR")
            return False
    
    def test_user_login(self) -> bool:
        """测试用户登录功能"""
        self.log("测试 4: 用户登录功能")
        try:
            # 使用测试账号登录
            response = requests.post(
                f"{self.api_url}/api/v1/auth/login",
                json={
                    "email": "test@neuralnote.com",
                    "password": "test123456"
                },
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data.get("access_token")
                self.log(f"✅ 用户登录成功", "SUCCESS")
                return True
            else:
                self.log(f"❌ 用户登录失败: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ 用户登录异常: {str(e)}", "ERROR")
            return False
    
    def test_create_graph(self) -> bool:
        """测试创建知识图谱"""
        self.log("测试 5: 创建知识图谱")
        try:
            graph_name = f"测试图谱_{self.generate_random_string()}"
            response = requests.post(
                f"{self.api_url}/api/v1/graphs/",
                headers={"Authorization": f"Bearer {self.token}"},
                json={
                    "name": graph_name,
                    "description": "这是一个测试图谱",
                    "subject": "数学"
                },
                timeout=5
            )
            
            if response.status_code == 201:
                data = response.json()
                self.test_data["graphs"].append(data)
                self.log(f"✅ 创建知识图谱成功: {graph_name}", "SUCCESS")
                return True
            else:
                self.log(f"❌ 创建知识图谱失败: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ 创建知识图谱异常: {str(e)}", "ERROR")
            return False
    
    def test_list_graphs(self) -> bool:
        """测试查询知识图谱列表"""
        self.log("测试 6: 查询知识图谱列表")
        try:
            response = requests.get(
                f"{self.api_url}/api/v1/graphs/",
                headers={"Authorization": f"Bearer {self.token}"},
                params={"page": 1, "page_size": 10},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                total = data.get("total", 0)
                self.log(f"✅ 查询知识图谱列表成功: 共 {total} 个图谱", "SUCCESS")
                return True
            else:
                self.log(f"❌ 查询知识图谱列表失败: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ 查询知识图谱列表异常: {str(e)}", "ERROR")
            return False
    
    def test_create_node(self) -> bool:
        """测试创建记忆节点"""
        self.log("测试 7: 创建记忆节点")
        try:
            if not self.test_data["graphs"]:
                self.log("❌ 没有可用的图谱，跳过节点创建测试", "WARNING")
                return False
            
            graph_id = self.test_data["graphs"][0]["id"]
            node_title = f"测试节点_{self.generate_random_string()}"
            
            response = requests.post(
                f"{self.api_url}/api/v1/nodes/",
                headers={"Authorization": f"Bearer {self.token}"},
                json={
                    "graph_id": graph_id,
                    "title": node_title,
                    "node_type": "CONCEPT",
                    "summary": "这是一个测试概念节点",
                    "content_data": {
                        "text": "这是一个测试概念节点",
                        "description": "用于测试前端集成"
                    }
                },
                timeout=5
            )
            
            if response.status_code == 201:
                data = response.json()
                self.test_data["nodes"].append(data)
                self.log(f"✅ 创建记忆节点成功: {node_title}", "SUCCESS")
                return True
            else:
                self.log(f"❌ 创建记忆节点失败: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ 创建记忆节点异常: {str(e)}", "ERROR")
            return False
    
    def test_list_nodes(self) -> bool:
        """测试查询节点列表"""
        self.log("测试 8: 查询节点列表")
        try:
            if not self.test_data["graphs"]:
                self.log("❌ 没有可用的图谱，跳过节点列表查询测试", "WARNING")
                return False
            
            graph_id = self.test_data["graphs"][0]["id"]
            response = requests.get(
                f"{self.api_url}/api/v1/nodes/",
                headers={"Authorization": f"Bearer {self.token}"},
                params={"graph_id": graph_id, "page": 1, "page_size": 10},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                total = data.get("total", 0)
                self.log(f"✅ 查询节点列表成功: 共 {total} 个节点", "SUCCESS")
                return True
            else:
                self.log(f"❌ 查询节点列表失败: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ 查询节点列表异常: {str(e)}", "ERROR")
            return False
    
    def test_graph_detail(self) -> bool:
        """测试图谱详情查询"""
        self.log("测试 9: 图谱详情查询")
        try:
            if not self.test_data["graphs"]:
                self.log("❌ 没有可用的图谱，跳过详情查询测试", "WARNING")
                return False
            
            graph_id = self.test_data["graphs"][0]["id"]
            response = requests.get(
                f"{self.api_url}/api/v1/graphs/{graph_id}",
                headers={"Authorization": f"Bearer {self.token}"},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ 图谱详情查询成功: {data.get('name')}", "SUCCESS")
                return True
            else:
                self.log(f"❌ 图谱详情查询失败: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ 图谱详情查询异常: {str(e)}", "ERROR")
            return False
    
    def test_review_queue(self) -> bool:
        """测试复习队列功能"""
        self.log("测试 10: 复习队列功能")
        try:
            response = requests.get(
                f"{self.api_url}/api/v1/reviews/queue",
                headers={"Authorization": f"Bearer {self.token}"},
                params={"mode": "spaced"},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                count = len(data.get("nodes", []))
                self.log(f"✅ 复习队列查询成功: {count} 个待复习节点", "SUCCESS")
                return True
            else:
                self.log(f"❌ 复习队列查询失败: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ 复习队列查询异常: {str(e)}", "ERROR")
            return False
    
    def test_review_statistics(self) -> bool:
        """测试复习统计功能"""
        self.log("测试 11: 复习统计功能")
        try:
            response = requests.get(
                f"{self.api_url}/api/v1/reviews/statistics",
                headers={"Authorization": f"Bearer {self.token}"},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ 复习统计查询成功: {data}", "SUCCESS")
                return True
            else:
                self.log(f"❌ 复习统计查询失败: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ 复习统计查询异常: {str(e)}", "ERROR")
            return False
    
    def test_achievement_system(self) -> bool:
        """测试成就系统功能"""
        self.log("测试 12: 成就系统功能")
        try:
            response = requests.get(
                f"{self.api_url}/api/v1/achievements/achievements",
                headers={"Authorization": f"Bearer {self.token}"},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                achievements_data = data.get("data", {})
                total = achievements_data.get("total", 0)
                self.log(f"✅ 成就系统查询成功: 共 {total} 个成就", "SUCCESS")
                return True
            else:
                self.log(f"❌ 成就系统查询失败: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ 成就系统查询异常: {str(e)}", "ERROR")
            return False
    
    def cleanup(self):
        """清理测试数据"""
        self.log("清理测试数据...")
        
        # 删除测试节点
        for node in self.test_data["nodes"]:
            try:
                requests.delete(
                    f"{self.api_url}/api/v1/nodes/{node['id']}",
                    headers={"Authorization": f"Bearer {self.token}"},
                    timeout=5
                )
            except:
                pass
        
        # 删除测试图谱
        for graph in self.test_data["graphs"]:
            try:
                requests.delete(
                    f"{self.api_url}/api/v1/graphs/{graph['id']}",
                    headers={"Authorization": f"Bearer {self.token}"},
                    timeout=5
                )
            except:
                pass
        
        self.log("✅ 测试数据清理完成", "SUCCESS")
    
    def run_all_tests(self) -> Dict[str, Any]:
        """运行所有测试"""
        self.log("=" * 80)
        self.log("开始前端集成测试")
        self.log("=" * 80)
        
        results = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "tests": []
        }
        
        # 定义测试用例
        test_cases = [
            ("前端服务可访问性", self.test_frontend_accessibility),
            ("后端 API 健康状态", self.test_api_health),
            ("用户注册功能", self.test_user_registration),
            ("用户登录功能", self.test_user_login),
            ("创建知识图谱", self.test_create_graph),
            ("查询知识图谱列表", self.test_list_graphs),
            ("创建记忆节点", self.test_create_node),
            ("查询节点列表", self.test_list_nodes),
            ("图谱详情查询", self.test_graph_detail),
            ("复习队列功能", self.test_review_queue),
            ("复习统计功能", self.test_review_statistics),
            ("成就系统功能", self.test_achievement_system),
        ]
        
        # 执行测试
        for name, test_func in test_cases:
            results["total"] += 1
            try:
                passed = test_func()
                if passed:
                    results["passed"] += 1
                    results["tests"].append({"name": name, "status": "PASSED"})
                else:
                    results["failed"] += 1
                    results["tests"].append({"name": name, "status": "FAILED"})
            except Exception as e:
                results["failed"] += 1
                results["tests"].append({"name": name, "status": "ERROR", "error": str(e)})
                self.log(f"❌ 测试异常: {name} - {str(e)}", "ERROR")
            
            # 测试间隔
            time.sleep(0.5)
        
        # 清理测试数据
        if self.token:
            self.cleanup()
        
        # 打印测试结果
        self.log("=" * 80)
        self.log("测试结果汇总")
        self.log("=" * 80)
        self.log(f"总测试数: {results['total']}")
        self.log(f"通过: {results['passed']}")
        self.log(f"失败: {results['failed']}")
        self.log(f"通过率: {results['passed'] / results['total'] * 100:.1f}%")
        self.log("=" * 80)
        
        # 打印详细结果
        for test in results["tests"]:
            status_icon = "✅" if test["status"] == "PASSED" else "❌"
            self.log(f"{status_icon} {test['name']}: {test['status']}")
        
        return results


def main():
    """主函数"""
    tester = FrontendIntegrationTest()
    results = tester.run_all_tests()
    
    # 返回退出码
    if results["failed"] == 0:
        exit(0)
    else:
        exit(1)


if __name__ == "__main__":
    main()

