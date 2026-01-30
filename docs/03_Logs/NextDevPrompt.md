# NeuralNote 下次开发提示词

> 本文档用于记录每次开发会话的提示词，帮助快速恢复开发上下文
> 
> ⚠️ **重要规则**：每次开发会话结束前，必须更新本文档！

---

## 📅 最后更新时间

**2026-01-30 21:05**

---

## 🎯 当前开发阶段

**第一阶段：基础设施搭建 - 后端API开发**

---

## 📝 下次开发提示词

```
你好！我是 NeuralNote（纽伦笔记）项目的开发者。

【项目背景】
NeuralNote 是一款基于AI的智能学习管理工具，核心功能是：
1. 用户上传题目图片 → OCR识别
2. AI自动解答并提取知识点
3. 构建可视化的知识图谱（2D/3D）
4. 基于遗忘曲线的智能复习系统

【技术栈】
- 后端：Python 3.14 + FastAPI + SQLAlchemy
- 前端：React 18 + Vite + TypeScript + Ant Design
- 数据库：PostgreSQL 15 + PgVector（向量搜索）
- AI服务：OpenAI GPT-4 / DeepSeek（解答）+ 百度/腾讯OCR（识别）
- 存储：阿里云OSS
- 容器化：Docker + Docker Compose

【当前进度】
✅ 已完成：
- 项目目录结构搭建
- Python开发环境配置（venv + 依赖安装）
- 前端开发环境配置（React + Vite + TypeScript）
- Git分支创建（dev分支）
- .gitignore配置
- Docker环境配置（PostgreSQL + Redis + pgAdmin）
- 数据库表结构创建（9张核心表）
- 测试数据初始化
- SQLAlchemy 数据库模型（9个模型）
- FastAPI 后端项目结构
- 数据库连接和会话管理（支持异步）
- 健康检查接口（基础、数据库、Redis）
- 后端服务成功启动并测试通过

⏳ 待完成：
- 实现用户认证系统（JWT）
- 创建 Pydantic Schemas
- 实现 CRUD 操作

【数据库服务信息】
- PostgreSQL: localhost:15432（注意：非标准端口）
- Redis: localhost:6379
- pgAdmin: http://localhost:15050
- 测试账号: test@neuralnote.com / test123456

【下一步任务】
请帮我继续后端开发：
1. 实现用户认证系统（JWT Token）
2. 创建 Pydantic Schemas（请求/响应模型）
3. 实现用户相关的 CRUD 接口
4. 实现知识图谱相关的 CRUD 接口
5. 添加单元测试

【重要文档】
- 产品需求文档：`docs/01_Product/NeuralNote_PRD_v1.3.md`
- 技术设计文档：`docs/02_Tech/API_Design.md`
- 数据库配置文档：`docs/02_Tech/Database_Setup.md`
- 开发日志：`docs/03_Logs/DevLog.md`
- 任务清单：`TODO.md`
- 下次开发提示词：`docs/03_Logs/NextDevPrompt.md`（本文档）

【开发规范】
- 每完成一个任务，请更新 `docs/03_Logs/DevLog.md`
- 每完成一个任务，请在 `TODO.md` 中标记为完成
- ⚠️ 每次开发结束前，必须更新 `docs/03_Logs/NextDevPrompt.md`

请开始吧！
```

---

## 📋 开发上下文信息

### 项目路径

```
工作目录：D:\Documents\Coding\MiniMax\纽伦笔记 (NeuralNote)\NeuralNote-Project
```

### 当前分支

```
dev（开发分支）
```

### Python环境

```
Python版本：3.14.0
虚拟环境：venv/
已安装依赖：
  - FastAPI 0.109.0
  - SQLAlchemy 2.0.23
  - Uvicorn 0.27.0
  - asyncpg 0.31.0
  - psycopg2-binary 2.9.11
  - pydantic-settings 2.12.0
  - redis 7.1.0
  - pgvector 0.2.4
  - Black 23.12.1
  - isort 5.13.2
  - Flake8 6.1.0
  - Mypy 1.7.1
```

### 前端环境

```
框架：React 18 + Vite
语言：TypeScript
UI库：Ant Design
状态管理：Redux Toolkit
路由：React Router v7
```

### 数据库状态

```
✅ 已配置：PostgreSQL 15 + PgVector
✅ 已创建：9张核心表
✅ 已初始化：测试数据
✅ 后端服务：运行中（http://localhost:8000）
```

---

## 🔄 开发会话历史

### 2026-01-30 20:50 - 21:05

**完成内容**：
1. ✅ 创建完整的后端目录结构
2. ✅ 编写9个SQLAlchemy数据库模型
3. ✅ 实现数据库连接和会话管理（异步支持）
4. ✅ 创建FastAPI应用骨架
5. ✅ 实现健康检查接口（基础、数据库、Redis）
6. ✅ 配置CORS和环境变量管理
7. ✅ 编写后端README文档
8. ✅ 后端服务成功启动并测试通过

**遇到的问题**：
1. SQLAlchemy 2.0 类型注解错误
   - 解决：使用 `Mapped[]` 和 `mapped_column()` 新API
2. 缺少依赖包（pydantic-settings, asyncpg, redis, psycopg2-binary）
   - 解决：更新 requirements.txt 并安装
3. 时间戳字段复用语法错误
   - 解决：直接定义 Column() 而非尝试复用

**决策记录**：
- 采用SQLAlchemy 2.0新特性（Mapped类型注解）
- 使用异步数据库操作（asyncpg）
- 配置管理使用Pydantic Settings
- API版本化路由（/api/v1/）

**测试结果**：
- ✅ GET /health - 基础健康检查通过
- ✅ GET /health/db - 数据库连接正常
- ✅ GET /api/v1/health/database - 数据库详细检查通过（9张表）
- ✅ 所有模型导入成功

**下次继续**：
- 实现用户认证系统（JWT）
- 创建 Pydantic Schemas
- 实现 CRUD 操作

---

### 2026-01-30 20:10 - 20:50

**完成内容**：
1. ✅ Docker环境配置（PostgreSQL + Redis + pgAdmin）
2. ✅ 数据库表结构创建（9张核心表）
3. ✅ 测试数据初始化
4. ✅ 解决Windows端口冲突问题（使用15432和15050端口）
5. ✅ 创建数据库配置文档

**遇到的问题**：
- Windows系统保留了5432和5050端口，导致容器启动失败
- 解决方案：使用15432和15050端口

**决策记录**：
- 采用Docker Compose管理所有服务
- 使用pgvector/pgvector:pg15镜像（内置PgVector扩展）
- 数据库初始化脚本自动执行

**下次继续**：
- 编写SQLAlchemy数据库模型
- 创建FastAPI后端项目结构

---

### 2026-01-30 19:00 - 19:45

**完成内容**：

1. ✅ 创建 Git 开发分支（dev）
2. ✅ 配置 .gitignore 文件
3. ✅ 检查项目文档结构
4. ✅ 创建本开发提示词文档

**遇到的问题**：

- 无

**决策记录**：

- 采用 dev 分支进行开发，后续合并到 master

**下次继续**：

- 配置 PostgreSQL 数据库环境

---

## 📚 快速参考

### 常用命令

```bash
# 激活虚拟环境
.\venv\Scripts\activate

# Docker 服务管理
docker-compose up -d          # 启动所有服务
docker-compose down           # 停止所有服务
docker-compose ps             # 查看服务状态
docker-compose logs postgres  # 查看PostgreSQL日志

# 数据库操作
docker exec neuralnote-db psql -U neuralnote -d neuralnote_dev  # 连接数据库
docker exec neuralnote-db psql -U neuralnote -d neuralnote_dev -c "\dt"  # 查看所有表

# 启动后端服务
cd src/backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 启动前端服务
cd src/frontend
npm run dev

# 代码格式化
black .
isort .

# 代码检查
flake8 .
mypy .
```

### 重要文件路径

```
项目根目录/
├── docs/
│   ├── 01_Product/NeuralNote_PRD_v1.3.md      # 产品需求文档
│   ├── 02_Tech/API_Design.md                  # 技术设计文档
│   └── 03_Logs/
│       ├── DevLog.md                          # 开发日志
│       └── NextDevPrompt.md                   # 本文档
├── src/
│   ├── backend/                               # 后端代码
│   │   ├── app/                               # 应用代码
│   │   │   ├── api/v1/endpoints/              # API端点
│   │   │   ├── core/                          # 核心配置
│   │   │   ├── models/                        # SQLAlchemy模型
│   │   │   ├── schemas/                       # Pydantic模型
│   │   │   └── services/                      # 业务逻辑
│   │   ├── main.py                            # 应用入口
│   │   └── README.md                          # 后端文档
│   └── frontend/                              # 前端代码
├── venv/                                      # Python虚拟环境
├── requirements.txt                           # Python依赖
├── TODO.md                                    # 任务清单
└── README.md                                  # 项目说明
```

---

## 🎯 里程碑目标

### M1：基础设施搭建（当前）

- [X] 开发环境配置
- [X] 数据库环境配置
- [X] Docker容器化配置
- [X] 项目骨架搭建
- [X] 数据库模型实现
- [X] 基础API接口

### M2：核心功能实现

- [ ] 用户认证系统
- [ ] 文件上传模块
- [ ] OCR识别模块
- [ ] AI分析模块
- [ ] 知识图谱模块

### M3：MVP发布

- [ ] 前端界面开发
- [ ] 复习管理系统
- [ ] 测试与优化
- [ ] 部署上线

---

## 💡 开发提示

### 数据库设计要点

- 核心实体：`memory_nodes`（记忆节点），采用JSONB存储灵活内容
- 向量搜索：使用PgVector扩展，存储1536维向量
- 关联关系：`node_relations` 表存储节点间的关联
- 复习状态：`review_stats` JSONB字段存储复习数据

### API设计原则

- RESTful风格，版本号 `/api/v1/`
- JWT Token认证
- 统一JSON响应格式
- Cursor-based分页

### 前端架构

- 组件化开发，复用性优先
- 状态管理使用Redux Toolkit
- 图谱可视化使用D3.js/Cytoscape.js（2D）和Three.js（3D）

---

## 🚨 注意事项

1. **环境变量管理**

   - 敏感信息（API Key、数据库密码）使用环境变量
   - 不要提交 `.env` 文件到Git
2. **代码规范**

   - Python代码使用Black格式化
   - TypeScript代码使用ESLint + Prettier
   - 提交前运行代码检查
3. **文档同步**

   - 每次开发后更新 `DevLog.md`
   - API变更后更新 `API_Design.md`
   - 功能完成后更新 `TODO.md`
4. **Git提交规范**

   - feat: 新功能
   - fix: 修复bug
   - docs: 文档更新
   - style: 代码格式调整
   - refactor: 重构
   - test: 测试相关
   - chore: 构建/工具相关

---

## 📞 联系方式

如有问题，请查阅：

1. 产品需求文档（PRD）
2. 技术设计文档（API Design）
3. 开发日志（DevLog）

---

*本文档会在每次开发会话结束时更新*  
*最后更新：2026-01-30 21:05*

---

## 📋 更新本文档的检查清单

每次开发会话结束前，请确保：

- [ ] 更新"最后更新时间"
- [ ] 更新"当前进度"部分（已完成/待完成）
- [ ] 更新"下次开发提示词"中的任务描述
- [ ] 在"开发会话历史"中添加本次会话记录
- [ ] 更新"数据库状态"（如有变化）
- [ ] 更新"里程碑目标"进度（如有变化）
- [ ] 检查"常用命令"是否需要更新
- [ ] 提交本文档的更改到Git
