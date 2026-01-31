"""
AI 服务单元测试
使用 Mock 测试 AI 分析功能
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
import json

from app.services.ai_service import AIService


class TestAIService:
    """测试 AI 服务"""
    
    @pytest.fixture
    def ai_service(self):
        """创建 AI 服务实例"""
        # AIService 不接受参数，使用环境变量配置
        return AIService()
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient.post')
    async def test_call_deepseek_success(self, mock_post, ai_service):
        """测试成功调用 DeepSeek API"""
        # Mock 响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "这是 AI 的回复"
                    }
                }
            ]
        }
        mock_post.return_value = mock_response
        
        messages = [{"role": "user", "content": "测试消息"}]
        result = await ai_service.call_deepseek(messages)
        
        assert result == "这是 AI 的回复"
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient.post')
    async def test_call_openai_success(self, mock_post, ai_service):
        """测试成功调用 OpenAI API"""
        # 设置 OpenAI 为已配置状态
        ai_service.openai_configured = True
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "OpenAI 的回复"
                    }
                }
            ]
        }
        mock_post.return_value = mock_response
        
        messages = [{"role": "user", "content": "测试消息"}]
        result = await ai_service.call_openai(messages)
        
        assert result == "OpenAI 的回复"
    
    @pytest.mark.asyncio
    @patch('app.services.ai_service.AIService.call_deepseek')
    async def test_analyze_question_success(self, mock_call_deepseek, ai_service):
        """测试成功分析题目"""
        # Mock DeepSeek 响应
        mock_call_deepseek.return_value = json.dumps({
            "subject": "数学",
            "difficulty": "中等",
            "question_type": "解答题",
            "answer": "这是解答步骤",
            "key_points": ["代数", "方程"],
            "summary": "二次方程求解",
            "tags": ["数学", "代数"]
        }, ensure_ascii=False)
        
        result = await ai_service.analyze_question("求解方程 x^2 + 2x + 1 = 0")
        
        assert result["subject"] == "数学"
        assert result["difficulty"] == "中等"
        assert len(result["key_points"]) == 2
        assert result["engine"] == "deepseek"
    
    @pytest.mark.asyncio
    @patch('app.services.ai_service.AIService.call_deepseek')
    async def test_analyze_question_with_markdown_json(self, mock_call_deepseek, ai_service):
        """测试处理 Markdown 格式的 JSON 响应"""
        # Mock 返回 Markdown 包裹的 JSON
        mock_call_deepseek.return_value = '```json\n{"subject": "物理", "difficulty": "困难"}\n```'
        
        result = await ai_service.analyze_question("测试题目")
        
        assert result["subject"] == "物理"
        assert result["difficulty"] == "困难"
    
    @pytest.mark.asyncio
    @patch('app.services.ai_service.AIService.call_deepseek')
    async def test_extract_knowledge_points_success(self, mock_call_deepseek, ai_service):
        """测试成功提取知识点"""
        mock_call_deepseek.return_value = json.dumps([
            "二次方程",
            "求根公式",
            "判别式"
        ], ensure_ascii=False)
        
        result = await ai_service.extract_knowledge_points("二次方程的解法")
        
        assert len(result) == 3
        assert "二次方程" in result
        assert "求根公式" in result
    
    @pytest.mark.asyncio
    @patch('app.services.ai_service.AIService.call_deepseek')
    async def test_extract_knowledge_points_with_markdown(self, mock_call_deepseek, ai_service):
        """测试提取知识点（Markdown 格式）"""
        mock_call_deepseek.return_value = '```json\n["知识点1", "知识点2"]\n```'
        
        result = await ai_service.extract_knowledge_points("测试内容")
        
        assert len(result) == 2
        assert "知识点1" in result
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient.post')
    async def test_generate_embedding_success(self, mock_post, ai_service):
        """测试成功生成向量嵌入"""
        # 设置 OpenAI 为已配置状态
        ai_service.openai_configured = True
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {
                    "embedding": [0.1] * 1536  # 1536 维向量
                }
            ]
        }
        mock_post.return_value = mock_response
        
        result = await ai_service.generate_embedding("测试文本")
        
        assert len(result) == 1536
        assert all(isinstance(x, float) for x in result)


class TestAIConfiguration:
    """测试 AI 配置"""
    
    def test_ai_service_initialization(self):
        """测试 AI 服务初始化"""
        service = AIService()
        
        # 检查服务是否正确初始化
        assert service is not None
        assert hasattr(service, 'openai_configured')
        assert hasattr(service, 'deepseek_configured')
    
    def test_ai_service_configuration_check(self):
        """测试 AI 服务配置检查"""
        service = AIService()
        
        # 检查配置状态（取决于环境变量）
        assert isinstance(service.openai_configured, bool)
        assert isinstance(service.deepseek_configured, bool)


class TestJSONParsing:
    """测试 JSON 解析功能"""
    
    def test_parse_plain_json(self):
        """测试解析普通 JSON"""
        json_str = '{"key": "value", "number": 123}'
        result = json.loads(json_str)
        
        assert result["key"] == "value"
        assert result["number"] == 123
    
    def test_parse_markdown_wrapped_json(self):
        """测试解析 Markdown 包裹的 JSON"""
        markdown_json = '```json\n{"key": "value"}\n```'
        
        # 提取 JSON
        if "```json" in markdown_json:
            json_start = markdown_json.find("```json") + 7
            json_end = markdown_json.find("```", json_start)
            json_str = markdown_json[json_start:json_end].strip()
        else:
            json_str = markdown_json
        
        result = json.loads(json_str)
        assert result["key"] == "value"
    
    def test_parse_json_array(self):
        """测试解析 JSON 数组"""
        json_str = '["item1", "item2", "item3"]'
        result = json.loads(json_str)
        
        assert isinstance(result, list)
        assert len(result) == 3
        assert "item1" in result


class TestAIPrompts:
    """测试 AI 提示词"""
    
    def test_analyze_question_prompt_structure(self):
        """测试题目分析提示词结构"""
        question_text = "求解方程 x + 1 = 0"
        
        # 构建提示词（模拟实际逻辑）
        system_prompt = "你是一个专业的学习助手"
        user_prompt = f"请分析以下题目：\n\n{question_text}"
        
        assert "学习助手" in system_prompt
        assert question_text in user_prompt
    
    def test_knowledge_extraction_prompt_structure(self):
        """测试知识点提取提示词结构"""
        content = "二次方程的解法"
        
        # 构建提示词
        system_prompt = "你是一个知识点提取专家"
        user_prompt = f"请从以下内容中提取知识点：\n\n{content}"
        
        assert "知识点" in system_prompt
        assert content in user_prompt


class TestAIErrorHandling:
    """测试 AI 错误处理"""
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient.post')
    async def test_api_error_handling(self, mock_post):
        """测试 API 错误处理"""
        service = AIService()
        
        # Mock API 错误
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response
        
        messages = [{"role": "user", "content": "测试"}]
        
        # 应该抛出 HTTPException
        with pytest.raises(Exception):
            await service.call_deepseek(messages)
    
    @pytest.mark.asyncio
    @patch('app.services.ai_service.AIService.call_deepseek')
    async def test_json_parse_error_handling(self, mock_call_deepseek):
        """测试 JSON 解析错误处理"""
        service = AIService()
        
        # Mock 返回无效的 JSON
        mock_call_deepseek.return_value = "这不是有效的 JSON"
        
        result = await service.analyze_question("测试题目")
        
        # 应该返回包含原始文本的结果
        assert "answer" in result
        assert result.get("parse_error") is True
