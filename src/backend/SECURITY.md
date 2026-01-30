# 🔒 安全配置说明

## ⚠️ 重要提醒

本项目已正确配置了敏感信息保护机制，请务必遵守以下安全规范。

---

## ✅ 已配置的安全措施

### 1. .gitignore 保护

`.env` 文件已被添加到 `.gitignore`，**不会被 Git 追踪和上传到 GitHub**。

验证方法：
```bash
git status
# .env 文件不应出现在输出中
```

### 2. 敏感信息存储

所有敏感信息（API Key、密码等）都存储在 `.env` 文件中，不会出现在代码中。

---

## 📋 当前配置状态

### ✅ 已配置的服务

| 服务 | 状态 | 说明 |
|------|------|------|
| 数据库 | ✅ 已配置 | PostgreSQL + Redis |
| 百度 OCR | ✅ 已配置 | 可以使用 OCR 识别功能 |
| JWT 密钥 | ✅ 已配置 | 开发环境密钥 |

### ⚠️ 待配置的服务

| 服务 | 状态 | 优先级 | 说明 |
|------|------|--------|------|
| DeepSeek API | ⚠️ 待配置 | 高 | 用于 AI 题目分析（推荐） |
| OpenAI API | ⚠️ 待配置 | 中 | 用于向量嵌入和高质量分析 |
| 阿里云 OSS | ⚠️ 待配置 | 低 | 生产环境推荐 |

---

## 🔑 敏感信息清单

### 已配置的敏感信息

以下信息已存储在 `.env` 文件中，**请勿分享或上传到公开平台**：

1. **百度 OCR**
   - ✅ 已配置到 `.env` 文件
   - 应用名称：纽伦笔记 NeuronNote
   - ⚠️ API Key 和 Secret Key 仅存储在本地 `.env` 文件中

2. **数据库密码**
   - ✅ 已配置到 `.env` 文件
   - ⚠️ 生产环境请使用强密码

3. **JWT 密钥**
   - ✅ 已配置到 `.env` 文件
   - ⚠️ 生产环境必须修改为强随机密钥！

### 待配置的敏感信息

请在 `.env` 文件中添加以下配置（根据需要）：

1. **DeepSeek API Key**（推荐）
   - 获取地址：https://platform.deepseek.com/
   - 用途：AI 题目分析、知识点提取

2. **OpenAI API Key**（可选）
   - 获取地址：https://platform.openai.com/
   - 用途：向量嵌入、高质量分析

3. **阿里云 OSS**（生产环境推荐）
   - 获取地址：https://www.aliyun.com/product/oss
   - 用途：文件存储、CDN 加速

---

## 🚨 安全检查清单

### 开发环境

- [x] `.env` 文件已创建
- [x] `.env` 文件在 `.gitignore` 中
- [x] 百度 OCR API Key 已配置
- [ ] AI 服务 API Key 已配置（待配置）
- [x] 数据库密码已设置

### 生产环境（部署前必查）

- [ ] 修改 JWT Secret Key 为强随机密钥
- [ ] 修改数据库密码
- [ ] 配置 HTTPS
- [ ] 使用环境变量而非 .env 文件
- [ ] 配置阿里云 OSS
- [ ] 启用 API 限流
- [ ] 配置日志监控

---

## 📝 配置 AI 服务的步骤

### 方法 1：配置 DeepSeek（推荐）

1. 访问 https://platform.deepseek.com/
2. 注册账号并登录
3. 创建 API Key
4. 编辑 `.env` 文件，添加：
   ```env
   DEEPSEEK_API_KEY=your_deepseek_api_key
   ```
5. 重启后端服务

### 方法 2：配置 OpenAI

1. 访问 https://platform.openai.com/
2. 注册账号并登录
3. 创建 API Key
4. 编辑 `.env` 文件，添加：
   ```env
   OPENAI_API_KEY=your_openai_api_key
   ```
5. 重启后端服务

### 推荐配置

同时配置 DeepSeek 和 OpenAI：
- DeepSeek：用于题目分析（成本低）
- OpenAI：用于向量嵌入（必需）

---

## 🔍 验证配置

### 1. 检查 .env 文件

```bash
cd src/backend
cat .env  # Linux/Mac
type .env  # Windows
```

### 2. 检查 Git 状态

```bash
git status
# 确认 .env 文件不在列表中
```

### 3. 测试 OCR 功能

```bash
cd src/backend
python test_new_features.py
```

### 4. 测试 AI 功能

配置 AI API Key 后，取消注释测试脚本中的 AI 测试代码。

---

## ⚠️ 安全注意事项

### 禁止的操作

❌ **禁止**将 `.env` 文件上传到 GitHub  
❌ **禁止**在代码中硬编码 API Key  
❌ **禁止**在公开场合分享 API Key  
❌ **禁止**将 API Key 提交到版本控制  
❌ **禁止**在截图中暴露 API Key  

### 推荐的操作

✅ **推荐**使用 `.env` 文件存储敏感信息  
✅ **推荐**定期更换 API Key  
✅ **推荐**为不同环境使用不同的密钥  
✅ **推荐**启用 API Key 的使用限制  
✅ **推荐**监控 API Key 的使用情况  

---

## 🆘 如果 API Key 泄露

### 立即行动

1. **立即撤销泄露的 API Key**
   - 百度 OCR：登录百度云控制台，删除或重置 API Key
   - DeepSeek：登录 DeepSeek 平台，撤销 API Key
   - OpenAI：登录 OpenAI 平台，撤销 API Key

2. **生成新的 API Key**
   - 在对应平台创建新的 API Key

3. **更新 .env 文件**
   - 将新的 API Key 更新到 `.env` 文件

4. **检查使用记录**
   - 查看 API 调用日志，确认是否有异常使用

5. **通知团队成员**
   - 如果是团队项目，通知所有成员更新配置

---

## 📚 相关文档

- [配置指南](./CONFIG.md) - 详细的配置说明
- [功能使用指南](./FEATURES.md) - 功能使用方法
- [开发总结](./DEVELOPMENT_SUMMARY.md) - 开发记录

---

## 📞 获取帮助

如有配置问题，请查阅：

1. [CONFIG.md](./CONFIG.md) - 配置指南
2. [README.md](./README.md) - 项目说明
3. 百度 OCR 文档：
   - 通用文字识别：https://cloud.baidu.com/doc/OCR/s/Ck3h7y2ia
   - 高精度识别：https://cloud.baidu.com/doc/OCR/s/Ek3h7xypm

---

*最后更新：2026-01-30*  
*配置状态：百度 OCR ✅ | AI 服务 ⚠️ | OSS ⚠️*

