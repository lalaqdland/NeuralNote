# NeuralNote 技术架构与接口设计文档

## 文档信息

| 项目 | 内容 |
|-----|------|
| 产品名称 | NeuralNote (纽伦笔记) |
| 文档类型 | 技术设计文档 |
| 版本 | V1.0 |
| 状态 | 施工中 |
| 创建日期 | 2026年1月28日 |
| 最后更新 | 2026年1月29日 |

---

## 一、技术架构总览

### 1.1 系统架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                         客户端层                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │   Web App   │  │  iOS App    │  │ Android App │             │
│  │   (React)   │  │  (Taro/RN)  │  │  (Taro/RN)  │             │
│  │   [MVP]     │  │  [Phase 2]  │  │  [Phase 2]  │             │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘             │
└─────────┼────────────────┼────────────────┼─────────────────────┘
          │                │                │
          └────────────────┼────────────────┘
                           │
┌──────────────────────────┼──────────────────────────┐
│                    API Gateway (Nginx)               │
│              ┌─────────────────────────┐             │
│              │  负载均衡 / 限流 / 认证  │             │
│              └───────────┬─────────────┘             │
└──────────────────────────┼──────────────────────────┘
                           │
┌──────────────────────────┼──────────────────────────┐
│                    应用服务层                          │
│  ┌─────────────────────────────────────────────────┐ │
│  │              Backend Service (FastAPI)           │ │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌───────┐  │ │
│  │  │ Auth    │ │ Upload  │ │  AI     │ │Graph  │  │ │
│  │  │ Service │ │ Service │ │ Service │ │Service│  │ │
│  │  └─────────┘ └─────────┘ └─────────┘ └───────┘  │ │
│  └─────────────────────────────────────────────────┘ │
└──────────────────────────┼──────────────────────────┘
                           │
┌──────────────────────────┼──────────────────────────┐
│                    数据存储层                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │  PostgreSQL │  │    Redis    │  │  对象存储    │   │
│  │  (主数据库)  │  │   (缓存)    │  │  (OSS/S3)   │   │
│  └─────────────┘  └─────────────┘  └─────────────┘   │
└────────────────────────────────────────────────────────┘
                           │
┌──────────────────────────┼──────────────────────────┐
│                    外部服务集成                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │   OCR服务   │  │  LLM服务    │  │  向量数据库  │   │
│  │ (百度/腾讯) │  │(OpenAI/DeepSeek)│ │  (PgVector) │   │
│  └─────────────┘  └─────────────┘  └─────────────┘   │
└────────────────────────────────────────────────────────┘
```

### 1.2 技术栈选型

| 层次 | 技术 | 版本 | 用途 |
|-----|------|------|------|
| **前端（第一阶段）** | | | | |
| Web | React | 18.x | 主Web应用 | MVP |
| 状态管理 | Redux Toolkit | 2.x | 全局状态管理 | MVP |
| 图谱可视化 | D3.js / Cytoscape.js | 7.x | 2D知识图谱 | MVP |
| 3D可视化 | Three.js + 3d-force-graph | 0.15.x | 3D知识图谱 | MVP |
| UI框架 | Ant Design / Material-UI | 5.x | 组件库 | MVP |
| **前端（第二阶段扩展）** | | | | |
| 跨平台框架 | Taro / Flutter | 4.x / 3.x | 多端编译 | Phase 2 |
| 小程序 | 微信小程序 | - | 移动端入口 | Phase 2 |
| **后端** | | | | |
| 运行时 | Python | 3.11+ | 后端语言 | MVP |
| Web框架 | FastAPI | 0.109+ | API框架 | MVP |
| ORM | SQLAlchemy | 2.x | 数据库ORM | MVP |
| 异步任务 | Celery + Redis | 5.x | 异步任务队列 | MVP |
| **数据库** | | | | |
| 主数据库 | PostgreSQL | 15.x | 关系型数据库 | MVP |
| 向量扩展 | PgVector | 0.5.x | 向量存储与搜索 | MVP |
| 缓存 | Redis | 7.x | 缓存与会话 | MVP |
| **AI/ML** | | | | |
| OCR | 百度OCR + 腾讯OCR | - | 文字识别 | MVP |
| LLM | OpenAI GPT-4 / DeepSeek | - | 智能分析与解答 | MVP |
| 向量嵌入 | OpenAI Embeddings | - | 文本向量化 | MVP |
| **基础设施** | | | | |
| 容器化 | Docker | 24.x | 应用容器化 | MVP |
| 编排 | Docker Compose | 2.x | 本地开发环境 | MVP |
| CDN | 阿里云CDN | - | 静态资源加速 | Phase 2 |
| 对象存储 | 阿里云OSS | - | 图片存储 | MVP |

---

### 1.3 前端平台策略

#### 1.3.1 平台演进路线

**第一阶段（MVP）：Web端优先**

- **技术选择**：React 18
- **核心目标**：验证产品核心价值
- **交付物**：可运行的Web应用，实现"上传→AI解答→查看图谱"闭环

**第二阶段（扩展）：跨平台适配**

- **技术选择**：Taro 或 Flutter（待定）
- **扩展目标**：覆盖移动端用户，提供更好的移动体验

#### 1.3.2 技术方案对比

| 维度 | React Web | Taro | Flutter |
|-----|----------|------|---------|
| **Web端** | ✅ 原生支持 | ✅ 支持 | ✅ 支持 |
| **iOS/Android** | ❌ 需要重写 | ✅ RN支持 | ✅ 原生性能 |
| **微信小程序** | ❌ 不支持 | ✅ 官方支持 | ⚠️ 有限 |
| **图谱可视化** | ✅ D3.js完整 | ⚠️ 需要适配 | ⚠️ 社区库少 |
| **开发难度** | ⭐ 简单 | ⭐⭐ 中等 | ⭐⭐⭐ 较难 |
| **代码复用率** | 100%（Web） | 70-80% | 90%+ |
| **后端兼容性** | ✅ 完全兼容 | ✅ 完全兼容 | ✅ 完全兼容 |

#### 1.3.3 跨平台方案详细分析

**方案A：Taro（推荐指数：⭐⭐⭐⭐）**

- **优势**：
  - 与React生态无缝对接，学习成本低
  - 国内生态成熟，文档丰富
  - 支持微信小程序（国内用户刚需）
  - 京东开源，团队维护活跃

- **劣势**：
  - 小程序和Web的API差异需要适配
  - 第三方组件库存在兼容性问题
  - D3.js图谱需要额外适配工作

- **适用场景**：主要用户在国内，需要微信小程序入口

**方案B：Flutter（推荐指数：⭐⭐⭐⭐⭐）**

- **优势**：
  - 真正一套代码，所有平台渲染一致
  - 性能接近原生应用
  - Google官方维护，生态成熟
  - Web、iOS、Android、桌面同时支持

- **劣势**：
  - 需要学习Dart语言
  - 与现有Web端React代码不共享
  - D3.js/Three.js图谱库需要用Flutter重写

- **适用场景**：追求极致跨平台体验，愿意投入前端重写

**方案C：React Native for Web（推荐指数：⭐⭐⭐）**

- **优势**：
  - 与Web端技术栈一致
  - 代码复用率较高
  - 社区成熟

- **劣势**：
  - 需要适配不同平台的交互差异
  - 某些浏览器API在RN中不可用
  - iOS对PWA支持有限

- **适用场景**：团队已有React Native经验，希望快速扩展移动端

#### 1.3.4 架构设计原则

**核心原则：前后端分离，API优先**

```
┌─────────────────────────────────────────┐
│              前端层（可替换）             │
│  ┌──────────┐  ┌──────────┐  ┌───────┐  │
│  │  React   │  │  Taro    │  │Flutter│  │
│  │  Web     │  │  RN/小程序│  │ App   │  │
│  └────┬─────┘  └────┬─────┘  └───┬───┘  │
└───────┼─────────────┼────────────┼──────┘
        │             │            │
        └─────────────┼────────────┘
                      │
        ┌─────────────┴────────────┐
        │    RESTful API (稳定)     │
        │  FastAPI Backend Service  │
        │                           │
        │  - 认证服务               │
        │  - 上传服务               │
        │  - AI服务                 │
        │  - 图谱服务               │
        └─────────────┬────────────┘
                      │
        ┌─────────────┴────────────┐
        │      数据存储层           │
        │  PostgreSQL + PgVector   │
        │  Redis + 阿里云OSS        │
        └──────────────────────────┘
```

**设计要点**：

1. **后端API稳定性**：
   - FastAPI后端始终保持稳定
   - 无论前端选择何种技术，后端API接口保持一致
   - API版本化管理（/api/v1/），便于后续升级

2. **前端可替换性**：
   - 前端代码独立于后端
   - 支持渐进式技术演进
   - MVP阶段专注Web端，后续可平滑迁移

3. **业务逻辑复用**：
   - 用户系统、复习算法等核心逻辑在后端实现
   - 前端仅负责UI渲染和用户交互
   - 移动端可直接复用后端业务能力

#### 1.3.5 跨平台适配工作清单

**第二阶段移动端适配需要完成的工作**：

| 类别 | 工作项 | 预估工作量 |
|-----|--------|----------|
| **响应式布局** | 屏幕尺寸适配（手机/平板） | 5人天 |
| **交互适配** | 触摸手势支持（滑动、捏合） | 7人天 |
| **拍照功能** | 相机集成与图片预处理 | 5人天 |
| **推送通知** | 消息推送服务集成 | 3人天 |
| **离线支持** | 本地数据缓存与同步 | 7人天 |
| **图谱适配** | 2D/3D图谱移动端适配 | 15人天 |
| **UI重写** | 移动端UI组件替换 | 10人天 |
| **平台适配** | iOS/Android分别测试调优 | 7人天 |
| **总计** | | **59人天** |

> **说明**：以上为估算，实际工作量可能因技术方案选择而有所调整。

#### 1.3.6 技术决策记录

| 日期 | 决策内容 | 理由 |
|-----|---------|------|
| 2026-01-28 | MVP阶段选择React Web | 图谱可视化功能在Web端最完整，开发效率高 |
| 2026-01-29 | 后端API优先设计 | 保证前后端分离，便于后续前端技术演进 |
| 2026-01-29 | 第二阶段选择TBD | 待第一阶段Web端验证后，根据用户反馈决定 |

---

## 二、数据库设计

### 2.1 数据库概览

**数据库名称**: `neuralnote_prod`

**字符集**: `UTF8MB4`

**时区**: `UTC+8`

### 2.2 核心表结构

#### 2.2.1 用户表 (users)

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20) UNIQUE,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    avatar_url VARCHAR(500),
    timezone VARCHAR(50) DEFAULT 'Asia/Shanghai',
    language VARCHAR(10) DEFAULT 'zh-CN',
    subscription_plan VARCHAR(20) DEFAULT 'free',
    subscription_expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE
);

-- 索引
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_subscription ON users(subscription_plan);
```

**字段说明**:
- `subscription_plan`: free, pro_monthly, pro_yearly, team
- `timezone`: 用户所在时区，用于复习提醒

#### 2.2.2 知识图谱表 (knowledge_graphs)

```sql
CREATE TABLE knowledge_graphs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    subject VARCHAR(50),  -- 学科分类: math, physics, cs, etc.
    cover_image_url VARCHAR(500),
    is_public BOOLEAN DEFAULT FALSE,
    is_preset BOOLEAN DEFAULT FALSE,  -- 是否为公有云预设图谱
    node_count INTEGER DEFAULT 0,
    edge_count INTEGER DEFAULT 0,
    total_review_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_accessed_at TIMESTAMP WITH TIME ZONE
);

-- 索引
CREATE INDEX idx_graphs_user ON knowledge_graphs(user_id);
CREATE INDEX idx_graphs_subject ON knowledge_graphs(subject);
CREATE INDEX idx_graphs_public ON knowledge_graphs(is_public);
```

#### 2.2.3 记忆节点表 (memory_nodes)

**核心设计理念**: 采用 JSONB 存储灵活的节点内容数据，实现"万物皆节点"的架构。

```sql
CREATE TABLE memory_nodes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    graph_id UUID NOT NULL REFERENCES knowledge_graphs(id) ON DELETE CASCADE,
    node_type VARCHAR(20) NOT NULL DEFAULT 'QUESTION',  -- QUESTION, CONCEPT, SNIPPET, INSIGHT
    title VARCHAR(200) NOT NULL,
    summary TEXT,
    
    -- 灵活的内容数据 (JSONB)
    content_data JSONB NOT NULL DEFAULT '{}'::jsonb,
    
    -- 向量嵌入 (用于语义搜索)
    content_embedding vector(1536),
    
    -- 图谱位置信息
    position_x FLOAT DEFAULT 0,
    position_y FLOAT DEFAULT 0,
    position_z FLOAT DEFAULT 0,  -- 3D坐标
    
    -- 复习状态
    review_stats JSONB NOT NULL DEFAULT '{
        "last_reviewed_at": null,
        "next_review_due": null,
        "review_count": 0,
        "forgetting_curve_index": 100,
        "mastery_status": "FRESH"
    }'::jsonb,
    
    -- 元数据
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- 索引
CREATE INDEX idx_nodes_graph ON memory_nodes(graph_id);
CREATE INDEX idx_nodes_type ON memory_nodes(node_type);
CREATE INDEX idx_nodes_embedding ON memory_nodes USING ivfflat (content_embedding vector_cosine_ops);
CREATE INDEX idx_nodes_content ON memory_nodes USING gin (content_data);
CREATE INDEX idx_nodes_review ON memory_nodes USING btree ((review_stats->>'next_review_due'));
```

**content_data 结构示例**:

```json
// QUESTION 类型
{
    "original_image_url": "https://oss.neuralnote.com/nodes/xxx.jpg",
    "ocr_text": "求函数f(x)=x²的导数",
    "ai_answer": "f'(x)=2x",
    "memory_points": ["幂函数求导法则", "链式法则"],
    "difficulty_score": 65.5,
    "difficulty_level": "medium",
    "source": "23年真题",
    "source_url": "https://example.com/question/123",
    "user_notes": "这道题要注意定义域",
    "is_cross_discipline": false,
    "original_subject": "数学",
    "external_references": [
        {"url": "https://example.com/solution", "title": "名师解析"}
    ]
}

// CONCEPT 类型
{
    "definition": "导数描述了函数在某一点的变化率",
    "formula": "f'(x) = lim(Δx→0) [f(x+Δx)-f(x)]/Δx",
    "related_theorems": ["拉格朗日中值定理", "泰勒公式"],
    "examples": ["求速度", "求斜率"],
    "category": "微分学"
}
```

**mastery_status 枚举值**:

| 状态值 | 说明 | 颜色标识 |
|-------|------|---------|
| FRESH | 刚加入，记忆新鲜 | 鲜绿 |
| STABLE | 记忆稳定 | 浅绿 |
| WARNING | 需要关注 | 枯黄 |
| RISK | 遗忘风险 | 浅灰 |
| FORGOTTEN | 需要复习 | 灰暗 |

#### 2.2.4 知识点标签表 (knowledge_tags)

```sql
CREATE TABLE knowledge_tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    graph_id UUID NOT NULL REFERENCES knowledge_graphs(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    parent_id UUID REFERENCES knowledge_tags(id),
    color VARCHAR(20) DEFAULT '#1890FF',
    icon VARCHAR(50),
    importance_score FLOAT DEFAULT 50.0,
    mastery_rate FLOAT DEFAULT 0.0,  -- 该知识点的整体掌握率
    node_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT unique_tag_name UNIQUE (graph_id, name, parent_id)
);

-- 索引
CREATE INDEX idx_tags_graph ON knowledge_tags(graph_id);
CREATE INDEX idx_tags_parent ON knowledge_tags(parent_id);
```

#### 2.2.5 节点-标签关联表 (node_tags)

```sql
CREATE TABLE node_tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    node_id UUID NOT NULL REFERENCES memory_nodes(id) ON DELETE CASCADE,
    tag_id UUID NOT NULL REFERENCES knowledge_tags(id) ON DELETE CASCADE,
    confidence FLOAT DEFAULT 1.0,  -- AI推荐的置信度
    is_manual BOOLEAN DEFAULT FALSE,  -- 是否用户手动添加
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT unique_node_tag UNIQUE (node_id, tag_id)
);

-- 索引
CREATE INDEX idx_node_tags_node ON node_tags(node_id);
CREATE INDEX idx_node_tags_tag ON node_tags(tag_id);
```

#### 2.2.6 节点关联表 (node_relations)

```sql
CREATE TABLE node_relations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    graph_id UUID NOT NULL REFERENCES knowledge_graphs(id) ON DELETE CASCADE,
    source_id UUID NOT NULL REFERENCES memory_nodes(id) ON DELETE CASCADE,
    target_id UUID NOT NULL REFERENCES memory_nodes(id) ON DELETE CASCADE,
    relation_type VARCHAR(20) NOT NULL,  -- PREREQUISITE, VARIANT, RELATED
    strength INTEGER DEFAULT 50,  -- 关联强度 0-100
    is_auto_generated BOOLEAN DEFAULT TRUE,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT unique_relation UNIQUE (source_id, target_id, relation_type)
);

-- 索引
CREATE INDEX idx_relations_graph ON node_relations(graph_id);
CREATE INDEX idx_relations_source ON node_relations(source_id);
CREATE INDEX idx_relations_target ON node_relations(target_id);
CREATE INDEX idx_relations_type ON node_relations(relation_type);
```

**relation_type 枚举值**:

| 类型 | 说明 | 示例 |
|-----|------|------|
| PREREQUISITE | 前置/依赖关系 | 极限 → 导数 |
| VARIANT | 变体/衍生关系 | 基本题 → 变形题 |
| RELATED | 一般关联关系 | 使用相同技巧的题目 |

#### 2.2.7 视图配置表 (view_configs)

```sql
CREATE TABLE view_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    graph_id UUID NOT NULL REFERENCES knowledge_graphs(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    view_type VARCHAR(20) NOT NULL DEFAULT 'custom',  -- preset, custom
    
    -- 过滤配置
    filter_config JSONB NOT NULL DEFAULT '{}'::jsonb,
    
    -- 布局配置
    layout_engine VARCHAR(50) DEFAULT 'force-directed',
    layout_params JSONB DEFAULT '{}'::jsonb,
    
    -- 视觉配置
    color_scheme VARCHAR(50) DEFAULT 'fresh-modern',
    node_size_mode VARCHAR(20) DEFAULT 'fixed',  -- fixed, by-degree, by-review-count
    show_labels BOOLEAN DEFAULT TRUE,
    animation_enabled BOOLEAN DEFAULT TRUE,
    
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_views_user ON view_configs(user_id);
CREATE INDEX idx_views_graph ON view_configs(graph_id);
```

**filter_config 结构示例**:

```json
{
    "node_types": ["QUESTION"],
    "tags": ["导数", "极限"],
    "difficulty_range": [0, 100],
    "mastery_status": ["WARNING", "RISK"],
    "date_range": {
        "start": "2026-01-01",
        "end": "2026-12-31"
    },
    "review_overdue": true
}
```

#### 2.2.8 复习记录表 (review_logs)

```sql
CREATE TABLE review_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    node_id UUID NOT NULL REFERENCES memory_nodes(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    review_mode VARCHAR(20) NOT NULL,  -- graph-traversal, random, focused, spaced
    
    -- 复习结果
    mastery_feedback VARCHAR(20) NOT NULL,  -- remembered, forgot, partial
    time_spent_seconds INTEGER,
    
    -- 复习时的状态快照
    node_state_snapshot JSONB,
    
    -- 上下文信息
    device_type VARCHAR(20),
    app_version VARCHAR(20),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_review_logs_node ON review_logs(node_id);
CREATE INDEX idx_review_logs_user ON review_logs(user_id);
CREATE INDEX idx_review_logs_time ON review_logs(created_at);
```

#### 2.2.9 文件上传记录表 (file_uploads)

```sql
CREATE TABLE file_uploads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    graph_id UUID REFERENCES knowledge_graphs(id),
    
    -- 文件信息
    original_filename VARCHAR(255) NOT NULL,
    stored_filename VARCHAR(255) NOT NULL,
    file_url VARCHAR(500) NOT NULL,
    file_size BIGINT NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    
    -- 处理状态
    status VARCHAR(20) NOT NULL DEFAULT 'pending',  -- pending, processing, completed, failed
    processing_result JSONB,
    error_message TEXT,
    
    -- 元数据
    uploaded_ip VARCHAR(45),
    device_info JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE
);

-- 索引
CREATE INDEX idx_uploads_user ON file_uploads(user_id);
CREATE INDEX idx_uploads_status ON file_uploads(status);
CREATE INDEX idx_uploads_created ON file_uploads(created_at);
```

### 2.3 ER图关系

```
┌─────────────┐         ┌─────────────────────┐
│    users    │ 1    N  │  knowledge_graphs   │
│─────────────│─────────│─────────────────────│
│ id (PK)     │         │ id (PK)             │
│ email       │         │ user_id (FK)        │
│ username    │         │ name                │
│ ...         │         │ subject             │
└─────────────┘         │ ...                 │
                        └──────────┬──────────┘
                                   │
                                   │ 1    N
                        ┌──────────┴──────────┐
                        │  memory_nodes       │
                        │─────────────────────│
                        │ id (PK)             │
                        │ graph_id (FK)       │
                        │ node_type           │
                        │ title               │
                        │ content_data (JSONB)│
                        │ content_embedding   │
                        │ position_x/y/z      │
                        │ review_stats (JSONB)│
                        └──────────┬──────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              │                    │                    │
              │ N                N │ N                N │
   ┌──────────┴──────────┐ ┌──────┴──────┐ ┌──────────┴──────────┐
   │   node_tags         │ │node_relations│ │    review_logs      │
   │─────────────────────│ │─────────────│ │─────────────────────│
   │ id (PK)             │ │id (PK)      │ │ id (PK)             │
   │ graph_id (FK)       │ │source_id    │ │ node_id (FK)        │
   │ name                │ │target_id    │ │ user_id (FK)        │
   │ parent_id           │ │relation_type│ │ mastery_feedback    │
   │ ...                 │ │strength     │ │ time_spent          │
   └─────────────────────┘ │ ...         │ │ ...                 │
                           └─────────────┘ └─────────────────────┘
```

### 2.4 数据库初始化脚本

```sql
-- 创建扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgvector";

-- 启用行级安全策略
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE knowledge_graphs ENABLE ROW LEVEL SECURITY;
ALTER TABLE memory_nodes ENABLE ROW LEVEL SECURITY;

-- 创建函数：自动更新updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 创建触发器
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_graphs_updated_at BEFORE UPDATE ON knowledge_graphs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_nodes_updated_at BEFORE UPDATE ON memory_nodes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

---

## 三、API接口设计

### 3.1 API设计原则

1. **RESTful风格**: 资源导向的URL设计
2. **版本控制**: URL中包含版本号 `/api/v1/`
3. **认证方式**: JWT Token (Bearer Token)
4. **请求格式**: JSON
5. **响应格式**: 统一JSON响应结构
6. **分页**: 使用Cursor-based pagination

### 3.2 统一响应结构

```json
{
    "code": 200,
    "message": "success",
    "data": {
        // 业务数据
    },
    "meta": {
        "request_id": "uuid-string",
        "timestamp": 1706467200,
        "latency_ms": 45
    },
    "pagination": {
        "has_more": true,
        "cursor": "next-page-cursor"
    }
}
```

**错误响应**:

```json
{
    "code": 400,
    "message": "validation_error",
    "error": {
        "field": "email",
        "message": "邮箱格式不正确"
    },
    "meta": {
        "request_id": "uuid-string",
        "timestamp": 1706467200
    }
}
```

**HTTP状态码**:

| 状态码 | 说明 |
|-------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未认证 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 429 | 请求过于频繁 |
| 500 | 服务器错误 |

### 3.3 认证接口

#### 3.3.1 用户注册

**POST** `/api/v1/auth/register`

**Request Body**:

```json
{
    "email": "user@example.com",
    "username": "username",
    "password": "password123",
    "timezone": "Asia/Shanghai"
}
```

**Response (201 Created)**:

```json
{
    "code": 201,
    "message": "registration_successful",
    "data": {
        "user_id": "uuid-string",
        "email": "user@example.com",
        "username": "username",
        "subscription_plan": "free"
    }
}
```

#### 3.3.2 用户登录

**POST** `/api/v1/auth/login`

**Request Body**:

```json
{
    "email": "user@example.com",
    "password": "password123"
}
```

**Response (200 OK)**:

```json
{
    "code": 200,
    "message": "login_successful",
    "data": {
        "access_token": "eyJhbGciOiJIUzI1NiIs...",
        "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
        "token_type": "Bearer",
        "expires_in": 3600,
        "user": {
            "id": "uuid-string",
            "email": "user@example.com",
            "username": "username",
            "avatar_url": "https://...",
            "subscription_plan": "free"
        }
    }
}
```

#### 3.3.3 刷新Token

**POST** `/api/v1/auth/refresh`

**Request Body**:

```json
{
    "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

### 3.4 知识图谱接口

#### 3.4.1 获取图谱列表

**GET** `/api/v1/graphs`

**Query Parameters**:

| 参数 | 类型 | 必填 | 说明 |
|-----|------|------|------|
| cursor | string | 否 | 分页游标 |
| limit | int | 否 | 每页数量 (默认20) |
| subject | string | 否 | 按学科筛选 |

**Response (200 OK)**:

```json
{
    "code": 200,
    "message": "success",
    "data": {
        "graphs": [
            {
                "id": "uuid-string",
                "name": "考研数学",
                "description": "2026考研数学知识点整理",
                "subject": "math",
                "node_count": 156,
                "edge_count": 423,
                "cover_image_url": "https://...",
                "created_at": "2026-01-01T00:00:00Z",
                "last_accessed_at": "2026-01-28T10:30:00Z"
            }
        ]
    },
    "pagination": {
        "has_more": true,
        "cursor": "next-cursor"
    }
}
```

#### 3.4.2 创建图谱

**POST** `/api/v1/graphs`

**Request Body**:

```json
{
    "name": "新图谱",
    "description": "图谱描述",
    "subject": "math"
}
```

**Response (201 Created)**:

```json
{
    "code": 201,
    "message": "graph_created",
    "data": {
        "id": "uuid-string",
        "name": "新图谱",
        "user_id": "uuid-string",
        "created_at": "2026-01-28T10:00:00Z"
    }
}
```

#### 3.4.3 获取图谱详情

**GET** `/api/v1/graphs/{graph_id}`

**Response (200 OK)**:

```json
{
    "code": 200,
    "message": "success",
    "data": {
        "graph": {
            "id": "uuid-string",
            "name": "考研数学",
            "description": "2026考研数学知识点整理",
            "subject": "math",
            "node_count": 156,
            "edge_count": 423,
            "statistics": {
                "total_nodes": 156,
                "total_questions": 142,
                "total_concepts": 14,
                "mastery_distribution": {
                    "fresh": 45,
                    "stable": 60,
                    "warning": 30,
                    "risk": 15,
                    "forgotten": 6
                },
                "avg_difficulty": 65.5,
                "total_review_count": 1234
            }
        }
    }
}
```

### 3.5 题目上传与处理接口

#### 3.5.1 预上传请求

**POST** `/api/v1/upload/prepare`

**Request Body**:

```json
{
    "filename": "question.jpg",
    "file_size": 1024000,
    "mime_type": "image/jpeg",
    "graph_id": "uuid-string"
}
```

**Response (200 OK)**:

```json
{
    "code": 200,
    "message": "upload_prepared",
    "data": {
        "upload_id": "uuid-string",
        "upload_url": "https://oss.neuralnote.com/upload/xxx",
        "expires_in": 3600,
        "fields": {
            "key": "uploads/xxx",
            "policy": "...",
            "signature": "...",
            "access_key_id": "..."
        }
    }
}
```

#### 3.5.2 上传文件

**PUT** `{upload_url}`

**Headers**:

```
Content-Type: image/jpeg
```

**Body**: (二进制文件流)

**Response (204 No Content)**: 上传成功

#### 3.5.3 处理上传的文件

**POST** `/api/v1/upload/process`

**Request Body**:

```json
{
    "upload_id": "uuid-string"
}
```

**Response (200 OK)**:

```json
{
    "code": 200,
    "message": "processing_started",
    "data": {
        "task_id": "uuid-string",
        "status": "processing"
    }
}
```

#### 3.5.4 获取处理结果

**GET** `/api/v1/upload/tasks/{task_id}`

**Response (200 OK)**:

```json
{
    "code": 200,
    "message": "success",
    "data": {
        "task_id": "uuid-string",
        "status": "completed",
        "result": {
            "ocr_result": {
                "text": "求函数f(x)=x²的导数",
                "confidence": 0.98,
                "formula_latex": "f'(x) = 2x"
            },
            "ai_analysis": {
                "suggested_title": "23真题-导数-幂函数求导",
                "suggested_tags": ["导数", "幂函数", "求导法则"],
                "difficulty_score": 65.5,
                "difficulty_level": "medium",
                "suggested_answer": "根据幂函数求导法则...",
                "memory_points": ["幂函数求导公式", "链式法则应用"]
            }
        }
    }
}
```

### 3.6 节点操作接口

#### 3.6.1 确认并保存节点

**POST** `/api/v1/nodes`

**Request Body**:

```json
{
    "graph_id": "uuid-string",
    "upload_id": "uuid-string",
    "title": "23真题-导数-幂函数求导",
    "node_type": "QUESTION",
    "content_data": {
        "ocr_text": "求函数f(x)=x²的导数",
        "ai_answer": "f'(x)=2x",
        "memory_points": ["幂函数求导公式"],
        "difficulty_level": "medium",
        "source": "23年真题"
    },
    "tags": ["导数", "幂函数"],
    "position": {
        "x": 100,
        "y": 200
    },
    "options": {
        "auto_layout": true,
        "find_similar": true
    }
}
```

**Response (201 Created)**:

```json
{
    "code": 201,
    "message": "node_created",
    "data": {
        "node": {
            "id": "uuid-string",
            "title": "23真题-导数-幂函数求导",
            "position": {
                "x": 100,
                "y": 200
            }
        },
        "related_nodes": [
            {
                "id": "uuid-string",
                "title": "基础题-导数定义",
                "relation_type": "PREREQUISITE",
                "strength": 85
            }
        ],
        "graph_stats": {
            "node_count": 157,
            "edge_count": 425
        }
    }
}
```

#### 3.6.2 获取节点详情

**GET** `/api/v1/nodes/{node_id}`

**Response (200 OK)**:

```json
{
    "code": 200,
    "message": "success",
    "data": {
        "node": {
            "id": "uuid-string",
            "graph_id": "uuid-string",
            "node_type": "QUESTION",
            "title": "23真题-导数-幂函数求导",
            "summary": "幂函数求导基础题",
            "content_data": {
                "original_image_url": "https://...",
                "ocr_text": "求函数f(x)=x²的导数",
                "ai_answer": "f'(x)=2x",
                "memory_points": ["幂函数求导公式"],
                "difficulty_level": "medium",
                "source": "23年真题"
            },
            "position": {
                "x": 100,
                "y": 200,
                "z": 0
            },
            "review_stats": {
                "last_reviewed_at": "2026-01-25T10:00:00Z",
                "next_review_due": "2026-02-01T10:00:00Z",
                "review_count": 3,
                "forgetting_curve_index": 45.5,
                "mastery_status": "STABLE"
            },
            "tags": ["导数", "幂函数"],
            "created_at": "2026-01-01T00:00:00Z"
        },
        "related_nodes": [
            {
                "id": "uuid-string",
                "title": "基础题-导数定义",
                "relation_type": "PREREQUISITE",
                "strength": 85
            }
        ]
    }
}
```

#### 3.6.3 获取图谱节点列表

**GET** `/api/v1/graphs/{graph_id}/nodes`

**Query Parameters**:

| 参数 | 类型 | 必填 | 说明 |
|-----|------|------|------|
| cursor | string | 否 | 分页游标 |
| limit | int | 否 | 每页数量 (默认50) |
| node_type | string | 否 | 节点类型筛选 |
| tags | string | 否 | 标签筛选 (逗号分隔) |
| mastery_status | string | 否 | 掌握状态筛选 |
| search | string | 否 | 关键词搜索 |

**Response (200 OK)**:

```json
{
    "code": 200,
    "message": "success",
    "data": {
        "nodes": [
            {
                "id": "uuid-string",
                "title": "23真题-导数-幂函数求导",
                "node_type": "QUESTION",
                "summary": "幂函数求导基础题",
                "position": {
                    "x": 100,
                    "y": 200
                },
                "review_stats": {
                    "mastery_status": "STABLE",
                    "forgetting_curve_index": 45.5
                },
                "tags": ["导数", "幂函数"]
            }
        ],
        "layout_data": {
            "nodes": [...],
            "edges": [...]
        }
    },
    "pagination": {
        "has_more": true,
        "cursor": "next-cursor"
    }
}
```

### 3.7 复习管理接口

#### 3.7.1 获取复习队列

**POST** `/api/v1/review/queue`

**Request Body**:

```json
{
    "graph_id": "uuid-string",
    "mode": "graph-traversal",  // graph-traversal, random, focused, spaced
    "limit": 10,
    "filters": {
        "tags": ["导数"],
        "mastery_status": ["WARNING", "RISK"],
        "difficulty_min": 0,
        "difficulty_max": 100
    }
}
```

**Response (200 OK)**:

```json
{
    "code": 200,
    "message": "success",
    "data": {
        "queue_id": "uuid-string",
        "mode": "graph-traversal",
        "total_count": 15,
        "items": [
            {
                "position": 1,
                "node": {
                    "id": "uuid-string",
                    "title": "23真题-导数-幂函数求导",
                    "content_data": {
                        "original_image_url": "https://...",
                        "memory_points": ["幂函数求导公式"]
                    }
                },
                "context": {
                    "previous_node_id": "uuid-string",
                    "next_node_id": "uuid-string",
                    "path_from_root": ["高等数学", "微分学", "导数"]
                }
            }
        ]
    }
}
```

#### 3.7.2 提交复习反馈

**POST** `/api/v1/review/feedback`

**Request Body**:

```json
{
    "queue_id": "uuid-string",
    "node_id": "uuid-string",
    "mastery_feedback": "remembered",  // remembered, forgot, partial
    "time_spent_seconds": 45,
    "memorandum": "这道题的关键是记住幂函数求导公式"
}
```

**Response (200 OK)**:

```json
{
    "code": 200,
    "message": "feedback_recorded",
    "data": {
        "node_review_stats": {
            "review_count": 4,
            "forgetting_curve_index": 38.2,
            "mastery_status": "STABLE",
            "next_review_due": "2026-02-04T10:00:00Z"
        },
        "queue_progress": {
            "current_position": 2,
            "remaining_count": 13
        }
    }
}
```

### 3.8 视图管理接口

#### 3.8.1 保存视图配置

**POST** `/api/v1/graphs/{graph_id}/views`

**Request Body**:

```json
{
    "name": "高频错题视图",
    "description": "显示所有标记为错题的题目",
    "filter_config": {
        "node_types": ["QUESTION"],
        "tags": ["错题"],
        "mastery_status": ["WARNING", "RISK"]
    },
    "layout_engine": "force-directed",
    "color_scheme": "warm-garden",
    "is_default": false
}
```

#### 3.8.2 获取视图列表

**GET** `/api/v1/graphs/{graph_id}/views`

**Response (200 OK)**:

```json
{
    "code": 200,
    "message": "success",
    "data": {
        "preset_views": [
            {
                "id": "uuid-string",
                "name": "教材映射视图",
                "description": "按教材章节组织",
                "view_type": "preset"
            }
        ],
        "custom_views": [
            {
                "id": "uuid-string",
                "name": "高频错题视图",
                "description": "显示所有标记为错题的题目",
                "view_type": "custom",
                "created_at": "2026-01-28T10:00:00Z"
            }
        ]
    }
}
```

---

## 四、第三方服务配置

### 4.1 OCR服务配置

#### 4.1.1 百度OCR

```yaml
# 百度OCR配置
BAIDU_OCR:
  enabled: true
  api_key: "${BAIDU_OCR_API_KEY}"
  secret_key: "${BAIDU_OCR_SECRET_KEY}"
  endpoint: "https://aip.baidubce.com/rest/2.0/ocr/v1"
  timeout: 30
  retry_times: 3
  
  # 启用服务
  services:
    - basic_general       # 通用文字识别
    - accurate_basic      # 高精度文字识别
    - formula recognition # 数学公式识别
  
  # 配额限制
  quota:
    daily_limit: 10000    # 每日调用次数
    monthly_limit: 300000
```

#### 4.1.2 腾讯OCR

```yaml
# 腾讯OCR配置
TENCENT_OCR:
  enabled: true
  secret_id: "${TENCENT_OCR_SECRET_ID}"
  secret_key: "${TENCENT_OCR_SECRET_KEY}"
  endpoint: "ocr.tencentcloudapi.com"
  timeout: 30
  retry_times: 3
  
  # 启用服务
  services:
    - general_ocr         # 通用OCR
    - formula_ocr         # 公式识别
```

#### 4.1.3 OCR结果融合策略

```python
# 伪代码：OCR结果融合
def fuse_ocr_results(results: List[OCRResult]) -> FusedResult:
    """
    融合多个OCR服务的结果
    """
    # 1. 文本识别结果投票
    text_votes = {}
    for result in results:
        if result.text:
            for text in result.text:
                text_votes[text] = text_votes.get(text, 0) + result.confidence
    
    best_text = max(text_votes, key=text_votes.get)
    
    # 2. 公式识别结果选择（选择置信度最高的）
    formula_results = [r.formula for r in results if r.formula]
    best_formula = max(formula_results, key=lambda x: x.confidence) if formula_results else None
    
    # 3. 边界框合并（用于多引擎定位）
    fused_boxes = merge_boxes([r.bounding_boxes for r in results])
    
    return FusedResult(
        text=best_text,
        formula=best_formula,
        bounding_boxes=fused_boxes,
        overall_confidence=calculate_overall_confidence(results)
    )
```

### 4.2 大语言模型配置

#### 4.2.1 OpenAI GPT-4

```yaml
# OpenAI配置
OPENAI:
  enabled: true
  api_key: "${OPENAI_API_KEY}"
  base_url: "https://api.openai.com/v1"
  timeout: 120
  max_retries: 3
  
  models:
    gpt4:
      name: "gpt-4-turbo-preview"
      max_tokens: 4096
      temperature: 0.3
      streaming: true
    gpt35:
      name: "gpt-3.5-turbo"
      max_tokens: 2048
      temperature: 0.3
      streaming: true
  
  # 速率限制
  rate_limit:
    requests_per_minute: 60
    tokens_per_minute: 100000
```

#### 4.2.2 DeepSeek

```yaml
# DeepSeek配置
DEEPSEEK:
  enabled: true
  api_key: "${DEEPSEEK_API_KEY}"
  base_url: "https://api.deepseek.com/v1"
  timeout: 120
  max_retries: 3
  
  models:
    deepseek:
      name: "deepseek-chat"
      max_tokens: 4096
      temperature: 0.3
      streaming: true
  
  # 速率限制
  rate_limit:
    requests_per_minute: 100
    tokens_per_minute: 200000
```

#### 4.2.3 提示词模板

```yaml
# 提示词模板库
PROMPT_TEMPLATES:
  
  question_analysis: |
    你是一个专业的教育AI助手。请分析以下题目，提供详细的解答和知识点分析。
    
    题目内容：
    {{question_text}}
    
    请按以下格式输出：
    1. 详细解答过程
    2. 核心知识点列表
    3. 解题技巧总结
    4. 难度评估 (1-100分)
    5. 推荐的关联题目类型
  
  tag_suggestion: |
    你是一个知识管理专家。请为以下题目推荐合适的标签。
    
    题目：{{question_text}}
    已有标签：{{existing_tags}}
    
    请推荐5-10个标签，包含：
    - 学科类别
    - 章节知识点
    - 解题方法
    - 难度等级
    - 常见错误点
  
  difficulty_assessment: |
    请评估以下题目的难度，从多个维度进行分析。
    
    题目：{{question_text}}
    解答：{{answer}}
    
    请给出以下维度的评分（1-10分）：
    1. 知识深度
    2. 思维复杂度
    3. 计算量
    4. 创新性
    5. 综合难度（1-100分）
```

### 4.3 对象存储配置

#### 4.3.1 阿里云OSS

```yaml
# 阿里云OSS配置
ALIYUN_OSS:
  enabled: true
  access_key_id: "${ALIYUN_ACCESS_KEY_ID}"
  access_key_secret: "${ALIYUN_ACCESS_KEY_SECRET}"
  endpoint: "oss-cn-hangzhou.aliyuncs.com"
  bucket: "neuralnote-media"
  
  # 访问配置
  public_endpoint: "https://neuralnote-media.oss-cn-hangzhou.aliyuncs.com"
  
  # 存储策略
  storage:
    images:
      dir: "images/"
      expires_days: 365
      max_size_mb: 10
    documents:
      dir: "documents/"
      expires_days: 365
      max_size_mb: 50
    thumbnails:
      dir: "thumbnails/"
      expires_days: 90
      max_size_mb: 2
  
  # CDN配置
  cdn:
    enabled: true
    domain: "cdn.neuralnote.com"
    https_enabled: true
```

#### 4.3.2 图片处理策略

```python
# 伪代码：图片上传处理
async def process_uploaded_image(file_data: bytes, upload_id: str) -> dict:
    """
    处理上传的图片：压缩、生成缩略图、OCR识别
    """
    # 1. 压缩图片
    compressed = await compress_image(file_data, quality=85, max_width=2000)
    
    # 2. 生成缩略图
    thumbnail = await generate_thumbnail(compressed, size=(300, 300))
    
    # 3. 上传到OSS
    original_url = await upload_to_oss(compressed, f"images/{upload_id}.jpg")
    thumbnail_url = await upload_to_oss(thumbnail, f"thumbnails/{upload_id}_thumb.jpg")
    
    # 4. 调用OCR服务
    ocr_result = await ocr_service.recognize(original_url)
    
    return {
        "original_url": original_url,
        "thumbnail_url": thumbnail_url,
        "ocr_result": ocr_result
    }
```

### 4.4 向量数据库配置

#### 4.4.1 PgVector配置

```yaml
# PgVector配置
PGVECTOR:
  enabled: true
  
  # 向量维度
  embedding_dim: 1536  # OpenAI text-embedding-3-small
  
  # 索引配置
  index_type: "ivfflat"  # ivfflat 或 hnsw
  ivfflat:
    lists: 100  # 聚类数量
    probes: 10  # 查询时检查的聚类数
  hnsw:
    m: 16       # 每个节点的连接数
    ef_construction: 64  # 构建时的搜索宽度
    ef: 10      # 查询时的搜索宽度
  
  # 相似度搜索参数
  similarity_threshold: 0.7
  max_results: 10
```

#### 4.4.2 相似题目查询

```sql
-- 查找与指定题目相似的题目
SELECT 
    node.id,
    node.title,
    1 - (node.content_embedding <=> query_embedding) AS similarity,
    node.content_data->>'difficulty_level' as difficulty
FROM memory_nodes node
WHERE node.graph_id = 'target-graph-id'
  AND node.node_type = 'QUESTION'
  AND node.deleted_at IS NULL
  AND 1 - (node.content_embedding <=> query_embedding) > 0.7
ORDER BY similarity DESC
LIMIT 10;
```

---

## 五、核心算法实现

### 5.1 遗忘曲线算法 (SM-2变体)

```python
"""
基于艾宾浩斯遗忘曲线的复习算法
参考 SuperMemo SM-2 算法
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional


class MasteryStatus(Enum):
    FRESH = "fresh"       # 刚加入
    STABLE = "stable"     # 稳定
    WARNING = "warning"   # 需要关注
    RISK = "risk"         # 遗忘风险
    FORGOTTEN = "forgotten"  # 需要复习


@dataclass
class ReviewResult:
    """复习结果"""
    node_id: str
    ease_factor: float  # 难度系数 (1.3 - 2.5)
    interval_days: int  # 下次复习间隔
    repetitions: int    # 重复次数
    mastery_status: MasteryStatus


class ForgettingCurveCalculator:
    """遗忘曲线计算器"""
    
    # 基础参数
    MIN_EASE_FACTOR = 1.3
    MAX_EASE_FACTOR = 2.5
    DEFAULT_EASE_FACTOR = 2.5
    
    # 状态阈值
    THRESHOLDS = {
        MasteryStatus.FRESH: 30,      # 0-30: 新鲜
        MasteryStatus.STABLE: 50,     # 30-50: 稳定
        MasteryStatus.WARNING: 70,    # 50-70: 需要关注
        MasteryStatus.RISK: 85,       # 70-85: 遗忘风险
        MasteryStatus.FORGOTTEN: 100  # 85+: 需要复习
    }
    
    def __init__(self, difficulty_weight: float = 1.0):
        """
        初始化计算器
        
        Args:
            difficulty_weight: 难度权重 (困难题目遗忘更快)
        """
        self.difficulty_weight = difficulty_weight
    
    def calculate_forgetting_index(
        self,
        last_reviewed_at: Optional[datetime],
        review_count: int,
        mastery_feedback: str,
        base_difficulty: float = 50.0
    ) -> float:
        """
        计算遗忘指数
        
        Args:
            last_reviewed_at: 上次复习时间
            review_count: 复习次数
            mastery_feedback: 掌握反馈 (remembered, forgot, partial)
            base_difficulty: 基础难度 (0-100)
        
        Returns:
            遗忘指数 (0-100)
        """
        if last_reviewed_at is None:
            return 100.0  # 新题目，遗忘指数最高
        
        # 计算距离上次复习的天数
        days_since_review = (datetime.now() - last_reviewed_at).days
        
        # 基础遗忘曲线 (指数衰减)
        base_decay = 100 * (0.9 ** days_since_review)
        
        # 复习次数影响 (复习次数越多，遗忘越慢)
        repetition_bonus = min(review_count * 3, 20)  # 最多减20分
        
        # 掌握反馈影响
        feedback_map = {
            "remembered": -15,   # 记得，减轻遗忘
            "partial": -5,       # 部分记得，轻微减轻
            "forgot": 10         # 忘了，加重遗忘
        }
        feedback_impact = feedback_map.get(mastery_feedback, 0)
        
        # 难度影响 (难度越高，遗忘越快)
        difficulty_impact = (base_difficulty / 100 - 0.5) * self.difficulty_weight * 10
        
        # 综合计算
        forgetting_index = base_decay - repetition_bonus + feedback_impact + difficulty_impact
        
        return max(0, min(100, forgetting_index))
    
    def get_mastery_status(self, forgetting_index: float) -> MasteryStatus:
        """根据遗忘指数获取掌握状态"""
        for status, threshold in sorted(self.THRESHOLDS.items(), key=lambda x: x[1]):
            if forgetting_index <= threshold:
                return status
        return MasteryStatus.FORGOTTEN
    
    def calculate_next_review_interval(
        self,
        ease_factor: float,
        repetitions: int,
        quality: int  # 0-5 回忆质量评分
    ) -> int:
        """
        计算下次复习间隔
        
        Args:
            ease_factor: 难度系数
            repetitions: 已复习次数
            quality: 回忆质量评分 (0-5)
        
        Returns:
            下次复习间隔天数
        """
        if quality < 3:
            # 回忆失败，重置
            return 1
        
        if repetitions == 0:
            return 1
        elif repetitions == 1:
            return 6
        else:
            # SM-2 公式
            interval = int(ease_factor * self._get_interval(repetitions - 1))
            return min(interval, 365)  # 最多一年
    
    def _get_interval(self, n: int) -> int:
        """获取第n次复习的基础间隔"""
        intervals = [0, 1, 6, 12, 24, 48, 96]  # 天数
        return intervals[min(n, len(intervals) - 1)]
    
    def update_ease_factor(
        self,
        ease_factor: float,
        quality: int
    ) -> float:
        """
        更新难度系数
        
        SM-2 公式: EF' = EF + (0.1 - (5-q) * (0.08 + (5-q) * 0.02))
        """
        if quality < 3:
            return ease_factor  # 回忆失败不更新
        
        new_ef = ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        return max(self.MIN_EASE_FACTOR, min(self.MAX_EASE_FACTOR, new_ef))


# 使用示例
def example_usage():
    calculator = ForgettingCurveCalculator(difficulty_weight=1.2)
    
    # 模拟一次复习
    last_reviewed = datetime.now() - timedelta(days=5)
    forgetting_idx = calculator.calculate_forgetting_index(
        last_reviewed_at=last_reviewed,
        review_count=3,
        mastery_feedback="remembered",
        base_difficulty=65.5
    )
    
    status = calculator.get_mastery_status(forgetting_idx)
    
    print(f"遗忘指数: {forgetting_idx:.1f}")
    print(f"掌握状态: {status.value}")
```

### 5.2 智能归类算法

```python
"""
智能题目归类算法
使用AI预测题目的最佳归类方案
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum


class RelationType(Enum):
    PREREQUISITE = "prerequisite"  # 前置关系
    VARIANT = "variant"            # 变体关系
    RELATED = "related"            # 一般关联


@dataclass
class ClassificationCandidate:
    """归类候选方案"""
    parent_tag_id: Optional[str]
    parent_tag_name: str
    confidence: float
    reason: str
    suggested_new_tag: Optional[str] = None


@dataclass
class RelationCandidate:
    """关联候选"""
    target_node_id: str
    target_title: str
    relation_type: RelationType
    strength: int  # 0-100
    reason: str


class SmartClassifier:
    """智能分类器"""
    
    def __init__(self, llm_client):
        self.llm = llm_client
    
    async def classify_question(
        self,
        question_text: str,
        ai_answer: str,
        existing_tags: List[Dict],
        graph_knowledge_structure: Dict
    ) -> List[ClassificationCandidate]:
        """
        为题目预测归类方案
        
        Args:
            question_text: 题目文本
            ai_answer: AI解答
            existing_tags: 现有标签列表
            graph_knowledge_structure: 图谱知识结构
        
        Returns:
            归类候选方案列表
        """
        prompt = self._build_classification_prompt(
            question_text, ai_answer, existing_tags, graph_knowledge_structure
        )
        
        response = await self.llm.generate(prompt)
        
        # 解析AI响应
        candidates = self._parse_classification_response(response)
        
        return candidates
    
    def find_similar_nodes(
        self,
        question_embedding: List[float],
        graph_id: str,
        exclude_node_id: Optional[str] = None,
        top_k: int = 10
    ) -> List[RelationCandidate]:
        """
        查找相似节点
        
        Args:
            question_embedding: 问题向量
            graph_id: 图谱ID
            exclude_node_id: 排除的节点ID
            top_k: 返回数量
        
        Returns:
            相似节点列表
        """
        # 向量数据库查询
        similar_nodes = self.vector_db.search(
            embedding=question_embedding,
            filter={"graph_id": graph_id},
            limit=top_k + 1
        )
        
        # 排除自身并转换为候选
        candidates = []
        for node in similar_nodes:
            if node.id == exclude_node_id:
                continue
            
            relation = self._determine_relation_type(
                node.similarity_score,
                node.content_type
            )
            
            candidates.append(RelationCandidate(
                target_node_id=node.id,
                target_title=node.title,
                relation_type=relation,
                strength=int(node.similarity_score * 100),
                reason=f"相似度: {node.similarity_score:.2f}"
            ))
        
        return candidates
    
    def _build_classification_prompt(
        self,
        question_text: str,
        ai_answer: str,
        existing_tags: List[Dict],
        knowledge_structure: Dict
    ) -> str:
        """构建分类提示词"""
        return f"""
        你是一个专业的题目分类专家。请分析以下题目，推荐最佳的归类方案。
        
        题目内容：
        {question_text}
        
        AI解答：
        {ai_answer}
        
        现有知识结构：
        {knowledge_structure}
        
        请分析这道题目的知识点，并给出归类建议。
        如果现有知识结构中没有合适的父节点，可以建议创建新节点。
        
        输出格式（JSON）：
        {{
            "candidates": [
                {{
                    "parent_tag_name": "导数",
                    "confidence": 0.85,
                    "reason": "题目涉及导数的基本计算"
                }},
                {{
                    "parent_tag_name": "新节点-幂函数",
                    "confidence": 0.6,
                    "reason": "这道题也可以归类到幂函数专题",
                    "suggested_new_tag": "幂函数求导"
                }}
            ]
        }}
        """
    
    def _parse_classification_response(self, response: str) -> List[ClassificationCandidate]:
        """解析AI分类响应"""
        import json
        
        data = json.loads(response)
        
        return [
            ClassificationCandidate(
                parent_tag_id=None,  # 后续查询
                parent_tag_name=c["parent_tag_name"],
                confidence=c["confidence"],
                reason=c["reason"],
                suggested_new_tag=c.get("suggested_new_tag")
            )
            for c in data.get("candidates", [])
        ]
    
    def _determine_relation_type(
        self,
        similarity: float,
        node_type: str
    ) -> RelationType:
        """根据相似度确定关联类型"""
        if similarity > 0.9:
            return RelationType.VARIANT  # 高度相似，可能是变体
        elif similarity > 0.7:
            return RelationType.PREREQUISITE  # 中高度相似，可能是前置
        else:
            return RelationType.RELATED  # 一般关联


# 使用示例
async def example_classification():
    classifier = SmartClassifier(llm_client=openai_client)
    
    candidates = await classifier.classify_question(
        question_text="求函数f(x)=x³的导数",
        ai_answer="使用幂函数求导法则，f'(x)=3x²",
        existing_tags=[
            {"id": "1", "name": "导数"},
            {"id": "2", "name": "微分学"}
        ],
        graph_knowledge_structure={
            "root": "高等数学",
            "children": ["极限", "导数", "积分"]
        }
    )
    
    for c in candidates:
        print(f"- {c.parent_tag_name} (置信度: {c.confidence})")
        print(f"  原因: {c.reason}")
```

---

## 六、部署配置

### 6.1 Docker Compose 配置

```yaml
# docker-compose.yml
version: '3.8'

services:
  # PostgreSQL + PgVector
  postgres:
    image: pgvector/pgvector:pg15
    container_name: neuralnote-db
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-neuralnote}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-password}
      POSTGRES_DB: ${POSTGRES_DB:-neuralnote_prod}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-scripts:/docker-entrypoint-initdb.d
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-neuralnote}"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  # Redis
  redis:
    image: redis:7-alpine
    container_name: neuralnote-redis
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  # 后端服务
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: neuralnote-backend
    environment:
      - DATABASE_URL=postgresql://${POSTGRES_USER:-neuralnote}:${POSTGRES_PASSWORD:-password}@postgres:5432/${POSTGRES_DB:-neuralnote_prod}
      - REDIS_URL=redis://redis:6379/0
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}
      - ALIYUN_ACCESS_KEY_ID=${ALIYUN_ACCESS_KEY_ID}
      - ALIYUN_ACCESS_KEY_SECRET=${ALIYUN_ACCESS_KEY_SECRET}
    volumes:
      - ./backend:/app
      - uploads_data:/app/uploads
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped

  # Nginx (API Gateway)
  nginx:
    image: nginx:alpine
    container_name: neuralnote-nginx
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./certs:/etc/nginx/certs:ro
      - static_data:/var/www/static
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - backend
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  uploads_data:
  static_data:

networks:
  default:
    name: neuralnote-network
```

### 6.2 Nginx 配置

```nginx
# nginx.conf
events {
    worker_connections 2048;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # 日志格式
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for" '
                    'rt=$request_time uct="$upstream_connect_time" '
                    'uht="$upstream_header_time" urt="$upstream_response_time"';

    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log warn;

    # Gzip压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/json application/xml;

    # 上游服务器
    upstream backend {
        server backend:8000;
        keepalive 32;
    }

    server {
        listen 80;
        server_name api.neuralnote.com;

        # 重定向到HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name api.neuralnote.com;

        ssl_certificate /etc/nginx/certs/cert.pem;
        ssl_certificate_key /etc/nginx/certs/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;

        # API路由
        location /api/ {
            limit_req zone=api_limit burst=20 nodelay;
            
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # 超时设置
            proxy_connect_timeout 30s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
            
            # 文件上传大小限制
            client_max_body_size 50M;
        }

        # 静态资源
        location /static/ {
            alias /var/www/static/;
            expires 30d;
            add_header Cache-Control "public, immutable";
        }

        # 健康检查
        location /health {
            access_log off;
            return 200 "OK";
            add_header Content-Type text/plain;
        }
    }

    # 文件上传大小限制
    client_max_body_size 50M;
}
```

### 6.3 环境变量配置

```bash
# .env.example

# 数据库
POSTGRES_USER=neuralnote
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=neuralnote_prod

# Redis
REDIS_PASSWORD=your_redis_password

# 应用配置
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=your_secret_key_here

# OpenAI
OPENAI_API_KEY=sk-your-openai-key

# DeepSeek
DEEPSEEK_API_KEY=sk-your-deepseek-key

# 阿里云OSS
ALIYUN_ACCESS_KEY_ID=your-access-key-id
ALIYUN_ACCESS_KEY_SECRET=your-access-key-secret
ALIYUN_OSS_BUCKET=neuralnote-media
ALIYUN_OSS_ENDPOINT=oss-cn-hangzhou.aliyuncs.com

# 百度OCR
BAIDU_OCR_API_KEY=your-api-key
BAIDU_OCR_SECRET_KEY=your-secret-key

# 腾讯OCR
TENCENT_OCR_SECRET_ID=your-secret-id
TENCENT_OCR_SECRET_KEY=your-secret-key
```

---

## 七、监控与日志

### 7.1 日志配置

```python
# logging_config.py
import logging
import sys
from pythonjsonlogger import jsonlogger


def setup_logging(log_level: str = "INFO"):
    """配置日志"""
    
    # 创建JSON格式日志处理器
    json_handler = logging.StreamHandler(sys.stdout)
    json_handler.setFormatter(jsonlogger.JsonFormatter(
        fmt='%(asctime)s %(levelname)s %(name)s %(message)s',
        datefmt='%Y-%m-%dT%H:%M:%SZ'
    ))
    
    # 根日志器配置
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level))
    root_logger.addHandler(json_handler)
    
    # 特定日志器配置
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


class RequestLogger:
    """请求日志中间件"""
    
    async def __call__(self, request, call_next):
        import time
        import uuid
        
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        
        # 记录请求开始
        start_time = time.time()
        
        # 处理请求
        response = await call_next(request)
        
        # 计算耗时
        duration_ms = (time.time() - start_time) * 1000
        
        # 记录日志
        logging.info(
            "request_completed",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round(duration_ms, 2),
                "client_ip": request.client.host if request.client else None
            }
        )
        
        # 添加request_id到响应头
        response.headers["X-Request-ID"] = request_id
        
        return response
```

### 7.2 性能指标

```python
# metrics.py
from prometheus_client import Counter, Histogram, Gauge, generate_latest

# 请求计数器
REQUEST_COUNT = Counter(
    'neuralnote_requests_total',
    'Total number of API requests',
    ['method', 'endpoint', 'status']
)

# 请求延迟直方图
REQUEST_LATENCY = Histogram(
    'neuralnote_request_duration_seconds',
    'Request latency in seconds',
    ['method', 'endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

# 活跃用户Gauge
ACTIVE_USERS = Gauge(
    'neuralnote_active_users',
    'Number of active users in the last 5 minutes'
)

# 图谱节点数
GRAPH_NODE_COUNT = Gauge(
    'neuralnote_graph_nodes_total',
    'Total number of nodes across all graphs',
    ['graph_id']
)


# 使用装饰器记录指标
def track_metrics(endpoint: str):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            import time
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                status = 200
            except Exception as e:
                status = 500
                raise
            finally:
                duration = time.time() - start_time
                REQUEST_COUNT.labels(
                    method='POST',
                    endpoint=endpoint,
                    status=status
                ).inc()
                REQUEST_LATENCY.labels(
                    method='POST',
                    endpoint=endpoint
                ).observe(duration)
            
            return result
        return wrapper
    return decorator
```

---

## 文档修订记录

| 版本 | 日期 | 修订人 | 修订内容 |
|-----|------|-------|---------|
| V1.0 | 2026-01-28 | Matrix Agent | 初稿完成，数据库设计、API接口、第三方配置 |

---

*本文档由 NeuralNote 技术团队编制，作为技术实现的施工图纸。*