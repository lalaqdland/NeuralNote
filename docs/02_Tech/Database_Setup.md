# NeuralNote 开发环境配置说明

## 数据库服务信息

### PostgreSQL 数据库
- **地址**: localhost:15432（注意：由于Windows端口限制，使用15432而非5432）
- **数据库名**: neuralnote_dev
- **用户名**: neuralnote
- **密码**: neuralnote_dev_password

### Redis 缓存
- **地址**: localhost:6379
- **密码**: 无

### pgAdmin 数据库管理工具
- **访问地址**: http://localhost:15050（注意：由于Windows端口限制，使用15050而非5050）
- **登录邮箱**: admin@neuralnote.com
- **登录密码**: admin

#### pgAdmin 连接数据库配置
在 pgAdmin 中添加服务器时使用以下配置：
- **Host**: postgres（Docker 内部网络）或 localhost（从宿主机连接）
- **Port**: 5432（Docker内部）或 15432（从宿主机连接）
- **Database**: neuralnote_dev
- **Username**: neuralnote
- **Password**: neuralnote_dev_password

---

## 测试账号信息

### 测试用户账号
- **邮箱**: test@neuralnote.com
- **密码**: test123456
- **用户名**: testuser
- **订阅计划**: free（免费版）
- **状态**: 已激活、已验证

### 测试知识图谱
- **名称**: 考研数学知识图谱
- **描述**: 2026考研数学复习知识图谱
- **学科**: math（数学）
- **所有者**: test@neuralnote.com

---

## Docker 服务管理

### 启动所有服务
```bash
docker-compose up -d
```

### 查看服务状态
```bash
docker-compose ps
```

### 查看服务日志
```bash
# 查看所有服务日志
docker-compose logs

# 查看特定服务日志
docker-compose logs postgres
docker-compose logs redis
docker-compose logs pgadmin
```

### 停止所有服务
```bash
docker-compose down
```

### 停止并删除数据卷（⚠️ 会删除所有数据）
```bash
docker-compose down -v
```

### 重启服务
```bash
docker-compose restart
```

---

## 数据库验证

### 方法1：使用 Docker 命令行
```bash
# 进入 PostgreSQL 容器
docker exec -it neuralnote-db psql -U neuralnote -d neuralnote_dev

# 查看所有表
\dt

# 查看用户表
SELECT * FROM users;

# 查看知识图谱表
SELECT * FROM knowledge_graphs;

# 退出
\q
```

### 方法2：使用 pgAdmin
1. 打开浏览器访问 http://localhost:5050
2. 使用上面的账号登录
3. 添加服务器连接（使用上面的配置）
4. 浏览数据库表和数据

---

## 常见问题

### 问题1：端口被占用（Windows系统）
Windows系统保留了某些端口范围，可能导致5432、5050等端口无法使用。

**解决方案**：
- 本项目已将端口修改为：
  - PostgreSQL: 15432（而非5432）
  - pgAdmin: 15050（而非5050）
  - Redis: 6379（正常）

### 问题2：容器启动失败
```bash
# 查看详细日志
docker-compose logs postgres

# 重新构建并启动
docker-compose up -d --force-recreate
```

### 问题3：数据库连接失败
- 确认容器正在运行：`docker-compose ps`
- 检查容器健康状态：`docker ps`
- 查看容器日志：`docker-compose logs postgres`

---

## 数据库表结构

已自动创建以下表：

| 表名 | 说明 |
|-----|------|
| users | 用户表 |
| knowledge_graphs | 知识图谱表 |
| memory_nodes | 记忆节点表（核心） |
| knowledge_tags | 知识点标签表 |
| node_tags | 节点-标签关联表 |
| node_relations | 节点关联表 |
| view_configs | 视图配置表 |
| review_logs | 复习记录表 |
| file_uploads | 文件上传记录表 |

---

## 安全提示

⚠️ **重要**：
- 这些是开发环境的测试账号和密码
- **生产环境必须修改所有密码**
- `.env` 文件已被 `.gitignore` 排除，不会提交到 Git
- 不要将真实的 API Key 提交到代码仓库

---

*最后更新：2026-01-30*

