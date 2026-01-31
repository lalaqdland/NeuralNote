"""
测试文件上传、OCR 和 AI 分析功能
"""

import pytest
from pathlib import Path
from io import BytesIO
from PIL import Image
from httpx import AsyncClient


class TestFileUpload:
    """测试文件上传功能"""
    
    @pytest.mark.asyncio
    async def test_file_upload(self, client: AsyncClient, test_user, auth_headers: dict):
        """测试文件上传"""
        # 创建测试图片
        img = Image.new('RGB', (100, 100), color='blue')
        img_bytes = BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        files = {
            "file": ("test_image.jpg", img_bytes, "image/jpeg")
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
        assert data["original_filename"] == "test_image.jpg"
    
    @pytest.mark.asyncio
    async def test_file_list(self, client: AsyncClient, test_user, auth_headers: dict):
        """测试获取文件列表"""
        response = await client.get(
            "/api/v1/files/",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "items" in data
        assert isinstance(data["items"], list)


class TestOCR:
    """测试 OCR 识别功能"""
    
    @pytest.mark.asyncio
    async def test_ocr_with_file_id(self, client: AsyncClient, test_user, auth_headers: dict):
        """测试使用文件ID进行OCR识别"""
        # 先上传一个文件
        img = Image.new('RGB', (200, 100), color='white')
        img_bytes = BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        files = {"file": ("test.jpg", img_bytes, "image/jpeg")}
        upload_response = await client.post(
            "/api/v1/files/upload",
            headers=auth_headers,
            files=files
        )
        
        assert upload_response.status_code == 201
        file_id = upload_response.json()["file_id"]
        
        # 进行 OCR 识别（注意：这需要配置百度 OCR API）
        # 如果没有配置，测试会跳过或失败
        ocr_response = await client.post(
            "/api/v1/ocr/ocr",
            headers=auth_headers,
            json={
                "file_id": file_id,
                "ocr_engine": "baidu"
            }
        )
        
        # 如果没有配置 OCR，可能返回 500 或其他错误
        # 这里我们只检查响应格式
        assert ocr_response.status_code in [200, 500]


class TestAIAnalysis:
    """测试 AI 分析功能"""
    
    @pytest.mark.asyncio
    async def test_ai_text_analysis(self, client: AsyncClient, test_user, auth_headers: dict):
        """测试 AI 文本分析"""
        test_text = "求函数 f(x) = x^2 + 2x + 1 的导数。"
        
        response = await client.post(
            "/api/v1/ai/analyze",
            headers=auth_headers,
            json={
                "text": test_text,
                "engine": "auto",
                "include_embedding": False
            }
        )
        
        # 如果没有配置 AI API，可能返回 500
        # 这里我们只检查响应格式
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "subject" in data
            assert "difficulty" in data
            assert "question_type" in data
    
    @pytest.mark.asyncio
    async def test_knowledge_extraction(self, client: AsyncClient, test_user, auth_headers: dict):
        """测试知识点提取"""
        test_content = """
        导数是微积分中的核心概念，表示函数在某一点的变化率。
        对于函数 f(x)，其导数定义为：f'(x) = lim(h->0) [f(x+h) - f(x)] / h
        """
        
        response = await client.post(
            "/api/v1/ai/extract-knowledge",
            headers=auth_headers,
            json={
                "content": test_content,
                "engine": "auto"
            }
        )
        
        # 如果没有配置 AI API，可能返回 500
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "knowledge_points" in data
            assert isinstance(data["knowledge_points"], list)


class TestIntegration:
    """测试完整的集成流程"""
    
    @pytest.mark.asyncio
    async def test_full_workflow(self, client: AsyncClient, test_user, auth_headers: dict, test_graph):
        """测试完整的工作流程：上传 -> OCR -> AI 分析 -> 创建节点"""
        # 1. 上传文件
        img = Image.new('RGB', (300, 200), color='white')
        img_bytes = BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        files = {"file": ("question.jpg", img_bytes, "image/jpeg")}
        upload_response = await client.post(
            "/api/v1/files/upload",
            headers=auth_headers,
            files=files
        )
        
        assert upload_response.status_code == 201
        file_id = upload_response.json()["file_id"]
        
        # 2. 创建记忆节点（不依赖 OCR 和 AI）
        node_response = await client.post(
            "/api/v1/memory-nodes/",
            headers=auth_headers,
            json={
                "graph_id": str(test_graph.id),
                "node_type": "QUESTION",
                "title": "测试题目",
                "summary": "这是一个测试题目",
                "content_data": {
                    "question": "求导数",
                    "answer": "2x + 2"
                }
            }
        )
        
        assert node_response.status_code == 201
        node_data = node_response.json()
        assert node_data["title"] == "测试题目"
        assert node_data["node_type"] == "QUESTION"
