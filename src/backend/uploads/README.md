# 用户上传文件目录

此目录用于存储用户上传的文件（本地存储模式）。

## 目录结构

```
uploads/
├── images/          # 图片文件
├── documents/       # 文档文件（未来）
└── .gitkeep         # 保持目录结构
```

## 注意事项

⚠️ **本目录内容不会提交到 Git**
- 已在 `.gitignore` 中配置
- 仅用于本地开发和测试

⚠️ **生产环境建议**
- 使用阿里云 OSS 或其他对象存储服务
- 配置 `.env` 文件中的 OSS 相关参数

## 配置

### 本地存储（默认）
无需配置，文件自动保存到此目录。

### 阿里云 OSS
在 `.env` 文件中配置：
```env
OSS_ACCESS_KEY_ID=your_access_key
OSS_ACCESS_KEY_SECRET=your_secret_key
OSS_BUCKET_NAME=your_bucket_name
OSS_ENDPOINT=oss-cn-hangzhou.aliyuncs.com
```

## 清理

定期清理测试文件：
```bash
# 删除所有图片（保留目录）
rm -rf uploads/images/*

# 或使用 Python 脚本清理
python scripts/clean_uploads.py
```

