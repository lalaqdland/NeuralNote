"""
AI 分析服务
支持 DeepSeek 和 OpenAI GPT-4
"""

import json
from typing import Dict, List, Optional, Tuple

import httpx
from fastapi import HTTPException

from app.core.config import settings


class AIService:
    """AI 分析服务"""
    
    def __init__(self):
        """初始化 AI 服务"""
        self.openai_configured = bool(settings.OPENAI_API_KEY)
        self.deepseek_configured = bool(settings.DEEPSEEK_API_KEY)
    
    async def call_openai(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """
        调用 OpenAI API
        
        Args:
            messages: 消息列表
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大 token 数
            
        Returns:
            AI 响应文本
        """
        if not self.openai_configured:
            raise HTTPException(status_code=500, detail="OpenAI API 未配置")
        
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, headers=headers, json=data)
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=500,
                    detail=f"OpenAI API 调用失败: {response.text}"
                )
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
    
    async def call_deepseek(
        self,
        messages: List[Dict[str, str]],
        model: str = "deepseek-chat",
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """
        调用 DeepSeek API
        
        Args:
            messages: 消息列表
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大 token 数
            
        Returns:
            AI 响应文本
        """
        if not self.deepseek_configured:
            raise HTTPException(status_code=500, detail="DeepSeek API 未配置")
        
        url = "https://api.deepseek.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, headers=headers, json=data)
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=500,
                    detail=f"DeepSeek API 调用失败: {response.text}"
                )
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
    
    async def analyze_question(
        self,
        question_text: str,
        engine: str = "auto"
    ) -> Dict:
        """
        分析题目并生成解答
        
        Args:
            question_text: 题目文本
            engine: AI 引擎 (openai, deepseek, auto)
            
        Returns:
            分析结果字典
        """
        # 构建提示词
        system_prompt = """你是一个专业的学习助手，擅长分析和解答各类学科问题。
请按照以下 JSON 格式返回分析结果：

{
    "subject": "学科分类（如：数学、物理、化学、英语等）",
    "difficulty": "难度等级（简单、中等、困难）",
    "question_type": "题目类型（选择题、填空题、解答题等）",
    "answer": "详细解答过程",
    "key_points": ["知识点1", "知识点2", "知识点3"],
    "summary": "核心要点总结（50字以内）",
    "tags": ["标签1", "标签2", "标签3"]
}

请确保返回的是有效的 JSON 格式。"""
        
        user_prompt = f"请分析以下题目：\n\n{question_text}"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # 选择 AI 引擎
        if engine == "auto":
            # 优先使用 DeepSeek（成本更低）
            if self.deepseek_configured:
                engine = "deepseek"
            elif self.openai_configured:
                engine = "openai"
            else:
                raise HTTPException(
                    status_code=500,
                    detail="没有可用的 AI 服务，请配置 OpenAI 或 DeepSeek API"
                )
        
        # 调用 AI
        if engine == "deepseek":
            response_text = await self.call_deepseek(messages)
        elif engine == "openai":
            response_text = await self.call_openai(messages)
        else:
            raise HTTPException(status_code=400, detail=f"不支持的 AI 引擎: {engine}")
        
        # 解析 JSON 响应
        try:
            # 尝试提取 JSON（可能包含在 markdown 代码块中）
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            
            result = json.loads(response_text)
            result["engine"] = engine
            return result
        except json.JSONDecodeError:
            # 如果解析失败，返回原始文本
            return {
                "subject": "未知",
                "difficulty": "未知",
                "question_type": "未知",
                "answer": response_text,
                "key_points": [],
                "summary": "AI 分析结果",
                "tags": [],
                "engine": engine,
                "parse_error": True
            }
    
    async def extract_knowledge_points(
        self,
        content: str,
        engine: str = "auto"
    ) -> List[str]:
        """
        从内容中提取知识点
        
        Args:
            content: 内容文本
            engine: AI 引擎
            
        Returns:
            知识点列表
        """
        system_prompt = """你是一个知识点提取专家。
请从给定的内容中提取关键知识点，以 JSON 数组格式返回。
例如：["知识点1", "知识点2", "知识点3"]

要求：
1. 每个知识点简洁明了（5-15字）
2. 提取3-8个核心知识点
3. 按重要性排序
4. 返回有效的 JSON 数组"""
        
        user_prompt = f"请从以下内容中提取知识点：\n\n{content}"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # 选择引擎
        if engine == "auto":
            engine = "deepseek" if self.deepseek_configured else "openai"
        
        # 调用 AI
        if engine == "deepseek":
            response_text = await self.call_deepseek(messages, max_tokens=500)
        else:
            response_text = await self.call_openai(messages, max_tokens=500)
        
        # 解析 JSON
        try:
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            
            knowledge_points = json.loads(response_text)
            return knowledge_points if isinstance(knowledge_points, list) else []
        except json.JSONDecodeError:
            # 解析失败，返回空列表
            return []
    
    async def generate_embedding(self, text: str) -> List[float]:
        """
        生成文本的向量嵌入
        
        Args:
            text: 文本内容
            
        Returns:
            向量嵌入（1536维）
        """
        if not self.openai_configured:
            raise HTTPException(status_code=500, detail="OpenAI API 未配置")
        
        url = "https://api.openai.com/v1/embeddings"
        headers = {
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": settings.EMBEDDING_MODEL,
            "input": text
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=data)
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=500,
                    detail=f"生成向量嵌入失败: {response.text}"
                )
            
            result = response.json()
            return result["data"][0]["embedding"]


# 创建全局 AI 服务实例
ai_service = AIService()

