"""
简化版端到端测试 - 专注于核心功能验证
"""
import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

class SimpleE2ETest:
    def __init__(self):
        self.token = None
        self.user_id = None
        self.graph_id = None
        self.node_ids = []
        self.passed = 0
        self.failed = 0
        
    def log(self, message, status="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        symbol = {"PASS": "✅", "FAIL": "❌", "INFO": "ℹ️"}.get(status, "•")
        print(f"[{timestamp}] {symbol} {message}")
    
    def test(self, name, func):
        """运行单个测试"""
        try:
            self.log(f"测试: {name}", "INFO")
            func()
            self.log(f"通过: {name}", "PASS")
            self.passed += 1
            return True
        except AssertionError as e:
            self.log(f"失败: {name} - {e}", "FAIL")
            self.failed += 1
            return False
        except Exception as e:
            self.log(f"错误: {name} - {e}", "FAIL")
            self.failed += 1
            return False
    
    def run_all(self):
        """运行所有测试"""
        self.log("=" * 60, "INFO")
        self.log("开始端到端测试", "INFO")
        self.log("=" * 60, "INFO")
        
        # 1. 健康检查
        self.test("1. 基础健康检查", self.test_health)
        self.test("2. 数据库连接检查", self.test_database)
        
        # 2. 用户认证
        if self.test("3. 用户注册", self.test_register):
            self.test("4. 用户登录", self.test_login)
        
        # 3. 知识图谱
        if self.token:
            self.test("5. 创建知识图谱", self.test_create_graph)
            self.test("6. 查询图谱列表", self.test_list_graphs)
            
            # 4. 记忆节点
            if self.graph_id:
                self.test("7. 创建概念节点", self.test_create_concept)
                self.test("8. 创建题目节点", self.test_create_question)
                self.test("9. 查询节点列表", self.test_list_nodes)
                
                # 5. 节点关联
                if len(self.node_ids) >= 2:
                    self.test("10. 创建节点关联", self.test_create_relation)
                
                # 6. 复习系统
                if len(self.node_ids) > 0:
                    self.test("11. 获取复习队列", self.test_review_queue)
                    self.test("12. 提交复习记录", self.test_submit_review)
                
                # 7. 清理
                self.test("13. 删除测试数据", self.test_cleanup)
        
        # 输出报告
        self.print_report()
    
    def test_health(self):
        """测试健康检查"""
        r = requests.get(f"{BASE_URL}/health")
        assert r.status_code == 200, f"状态码: {r.status_code}"
        data = r.json()
        assert data["status"] == "healthy", f"服务状态: {data['status']}"
    
    def test_database(self):
        """测试数据库连接"""
        r = requests.get(f"{BASE_URL}/api/v1/health/database")
        assert r.status_code == 200, f"状态码: {r.status_code}"
        data = r.json()
        assert data["status"] in ["healthy", "connected"], f"数据库状态: {data['status']}"
    
    def test_register(self):
        """测试用户注册"""
        ts = int(time.time())
        user_data = {
            "email": f"e2e_test_{ts}@test.com",
            "username": f"e2e_test_{ts}",
            "password": "test123456"
        }
        r = requests.post(f"{BASE_URL}/api/v1/auth/register", json=user_data)
        assert r.status_code == 201, f"状态码: {r.status_code}, 响应: {r.text}"
        data = r.json()
        self.user_id = data["id"]
        self.log(f"  用户ID: {self.user_id}")
    
    def test_login(self):
        """测试用户登录"""
        # 使用已存在的测试账号
        login_data = {
            "email": "test@neuralnote.com",
            "password": "test123456"
        }
        r = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data)
        
        # 如果账号不存在，先注册
        if r.status_code == 401:
            reg_data = {
                "email": "test@neuralnote.com",
                "username": "test_user",
                "password": "test123456"
            }
            r = requests.post(f"{BASE_URL}/api/v1/auth/register", json=reg_data)
            assert r.status_code == 201, f"注册失败: {r.text}"
            # 注册后再登录
            r = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data)
        
        assert r.status_code == 200, f"状态码: {r.status_code}, 响应: {r.text}"
        data = r.json()
        self.token = data["access_token"]
        self.log(f"  Token: {self.token[:30]}...")
    
    def test_create_graph(self):
        """测试创建知识图谱"""
        graph_data = {
            "name": f"E2E测试图谱_{int(time.time())}",
            "description": "端到端测试创建的图谱",
            "subject": "数学"
        }
        headers = {"Authorization": f"Bearer {self.token}"}
        r = requests.post(f"{BASE_URL}/api/v1/graphs", json=graph_data, headers=headers)
        assert r.status_code == 201, f"状态码: {r.status_code}, 响应: {r.text}"
        data = r.json()
        self.graph_id = data["id"]
        self.log(f"  图谱ID: {self.graph_id}")
    
    def test_list_graphs(self):
        """测试查询图谱列表"""
        headers = {"Authorization": f"Bearer {self.token}"}
        r = requests.get(f"{BASE_URL}/api/v1/graphs", headers=headers)
        assert r.status_code == 200, f"状态码: {r.status_code}"
        data = r.json()
        assert "items" in data, "响应缺少 items"
        assert data["total"] > 0, "图谱列表为空"
        self.log(f"  图谱总数: {data['total']}")
    
    def test_create_concept(self):
        """测试创建概念节点"""
        node_data = {
            "graph_id": self.graph_id,
            "node_type": "CONCEPT",
            "title": "二次函数",
            "content_data": {
                "definition": "形如 y = ax² + bx + c 的函数"
            },
            "tags": ["数学", "函数"]
        }
        headers = {"Authorization": f"Bearer {self.token}"}
        r = requests.post(f"{BASE_URL}/api/v1/nodes", json=node_data, headers=headers)
        assert r.status_code == 201, f"状态码: {r.status_code}, 响应: {r.text}"
        data = r.json()
        self.node_ids.append(data["id"])
        self.log(f"  节点ID: {data['id']}")
    
    def test_create_question(self):
        """测试创建题目节点"""
        node_data = {
            "graph_id": self.graph_id,
            "node_type": "QUESTION",
            "title": "求二次函数顶点",
            "content_data": {
                "question": "求 y = 2x² - 4x + 1 的顶点坐标",
                "answer": "(1, -1)"
            },
            "tags": ["数学", "二次函数"]
        }
        headers = {"Authorization": f"Bearer {self.token}"}
        r = requests.post(f"{BASE_URL}/api/v1/nodes", json=node_data, headers=headers)
        assert r.status_code == 201, f"状态码: {r.status_code}, 响应: {r.text}"
        data = r.json()
        self.node_ids.append(data["id"])
        self.log(f"  节点ID: {data['id']}")
    
    def test_list_nodes(self):
        """测试查询节点列表"""
        headers = {"Authorization": f"Bearer {self.token}"}
        r = requests.get(f"{BASE_URL}/api/v1/nodes?graph_id={self.graph_id}", headers=headers)
        assert r.status_code == 200, f"状态码: {r.status_code}"
        data = r.json()
        assert data["total"] >= 2, f"节点数量不足: {data['total']}"
        self.log(f"  节点总数: {data['total']}")
    
    def test_create_relation(self):
        """测试创建节点关联"""
        relation_data = {
            "source_node_id": self.node_ids[0],
            "target_node_id": self.node_ids[1],
            "relation_type": "prerequisite",
            "strength": 8  # 改为整数 (0-10)
        }
        headers = {"Authorization": f"Bearer {self.token}"}
        # 使用第一个节点的ID作为路径参数
        r = requests.post(f"{BASE_URL}/api/v1/nodes/{self.node_ids[0]}/relations", json=relation_data, headers=headers)
        assert r.status_code == 201, f"状态码: {r.status_code}, 响应: {r.text}"
        self.log(f"  关联创建成功")
    
    def test_review_queue(self):
        """测试获取复习队列"""
        headers = {"Authorization": f"Bearer {self.token}"}
        r = requests.get(f"{BASE_URL}/api/v1/reviews/queue?graph_id={self.graph_id}", headers=headers)
        assert r.status_code == 200, f"状态码: {r.status_code}, 响应: {r.text}"
        data = r.json()
        self.log(f"  待复习节点: {len(data.get('items', []))}")
    
    def test_submit_review(self):
        """测试提交复习记录"""
        review_data = {
            "quality": 4,  # 修正字段名
            "review_duration": 120  # 修正字段名
        }
        headers = {"Authorization": f"Bearer {self.token}"}
        # 使用节点ID作为路径参数
        r = requests.post(f"{BASE_URL}/api/v1/reviews/{self.node_ids[0]}", json=review_data, headers=headers)
        assert r.status_code == 200, f"状态码: {r.status_code}, 响应: {r.text}"
        self.log(f"  复习记录已提交")
    
    def test_cleanup(self):
        """测试清理数据"""
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # 删除节点
        for node_id in self.node_ids:
            r = requests.delete(f"{BASE_URL}/api/v1/nodes/{node_id}", headers=headers)
            assert r.status_code == 204, f"删除节点失败: {r.status_code}"
        
        # 删除图谱
        r = requests.delete(f"{BASE_URL}/api/v1/graphs/{self.graph_id}", headers=headers)
        assert r.status_code == 204, f"删除图谱失败: {r.status_code}"
        
        self.log(f"  清理完成")
    
    def print_report(self):
        """打印测试报告"""
        total = self.passed + self.failed
        pass_rate = (self.passed / total * 100) if total > 0 else 0
        
        self.log("=" * 60, "INFO")
        self.log("测试报告", "INFO")
        self.log("=" * 60, "INFO")
        self.log(f"总测试数: {total}", "INFO")
        self.log(f"通过: {self.passed}", "PASS")
        self.log(f"失败: {self.failed}", "FAIL")
        self.log(f"通过率: {pass_rate:.1f}%", "INFO")
        self.log("=" * 60, "INFO")


if __name__ == "__main__":
    # 检查后端服务
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=5)
        if r.status_code != 200:
            print("❌ 后端服务未运行")
            exit(1)
    except:
        print("❌ 无法连接到后端服务")
        exit(1)
    
    # 运行测试
    test = SimpleE2ETest()
    test.run_all()

