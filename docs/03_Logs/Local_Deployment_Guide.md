# NeuralNote 本地部署指南

> 本文档介绍如何在本地环境使用 Docker 部署完整的 NeuralNote 应用

---

## 📋 目录

- [环境要求](#环境要求)
- [快速开始](#快速开始)
- [详细步骤](#详细步骤)
- [配置说明](#配置说明)
- [常见问题](#常见问题)
- [服务管理](#服务管理)
- [自动发布（dev/master 双机）](#自动发布devmaster-双机)
- [回滚与故障排查（生产）](#回滚与故障排查生产)

---

## 🔧 环境要求

### 必需软件

- **Docker Desktop** 24.x+
  - Windows: [下载地址](https://www.docker.com/products/docker-desktop/)
  - macOS: [下载地址](https://www.docker.com/products/docker-desktop/)
  - Linux: 安装 Docker Engine + Docker Compose

- **Git** 2.x+

### 系统要求

- **内存**: 至少 4GB RAM（推荐 8GB+）
- **磁盘**: 至少 10GB 可用空间
- **CPU**: 2核心+（推荐 4核心+）

---

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/your-org/NeuralNote.git
cd NeuralNote
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入必要的 API 密钥
# 至少需要配置：
# - SECRET_KEY（JWT 密钥）
# - BAIDU_OCR_API_KEY 和 BAIDU_OCR_SECRET_KEY（OCR 服务）
# - DEEPSEEK_API_KEY 或 OPENAI_API_KEY（AI 服务）
```

### 3. 启动所有服务

```bash
# 构建并启动所有服务
docker-compose up -d --build

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 4. 访问应用

- **前端应用**: http://localhost:3000
- **后端 API**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs
- **pgAdmin**: http://localhost:15050 (可选，需要启动 dev profile)

### 5. 初始化数据库

```bash
# 进入后端容器
docker-compose exec backend bash

# 运行数据库迁移（如果有）
# alembic upgrade head

# 创建测试用户（可选）
# python scripts/create_test_user.py
```

---

## 📖 详细步骤

### 步骤 1：准备环境变量

编辑 `.env` 文件，配置以下关键参数：

```bash
# ==================== JWT 配置 ====================
# 生成强密钥：openssl rand -hex 32
SECRET_KEY=your-secret-key-please-change-in-production

# ==================== 百度 OCR 配置 ====================
BAIDU_OCR_API_KEY=your_baidu_ocr_api_key
BAIDU_OCR_SECRET_KEY=your_baidu_ocr_secret_key

# ==================== AI 服务配置 ====================
# 至少配置一个
DEEPSEEK_API_KEY=your_deepseek_api_key
OPENAI_API_KEY=your_openai_api_key

# ==================== 可选配置 ====================
# 阿里云 OSS（如果使用云存储）
ALIYUN_OSS_ACCESS_KEY_ID=your_access_key
ALIYUN_OSS_ACCESS_KEY_SECRET=your_secret_key
ALIYUN_OSS_BUCKET=your_bucket_name
```

### 步骤 2：构建 Docker 镜像

```bash
# 构建所有服务
docker-compose build

# 或者单独构建某个服务
docker-compose build backend
docker-compose build frontend
```

### 步骤 3：启动服务

```bash
# 启动所有服务（后台运行）
docker-compose up -d

# 启动所有服务（前台运行，查看日志）
docker-compose up

# 启动特定服务
docker-compose up -d postgres redis backend

# 启动开发工具（包括 pgAdmin）
docker-compose --profile dev up -d
```

### 步骤 4：验证服务

```bash
# 检查所有容器状态
docker-compose ps

# 应该看到以下服务都是 healthy 状态：
# - neuralnote-db (postgres)
# - neuralnote-redis (redis)
# - neuralnote-backend (backend)
# - neuralnote-frontend (frontend)

# 检查后端健康状态
curl http://localhost:8000/health

# 检查前端
curl http://localhost:3000
```

### 步骤 5：查看日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend

# 查看最近 100 行日志
docker-compose logs --tail=100 backend
```

---

## ⚙️ 配置说明

### Docker Compose 服务说明

| 服务 | 容器名 | 端口 | 说明 |
|-----|--------|------|------|
| postgres | neuralnote-db | 15432:5432 | PostgreSQL 15 + PgVector |
| redis | neuralnote-redis | 6379:6379 | Redis 7 缓存 |
| backend | neuralnote-backend | 8000:8000 | FastAPI 后端服务 |
| frontend | neuralnote-frontend | 3000:80 | React 前端应用 |
| pgadmin | neuralnote-pgadmin | 15050:80 | 数据库管理工具（可选）|

### 环境变量说明

#### 数据库配置

```bash
# 开发环境（本地访问）
DATABASE_URL=postgresql+asyncpg://neuralnote:neuralnote_dev_password@localhost:15432/neuralnote_dev

# Docker 环境（容器间访问）
DATABASE_URL=postgresql+asyncpg://neuralnote:neuralnote_dev_password@postgres:5432/neuralnote_dev
```

#### Redis 配置

```bash
# 开发环境
REDIS_URL=redis://localhost:6379/0

# Docker 环境
REDIS_URL=redis://redis:6379/0
```

#### 文件上传配置

```bash
# 最大上传大小（字节）
MAX_UPLOAD_SIZE=10485760  # 10MB

# 上传目录
UPLOAD_DIR=./uploads  # 本地开发
UPLOAD_DIR=/app/uploads  # Docker 环境
```

---

## 🔍 常见问题

### 1. 端口冲突

**问题**：启动时提示端口已被占用

**解决方案**：

```bash
# 方案 1：修改 docker-compose.yml 中的端口映射
# 例如：将 "3000:80" 改为 "3001:80"

# 方案 2：停止占用端口的服务
# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Linux/macOS
lsof -i :3000
kill -9 <PID>
```

### 2. 数据库连接失败

**问题**：后端无法连接数据库

**解决方案**：

```bash
# 1. 检查数据库容器状态
docker-compose ps postgres

# 2. 检查数据库日志
docker-compose logs postgres

# 3. 手动测试连接
docker-compose exec postgres psql -U neuralnote -d neuralnote_dev

# 4. 重启数据库服务
docker-compose restart postgres
```

### 3. 前端无法访问后端 API

**问题**：前端请求后端 API 失败

**解决方案**：

```bash
# 1. 检查后端服务状态
docker-compose ps backend
docker-compose logs backend

# 2. 检查 Nginx 配置
docker-compose exec frontend cat /etc/nginx/conf.d/default.conf

# 3. 检查网络连接
docker-compose exec frontend ping backend

# 4. 重启前端服务
docker-compose restart frontend
```

### 4. 构建失败

**问题**：Docker 镜像构建失败

**解决方案**：

```bash
# 1. 清理 Docker 缓存
docker-compose down
docker system prune -a

# 2. 重新构建（不使用缓存）
docker-compose build --no-cache

# 3. 检查 Dockerfile 语法
docker-compose config
```

### 5. 容器内存不足

**问题**：容器运行缓慢或崩溃

**解决方案**：

```bash
# 1. 增加 Docker Desktop 内存限制
# Settings -> Resources -> Memory -> 调整到 4GB+

# 2. 限制 Redis 内存使用
# 已在 docker-compose.yml 中配置：--maxmemory 256mb

# 3. 减少后端 worker 数量
# 修改 backend/Dockerfile 中的 --workers 参数
```

### 6. 文件上传失败

**问题**：上传文件时报错

**解决方案**：

```bash
# 1. 检查上传目录权限
docker-compose exec backend ls -la /app/uploads

# 2. 创建上传目录
docker-compose exec backend mkdir -p /app/uploads

# 3. 修改目录权限
docker-compose exec backend chown -R neuralnote:neuralnote /app/uploads

# 4. 检查文件大小限制
# 修改 .env 中的 MAX_UPLOAD_SIZE
```

---

## 🛠️ 服务管理

### 启动服务

```bash
# 启动所有服务
docker-compose up -d

# 启动特定服务
docker-compose up -d backend

# 启动并查看日志
docker-compose up
```

### 停止服务

```bash
# 停止所有服务
docker-compose stop

# 停止特定服务
docker-compose stop backend

# 停止并删除容器
docker-compose down

# 停止并删除容器、网络、卷
docker-compose down -v
```

### 重启服务

```bash
# 重启所有服务
docker-compose restart

# 重启特定服务
docker-compose restart backend
```

### 查看服务状态

```bash
# 查看所有服务状态
docker-compose ps

# 查看服务详细信息
docker-compose ps -a

# 查看服务资源使用
docker stats
```

### 查看日志

```bash
# 查看所有服务日志
docker-compose logs

# 实时查看日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs backend

# 查看最近 N 行日志
docker-compose logs --tail=100 backend
```

### 进入容器

```bash
# 进入后端容器
docker-compose exec backend bash

# 进入数据库容器
docker-compose exec postgres bash

# 以 root 用户进入
docker-compose exec -u root backend bash
```

### 执行命令

```bash
# 在后端容器中执行命令
docker-compose exec backend python --version

# 在数据库容器中执行 SQL
docker-compose exec postgres psql -U neuralnote -d neuralnote_dev -c "SELECT COUNT(*) FROM users;"

# 运行测试
docker-compose exec backend pytest
```

### 更新服务

```bash
# 1. 拉取最新代码
git pull origin main

# 2. 重新构建镜像
docker-compose build

# 3. 重启服务
docker-compose up -d

# 或者一步完成
docker-compose up -d --build
```

### 清理资源

```bash
# 停止并删除所有容器
docker-compose down

# 删除所有容器和卷
docker-compose down -v

# 清理未使用的镜像
docker image prune -a

# 清理所有未使用的资源
docker system prune -a --volumes
```

---

## 🚚 自动发布（dev/master 双机）

### 工作流位置

- `.github/workflows/deploy-branches.yml`

### 触发条件

- `push` 到 `dev` 或 `master` 分支
- 手动触发 `workflow_dispatch`

### 分支路由

- `dev` -> 上海服务器（`HOST_SHANGHAI`，当前为 `47.101.214.41`）
- `master` -> 香港服务器（`HOST_HK_NEURALNOTE`，当前为 `47.242.60.251`）

### 必需 Secrets

- `HOST_SHANGHAI`：上海服务器 IP/域名
- `HOST_HK_NEURALNOTE`：香港服务器 IP/域名
- `SSH_PRIVATE_KEY`：部署私钥（工作流固定使用 `root@host:22`）
- `LETSENCRYPT_EMAIL`（可选）：香港域名证书申请邮箱

### Registry 模式相关 Secrets（可选但推荐）

- `ALIYUN_REGISTRY`：阿里云镜像仓库地址（可带命名空间；若不带默认补 `capoo`）
- `ALIYUN_REGISTRY_USER`：镜像仓库用户名
- `ALIYUN_REGISTRY_PASSWORD`：镜像仓库密码

### workflow_dispatch 输入参数

- `deploy_mode`：`auto | registry | build`（默认 `auto`）
- `force_branch`：`dev | master`（手动部署目标）

### 部署模式说明

- `auto`：优先 `registry`，失败自动回退 `build`
- `registry`：强制镜像仓库模式（失败即失败）
- `build`：强制服务器本地构建模式（不依赖 ACR）

### 香港域名网关路由（固定）

- `https://neuralnote.capoo.tech` -> 香港本机 `http://127.0.0.1:18080`
- `https://dev.neuralnote.capoo.tech` -> 上海公网 `http://47.101.214.41:80`（全站反代）

### 前端端口绑定变量（生产）

- `FRONTEND_BIND_ADDR`：前端容器绑定地址（默认 `0.0.0.0`）
- `FRONTEND_BIND_PORT`：前端容器绑定端口（默认 `80`）
- 分支默认值：
  - `dev`: `0.0.0.0:80`
  - `master`: `127.0.0.1:18080`（仅香港 Nginx 访问）

### 发布流程

1. GitHub Actions 根据分支选择目标服务器
2. 解析部署模式与目标：生成 `RELEASE_ID`、健康检查 URL 与模式元数据
3. 若分支为 `master`，先在香港执行 `scripts/setup_hk_edge_proxy.sh`：
   - 安装 Nginx + Certbot
   - 申请/续签 `neuralnote.capoo.tech` 与 `dev.neuralnote.capoo.tech` 证书
   - 配置双域名反代与自动续期
4. 若允许且可用，尝试 `registry` 构建并推送镜像；失败时在 `auto` 模式自动回退 `build`
5. 打包仓库源码为 `neuralnote_release_<timestamp>.tar.gz`
6. 通过 SCP 上传发布包、`scripts/deploy_release.sh`、`deploy_runtime.env` 到服务器 `/tmp`
7. 执行部署脚本（`DEPLOY_MODE=auto/registry/build`），自动完成：
   - 解压到 `/opt/neuralnote/releases/<timestamp>`
   - 将 `src/backend/.env` 链接到 `/opt/neuralnote/shared/backend.env`
   - `registry` 模式写入 `.deploy-images.env`；`build` 模式不依赖镜像环境文件
   - 切换软链 `/opt/neuralnote/current`
   - `registry`：`pull + up --no-build`
   - `build`：`up -d --build`
   - 健康检查：
     - `dev`：`http://<上海IP>/` 与 `http://<上海IP>/api/v1/health/ping`
     - `master`：`https://neuralnote.capoo.tech/` 与 `https://neuralnote.capoo.tech/api/v1/health/ping`
8. 强校验远端 `/opt/neuralnote/current` 已切换到本次 `RELEASE_ID`
9. 若健康检查失败，自动回滚到上一版本并优先使用上一版 `.deploy-images.env` 重启容器
10. 失败时输出诊断信息（模式决策、远端 current、compose ps），并写入 `GITHUB_STEP_SUMMARY`

### 服务器一次性初始化

```bash
# 两台机器都执行
mkdir -p /opt/neuralnote/shared /opt/neuralnote/releases

# 上海：若已有历史部署，可迁移旧 env
cp /opt/neuralnote/current/src/backend/.env /opt/neuralnote/shared/backend.env

# 香港：首次独立环境，手工创建
vi /opt/neuralnote/shared/backend.env
```

---

## 🔁 回滚与故障排查（生产）

### 手动回滚命令

```bash
# 1) 查看历史版本
ls -la /opt/neuralnote/releases

# 2) 切换 current 到目标版本（替换为实际时间戳）
ln -sfn /opt/neuralnote/releases/<release_id> /opt/neuralnote/current

# 3) 重新拉起服务（镜像模式）
cd /opt/neuralnote/current
docker compose --env-file .deploy-images.env -f docker-compose.prod.yml pull backend frontend
docker compose --env-file .deploy-images.env -f docker-compose.prod.yml up -d --no-build --remove-orphans

# 4) 验证
curl -f http://127.0.0.1/
curl -f http://127.0.0.1/api/v1/health/ping
docker compose --env-file .deploy-images.env -f docker-compose.prod.yml ps
```

香港域名入口验证（master 环境）：

```bash
curl -I https://neuralnote.capoo.tech
curl -fsS https://neuralnote.capoo.tech/api/v1/health/ping
curl -I https://dev.neuralnote.capoo.tech
```

### 常见失败点与处理

1. 依赖安装失败（`npm install` / `npm ci`）
   - 现象：构建阶段报 `npm ERR!` 或 peer dependency 冲突
   - 处理：
     ```bash
     cd src/frontend
     rm -rf node_modules package-lock.json
     npm install
     npm run build
     ```
   - 说明：确保锁文件与 `package.json` 保持一致后再发布

2. 镜像拉取/启动失败（`docker compose ... pull` / `up -d --no-build`）
   - 现象：镜像 tag 不存在、仓库认证失败、网络超时
   - 处理：
     ```bash
     cd /opt/neuralnote/current
     cat .deploy-images.env
     echo "$ALIYUN_REGISTRY_PASSWORD" | docker login <registry-host> -u "$ALIYUN_REGISTRY_USER" --password-stdin
     docker compose --env-file .deploy-images.env -f docker-compose.prod.yml pull backend frontend
     docker compose --env-file .deploy-images.env -f docker-compose.prod.yml up -d --no-build
     docker compose -f docker-compose.prod.yml logs --tail=200 backend
     ```
   - 说明：优先确认镜像 tag、仓库权限、服务器到 ACR 网络连通性

3. 健康检查失败（前端或后端）
   - 现象：脚本等待超时，触发自动回滚
   - 处理：
     ```bash
     cd /opt/neuralnote/current
     docker compose -f docker-compose.prod.yml ps
     docker compose -f docker-compose.prod.yml logs --tail=200 frontend
     docker compose -f docker-compose.prod.yml logs --tail=200 backend
     curl -v http://127.0.0.1/
     curl -v http://127.0.0.1/api/v1/health/ping
     ```
   - 说明：优先确认端口映射、Nginx 反代、后端容器健康状态

---

## 📊 监控和调试

### 健康检查

```bash
# 检查后端健康状态
curl http://localhost:8000/health

# 检查数据库健康状态
curl http://localhost:8000/health/db

# 检查 Redis 健康状态
docker-compose exec redis redis-cli ping
```

### 性能监控

```bash
# 查看容器资源使用
docker stats

# 查看特定容器资源使用
docker stats neuralnote-backend

# 查看容器进程
docker-compose top
```

### 数据库管理

```bash
# 使用 pgAdmin（浏览器访问）
# http://localhost:15050
# 邮箱：admin@neuralnote.com
# 密码：admin

# 使用命令行
docker-compose exec postgres psql -U neuralnote -d neuralnote_dev

# 备份数据库
docker-compose exec postgres pg_dump -U neuralnote neuralnote_dev > backup.sql

# 恢复数据库
docker-compose exec -T postgres psql -U neuralnote neuralnote_dev < backup.sql
```

---

## 🔐 安全建议

### 生产环境部署

1. **修改默认密码**
   ```bash
   # 修改数据库密码
   POSTGRES_PASSWORD=strong_random_password
   
   # 修改 JWT 密钥
   SECRET_KEY=$(openssl rand -hex 32)
   
   # 修改 pgAdmin 密码
   PGADMIN_DEFAULT_PASSWORD=strong_admin_password
   ```

2. **禁用调试模式**
   ```bash
   DEBUG=false
   LOG_LEVEL=warning
   ```

3. **配置 HTTPS**
   - 使用 Let's Encrypt 证书
   - 配置 Nginx SSL

4. **限制端口暴露**
   - 只暴露必要的端口（80, 443）
   - 数据库和 Redis 不对外暴露

5. **配置防火墙**
   - 只允许必要的入站连接
   - 配置 fail2ban 防止暴力破解

---

## 📚 相关文档

- [API 设计文档](../02_Tech/API_Design.md)
- [数据库设计文档](../02_Tech/Database_Setup.md)
- [开发日志](DevLog.md)
- [项目 README](../../README.md)

---

## 🆘 获取帮助

如果遇到问题：

1. 查看本文档的「常见问题」部分
2. 查看服务日志：`docker-compose logs -f`
3. 查看开发日志：`docs/03_Logs/DevLog.md`
4. 提交 Issue：https://github.com/your-org/NeuralNote/issues

---

**创建时间**：2026-02-02  
**最后更新**：2026-02-07  
**版本**：v1.1.0





