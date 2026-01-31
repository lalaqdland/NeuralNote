"""
OCR 服务单元测试
使用 Mock 测试 OCR 识别功能
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from io import BytesIO
from pathlib import Path

from app.services.ocr_service import OCRService


class TestOCRService:
    """测试 OCR 服务"""
    
    @pytest.fixture
    def ocr_service(self):
        """创建 OCR 服务实例"""
        # OCRService 不接受参数，使用环境变量配置
        return OCRService()
    
    @pytest.fixture
    def mock_image_path(self, tmp_path):
        """创建模拟图片文件"""
        from PIL import Image
        img = Image.new('RGB', (100, 100), color='white')
        img_path = tmp_path / "test.jpg"
        img.save(img_path)
        return img_path
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient.post')
    async def test_get_access_token_success(self, mock_post, ocr_service):
        """测试成功获取 Access Token"""
        # Mock 响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "test_access_token_123",
            "expires_in": 2592000
        }
        mock_post.return_value = mock_response
        
        token = await ocr_service.get_baidu_access_token()
        
        assert token == "test_access_token_123"
        assert ocr_service.baidu_access_token == "test_access_token_123"
        assert ocr_service.baidu_token_expires_at > 0
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient.post')
    async def test_get_access_token_cached(self, mock_post, ocr_service):
        """测试 Access Token 缓存"""
        # 第一次调用
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "cached_token",
            "expires_in": 2592000
        }
        mock_post.return_value = mock_response
        
        token1 = await ocr_service.get_baidu_access_token()
        
        # 第二次调用应该使用缓存
        token2 = await ocr_service.get_baidu_access_token()
        
        assert token1 == token2
        # 只应该调用一次 API
        assert mock_post.call_count == 1
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient.post')
    async def test_ocr_baidu_success(self, mock_post, ocr_service, mock_image_path):
        """测试成功识别文本"""
        # Mock Access Token
        ocr_service.baidu_access_token = "test_token"
        ocr_service.baidu_token_expires_at = 9999999999
        
        # Mock OCR 响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "words_result": [
                {"words": "这是第一行文字"},
                {"words": "这是第二行文字"}
            ],
            "words_result_num": 2
        }
        mock_post.return_value = mock_response
        
        result = await ocr_service.ocr_baidu(mock_image_path)
        
        assert "words_result" in result
        assert len(result["words_result"]) == 2
    
    @pytest.mark.asyncio
    async def test_parse_baidu_result(self, ocr_service):
        """测试解析百度 OCR 结果"""
        result = {
            "words_result": [
                {"words": "这是第一行文字"},
                {"words": "这是第二行文字"}
            ],
            "words_result_num": 2
        }
        
        text, confidence = ocr_service.parse_baidu_result(result)
        
        assert "这是第一行文字" in text
        assert "这是第二行文字" in text
        assert confidence > 0
    
    @pytest.mark.asyncio
    async def test_parse_baidu_result_empty(self, ocr_service):
        """测试解析空结果"""
        result = {
            "words_result": [],
            "words_result_num": 0
        }
        
        text, confidence = ocr_service.parse_baidu_result(result)
        
        assert text == ""
        assert confidence == 0.0
    
    @pytest.mark.asyncio
    @patch('app.services.ocr_service.OCRService.ocr_baidu')
    async def test_ocr_image_success(self, mock_ocr_baidu, ocr_service, mock_image_path):
        """测试 OCR 图片识别"""
        mock_ocr_baidu.return_value = {
            "words_result": [
                {"words": "测试文本"}
            ],
            "words_result_num": 1
        }
        
        text, confidence, raw_result = await ocr_service.ocr_image(mock_image_path, engine="baidu")
        
        assert "测试文本" in text
        assert confidence > 0
        assert raw_result["engine"] == "baidu"


class TestOCRSchemas:
    """测试 OCR 相关的 Schemas"""
    
    def test_ocr_request_validation(self):
        """测试 OCR 请求验证"""
        from app.schemas.file_upload import OCRRequest
        import uuid
        
        # 有效的请求
        valid_request = OCRRequest(file_id=uuid.uuid4(), ocr_engine="baidu")
        assert valid_request.file_id is not None
        assert valid_request.ocr_engine == "baidu"
        
        # 测试默认值（默认是 baidu）
        default_request = OCRRequest(file_id=uuid.uuid4())
        assert default_request.ocr_engine == "baidu"
        
        # 测试其他引擎
        auto_request = OCRRequest(file_id=uuid.uuid4(), ocr_engine="auto")
        assert auto_request.ocr_engine == "auto"
    
    def test_ocr_response_schema(self):
        """测试 OCR 响应 Schema"""
        from app.schemas.file_upload import OCRResponse
        import uuid
        
        response = OCRResponse(
            file_id=uuid.uuid4(),
            text="测试文本",
            confidence=0.95,
            engine="baidu",
            processing_time=0.5
        )
        
        assert response.text == "测试文本"
        assert response.confidence == 0.95
        assert response.engine == "baidu"
        assert response.processing_time == 0.5


class TestOCRUtilities:
    """测试 OCR 工具函数"""
    
    def test_image_preprocessing(self):
        """测试图片预处理"""
        from PIL import Image
        
        # 创建测试图片
        img = Image.new('RGB', (200, 200), color='blue')
        img_bytes = BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        # 这里可以添加图片预处理的测试
        # 例如：调整大小、增强对比度等
        assert img_bytes.getvalue() is not None
    
    def test_text_postprocessing(self):
        """测试文本后处理"""
        # 测试去除多余空格
        text = "  这是  测试   文本  "
        cleaned = " ".join(text.split())
        assert cleaned == "这是 测试 文本"
        
        # 测试去除特殊字符
        text_with_special = "测试\n\r\t文本"
        cleaned = text_with_special.replace("\n", " ").replace("\r", "").replace("\t", " ")
        assert "测试" in cleaned
        assert "文本" in cleaned


class TestOCRConfiguration:
    """测试 OCR 配置"""
    
    def test_ocr_service_initialization(self):
        """测试 OCR 服务初始化"""
        service = OCRService()
        
        # 检查服务是否正确初始化
        assert service is not None
        assert hasattr(service, 'baidu_configured')
        assert hasattr(service, 'baidu_access_token')
        assert hasattr(service, 'baidu_token_expires_at')
    
    def test_ocr_service_configuration_check(self):
        """测试 OCR 服务配置检查"""
        service = OCRService()
        
        # 检查配置状态（取决于环境变量）
        assert isinstance(service.baidu_configured, bool)
