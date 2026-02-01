# NeuralNote 下次开发提示词

> 本文档用于记录每次开发会话的提示词，帮助快速恢复开发上下文
> 
> ⚠️ **重要规则**：每次开发会话结束前，必须更新本文档！

---

## 📅 最后更新时间

**2026-02-01 09:13**

---

## 🎯 当前开发阶段

**第一阶段：MVP 开发 - 前端界面开发（当前重点）**

> 💡 **阶段转换说明**：后端 API 已基本完成，现在进入前端开发阶段，实现端到端的产品功能验证。

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
- 用户认证系统（JWT Token）
- Pydantic Schemas（用户、知识图谱、记忆节点）
- 知识图谱 CRUD 接口（创建、查询、更新、删除、统计）
- 记忆节点 CRUD 接口（创建、查询、更新、删除）
- 节点关联管理接口（创建、查询、删除）
- 用户管理接口（查询、更新、删除）
- 完整的 API 测试脚本
- 所有接口测试通过 ✅
- **文件上传功能（本地存储 + OSS 支持）** ✅
- **OCR 识别服务（百度 OCR 集成）** ✅
- **AI 分析服务（DeepSeek + GPT-4）** ✅
- **完整的题目分析流程（上传 → OCR → AI → 创建节点）** ✅
- **复习算法服务（SM-2 遗忘曲线）** ✅
- **复习队列和统计功能** ✅
- **时区问题修复** ✅
- **所有复习模式测试通过（spaced, focused, random, graph_traversal）** ✅
- **单元测试框架搭建** ✅
- **复习服务单元测试（27个测试，100%通过）** ✅
- **OCR 服务测试修复（12个测试，100%通过）** ✅
- **AI 服务测试修复（16个测试，100%通过）** ✅
- **项目文件清理和组织（删除4个冗余MD文档，整理测试文件）** ✅
- **测试系统修复和完善（122/135 测试通过，90.4%通过率）** ✅
- **向量相似度搜索功能** ✅
- **前端基础架构搭建** ✅
  - 前端依赖安装（React 18 + Vite 5 + Ant Design 5）
  - API 服务层（axios + 拦截器）
  - Redux 状态管理（auth + graph）
  - 路由系统（懒加载 + 路由守卫）
  - 用户认证页面（登录/注册）
  - 主布局框架（导航栏 + 用户菜单）
  - 核心页面（首页、知识图谱、复习、个人中心）
  - 前端服务启动成功（http://localhost:3001/）
- **前端核心功能开发** ✅ 新增
  - 文件上传组件（拖拽上传、预览、进度）
  - OCR 识别界面（实时进度、结果展示、手动校正）
  - AI 分析结果展示（题目、答案、解析、知识点）
  - 题目分析流程（4步骤：上传 → OCR → AI → 完成）
  - 2D 知识图谱可视化（Cytoscape.js + 4种布局）
  - 图谱交互（点击、悬停、缩放、拖拽）
  - 节点管理（创建、编辑、删除、列表）
  - 复习系统界面（4种模式、复习卡片、反馈）
  - 复习统计展示（今日复习、连续打卡、掌握度）
  - 图谱详情页面（统计、可视化、节点列表）
- **已知问题：13个文件上传相关测试失败** ⚠️
  - 问题：测试 fixture 中创建的用户数据在 API 请求中不可见
  - 原因：SQLAlchemy 异步测试中的数据库事务隔离问题
  - 影响：文件上传、OCR、AI 分析等需要用户关联的集成测试
  - 状态：已深入调试但未解决，需要重构测试架构
  - 决策：暂时接受 90.4% 通过率，继续功能开发
  - 详情：见 DevLog.md 中的 [技术债] 标签

⏳ 待完成：
- **前端开发（当前重点）** 🎯
  - 节点关联管理界面
  - 统计图表展示（Recharts）
  - 个人中心完善（信息编辑、学习数据）
  - 向量搜索界面
  - 3D 知识图谱可视化（Three.js）
  - 搜索功能（全局搜索、节点搜索）
  - 通知系统（复习提醒）
- 后端优化（按需进行）
  - 优化 AI 提示词
  - 实现批量操作 API
  - API 性能优化
  - 添加缓存机制

【数据库服务信息】
- PostgreSQL: localhost:15432（注意：非标准端口）
- Redis: localhost:6379
- pgAdmin: http://localhost:15050
- 测试账号: test@neuralnote.com / test123456

【API 服务配置状态】
- ✅ 百度 OCR：已配置（存储在 .env 文件中）
- ⚠️ DeepSeek：待配置（用于 AI 分析）
- ⚠️ OpenAI：待配置（用于向量嵌入）

【下一步任务】
请帮我继续前端开发：

**优先级 1：前端功能完善（当前重点）** 🎯
1. 节点关联管理
   - 查看节点关联关系
   - 创建节点关联
   - 删除节点关联
   - 关联类型选择
2. 统计图表展示
   - 学习时长趋势图（Recharts）
   - 掌握度分布图
   - 复习频率图
   - 知识点覆盖图
3. 个人中心完善
   - 用户信息编辑
   - 密码修改
   - 学习数据展示
   - 学习成就系统
4. 向量搜索界面
   - 智能搜索框
   - 相似节点推荐
   - 学习路径推荐
5. 其他功能
   - 全局搜索功能
   - 复习提醒通知
   - 3D 图谱可视化（Three.js）

**优先级 2：后端优化（按需进行）**
1. 优化 AI 提示词
   - 提高知识点提取准确度
   - 优化题目解答质量
2. 批量操作 API
   - 批量创建节点
   - 批量更新节点
   - 批量删除节点
3. API 性能优化
   - 添加 Redis 缓存
   - 优化数据库查询
   - 实现分页优化

**优先级 3：测试和部署（后期进行）**
1. 解决数据库事务隔离问题（技术债务）
2. E2E 测试（Playwright/Cypress）
3. Docker 镜像构建和部署准备
4. 生产环境配置

【重要文档】
- 产品需求文档：`docs/01_Product/NeuralNote_PRD_v1.3.md`
- 技术设计文档：`docs/02_Tech/API_Design.md`
- 数据库配置文档：`docs/02_Tech/Database_Setup.md`
- 开发日志：`docs/03_Logs/DevLog.md`
- 任务清单：`TODO.md`
- 项目说明：`README.md`
- 下次开发提示词：`docs/03_Logs/NextDevPrompt.md`（本文档）

【文档更新规范】⚠️ 重要！
请严格遵守以下文档同步更新规则，确保项目文档体系的一致性：

**核心原则：保持文档精简，只保留必要的文档，不要不停创建新文档！**

1. **开发过程中遇到问题** → 立即记录到 `docs/03_Logs/DevLog.md`
   - 使用标签：[问题] [决策] [技术债]
   - 记录：问题现象、根本原因、解决方案、经验教训
   - 更新技术债记录表
   - ❌ 不要创建单独的问题总结文档

2. **完成一个功能模块** → 更新多个文档
   - `TODO.md`：标记任务完成状态
   - `docs/03_Logs/DevLog.md`：记录开发会话历史
   - `README.md`：更新项目进度和功能列表（如有重大更新）
   - `src/backend/README.md` 或 `src/frontend/README.md`：更新模块文档
   - ❌ 不要创建单独的功能总结文档

3. **API 接口变更** → 同步更新
   - `docs/02_Tech/API_Design.md`：更新接口文档
   - `docs/03_Logs/DevLog.md`：记录变更原因和决策
   - `src/backend/README.md`：更新 API 端点列表
   - ❌ 不要创建单独的 API 变更文档

4. **数据库结构变更** → 同步更新
   - `docs/02_Tech/Database_Setup.md`：更新表结构说明
   - `docs/03_Logs/DevLog.md`：记录变更原因
   - 数据库迁移脚本：创建 Alembic 迁移文件
   - ❌ 不要创建单独的数据库变更文档

5. **每次开发会话结束** → 必须更新
   - `docs/03_Logs/NextDevPrompt.md`（本文档）：更新下次开发提示词
   - `docs/03_Logs/DevLog.md`：添加本次会话记录
   - `TODO.md`：更新任务进度
   - ❌ 不要创建单独的会话总结文档

【文档关系图】
```
README.md (项目总览)
    ↓
    ├─→ docs/01_Product/NeuralNote_PRD_v1.3.md (产品需求)
    │       ↓
    ├─→ docs/02_Tech/API_Design.md (技术设计)
    │       ↓
    ├─→ docs/02_Tech/Database_Setup.md (数据库设计)
    │       ↓
    ├─→ src/backend/README.md (后端实现)
    │   src/frontend/README.md (前端实现)
    │       ↓
    ├─→ TODO.md (任务清单) ←→ docs/03_Logs/DevLog.md (开发日志)
    │       ↓                           ↓
    └─→ docs/03_Logs/NextDevPrompt.md (下次开发提示词)

更新流程：
需求变更 → PRD → API设计 → 数据库设计 → 代码实现 → DevLog记录 → TODO更新 → NextDevPrompt更新
```

【开发规范】
- ⚠️ **遇到问题立即记录**：不要等到开发结束，问题解决后立即更新 DevLog.md
- ⚠️ **每完成一个任务**：同步更新 TODO.md 和 DevLog.md
- ⚠️ **API/数据库变更**：必须同步更新技术文档
- ⚠️ **每次开发结束前**：必须更新 NextDevPrompt.md
- ⚠️ **重大决策**：在 DevLog.md 中使用 [决策] 标签详细记录

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

### 2026-02-01 00:00 - 01:20

**完成内容**：
1. ✅ 前端基础架构搭建
   - 安装前端依赖（React 18 + Vite 5 + Ant Design 5 + Redux Toolkit）
   - 创建 API 服务层（axios 配置、认证服务、图谱服务、节点服务）
   - 实现 Redux 状态管理（authSlice、graphSlice）
   - 创建路由系统（懒加载、路由守卫）
   - 实现用户认证页面（登录/注册，精美渐变动画）
   - 创建主布局（响应式导航栏、用户下拉菜单）
   - 实现核心页面（首页、知识图谱管理、复习中心、个人中心）
   - 配置 Vite、TypeScript、环境变量
   - 创建前端 README 文档
2. ✅ 解决 Vite 版本兼容问题（降级到 5.4.0）
3. ✅ 解决 TypeScript 配置问题（禁用 verbatimModuleSyntax）
4. ✅ 前端服务成功启动（http://localhost:3000/）

**技术决策**：
1. **UI 设计**：紫色渐变主题（#667eea → #764ba2）+ Inter 字体
2. **状态管理**：Redux Toolkit（全局） + useState（本地）
3. **路由设计**：公开路由（/login）+ 受保护路由（/, /graph, /review, /profile）
4. **API 调用**：统一错误处理、自动 Token 注入、401 自动跳转

**遇到的问题**：
1. Vite 7.x 要求 Node.js 22.12+，降级到 5.4.0 解决
2. TypeScript 配置过于严格，禁用 verbatimModuleSyntax 解决

**下次继续**：
- 实现文件上传组件
- 实现 OCR 识别界面
- 实现 AI 分析结果展示
- 实现 2D 知识图谱可视化

---

### 2026-02-01 14:00 - 15:30

**完成内容**：
1. ✅ 实现向量相似度搜索功能
   - 创建 VectorSearchService（向量搜索服务）
   - 实现文本查询搜索相似节点
   - 实现基于节点ID查找相似节点
   - 实现节点推荐功能（学习路径）
   - 实现节点聚类功能（基于相似度）
   - 实现向量嵌入更新（单个/批量）
2. ✅ 创建向量搜索 API 端点（6个端点）
   - POST /api/v1/vector-search/search
   - GET /api/v1/vector-search/similar/{node_id}
   - GET /api/v1/vector-search/recommend/{node_id}
   - GET /api/v1/vector-search/cluster/{graph_id}
   - POST /api/v1/vector-search/update-embedding
   - POST /api/v1/vector-search/batch-update-embedding
3. ✅ 创建向量搜索 Schemas
4. ✅ 集成到主路由
5. ✅ 创建测试脚本（test_vector_search.py）
6. ✅ 文档整理（合并测试指南到 README.md）

**技术决策**：
1. **向量搜索算法**：使用 PgVector 的余弦相似度
2. **聚类算法**：采用贪心聚类（简单高效）
3. **向量嵌入**：使用 OpenAI text-embedding-ada-002（1536维）
4. **相似度阈值**：默认 0.7（搜索）/ 0.8（聚类）

**使用场景**：
- 智能搜索：用户输入问题，找到相关题目和概念
- 学习推荐：学完一个知识点后，推荐相关内容
- 知识发现：自动发现知识图谱中的相似主题簇
- 去重检测：识别重复或高度相似的题目

**注意事项**：
- ⚠️ 需要配置 OPENAI_API_KEY 才能使用
- ⚠️ 批量更新向量嵌入可能耗时较长

**下次继续**：
- 优化 AI 提示词
- 实现 OCR 结果手动校正功能

---

### 2026-01-31 13:00 - 13:15

**完成内容**：
1. ✅ 项目文件清理和组织
   - 删除 4 个冗余 MD 文档（CONFIG.md, DEVELOPMENT_SUMMARY.md, FEATURES.md, OCR_CONFIGURED.md）
   - 确认所有测试文件已在 tests/ 目录
   - 删除重复的 test_auth.py
   - 更新开发日志和提示词文档

**决策记录**：
1. **文档精简原则**：避免信息重复，保持文档体系清晰
2. **测试文件组织**：统一放在 tests/ 目录，避免散落

**清理结果**：
- 删除文档：4 个
- 整理测试文件：16 个测试文件统一在 tests/ 目录
- 项目结构更加清晰

---

### 2026-01-30 23:00 - 23:30

**完成内容**：
1. ✅ 实现文件上传功能
   - 创建 FileStorageService（支持本地存储和 OSS）
   - 实现文件上传 API（/api/v1/files/upload）
   - 文件列表查询、详情查询、更新、删除
   - 文件类型验证和大小限制
   - 静态文件服务配置
2. ✅ 实现 OCR 识别服务
   - 集成百度 OCR API
   - 实现 OCR 识别端点（/api/v1/ocr/ocr）
   - 实现数学公式识别端点（/api/v1/ocr/math）
   - Access Token 缓存机制
   - 文件处理状态管理
3. ✅ 实现 AI 分析服务
   - 集成 DeepSeek 和 OpenAI GPT-4 API
   - 实现文本分析端点（/api/v1/ai/analyze）
   - 实现知识点提取端点（/api/v1/ai/extract-knowledge）
   - 实现向量嵌入生成端点（/api/v1/ai/embedding）
   - 实现完整题目分析流程（/api/v1/ai/analyze-question）
4. ✅ 创建测试脚本
   - test_new_features.py（测试新功能）
5. ✅ 更新文档
   - 更新 DevLog.md（记录开发过程）
   - 更新 NextDevPrompt.md（更新进度）
   - 更新 requirements.txt（添加新依赖）

**技术决策**：
1. **文件存储**：本地存储优先，OSS 可选，统一接口设计
2. **OCR 服务**：百度 OCR 为主力引擎，Token 缓存优化
3. **AI 服务**：DeepSeek（主力）+ GPT-4（兜底），自动选择策略
4. **API 设计**：职责分离 + 流程整合，提供灵活的调用方式

**遇到的问题**：
1. 静态文件访问：使用 StaticFiles 挂载 /uploads 目录
2. OCR Token 管理：缓存 Access Token，有效期内复用
3. AI 结果解析：处理 Markdown 格式的 JSON 返回

**API 端点新增**：
- 文件上传：5个端点（上传、列表、详情、更新、删除）
- OCR 识别：2个端点（通用识别、数学公式识别）
- AI 分析：4个端点（文本分析、知识点提取、向量嵌入、完整分析）

**下次继续**：
- 添加单元测试（文件上传、OCR、AI）
- 实现复习算法（遗忘曲线）
- 实现向量相似度搜索

---

### 2026-01-30 21:30 - 23:45

**完成内容**：
1. ✅ 创建知识图谱相关的 Pydantic Schemas
2. ✅ 创建记忆节点相关的 Pydantic Schemas
3. ✅ 实现知识图谱 CRUD 接口（6个端点）
4. ✅ 实现记忆节点 CRUD 接口（5个端点）
5. ✅ 实现节点关联管理接口（3个端点）
6. ✅ 实现用户管理接口（3个端点）
7. ✅ 编写完整的 API 测试脚本
8. ✅ 所有接口测试通过
9. ✅ 更新开发日志（DevLog.md）

**遇到的问题**：
1. Schema 字段名与数据库模型不匹配
   - 知识图谱：`color/icon` → `subject/cover_image_url`
   - 记忆节点：`content` → `content_data`
   - 节点关联：`source_node_id/target_node_id` → `source_id/target_id`
   - 解决：更新所有 Schema 和 API 端点以匹配数据库模型

**决策记录**：
- 统一使用数据库模型的字段名
- 分页查询统一使用 PaginatedResponse
- 所有接口都需要 JWT Token 认证
- 删除操作采用级联删除

**测试结果**：
- ✅ 创建知识图谱：201 Created
- ✅ 创建记忆节点：201 Created（CONCEPT 和 QUESTION 类型）
- ✅ 创建节点关联：201 Created
- ✅ 查询图谱列表：200 OK（分页）
- ✅ 查询节点列表：200 OK（分页）
- ✅ 查询节点详情：200 OK
- ✅ 查询节点关联：200 OK
- ✅ 查询图谱统计：200 OK
- ✅ 更新节点信息：200 OK
- ✅ 更新用户信息：200 OK
- ✅ 所有测试通过 ✅

**API 端点总览**：
- 知识图谱：6个端点（创建、列表、详情、更新、删除、统计）
- 记忆节点：5个端点（创建、列表、详情、更新、删除）
- 节点关联：3个端点（创建、查询、删除）
- 用户管理：3个端点（查询、更新、删除）

**下次继续**：
- 添加单元测试（pytest）
- 实现文件上传功能
- 集成 OCR 服务

---

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

### M1：基础设施搭建（✅ 已完成）

- [X] 开发环境配置
- [X] 数据库环境配置
- [X] Docker容器化配置
- [X] 项目骨架搭建
- [X] 数据库模型实现
- [X] 基础API接口
- [X] 用户认证系统
- [X] 知识图谱 CRUD
- [X] 记忆节点 CRUD

### M2：核心功能实现（当前）

- [X] 用户认证系统 ✅
- [ ] 文件上传模块
- [ ] OCR识别模块
- [ ] AI分析模块
- [X] 知识图谱模块 ✅（基础 CRUD）
- [ ] 复习算法模块

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

### 1. 环境变量管理

- 敏感信息（API Key、数据库密码）使用环境变量
- 不要提交 `.env` 文件到Git
- 使用 `.env.example` 作为模板

### 2. 代码规范

- Python代码使用Black格式化
- TypeScript代码使用ESLint + Prettier
- 提交前运行代码检查

### 3. 文档同步更新 ⚠️ 核心规则

**文档体系说明**：

项目采用**分层文档体系**，各文档职责明确、相互关联：

| 文档 | 职责 | 更新时机 | 关联文档 |
|------|------|---------|---------|
| `README.md` | 项目总览、快速开始 | 重大功能完成 | 所有文档 |
| `TODO.md` | 任务清单、进度跟踪 | 每完成一个任务 | DevLog.md |
| `docs/01_Product/PRD` | 产品需求定义 | 需求变更时 | API_Design.md |
| `docs/02_Tech/API_Design.md` | API接口设计 | API变更时 | Database_Setup.md, DevLog.md |
| `docs/02_Tech/Database_Setup.md` | 数据库设计 | 表结构变更时 | DevLog.md |
| `docs/03_Logs/DevLog.md` | 开发日志、问题记录 | **实时更新** | 所有文档 |
| `docs/03_Logs/NextDevPrompt.md` | 下次开发提示词 | 每次会话结束 | DevLog.md, TODO.md |
| `src/backend/README.md` | 后端模块文档 | 后端功能变更 | API_Design.md |
| `src/frontend/README.md` | 前端模块文档 | 前端功能变更 | - |

**更新规则**：

**规则 1：问题即时记录** 🔥
```
遇到问题 → 立即记录到 DevLog.md
- 不要等到开发结束
- 使用标签：[问题] [决策] [技术债]
- 记录：现象 + 原因 + 解决方案 + 经验教训
- 更新技术债记录表（如适用）
```

**规则 2：任务完成同步**
```
完成任务 → 同步更新多个文档
1. TODO.md：✅ 标记任务完成
2. DevLog.md：📝 记录开发会话历史
3. README.md：📄 更新功能列表（重大功能）
4. 模块README：📚 更新模块文档
```

**规则 3：API 变更同步**
```
API 变更 → 三处同步更新
1. docs/02_Tech/API_Design.md：更新接口文档
2. docs/03_Logs/DevLog.md：记录变更原因
3. src/backend/README.md：更新端点列表
```

**规则 4：数据库变更同步**
```
数据库变更 → 三处同步更新
1. docs/02_Tech/Database_Setup.md：更新表结构
2. docs/03_Logs/DevLog.md：记录变更原因
3. 创建 Alembic 迁移文件
```

**规则 5：会话结束必更新**
```
开发结束 → 必须更新两个文档
1. docs/03_Logs/NextDevPrompt.md：更新提示词
2. docs/03_Logs/DevLog.md：添加会话记录
```

**文档更新检查清单**：
- [ ] 遇到问题了吗？→ 立即更新 DevLog.md
- [ ] 完成任务了吗？→ 更新 TODO.md + DevLog.md
- [ ] API 变更了吗？→ 更新 API_Design.md + DevLog.md
- [ ] 数据库变更了吗？→ 更新 Database_Setup.md + DevLog.md
- [ ] 开发结束了吗？→ 更新 NextDevPrompt.md + DevLog.md

### 4. Git提交规范

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

**必须更新**：
- [ ] 更新"最后更新时间"
- [ ] 更新"当前进度"部分（已完成/待完成）
- [ ] 更新"下次开发提示词"中的任务描述
- [ ] 在"开发会话历史"中添加本次会话记录
- [ ] **同步更新 DevLog.md**（添加本次会话的问题和决策）
- [ ] **同步更新 TODO.md**（标记完成的任务）

**按需更新**：
- [ ] 更新"数据库状态"（如有变化）
- [ ] 更新"里程碑目标"进度（如有变化）
- [ ] 检查"常用命令"是否需要更新
- [ ] 更新 API_Design.md（如有 API 变更）
- [ ] 更新 Database_Setup.md（如有数据库变更）
- [ ] 更新 README.md（如有重大功能完成）

**最后步骤**：
- [ ] 提交所有文档更改到Git
- [ ] 使用规范的 commit message（如：docs: 更新开发日志和下次开发提示词）

---

## 📖 文档更新示例

**场景 1：遇到并解决了一个问题**

1. **立即更新 DevLog.md**：
```markdown
### 2026-01-30 - 用户认证系统实现

#### [问题] bcrypt 版本兼容性问题

**问题现象**：API 返回 500 错误
**根本原因**：bcrypt 5.0.0 与 passlib 1.7.4 不兼容
**解决方案**：降级到 bcrypt 4.0.1
**经验教训**：依赖包应固定版本
```

2. **会话结束时更新 NextDevPrompt.md**：
```markdown
**遇到的问题**：
- bcrypt 版本兼容性问题
  - 解决：降级到 bcrypt 4.0.1 并固定版本
```

---

**场景 2：完成了用户认证功能**

1. **更新 TODO.md**：
```markdown
- [X] 实现用户认证系统（JWT）
  - [X] 实现密码加密工具
  - [X] 实现JWT Token生成和验证
  - [X] 实现用户注册接口
  - [X] 实现用户登录接口
```

2. **更新 DevLog.md**：
```markdown
### 2026-01-30 - 用户认证系统实现完成

**完成内容**：
1. ✅ 实现密码加密工具（bcrypt）
2. ✅ 实现JWT Token生成和验证
...

**测试结果**：
✅ 所有接口测试通过
```

3. **更新 src/backend/README.md**：
```markdown
## API 端点

### 认证相关
- POST /api/v1/auth/register - 用户注册
- POST /api/v1/auth/login - 用户登录
...
```

4. **更新 NextDevPrompt.md**：
```markdown
✅ 已完成：
- 用户认证系统（JWT）

⏳ 待完成：
- 实现用户管理 CRUD 接口
```

---

**场景 3：修改了 API 接口**

1. **更新 API_Design.md**：
```markdown
### POST /api/v1/auth/register

**请求参数**：
- email: string (必填)
- username: string (必填)
- password: string (必填，最少6位)
```

2. **更新 DevLog.md**：
```markdown
#### [决策] 密码最小长度设为6位

**原因**：平衡安全性和用户体验
**影响**：注册接口增加密码长度验证
```

3. **更新 src/backend/README.md**：
```markdown
## API 端点

| 端点 | 方法 | 功能 | 状态码 |
|------|------|------|--------|
| `/api/v1/auth/register` | POST | 用户注册 | 201 |
```

---

*本文档会在每次开发会话结束时更新*  
*最后更新：2026-01-30 23:45*
