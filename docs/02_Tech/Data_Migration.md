# 数据迁移指南

本文档说明如何将开发环境的数据迁移到生产环境（云服务器）。

## 📊 数据类型说明

### 1. 数据库数据（用户、节点、图谱等）

**存储位置**：PostgreSQL Docker Volume
- 开发环境：`postgres_data/`
- 不会上传到 GitHub ❌
- 需要手动迁移 ✅

### 2. 用户上传文件（图片、文档等）

**存储位置**：`src/backend/uploads/`
- 不会上传到 GitHub ❌
- 需要手动迁移 ✅

### 3. 源代码和配置

**存储位置**：整个项目目录
- 会上传到 GitHub ✅
- 自动同步 ✅

---

## 🚀 迁移方案

### 方案1：数据库导出/导入（推荐）

#### 步骤1：导出开发环境数据

```bash
# 导出整个数据库
docker exec neuralnote-db pg_dump -U neuralnote -d neuralnote_dev > backup.sql

# 或者只导出特定表
docker exec neuralnote-db pg_dump -U neuralnote -d neuralnote_dev -t users -t knowledge_graphs -t memory_nodes > backup.sql
```

#### 步骤2：上传到云服务器

```bash
# 使用 scp 上传
scp backup.sql user@your-server:/path/to/backup/

# 或使用 rsync
rsync -avz backup.sql user@your-server:/path/to/backup/
```

#### 步骤3：在云服务器导入

```bash
# 在云服务器上执行
docker exec neuralnote-db psql -U neuralnote -d neuralnote_dev < backup.sql
```

### 方案2：Docker Volume 迁移

#### 步骤1：打包 Volume 数据

```bash
# 停止容器
docker-compose down

# 打包数据
docker run --rm -v neuralnote-project_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_data.tar.gz -C /data .
```

#### 步骤2：上传到云服务器

```bash
scp postgres_data.tar.gz user@your-server:/path/to/backup/
```

#### 步骤3：在云服务器恢复

```bash
# 创建 Volume
docker volume create neuralnote-project_postgres_data

# 解压数据
docker run --rm -v neuralnote-project_postgres_data:/data -v $(pwd):/backup alpine tar xzf /backup/postgres_data.tar.gz -C /data

# 启动服务
docker-compose up -d
```

### 方案3：使用云数据库（生产环境推荐）

不使用 Docker 数据库，直接使用云服务商的数据库服务：

- **阿里云 RDS**
- **腾讯云 CDB**
- **AWS RDS**

**优势**：
- ✅ 自动备份
- ✅ 高可用
- ✅ 易于扩展
- ✅ 专业运维

**配置方法**：
修改 `.env` 文件：
```env
POSTGRES_HOST=your-rds-host.com
POSTGRES_PORT=5432
POSTGRES_DB=neuralnote_prod
POSTGRES_USER=neuralnote
POSTGRES_PASSWORD=your-secure-password
```

---

## 📁 用户上传文件迁移

### 方案1：直接复制（小规模）

```bash
# 打包上传文件
tar czf uploads.tar.gz src/backend/uploads/

# 上传到服务器
scp uploads.tar.gz user@your-server:/path/to/project/

# 在服务器解压
tar xzf uploads.tar.gz
```

### 方案2：使用对象存储（推荐）

将文件存储到云端对象存储服务：

- **阿里云 OSS**
- **腾讯云 COS**
- **AWS S3**

**优势**：
- ✅ 无需迁移
- ✅ CDN 加速
- ✅ 无限容量
- ✅ 按需付费

**已实现**：项目已支持阿里云 OSS，只需配置：

```env
# .env 文件
STORAGE_TYPE=oss  # 或 local

# 阿里云 OSS 配置
ALIYUN_OSS_ACCESS_KEY_ID=your_access_key
ALIYUN_OSS_ACCESS_KEY_SECRET=your_secret_key
ALIYUN_OSS_BUCKET=your_bucket_name
ALIYUN_OSS_ENDPOINT=oss-cn-hangzhou.aliyuncs.com
```

---

## 🔄 完整迁移流程

### 开发环境 → 生产环境

#### 1. 准备阶段

```bash
# 1. 导出数据库
docker exec neuralnote-db pg_dump -U neuralnote -d neuralnote_dev > backup_$(date +%Y%m%d).sql

# 2. 打包上传文件（如果使用本地存储）
tar czf uploads_$(date +%Y%m%d).tar.gz src/backend/uploads/

# 3. 推送代码到 GitHub
git push origin master
```

#### 2. 云服务器部署

```bash
# 1. 克隆代码
git clone https://github.com/your-org/NeuralNote.git
cd NeuralNote

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env，填入生产环境配置

# 3. 启动服务
docker-compose up -d

# 4. 导入数据库
scp backup_20260201.sql user@server:/tmp/
docker exec neuralnote-db psql -U neuralnote -d neuralnote_dev < /tmp/backup_20260201.sql

# 5. 恢复上传文件（如果使用本地存储）
scp uploads_20260201.tar.gz user@server:/path/to/project/
tar xzf uploads_20260201.tar.gz
```

#### 3. 验证

```bash
# 检查服务状态
docker-compose ps

# 检查数据库
docker exec neuralnote-db psql -U neuralnote -d neuralnote_dev -c "SELECT COUNT(*) FROM users;"

# 测试 API
curl http://your-server:8000/health
```

---

## 🔒 安全注意事项

### 1. 敏感信息保护

❌ **绝对不要上传到 GitHub**：
- `.env` 文件（包含密钥）
- 数据库备份文件
- 用户上传的文件
- `postgres_data/` 目录

✅ **已在 .gitignore 中配置**：
```
.env
postgres_data/
redis_data/
src/backend/uploads/
*.sql
*.tar.gz
```

### 2. 生产环境配置

修改生产环境的 `.env`：

```env
# 修改为强密码
POSTGRES_PASSWORD=your_very_strong_password_here
SECRET_KEY=your_very_long_random_secret_key_here

# 关闭调试模式
DEBUG=False

# 配置生产域名
CORS_ORIGINS=["https://your-domain.com"]
```

### 3. 数据库备份策略

**自动备份脚本**（建议每天执行）：

```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/path/to/backups"

# 创建备份
docker exec neuralnote-db pg_dump -U neuralnote -d neuralnote_dev > $BACKUP_DIR/backup_$DATE.sql

# 压缩
gzip $BACKUP_DIR/backup_$DATE.sql

# 删除 7 天前的备份
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete

echo "Backup completed: backup_$DATE.sql.gz"
```

**设置定时任务**：
```bash
# 编辑 crontab
crontab -e

# 每天凌晨 2 点执行备份
0 2 * * * /path/to/backup.sh
```

---

## 📝 迁移检查清单

### 迁移前

- [ ] 导出数据库备份
- [ ] 打包用户上传文件
- [ ] 推送最新代码到 GitHub
- [ ] 记录当前数据量（用户数、节点数等）
- [ ] 测试备份文件完整性

### 迁移中

- [ ] 在云服务器部署 Docker 环境
- [ ] 配置生产环境变量
- [ ] 启动服务容器
- [ ] 导入数据库
- [ ] 恢复上传文件
- [ ] 配置域名和 SSL

### 迁移后

- [ ] 验证服务可访问
- [ ] 验证数据完整性
- [ ] 测试登录功能
- [ ] 测试文件上传
- [ ] 配置监控和告警
- [ ] 设置自动备份

---

## 🆘 常见问题

### Q1: 数据库导入失败？

**可能原因**：
- PostgreSQL 版本不一致
- 数据库已存在数据

**解决方案**：
```bash
# 清空数据库后重新导入
docker exec neuralnote-db psql -U neuralnote -d neuralnote_dev -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
docker exec neuralnote-db psql -U neuralnote -d neuralnote_dev < backup.sql
```

### Q2: 上传文件路径不对？

**解决方案**：
确保 `uploads/` 目录权限正确：
```bash
chmod -R 755 src/backend/uploads/
chown -R www-data:www-data src/backend/uploads/
```

### Q3: 如何只迁移部分数据？

**解决方案**：
```bash
# 只导出特定用户的数据
docker exec neuralnote-db pg_dump -U neuralnote -d neuralnote_dev -t users --data-only --column-inserts -c "WHERE email='user@example.com'" > user_backup.sql
```

---

## 📚 相关文档

- [Docker 部署文档](./Docker_Deployment.md)
- [数据库设计文档](../02_Tech/Database_Setup.md)
- [环境配置说明](./.env.example)

---

*最后更新：2026-02-01*






