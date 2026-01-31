"""
文件上传服务单元测试
测试文件存储、验证、管理等功能
"""

import pytest
import uuid
from pathlib import Path
from io import BytesIO
from PIL import Image
from fastapi import UploadFile, HTTPException
from httpx import AsyncClient
from starlette.datastructures import Headers

from app.services.file_storage import FileStorageService


class TestFileValidation:
    """测试文件验证功能"""
    
    @pytest.fixture
    def service(self):
        """创建文件存储服务实例"""
        return FileStorageService()
    
    @pytest.mark.asyncio
    async def test_validate_file_valid_image(self, service):
        """测试有效的图片类型"""
        # 创建测试图片
        img = Image.new('RGB', (100, 100), color='red')
        img_bytes = BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        # 创建 UploadFile 对象
        headers = Headers({"content-type": "image/jpeg"})
        upload_file = UploadFile(
            file=img_bytes,
            filename="test.jpg",
            headers=headers
        )
        
        # 应该不抛出异常
        service.validate_file(upload_file)
    
    @pytest.mark.asyncio
    async def test_validate_file_invalid_type(self, service):
        """测试无效的文件类型"""
        # 创建文本文件
        text_bytes = BytesIO(b"This is a text file")
        
        headers = Headers({"content-type": "text/plain"})
        upload_file = UploadFile(
            file=text_bytes,
            filename="test.txt",
            headers=headers
        )
        
        # 应该抛出 HTTPException
        with pytest.raises(HTTPException) as exc_info:
            service.validate_file(upload_file)
        
        assert exc_info.value.status_code == 400
        assert "不支持的文件类型" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_validate_file_too_large(self, service):
        """测试文件过大"""
        # 创建一个大文件（11MB）
        large_bytes = BytesIO(b"x" * (11 * 1024 * 1024))
        
        headers = Headers({"content-type": "image/jpeg"})
        upload_file = UploadFile(
            file=large_bytes,
            filename="large.jpg",
            headers=headers
        )
        
        # 应该抛出 HTTPException
        with pytest.raises(HTTPException) as exc_info:
            service.validate_file(upload_file)
        
        assert exc_info.value.status_code == 400
        assert "文件大小超过限制" in exc_info.value.detail


class TestFileNameGeneration:
    """测试文件名生成"""
    
    @pytest.fixture
    def service(self):
        """创建文件存储服务实例"""
        return FileStorageService()
    
    def test_generate_filename(self, service):
        """测试生成唯一文件名"""
        filename1, ext1 = service.generate_filename("test.jpg")
        filename2, ext2 = service.generate_filename("test.jpg")
        
        # 两次生成的文件名应该不同
        assert filename1 != filename2
        
        # 应该保留原始扩展名
        assert ext1 == ".jpg"
        assert ext2 == ".jpg"
        assert filename1.endswith(".jpg")
        assert filename2.endswith(".jpg")
    
    def test_generate_filename_preserves_extension(self, service):
        """测试保留文件扩展名"""
        extensions = [".jpg", ".png", ".jpeg", ".gif", ".webp"]
        
        for ext in extensions:
            filename, returned_ext = service.generate_filename(f"test{ext}")
            assert returned_ext == ext.lower()
            assert filename.endswith(ext.lower())
    
    def test_generate_filename_no_extension(self, service):
        """测试没有扩展名的文件"""
        filename, ext = service.generate_filename("test")
        assert len(filename) > 0
        assert ext == ""


class TestLocalStorage:
    """测试本地存储功能"""
    
    @pytest.fixture
    def service(self, tmp_path):
        """创建文件存储服务实例（使用临时目录）"""
        service = FileStorageService()
        # 使用临时目录
        service.upload_dir = tmp_path / "uploads"
        service.upload_dir.mkdir(exist_ok=True)
        service.images_dir = service.upload_dir / "images"
        service.images_dir.mkdir(exist_ok=True)
        service.use_oss = False  # 强制使用本地存储
        return service
    
    @pytest.fixture
    def test_image(self):
        """创建测试图片"""
        img = Image.new('RGB', (100, 100), color='red')
        img_bytes = BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        return img_bytes
    
    @pytest.mark.asyncio
    async def test_save_file_local(self, service, test_image):
        """测试保存文件到本地"""
        headers = Headers({"content-type": "image/jpeg"})
        upload_file = UploadFile(
            file=test_image,
            filename="test.jpg",
            headers=headers
        )
        
        stored_filename, ext = service.generate_filename("test.jpg")
        file_url = await service.save_file_local(upload_file, stored_filename)
        
        assert file_url is not None
        assert file_url.startswith("/uploads/images/")
        assert stored_filename in file_url
        
        # 验证文件存在
        file_path = service.images_dir / stored_filename
        assert file_path.exists()
    
    @pytest.mark.asyncio
    async def test_delete_file_local(self, service, test_image):
        """测试删除本地文件"""
        headers = Headers({"content-type": "image/jpeg"})
        upload_file = UploadFile(
            file=test_image,
            filename="test.jpg",
            headers=headers
        )
        
        # 先保存文件
        stored_filename, ext = service.generate_filename("test.jpg")
        await service.save_file_local(upload_file, stored_filename)
        
        file_path = service.images_dir / stored_filename
        assert file_path.exists()
        
        # 删除文件
        success = service.delete_file_local(stored_filename)
        
        assert success
        assert not file_path.exists()
    
    def test_delete_nonexistent_file(self, service):
        """测试删除不存在的文件"""
        success = service.delete_file_local("nonexistent_file.jpg")
        
        # 删除不存在的文件应该返回 False
        assert not success


class TestFileUploadIntegration:
    """测试文件上传的集成功能"""
    
    @pytest.mark.asyncio
    async def test_upload_image_endpoint(self, client: AsyncClient, test_user, auth_headers: dict):
        """测试图片上传接口"""
        # 创建测试图片
        img = Image.new('RGB', (100, 100), color='blue')
        img_bytes = BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        files = {
            "file": ("test.jpg", img_bytes, "image/jpeg")
        }
        
        response = await client.post(
            "/api/v1/files/upload",
            headers=auth_headers,
            files=files
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "file_id" in data
        assert "file_url" in data
        assert "original_filename" in data
        assert data["original_filename"] == "test.jpg"
    
    @pytest.mark.asyncio
    async def test_upload_invalid_file_type(self, client: AsyncClient, test_user, auth_headers: dict):
        """测试上传无效文件类型"""
        # 创建文本文件
        text_content = BytesIO(b"This is a text file")
        
        files = {
            "file": ("test.txt", text_content, "text/plain")
        }
        
        response = await client.post(
            "/api/v1/files/upload",
            headers=auth_headers,
            files=files
        )
        
        assert response.status_code == 400
        assert "不支持的文件类型" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_upload_file_too_large(self, client: AsyncClient, test_user, auth_headers: dict):
        """测试上传过大的文件"""
        # 创建一个大文件（11MB）
        large_content = BytesIO(b"x" * (11 * 1024 * 1024))
        
        files = {
            "file": ("large.jpg", large_content, "image/jpeg")
        }
        
        response = await client.post(
            "/api/v1/files/upload",
            headers=auth_headers,
            files=files
        )
        
        # 应该返回 400
        assert response.status_code == 400
        assert "文件大小超过限制" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_get_file_list(self, client: AsyncClient, test_user, auth_headers: dict):
        """测试获取文件列表"""
        response = await client.get(
            "/api/v1/files/",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert isinstance(data["items"], list)
    
    @pytest.mark.asyncio
    async def test_delete_file_endpoint(self, client: AsyncClient, test_user, auth_headers: dict):
        """测试删除文件接口"""
        # 先上传一个文件
        img = Image.new('RGB', (50, 50), color='green')
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        files = {
            "file": ("delete_test.png", img_bytes, "image/png")
        }
        
        upload_response = await client.post(
            "/api/v1/files/upload",
            headers=auth_headers,
            files=files
        )
        
        assert upload_response.status_code == 201
        file_id = upload_response.json()["file_id"]
        
        # 删除文件
        delete_response = await client.delete(
            f"/api/v1/files/{file_id}",
            headers=auth_headers
        )
        
        assert delete_response.status_code == 200


class TestFileMetadata:
    """测试文件元数据管理"""
    
    @pytest.mark.asyncio
    async def test_update_file_metadata(self, client: AsyncClient, test_user, auth_headers: dict):
        """测试更新文件元数据"""
        # 先上传一个文件
        img = Image.new('RGB', (50, 50), color='yellow')
        img_bytes = BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        files = {
            "file": ("metadata_test.jpg", img_bytes, "image/jpeg")
        }
        
        upload_response = await client.post(
            "/api/v1/files/upload",
            headers=auth_headers,
            files=files
        )
        
        assert upload_response.status_code == 201
        file_id = upload_response.json()["file_id"]
        
        # 更新元数据
        update_response = await client.put(
            f"/api/v1/files/{file_id}",
            headers=auth_headers,
            json={
                "status": "processed"
            }
        )
        
        assert update_response.status_code == 200
        data = update_response.json()
        assert data["status"] == "processed"
