# 测试套件

NeuralNote 后端的完整测试套件，使用 pytest 框架。

## 测试结构

```
tests/
├── __init__.py
├── conftest.py              # pytest 配置和共享 fixtures
├── test_auth.py             # 用户认证测试
├── test_knowledge_graphs.py # 知识图谱测试
├── test_memory_nodes.py     # 记忆节点测试
└── test_users.py            # 用户管理测试
```

## 快速开始

### 1. 安装测试依赖

```bash
pip install pytest pytest-asyncio pytest-cov httpx
```

### 2. 创建测试数据库

在 PostgreSQL 中创建测试数据库：

```sql
CREATE DATABASE neuralnote_test;
```

### 3. 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_auth.py

# 运行特定测试类
pytest tests/test_auth.py::TestUserRegistration

# 运行特定测试函数
pytest tests/test_auth.py::TestUserRegistration::test_register_success

# 显示详细输出
pytest -v

# 显示打印输出
pytest -s
```

### 4. 生成覆盖率报告

```bash
# 生成终端覆盖率报告
pytest --cov=app --cov-report=term

# 生成 HTML 覆盖率报告
pytest --cov=app --cov-report=html

# 查看 HTML 报告
# 打开 htmlcov/index.html
```

## 使用测试脚本

```bash
# 运行所有测试
python run_tests.py all

# 运行测试并生成覆盖率报告
python run_tests.py coverage

# 运行特定模块测试
python run_tests.py auth      # 认证测试
python run_tests.py graphs    # 知识图谱测试
python run_tests.py nodes     # 记忆节点测试
python run_tests.py users     # 用户管理测试
```

## 测试覆盖范围

### 用户认证 (test_auth.py)

- ✅ 用户注册（成功、重复邮箱、重复用户名、无效邮箱、密码过短）
- ✅ 用户登录（成功、错误密码、不存在的用户）
- ✅ Token 操作（获取当前用户、无效 Token、刷新 Token）
- ✅ 密码操作（修改密码、旧密码错误）

### 知识图谱 (test_knowledge_graphs.py)

- ✅ 创建图谱（成功、未认证、缺少字段）
- ✅ 查询图谱（列表、分页、详情、不存在、统计信息）
- ✅ 更新图谱（成功、不存在、部分更新）
- ✅ 删除图谱（成功、不存在）
- ✅ 筛选功能（按学科、按名称搜索）

### 记忆节点 (test_memory_nodes.py)

- ✅ 创建节点（成功、未认证、无效图谱、不同类型）
- ✅ 查询节点（列表、详情、不存在、按类型筛选）
- ✅ 更新节点（成功、不存在）
- ✅ 删除节点（成功、不存在）
- ✅ 节点关联（创建、查询、删除）

### 用户管理 (test_users.py)

- ✅ 用户信息（获取、未认证、更新、部分更新）
- ✅ 用户删除（删除账号）
- ✅ 用户统计（统计信息）

## Fixtures 说明

### 数据库相关

- `db_session`: 测试数据库会话，每个测试函数独立
- `client`: HTTP 测试客户端

### 用户相关

- `test_user`: 测试用户实例
- `test_user_token`: 测试用户的访问令牌
- `auth_headers`: 认证请求头

### 数据相关

- `test_graph`: 测试知识图谱实例
- `test_node`: 测试记忆节点实例

## 测试数据

测试使用的默认数据定义在 `conftest.py` 中：

```python
TEST_USER_DATA = {
    "email": "newuser@example.com",
    "username": "newuser",
    "password": "password123"
}

TEST_GRAPH_DATA = {
    "name": "高等数学",
    "description": "高等数学知识图谱",
    "subject": "math",
    "is_public": False
}

TEST_NODE_DATA = {
    "node_type": "CONCEPT",
    "title": "导数的定义",
    "summary": "函数在某一点的导数是该点切线的斜率",
    "content_data": {...}
}
```

## 注意事项

### 1. 测试数据库隔离

- 每个测试函数使用独立的数据库会话
- 测试结束后自动回滚，不影响其他测试
- 测试数据库与开发数据库分离

### 2. 异步测试

- 所有测试函数都是异步的，使用 `@pytest.mark.asyncio` 装饰器
- 使用 `async/await` 语法

### 3. 测试顺序

- 测试之间相互独立，可以任意顺序运行
- 不依赖其他测试的结果

### 4. 清理工作

- 测试结束后自动清理数据
- 不需要手动清理

## 持续集成

测试可以集成到 CI/CD 流程中：

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: pgvector/pgvector:pg15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest --cov=app --cov-report=xml
      - uses: codecov/codecov-action@v2
```

## 调试测试

```bash
# 进入 pdb 调试器
pytest --pdb

# 在第一个失败时停止
pytest -x

# 显示最慢的 10 个测试
pytest --durations=10

# 只运行失败的测试
pytest --lf

# 运行上次失败和新增的测试
pytest --lf --ff
```

## 扩展测试

添加新测试时：

1. 在 `tests/` 目录下创建 `test_*.py` 文件
2. 创建测试类 `Test*`
3. 编写测试函数 `test_*`
4. 使用 fixtures 获取测试数据
5. 使用 assert 断言验证结果

示例：

```python
import pytest
from httpx import AsyncClient

class TestNewFeature:
    """新功能测试"""
    
    @pytest.mark.asyncio
    async def test_new_feature(self, client: AsyncClient, auth_headers: dict):
        """测试新功能"""
        response = await client.get(
            "/api/v1/new-endpoint",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert "expected_field" in response.json()
```

## 常见问题

### Q: 测试数据库连接失败

A: 确保 PostgreSQL 服务运行，并且已创建 `neuralnote_test` 数据库。

### Q: 测试运行很慢

A: 使用 `-n auto` 参数并行运行测试（需要安装 pytest-xdist）：

```bash
pip install pytest-xdist
pytest -n auto
```

### Q: 某些测试失败

A: 检查：
1. 数据库连接配置是否正确
2. 依赖包是否都已安装
3. 后端服务是否正常运行
4. 测试数据库是否为空

---

*最后更新：2026-01-30*

