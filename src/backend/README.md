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

**配置状态**：

- ✅ **数据库和 Redis**：已配置（使用 Docker Compose 默认配置）
- ✅ **百度 OCR**：已配置，可以直接使用 OCR 识别功能
- ⚠️ **AI 服务**：需要配置（DeepSeek 或 OpenAI）才能使用 AI 分析功能

**需要配置的 AI 服务**：

编辑 `.env` 文件，添加以下至少一个：

```env
# DeepSeek（推荐）
DEEPSEEK_API_KEY=your_deepseek_api_key

# 或 OpenAI
OPENAI_API_KEY=your_openai_api_key
```

详细配置说明请查看：[CONFIG.md](./CONFIG.md)

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

## 功能测试指南

### 已实现的功能

✅ **后端功能（已完成，可测试）**
- 用户认证系统
- 知识图谱管理
- 记忆节点管理
- 文件上传功能
- OCR 识别服务
- AI 分析服务
- 复习系统（SM-2 算法）
- **向量相似度搜索** ✨ 新功能

### 测试方法

#### 方法 1：Swagger UI（推荐）

1. **启动后端服务**
   ```bash
   cd src/backend
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **访问 Swagger UI**
   ```
   http://localhost:8000/docs
   ```

3. **测试流程**

   **步骤 1：注册用户**
   - 找到 `POST /api/v1/auth/register`
   - 点击 "Try it out"
   - 填写信息：
     ```json
     {
       "email": "test@example.com",
       "username": "测试用户",
       "password": "password123"
     }
     ```

   **步骤 2：登录获取 Token**
   - 找到 `POST /api/v1/auth/login`
   - 填写登录信息
   - 复制返回的 `access_token`

   **步骤 3：授权**
   - 点击页面右上角的 🔓 "Authorize" 按钮
   - 输入：`Bearer 你的token`（注意空格）
   - 点击 "Authorize"

   **步骤 4：测试其他功能**
   - 创建知识图谱：`POST /api/v1/graphs/`
   - 上传文件：`POST /api/v1/files/upload`
   - OCR 识别：`POST /api/v1/ocr/ocr`
   - AI 分析：`POST /api/v1/ai/analyze`
   - 复习系统：`GET /api/v1/review/queue`
   - **向量搜索**：`POST /api/v1/vector-search/search` ✨

#### 方法 2：使用测试脚本

```bash
# 运行所有测试
python -m pytest tests/ -v

# 运行特定测试
python -m pytest tests/test_auth.py -v
python -m pytest tests/test_review_service.py -v

# 测试向量搜索功能（需要配置 OPENAI_API_KEY）
python test_vector_search.py

# 生成覆盖率报告
pytest --cov=app tests/
```

#### 方法 3：使用 Postman

1. 访问：http://localhost:8000/openapi.json
2. 复制 JSON 内容
3. 在 Postman 中导入

### 完整测试流程（推荐）

1. **注册并登录** → 获取 Token
2. **创建知识图谱** → 获取 graph_id
3. **上传题目图片** → 获取 file_id
4. **OCR 识别** → 获取文本内容
5. **AI 分析** → 自动创建记忆节点
6. **查询节点列表** → 查看创建的节点
7. **开始复习** → 测试复习系统
8. **提交复习结果** → 更新记忆状态
9. **查看统计** → 查看复习数据
10. **向量搜索** → 测试智能搜索功能 ✨

### 可测试的功能列表

**1. 用户认证**
- ✅ 用户注册
- ✅ 用户登录
- ✅ Token 验证

**2. 知识图谱管理**
- ✅ 创建知识图谱
- ✅ 查询图谱列表（分页）
- ✅ 查询图谱详情
- ✅ 更新图谱信息
- ✅ 删除图谱
- ✅ 查询图谱统计

**3. 记忆节点管理**
- ✅ 创建记忆节点（概念、题目）
- ✅ 查询节点列表（分页、筛选）
- ✅ 查询节点详情
- ✅ 更新节点信息
- ✅ 删除节点

**4. 节点关联**
- ✅ 创建节点关联
- ✅ 查询节点关联
- ✅ 删除节点关联

**5. 文件上传**
- ✅ 上传图片文件
- ✅ 查询文件列表
- ✅ 查询文件详情
- ✅ 删除文件

**6. OCR 识别**
- ✅ 通用文字识别
- ✅ 数学公式识别

**7. AI 分析**
- ✅ 文本分析
- ✅ 知识点提取
- ✅ 向量嵌入生成
- ✅ 完整题目分析流程

**8. 复习系统**
- ✅ 获取复习队列（4种模式）
- ✅ 提交复习结果
- ✅ 查询复习统计

**9. 向量搜索** ✨ 新功能
- ✅ 文本查询搜索相似节点
- ✅ 查找与指定节点相似的节点
- ✅ 节点推荐（学习路径）
- ✅ 节点聚类（相似度分组）
- ✅ 更新向量嵌入（单个/批量）

### 向量搜索功能说明 ✨

**使用场景**：
1. **智能搜索**：输入"如何求导数"，找到所有相关的题目和概念
2. **学习推荐**：学完一个知识点后，推荐相关内容
3. **知识发现**：自动发现知识图谱中的相似主题簇
4. **去重检测**：识别重复或高度相似的题目

**API 端点**：
- `POST /api/v1/vector-search/search` - 文本查询搜索
- `GET /api/v1/vector-search/similar/{node_id}` - 查找相似节点
- `GET /api/v1/vector-search/recommend/{node_id}` - 节点推荐
- `GET /api/v1/vector-search/cluster/{graph_id}` - 节点聚类
- `POST /api/v1/vector-search/update-embedding` - 更新向量嵌入

**注意事项**：
- ⚠️ 需要配置 `OPENAI_API_KEY` 才能使用向量搜索功能
- ⚠️ 首次使用需要为节点生成向量嵌入（调用 update-embedding 接口）
- ⚠️ 批量更新向量嵌入可能耗时较长

## 常见问题

### 1. 后端启动失败

**检查：**
- Docker 服务是否运行：`docker-compose ps`
- 端口是否被占用：`netstat -ano | findstr :8000`
- 虚拟环境是否激活

### 2. 数据库连接失败

**检查：**
- PostgreSQL 容器是否运行
- 端口是否正确（15432）
- `.env` 文件配置是否正确

### 3. OCR 识别失败

**原因：**
- 百度 OCR 已配置，应该可以正常使用
- 如果失败，检查 API 额度是否用完

### 4. AI 分析失败

**原因：**
- 需要配置 DeepSeek 或 OpenAI API Key
- 检查 API Key 是否有效
- 检查 API 额度是否充足

### 5. 向量搜索失败 ✨

**原因：**
- 需要配置 OpenAI API Key（用于生成向量嵌入）
- 节点可能还没有生成向量嵌入
- 解决：调用 `/api/v1/vector-search/batch-update-embedding` 批量生成

### 6. Token 过期

**解决：**
- 重新登录获取新的 Token
- Token 默认有效期 30 分钟

### 7. 模型导入错误

确保已安装所有依赖：
```bash
pip install -r requirements.txt
```

## 下一步开发

- [X] 实现用户认证系统（JWT）✅
- [X] 创建 Pydantic Schemas ✅
- [X] 实现 CRUD 操作 ✅
- [X] 添加文件上传功能 ✅
- [X] 集成 OCR 服务 ✅
- [X] 集成 AI 分析服务 ✅
- [X] 实现复习系统 ✅
- [X] 实现向量相似度搜索 ✅
- [ ] 优化 AI 提示词
- [ ] 实现 OCR 结果手动校正
- [ ] 前端开发

## 相关文档

- [产品需求文档](../../docs/01_Product/NeuralNote_PRD_v1.3.md)
- [API 设计文档](../../docs/02_Tech/API_Design.md)
- [数据库配置文档](../../docs/02_Tech/Database_Setup.md)
- [开发日志](../../docs/03_Logs/DevLog.md)

## 许可证

MIT License

