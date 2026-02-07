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
**最后更新**：2026-02-02  
**版本**：v1.0.0





