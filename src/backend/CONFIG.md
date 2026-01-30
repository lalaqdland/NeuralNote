# 环境变量配置指南

本文档说明 NeuralNote 后端所需的环境变量配置。

## 配置文件

在 `src/backend/` 目录下创建 `.env` 文件，参考以下配置：

## 必需配置

### 1. 数据库配置

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=15432
POSTGRES_USER=neuralnote
POSTGRES_PASSWORD=neuralnote_dev_password
POSTGRES_DB=neuralnote_dev
```

**说明**：
- 如果使用 Docker Compose，默认配置即可
- 端口 15432 是为了避免与系统 PostgreSQL 冲突

### 2. Redis 配置

```env
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
```

### 3. JWT 配置

```env
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

**⚠️ 重要**：生产环境必须修改 `SECRET_KEY` 为强随机密钥！

生成强密钥的方法：
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## 可选配置

### 1. 百度 OCR（用于图片文字识别）

```env
BAIDU_OCR_API_KEY=your_api_key
BAIDU_OCR_SECRET_KEY=your_secret_key
```

**✅ 已配置**：百度 OCR 已配置完成，可以直接使用！

**获取方式**：
1. 访问 https://cloud.baidu.com/product/ocr
2. 注册并创建应用
3. 获取 API Key 和 Secret Key

**免费额度**：
- 通用文字识别：500次/天
- 高精度识别：50次/天

**API 文档**：
- 通用文字识别：https://cloud.baidu.com/doc/OCR/s/Ck3h7y2ia
- 高精度文字识别：https://cloud.baidu.com/doc/OCR/s/Ek3h7xypm

### 2. AI 服务（⚠️ 需要配置至少一个）

#### DeepSeek（推荐）

```env
DEEPSEEK_API_KEY=your_deepseek_api_key
```

**⚠️ 待配置**：请配置 DeepSeek API Key 以使用 AI 分析功能！

**获取方式**：
1. 访问 https://platform.deepseek.com/
2. 注册并创建 API Key
3. 将 API Key 添加到 `.env` 文件中

**优势**：
- 成本低（约 GPT-4 的 1/10）
- 中文理解好
- API 稳定
- **推荐用于题目分析和知识点提取**

#### OpenAI

```env
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4
```

**⚠️ 待配置**：或者配置 OpenAI API Key（可选）

**获取方式**：
1. 访问 https://platform.openai.com/
2. 注册并创建 API Key
3. 将 API Key 添加到 `.env` 文件中

**优势**：
- 质量最高
- 生态完善
- **用于向量嵌入生成（必需）**

**注意**：
- 如果只配置 DeepSeek，向量嵌入功能将不可用
- 建议同时配置 DeepSeek（分析）+ OpenAI（向量嵌入）

### 3. 阿里云 OSS（生产环境推荐）

```env
OSS_ACCESS_KEY_ID=your_access_key_id
OSS_ACCESS_KEY_SECRET=your_access_key_secret
OSS_BUCKET_NAME=your_bucket_name
OSS_ENDPOINT=oss-cn-hangzhou.aliyuncs.com
```

**获取方式**：
1. 访问 https://www.aliyun.com/product/oss
2. 创建 Bucket
3. 获取 Access Key

**说明**：
- 开发环境可使用本地存储
- 生产环境推荐使用 OSS（CDN 加速、高可用）

## 其他配置

### CORS 配置

```env
BACKEND_CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### 文件上传配置

```env
MAX_UPLOAD_SIZE=10485760  # 10MB
```

### 分页配置

```env
DEFAULT_PAGE_SIZE=20
MAX_PAGE_SIZE=100
```

## 完整配置示例

```env
# 应用配置
APP_NAME=NeuralNote
APP_VERSION=0.1.0
DEBUG=True

# 数据库配置
POSTGRES_HOST=localhost
POSTGRES_PORT=15432
POSTGRES_USER=neuralnote
POSTGRES_PASSWORD=neuralnote_dev_password
POSTGRES_DB=neuralnote_dev

# Redis 配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# JWT 配置
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS 配置
BACKEND_CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# 百度 OCR（可选）
BAIDU_OCR_API_KEY=your_api_key
BAIDU_OCR_SECRET_KEY=your_secret_key

# DeepSeek（可选）
DEEPSEEK_API_KEY=your_api_key

# OpenAI（可选）
OPENAI_API_KEY=your_api_key

# 阿里云 OSS（可选）
OSS_ACCESS_KEY_ID=your_key_id
OSS_ACCESS_KEY_SECRET=your_key_secret
OSS_BUCKET_NAME=your_bucket
OSS_ENDPOINT=oss-cn-hangzhou.aliyuncs.com
```

## 快速开始

### 1. 最小配置（仅基础功能）

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=15432
POSTGRES_USER=neuralnote
POSTGRES_PASSWORD=neuralnote_dev_password
POSTGRES_DB=neuralnote_dev

REDIS_HOST=localhost
REDIS_PORT=6379

SECRET_KEY=dev-secret-key-change-in-production
```

### 2. 完整功能配置

在最小配置基础上，添加：

```env
# OCR 功能
BAIDU_OCR_API_KEY=your_api_key
BAIDU_OCR_SECRET_KEY=your_secret_key

# AI 分析功能
DEEPSEEK_API_KEY=your_api_key
```

## 配置验证

启动服务后，访问以下端点检查配置：

- 基础健康检查：http://localhost:8000/health
- 数据库检查：http://localhost:8000/health/db
- API 文档：http://localhost:8000/docs

## 常见问题

### Q1: 数据库连接失败

**A**: 检查：
1. Docker 服务是否运行：`docker-compose ps`
2. 端口是否正确（15432）
3. 密码是否正确

### Q2: OCR 功能不可用

**A**: 检查：
1. 是否配置了 `BAIDU_OCR_API_KEY` 和 `BAIDU_OCR_SECRET_KEY`
2. API Key 是否有效
3. 是否有剩余额度

### Q3: AI 分析功能不可用

**A**: 检查：
1. 是否配置了 `DEEPSEEK_API_KEY` 或 `OPENAI_API_KEY`
2. API Key 是否有效
3. 是否有剩余额度

### Q4: 文件上传后无法访问

**A**: 检查：
1. `uploads/` 目录是否存在
2. 文件权限是否正确
3. 静态文件服务是否正常（访问 http://localhost:8000/uploads/）

## 安全建议

### 开发环境
- 可以使用简单的 SECRET_KEY
- 可以使用默认的数据库密码

### 生产环境
- ⚠️ 必须使用强随机 SECRET_KEY
- ⚠️ 必须修改数据库密码
- ⚠️ 必须配置 HTTPS
- ⚠️ 建议使用环境变量而非 .env 文件
- ⚠️ 建议使用 OSS 而非本地存储

## 相关文档

- [功能使用指南](./FEATURES.md)
- [开发总结](./DEVELOPMENT_SUMMARY.md)
- [后端 README](./README.md)

---

*最后更新：2026-01-30*

