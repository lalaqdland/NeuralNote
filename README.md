# NeuralNote (纽伦笔记)

<p align="center">
  <strong>Be Your Own Memory Architect.</strong><br>
  做你自己的记忆架构师
</p>

<p align="center">
  <a href="#功能特性">功能特性</a> •
  <a href="#技术栈">技术栈</a> •
  <a href="#快速开始">快速开始</a> •
  <a href="#文档体系">文档体系</a> •
  <a href="#开发路线图">开发路线图</a>
</p>

---

## 📖 项目简介

NeuralNote 是一款基于人工智能的智能学习管理工具，致力于帮助用户将零散的刷题经历转化为结构化的个人知识资产。

### 核心价值

- **自动化**：拍照上传题目，AI自动识别、解答、归类
- **可视化**：知识图谱直观展示知识点分布与关联
- **资产化**：题目越存越多，知识网络越织越密，形成个人知识资产

### 目标用户

- 📚 **考试备考族**：考研、考公、考编等需要大量刷题的用户
- 💻 **技术面试者**：准备算法面试，需要系统掌握算法和数据结构
- 🎓 **终身学习者**：持续学习新知识，希望构建个人知识体系

---

## ✨ 功能特性

### 核心功能

| 功能 | 描述 |
|-----|------|
| 📷 **智能采集** | 支持拍照、截图、文件上传，OCR自动识别题目 |
| 🤖 **AI解答** | AI自动生成详细解答和关键记忆点 |
| 🏷️ **智能归类** | AI预测归类方案，用户确认即可完成整理 |
| 📊 **知识图谱** | 可视化展示知识点分布，支持2D/3D视图 |
| 🧠 **智能复习** | 基于遗忘曲线算法，智能提醒最佳复习时机 |
| 🎨 **多视图切换** | 支持多种布局风格，满足不同使用场景 |
| 🚫 **跨学科检测** | 智能识别并提醒跨学科题目，避免误操作 |

### 特色功能

- **题目数字指纹**：AI生成题目唯一标识，快速回忆题目内容
- **颜色标注系统**：根据掌握状态自动着色，直观了解知识盲区
- **游戏化激励**：点亮地图、闪念卡片等设计，提升复习动力
- **公有云图谱**：接入标准知识树，快速上手无需自行整理

---

## 🛠️ 技术栈

### 后端技术

- **运行时**：Python 3.11+
- **Web框架**：FastAPI
- **数据库**：PostgreSQL 15 + PgVector
- **缓存**：Redis 7
- **ORM**：SQLAlchemy 2.x
- **异步任务**：Celery + Redis

### 前端技术

- **框架**：React 18
- **状态管理**：Redux Toolkit
- **2D图谱**：D3.js / Cytoscape.js
- **3D图谱**：Three.js + 3d-force-graph
- **UI组件**：Ant Design / Material-UI

### AI/ML服务

- **OCR**：百度OCR + 腾讯OCR（多引擎融合）
- **LLM**：DeepSeek（主力）+ GPT-4（兜底）
- **向量数据库**：PgVector（语义搜索）

### 基础设施

- **容器化**：Docker 24.x
- **编排**：Docker Compose
- **CDN**：阿里云CDN
- **对象存储**：阿里云OSS

---

## 🚀 快速开始

### 环境要求

- Docker Desktop 24.x+
- Python 3.11+（本地开发）
- PostgreSQL 15+（本地开发）
- Redis 7+（本地开发）

### 本地开发

1. **克隆项目**

```bash
git clone https://github.com/your-org/NeuralNote.git
cd NeuralNote
```

2. **启动基础设施**

```bash
docker-compose up -d postgres redis
```

3. **配置环境变量**

```bash
cp .env.example .env
# 编辑 .env 文件，填入必要的配置
```

4. **安装依赖**

```bash
pip install -r requirements.txt
```

5. **运行后端服务**

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

6. **启动前端开发服务器**

```bash
cd frontend
npm install
npm start
```

### Docker 部署

```bash
# 构建并启动所有服务
docker-compose up -d --build

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 自动发布（`dev/master` 双机）

仓库使用 GitHub Actions 双机自动发布，工作流文件：`.github/workflows/deploy-branches.yml`。

触发方式：
- 推送到 `dev` 或 `master` 分支
- 手动触发 `workflow_dispatch`（可选强制模式与目标分支）

分支路由：
- `dev` -> 上海服务器（`HOST_SHANGHAI`）
- `master` -> 香港服务器（`HOST_HK_NEURALNOTE`）

必需 Secrets：
- `HOST_SHANGHAI`
- `HOST_HK_NEURALNOTE`
- `SSH_PRIVATE_KEY`
- `LETSENCRYPT_EMAIL`（可选，用于香港域名证书申请）

Registry 模式相关 Secrets（可选但推荐）：
- `ALIYUN_REGISTRY`
- `ALIYUN_REGISTRY_USER`
- `ALIYUN_REGISTRY_PASSWORD`

`workflow_dispatch` 输入参数：
- `deploy_mode`：`auto | registry | build`（默认 `auto`）
- `force_branch`：`dev | master`（手动部署目标）

部署模式说明：
- `auto`：优先 `registry`，失败自动回退 `build`
- `registry`：强制镜像仓库模式（失败即失败）
- `build`：强制服务器本地构建模式（不依赖 ACR）

发布流程：
1. 按分支选择目标服务器
2. 解析部署模式与目标：生成 `RELEASE_ID`、健康检查 URL 与模式元数据
3. 若目标分支为 `master`，先在香港自动执行 `scripts/setup_hk_edge_proxy.sh`
4. 若允许且可用，尝试 `registry` 构建并推送镜像；失败时在 `auto` 模式自动回退 `build`
5. 打包源码并上传发布包、部署脚本、运行时环境到目标服务器
6. 运行 `scripts/deploy_release.sh` 切换 `/opt/neuralnote/current`，并执行健康检查
7. 强校验远端 `current` 已切换到本次 `RELEASE_ID`
8. 发布失败时输出分阶段诊断，成功/失败均写入 `GITHUB_STEP_SUMMARY`

香港域名网关路由：
- `https://neuralnote.capoo.tech` -> 香港本机容器 `127.0.0.1:18080`（master）
- `https://dev.neuralnote.capoo.tech` -> 上海服务器 `http://47.101.214.41:80`（dev，全站反代）

生产前端端口绑定变量（`docker-compose.prod.yml`）：
- `FRONTEND_BIND_ADDR`（默认 `0.0.0.0`）
- `FRONTEND_BIND_PORT`（默认 `80`）

分支默认绑定：
- `dev`: `0.0.0.0:80`
- `master`: `127.0.0.1:18080`（仅香港 Nginx 可访问）

服务器前置要求：
- 两台机器都需准备 `/opt/neuralnote/shared/backend.env`
- 首次部署执行：`mkdir -p /opt/neuralnote/shared /opt/neuralnote/releases`
- 上海可从现有 release 迁移 `.env`，香港需手动创建独立配置

### 前端 API 基址

前端默认以同源路径访问 API（`/api/...`），不再默认指向 `http://localhost:8000`。  
如需覆盖，可通过环境变量 `VITE_API_BASE_URL` 指定完整地址。

---

## 📚 文档体系

本项目采用三文档体系进行项目管理：

```
NeuralNote-Project/
├── README.md                    # 项目入口说明
├── src/                         # 源代码
│
└── docs/                        # 文档中心
    ├── 01_Product/              # 产品相关
    │    └── NeuralNote_PRD_v1.3.md   # 蓝图
    │
    ├── 02_Tech/                 # 技术相关
    │    └── API_Design.md            # 施工图
    │
    └── 03_Logs/                 # 过程记录
         └── DevLog.md                # 航海日记
```

### 文档说明

| 文档 | 类型 | 作用 | 更新频率 |
|-----|------|------|---------|
| **PRD** | 蓝图 | What & Why。定义产品长什么样、有什么功能、交互流程是什么 | 低 |
| **API_Design** | 施工图 | How。记录具体的实现细节，如数据库结构、API接口、算法逻辑 | 中 |
| **DevLog** | 航海日记 | Process & Thoughts。记录开发过程中的问题、决策、灵感 | 高 |

### 文档阅读指引

1. **新产品成员** → 先读 `README.md` 了解项目全貌，再读 `PRD` 理解产品设计
2. **后端开发** → 重点阅读 `API_Design.md` 中的数据库设计和API接口
3. **前端开发** → 重点阅读 `API_Design.md` 中的交互设计和图谱可视化方案
4. **架构决策** → 阅读 `DevLog.md` 了解关键技术决策的背景和权衡

---

## 🗺️ 开发路线图

### 第一阶段：MVP（当前阶段）

**目标**：验证产品核心价值

**后端开发**（✅ 基本完成）
- [x] 用户系统（注册、登录、JWT认证）✅
- [x] 题目管理（上传、OCR识别、存储）✅
- [x] AI解答功能（DeepSeek + GPT-4）✅
- [x] 知识图谱 CRUD 接口 ✅
- [x] 复习系统（SM-2 算法）✅
- [x] 向量相似度搜索 ✅

**前端开发**（✅ 已完成）
- [x] 用户界面（登录、注册页面）✅
- [x] 知识图谱列表和详情页面 ✅
- [x] 文件上传和 OCR 识别界面 ✅
- [x] AI 分析结果展示 ✅
- [x] 2D 知识图谱可视化（Cytoscape.js）✅
- [x] 3D 知识图谱可视化（Three.js）✅
- [x] 复习界面（4种复习模式）✅
- [x] 统计图表展示 ✅
- [x] 学习成就系统 ✅
- [x] 性能优化（代码分割、懒加载、缓存）✅
- [x] 移动端适配（响应式布局、抽屉菜单）✅
- [x] 主题切换（暗黑模式）✅

**预计时间**：3个月（✅ 已完成 100%）

### 第二阶段：测试与部署（当前阶段）

**目标**：完善测试体系，准备生产部署

- [ ] 端到端测试（E2E）
- [ ] Docker 镜像构建（前端 + 后端）
- [ ] 生产环境配置
- [ ] 部署文档编写
- [ ] 性能测试和优化
- [ ] 安全审计和加固

**预计时间**：2-3周

### 第三阶段：功能完善

**目标**：丰富产品功能，提升用户体验

- [ ] 智能归类系统（AI 预测 + 用户确认）
- [ ] 多视图功能（力导向、树形、环形布局）
- [ ] OCR 结果手动校正
- [ ] 跨学科识别功能
- [ ] 批量操作功能

**预计时间**：2-3个月

### 第四阶段：高级功能

**目标**：打造差异化优势

- [ ] 高级复习模式（游戏化、闪念卡片）
- [ ] 多设备同步（云端存储）
- [ ] 社区功能（公有云图谱、知识分享）
- [ ] 移动端 App（React Native）
- [ ] AI 提示词优化

**预计时间**：3-4个月

---

## 📂 项目结构

```
NeuralNote-Project/
├── README.md                    # 项目入口文档
├── .gitignore                   # Git忽略规则
├── requirements.txt             # Python依赖清单
├── TODO.md                      # 开发任务清单
├── docs/                        # 文档目录
│   ├── 01_Product/              # 产品文档（PRD）
│   ├── 02_Tech/                 # 技术文档（API Design、Git Workflow）
│   └── 03_Logs/                 # 开发日志（DevLog）
├── src/                         # 源代码目录
│   ├── backend/                 # 后端代码
│   │   ├── main.py              # FastAPI入口
│   │   ├── app/                 # 应用代码
│   │   │   ├── api/             # API路由
│   │   │   ├── models/          # 数据模型
│   │   │   ├── schemas/         # Pydantic模式
│   │   │   └── services/        # 业务逻辑
│   │   └── tests/               # ⚠️ 测试文件（必须放这里！）
│   │       ├── test_auth.py
│   │       ├── test_api.py
│   │       └── test_*.py
│   └── frontend/                # 前端代码
│       ├── public/
│       └── src/
│           ├── components/      # React组件
│           ├── pages/           # 页面
│           ├── store/           # Redux store
│           └── services/        # API服务
├── docker/                      # Docker配置
└── scripts/                     # 辅助脚本
```

**⚠️ 重要规范**：
- 所有测试文件必须放在 `src/backend/tests/` 目录
- 不要在 `src/backend/` 根目录放置测试文件
- 测试文件命名：`test_*.py`

---

## 🤝 贡献指南

### 贡献流程

1. **Fork** 本项目
2. 创建特性分支：`git checkout -b feature/xxx`
3. 提交更改：`git commit -m 'Add xxx'`
4. 推送分支：`git push origin feature/xxx`
5. 提交 **Pull Request**

### 代码规范

- **Python**：遵循 PEP 8，使用 Black 格式化
- **JavaScript/TypeScript**：遵循 ESLint 配置
- **提交信息**：使用 Conventional Commits 格式
- **测试**：新增功能需包含单元测试
- **测试文件位置**：所有测试文件必须放在 `src/backend/tests/` 目录

### Git 工作流规范

- **分支策略**：
  - `master`：稳定版本分支，推送后自动部署到香港服务器
  - `dev`：日常开发分支，推送后自动部署到上海服务器
- **合并规则**：使用 `git merge dev --no-ff` 保留合并历史
- **推送规则**：`dev` 与 `master` 都触发 CI/CD，部署目标由分支路由决定

详细规范请查看：[Git 工作流程文档](docs/02_Tech/Git_Workflow.md)

### 文档更新

- **PRD 变更**：提交 PR 后由产品负责人审核
- **技术设计变更**：需要技术负责人评审
- **DevLog**：可随时更新，记录开发过程中的发现

---

## 📄 许可证

本项目采用 MIT 许可证开源。

---

## 📞 联系方式

- **项目负责人**：[你的名字]
- **邮箱**：contact@neuralnote.com
- **GitHub**：https://github.com/neuralnote

---

## 🙏 致谢

- 感谢 [Anki](https://apps.ankiweb.net/) 提供的间隔复习算法灵感
- 感谢 [Notion](https://www.notion.so/) 提供的知识管理设计参考
- 感谢 [Roam Research](https://roamresearch.com/) 提供的双向链接理念

---

<p align="center">
  <sub>Built with ❤️ by NeuralNote Team</sub>
</p>

*最后更新：2026年2月2日*
