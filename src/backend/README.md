# NeuralNote Backend

NeuralNote 智能学习管理工具的后端服务。

## 技术栈

- **框架**: FastAPI 0.109.0
- **数据库**: PostgreSQL 15 + PgVector
- **ORM**: SQLAlchemy 2.0.23 (异步)
- **缓存**: Redis 7
- **Python**: 3.14.0

## 项目结构

```
src/backend/
├── app/
│   ├── __init__.py
│   ├── api/                    # API 路由
│   │   ├── __init__.py
│   │   ├── deps.py            # 依赖注入
│   │   └── v1/                # API v1
│   │       ├── __init__.py
│   │       ├── api.py         # 路由聚合
│   │       └── endpoints/     # 端点实现
│   │           ├── __init__.py
│   │           └── health.py  # 健康检查
│   ├── core/                  # 核心配置
│   │   ├── __init__.py
│   │   ├── config.py          # 应用配置
│   │   └── database.py        # 数据库连接
│   ├── models/                # SQLAlchemy 模型
│   │   ├── __init__.py
│   │   ├── base.py            # 基类和混入
│   │   ├── user.py            # 用户模型
│   │   ├── knowledge_graph.py # 知识图谱模型
│   │   ├── memory_node.py     # 记忆节点模型
│   │   ├── knowledge_tag.py   # 知识点标签模型
│   │   ├── node_tag.py        # 节点-标签关联
│   │   ├── node_relation.py   # 节点关联模型
│   │   ├── view_config.py     # 视图配置模型
│   │   ├── review_log.py      # 复习记录模型
│   │   └── file_upload.py     # 文件上传记录
│   ├── schemas/               # Pydantic 模型（待实现）
│   │   └── __init__.py
│   └── services/              # 业务逻辑（待实现）
│       └── __init__.py
├── tests/                     # 测试（待实现）
├── .env.example               # 环境变量示例
├── main.py                    # 应用入口
└── README.md                  # 本文档
```

## 快速开始

### 1. 安装依赖

```bash
# 激活虚拟环境
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并配置：

```bash
cp .env.example .env
```

主要配置项：
- `POSTGRES_HOST`: 数据库地址（默认 localhost）
- `POSTGRES_PORT`: 数据库端口（默认 15432）
- `POSTGRES_USER`: 数据库用户（默认 neuralnote）
- `POSTGRES_PASSWORD`: 数据库密码
- `POSTGRES_DB`: 数据库名（默认 neuralnote_dev）

### 3. 启动服务

```bash
cd src/backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

服务将在 http://localhost:8000 启动。

### 4. 访问文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

## API 端点

### 根路由

- `GET /` - API 欢迎信息
- `GET /health` - 基础健康检查
- `GET /health/db` - 数据库健康检查

### API v1

- `GET /api/v1/health/ping` - Ping 检查
- `GET /api/v1/health/status` - 服务状态
- `GET /api/v1/health/database` - 数据库详细检查
- `GET /api/v1/health/redis` - Redis 连接检查

## 数据库模型

### 核心模型

1. **User** (`users`) - 用户表
2. **KnowledgeGraph** (`knowledge_graphs`) - 知识图谱表
3. **MemoryNode** (`memory_nodes`) - 记忆节点表（核心）
4. **KnowledgeTag** (`knowledge_tags`) - 知识点标签表
5. **NodeTag** (`node_tags`) - 节点-标签关联表
6. **NodeRelation** (`node_relations`) - 节点关联表
7. **ViewConfig** (`view_configs`) - 视图配置表
8. **ReviewLog** (`review_logs`) - 复习记录表
9. **FileUpload** (`file_uploads`) - 文件上传记录表

### 模型特性

- **UUID 主键**: 所有表使用 UUID 作为主键
- **时间戳**: 自动管理 `created_at` 和 `updated_at`
- **软删除**: 部分表支持软删除（`deleted_at`）
- **JSONB 字段**: 灵活存储复杂数据结构
- **向量搜索**: `MemoryNode` 支持 1536 维向量嵌入

## 开发规范

### 代码风格

```bash
# 格式化代码
black .
isort .

# 代码检查
flake8 .
mypy .
```

### 提交规范

- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建/工具相关

## 测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_models.py

# 生成覆盖率报告
pytest --cov=app tests/
```

## 常见问题

### 1. 数据库连接失败

检查 Docker 服务是否运行：
```bash
docker-compose ps
```

### 2. 端口被占用

修改 `.env` 中的端口配置或停止占用端口的进程。

### 3. 模型导入错误

确保已安装所有依赖：
```bash
pip install -r requirements.txt
```

## 下一步开发

- [ ] 实现用户认证系统（JWT）
- [ ] 创建 Pydantic Schemas
- [ ] 实现 CRUD 操作
- [ ] 添加文件上传功能
- [ ] 集成 OCR 服务
- [ ] 集成 AI 分析服务
- [ ] 实现向量搜索
- [ ] 添加单元测试

## 相关文档

- [产品需求文档](../../docs/01_Product/NeuralNote_PRD_v1.3.md)
- [API 设计文档](../../docs/02_Tech/API_Design.md)
- [数据库配置文档](../../docs/02_Tech/Database_Setup.md)
- [开发日志](../../docs/03_Logs/DevLog.md)

## 许可证

MIT License

