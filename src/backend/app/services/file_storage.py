"""
文件存储服务
支持本地存储和阿里云 OSS
"""

import os
import uuid
from pathlib import Path
from typing import Optional, Tuple
from datetime import datetime

from fastapi import UploadFile, HTTPException

from app.core.config import settings


class FileStorageService:
    """文件存储服务"""
    
    def __init__(self):
        """初始化文件存储服务"""
        self.upload_dir = Path("uploads")
        self.upload_dir.mkdir(exist_ok=True)
        
        # 创建子目录
        self.images_dir = self.upload_dir / "images"
        self.images_dir.mkdir(exist_ok=True)
        
        # OSS 配置（如果配置了 OSS）
        self.use_oss = all([
            settings.OSS_ACCESS_KEY_ID,
            settings.OSS_ACCESS_KEY_SECRET,
            settings.OSS_BUCKET_NAME,
            settings.OSS_ENDPOINT,
        ])
        
        if self.use_oss:
            try:
                import oss2
                auth = oss2.Auth(
                    settings.OSS_ACCESS_KEY_ID,
                    settings.OSS_ACCESS_KEY_SECRET
                )
                self.oss_bucket = oss2.Bucket(
                    auth,
                    settings.OSS_ENDPOINT,
                    settings.OSS_BUCKET_NAME
                )
            except ImportError:
                print("警告: oss2 未安装，将使用本地存储")
                self.use_oss = False
    
    def validate_file(self, file: UploadFile) -> None:
        """
        验证上传的文件
        
        Args:
            file: 上传的文件
            
        Raises:
            HTTPException: 文件验证失败
        """
        # 检查文件类型
        if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件类型: {file.content_type}。"
                       f"支持的类型: {', '.join(settings.ALLOWED_IMAGE_TYPES)}"
            )
        
        # 检查文件大小（需要读取文件）
        file.file.seek(0, 2)  # 移动到文件末尾
        file_size = file.file.tell()
        file.file.seek(0)  # 重置到文件开头
        
        if file_size > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"文件大小超过限制: {file_size} bytes > {settings.MAX_UPLOAD_SIZE} bytes"
            )
    
    def generate_filename(self, original_filename: str) -> Tuple[str, str]:
        """
        生成唯一的文件名
        
        Args:
            original_filename: 原始文件名
            
        Returns:
            (存储文件名, 文件扩展名)
        """
        # 获取文件扩展名
        ext = Path(original_filename).suffix.lower()
        
        # 生成唯一文件名: 日期_UUID.ext
        date_str = datetime.now().strftime("%Y%m%d")
        unique_id = str(uuid.uuid4())[:8]
        stored_filename = f"{date_str}_{unique_id}{ext}"
        
        return stored_filename, ext
    
    async def save_file_local(
        self,
        file: UploadFile,
        stored_filename: str
    ) -> str:
        """
        保存文件到本地
        
        Args:
            file: 上传的文件
            stored_filename: 存储文件名
            
        Returns:
            文件访问 URL
        """
        # 保存到本地
        file_path = self.images_dir / stored_filename
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # 返回相对 URL
        return f"/uploads/images/{stored_filename}"
    
    async def save_file_oss(
        self,
        file: UploadFile,
        stored_filename: str
    ) -> str:
        """
        保存文件到阿里云 OSS
        
        Args:
            file: 上传的文件
            stored_filename: 存储文件名
            
        Returns:
            文件访问 URL
        """
        # OSS 路径
        oss_path = f"images/{stored_filename}"
        
        # 上传到 OSS
        content = await file.read()
        self.oss_bucket.put_object(oss_path, content)
        
        # 返回 OSS URL
        return f"https://{settings.OSS_BUCKET_NAME}.{settings.OSS_ENDPOINT}/{oss_path}"
    
    async def save_file(
        self,
        file: UploadFile,
        user_id: uuid.UUID
    ) -> Tuple[str, str, int]:
        """
        保存上传的文件
        
        Args:
            file: 上传的文件
            user_id: 用户ID
            
        Returns:
            (存储文件名, 文件URL, 文件大小)
        """
        # 验证文件
        self.validate_file(file)
        
        # 生成文件名
        stored_filename, ext = self.generate_filename(file.filename or "upload")
        
        # 获取文件大小
        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)
        
        # 保存文件
        if self.use_oss:
            file_url = await self.save_file_oss(file, stored_filename)
        else:
            file_url = await self.save_file_local(file, stored_filename)
        
        return stored_filename, file_url, file_size
    
    def delete_file_local(self, stored_filename: str) -> bool:
        """
        删除本地文件
        
        Args:
            stored_filename: 存储文件名
            
        Returns:
            是否删除成功
        """
        file_path = self.images_dir / stored_filename
        
        if file_path.exists():
            file_path.unlink()
            return True
        
        return False
    
    def delete_file_oss(self, stored_filename: str) -> bool:
        """
        删除 OSS 文件
        
        Args:
            stored_filename: 存储文件名
            
        Returns:
            是否删除成功
        """
        oss_path = f"images/{stored_filename}"
        
        try:
            self.oss_bucket.delete_object(oss_path)
            return True
        except Exception as e:
            print(f"删除 OSS 文件失败: {e}")
            return False
    
    def delete_file(self, stored_filename: str) -> bool:
        """
        删除文件
        
        Args:
            stored_filename: 存储文件名
            
        Returns:
            是否删除成功
        """
        if self.use_oss:
            return self.delete_file_oss(stored_filename)
        else:
            return self.delete_file_local(stored_filename)


# 创建全局文件存储服务实例
file_storage_service = FileStorageService()

