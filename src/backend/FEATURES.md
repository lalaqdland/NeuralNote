# 文件上传、OCR 和 AI 分析功能使用指南

本文档介绍 NeuralNote 新增的文件上传、OCR 识别和 AI 分析功能。

## 功能概述

### 1. 文件上传
- 支持上传图片文件（JPEG, PNG）
- 文件大小限制：10MB
- 支持本地存储和阿里云 OSS
- 自动生成唯一文件名

### 2. OCR 识别
- 集成百度 OCR API
- 支持通用文字识别
- 支持数学公式识别
- 返回识别文本和置信度

### 3. AI 分析
- 集成 DeepSeek 和 OpenAI GPT-4
- 自动分析题目内容
- 提取知识点
- 生成向量嵌入
- 自动创建记忆节点

## 快速开始

### 1. 配置环境变量

**配置状态**：

- ✅ **百度 OCR**：已配置，可以直接使用 OCR 识别功能
- ⚠️ **AI 服务**：需要配置（DeepSeek 或 OpenAI）才能使用 AI 分析功能
- ⚠️ **阿里云 OSS**：可选，生产环境推荐配置

**需要配置的服务**：

编辑 `src/backend/.env` 文件，添加以下配置：

```env
# ==================== AI 服务配置（⚠️ 需要配置）====================

# DeepSeek API（推荐，成本低）
# 获取方式：https://platform.deepseek.com/
DEEPSEEK_API_KEY=your_deepseek_api_key

# 或 OpenAI API
# 获取方式：https://platform.openai.com/
OPENAI_API_KEY=your_openai_api_key

# ==================== 阿里云 OSS（可选）====================
# 生产环境推荐使用 OSS 存储文件
# OSS_ACCESS_KEY_ID=your_key_id
# OSS_ACCESS_KEY_SECRET=your_key_secret
# OSS_BUCKET_NAME=your_bucket
# OSS_ENDPOINT=oss-cn-hangzhou.aliyuncs.com
```

**注意**：
- 百度 OCR 已配置完成，无需额外配置
- AI 服务至少需要配置一个（DeepSeek 或 OpenAI）
- 向量嵌入功能需要 OpenAI API Key

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 启动服务

```bash
cd src/backend
uvicorn main:app --reload
```

## API 使用示例

### 1. 文件上传

```python
import httpx

async def upload_file():
    # 登录获取 Token
    async with httpx.AsyncClient() as client:
        # 登录
        login_response = await client.post(
            "http://localhost:8000/api/v1/auth/login",
            json={"email": "test@example.com", "password": "password123"}
        )
        token = login_response.json()["access_token"]
        
        # 上传文件
        headers = {"Authorization": f"Bearer {token}"}
        with open("test_image.jpg", "rb") as f:
            files = {"file": ("test_image.jpg", f, "image/jpeg")}
            response = await client.post(
                "http://localhost:8000/api/v1/files/upload",
                headers=headers,
                files=files
            )
        
        print(response.json())
        # 返回：
        # {
        #     "file_id": "uuid",
        #     "file_url": "/uploads/images/20260130_abc123.jpg",
        #     "original_filename": "test_image.jpg",
        #     "file_size": 123456,
        #     "mime_type": "image/jpeg",
        #     "message": "文件上传成功"
        # }
```

### 2. OCR 识别

```python
async def ocr_recognize(file_id: str, token: str):
    async with httpx.AsyncClient(timeout=60.0) as client:
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.post(
            "http://localhost:8000/api/v1/ocr/ocr",
            headers=headers,
            json={
                "file_id": file_id,
                "ocr_engine": "baidu"
            }
        )
        
        print(response.json())
        # 返回：
        # {
        #     "file_id": "uuid",
        #     "text": "识别的文本内容",
        #     "confidence": 0.95,
        #     "engine": "baidu",
        #     "raw_result": {...},
        #     "processing_time": 1.23
        # }
```

### 3. AI 分析

```python
async def ai_analyze(text: str, token: str):
    async with httpx.AsyncClient(timeout=60.0) as client:
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.post(
            "http://localhost:8000/api/v1/ai/analyze",
            headers=headers,
            json={
                "text": text,
                "engine": "auto",
                "include_embedding": False
            }
        )
        
        print(response.json())
        # 返回：
        # {
        #     "subject": "数学",
        #     "difficulty": "中等",
        #     "question_type": "解答题",
        #     "answer": "详细解答过程...",
        #     "key_points": ["导数", "求导法则"],
        #     "summary": "求函数的导数",
        #     "tags": ["微积分", "导数"],
        #     "engine": "deepseek"
        # }
```

### 4. 完整流程（上传 → OCR → AI → 创建节点）

```python
async def complete_workflow(file_id: str, graph_id: str, token: str):
    async with httpx.AsyncClient(timeout=60.0) as client:
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.post(
            "http://localhost:8000/api/v1/ai/analyze-question",
            headers=headers,
            json={
                "file_id": file_id,
                "engine": "auto",
                "create_node": True,
                "graph_id": graph_id
            }
        )
        
        print(response.json())
        # 返回：
        # {
        #     "file_id": "uuid",
        #     "analysis": {
        #         "subject": "数学",
        #         "difficulty": "中等",
        #         ...
        #     },
        #     "node_id": "uuid"  # 创建的记忆节点ID
        # }
```

## API 端点列表

### 文件上传 (`/api/v1/files`)

| 方法 | 端点 | 描述 |
|------|------|------|
| POST | `/upload` | 上传文件 |
| GET | `/` | 获取文件列表（分页） |
| GET | `/{file_id}` | 获取文件详情 |
| PATCH | `/{file_id}` | 更新文件记录 |
| DELETE | `/{file_id}` | 删除文件 |

### OCR 识别 (`/api/v1/ocr`)

| 方法 | 端点 | 描述 |
|------|------|------|
| POST | `/ocr` | 识别图片文字 |
| POST | `/ocr/math` | 识别数学公式 |

### AI 分析 (`/api/v1/ai`)

| 方法 | 端点 | 描述 |
|------|------|------|
| POST | `/analyze` | 分析文本内容 |
| POST | `/extract-knowledge` | 提取知识点 |
| POST | `/embedding` | 生成向量嵌入 |
| POST | `/analyze-question` | 完整题目分析 |

## 测试

### 运行测试脚本

```bash
cd src/backend
python test_new_features.py
```

### 使用 Swagger UI

访问 http://localhost:8000/docs 查看和测试所有 API 端点。

## 注意事项

### 1. API 密钥配置

- **百度 OCR**：需要在百度智能云注册并创建应用
- **DeepSeek**：访问 https://platform.deepseek.com/ 获取 API Key
- **OpenAI**：访问 https://platform.openai.com/ 获取 API Key

### 2. 文件存储

- **开发环境**：默认使用本地存储（`uploads/` 目录）
- **生产环境**：建议配置阿里云 OSS

### 3. 成本控制

- **OCR**：百度 OCR 有免费额度，超出后按次计费
- **AI**：DeepSeek 成本约为 GPT-4 的 1/10，建议优先使用

### 4. 性能优化

- **OCR Token 缓存**：Access Token 有效期 30 天，自动缓存
- **AI 结果缓存**：TODO - 相同题目复用分析结果
- **向量搜索**：TODO - 使用 PgVector 进行相似题目推荐

## 常见问题

### Q1: 文件上传失败

**A**: 检查：
1. 文件类型是否支持（JPEG, PNG）
2. 文件大小是否超过 10MB
3. 是否提供了有效的 Token

### Q2: OCR 识别失败

**A**: 检查：
1. 是否配置了百度 OCR API Key
2. 文件是否已成功上传
3. 图片是否清晰可读

### Q3: AI 分析失败

**A**: 检查：
1. 是否配置了 AI API Key（DeepSeek 或 OpenAI）
2. API Key 是否有效
3. 是否有足够的 API 额度

### Q4: 如何切换 AI 引擎？

**A**: 在请求中设置 `engine` 参数：
- `"auto"`: 自动选择（优先 DeepSeek）
- `"deepseek"`: 使用 DeepSeek
- `"openai"`: 使用 OpenAI GPT-4

## 下一步计划

- [ ] 添加单元测试
- [ ] 实现 AI 结果缓存
- [ ] 实现向量相似度搜索
- [ ] 优化 AI 提示词
- [ ] 实现 OCR 结果手动校正
- [ ] 支持更多 OCR 引擎（腾讯 OCR）
- [ ] 支持更多文件格式（PDF）

## 相关文档

- [API 设计文档](../../docs/02_Tech/API_Design.md)
- [开发日志](../../docs/03_Logs/DevLog.md)
- [下次开发提示词](../../docs/03_Logs/NextDevPrompt.md)

---

*最后更新：2026-01-30*

