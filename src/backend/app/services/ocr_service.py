"""
OCR 识别服务
支持百度 OCR 和腾讯 OCR
"""

import time
import base64
from typing import Dict, Optional, Tuple
from pathlib import Path

import httpx
from fastapi import HTTPException

from app.core.config import settings


class OCRService:
    """OCR 识别服务"""
    
    def __init__(self):
        """初始化 OCR 服务"""
        self.baidu_configured = all([
            settings.BAIDU_OCR_API_KEY,
            settings.BAIDU_OCR_SECRET_KEY,
        ])
        
        # 百度 OCR Token 缓存
        self.baidu_access_token: Optional[str] = None
        self.baidu_token_expires_at: float = 0
    
    async def get_baidu_access_token(self) -> str:
        """
        获取百度 OCR Access Token
        
        Returns:
            Access Token
        """
        # 检查缓存的 Token 是否有效
        if self.baidu_access_token and time.time() < self.baidu_token_expires_at:
            return self.baidu_access_token
        
        # 获取新的 Token
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {
            "grant_type": "client_credentials",
            "client_id": settings.BAIDU_OCR_API_KEY,
            "client_secret": settings.BAIDU_OCR_SECRET_KEY,
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, params=params)
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=500,
                    detail="获取百度 OCR Access Token 失败"
                )
            
            data = response.json()
            self.baidu_access_token = data["access_token"]
            # Token 有效期 30 天，提前 1 天刷新
            self.baidu_token_expires_at = time.time() + (29 * 24 * 3600)
            
            return self.baidu_access_token
    
    async def ocr_baidu(self, image_path: Path) -> Dict:
        """
        使用百度 OCR 识别图片
        
        Args:
            image_path: 图片路径
            
        Returns:
            识别结果
        """
        if not self.baidu_configured:
            raise HTTPException(
                status_code=500,
                detail="百度 OCR 未配置"
            )
        
        # 获取 Access Token
        access_token = await self.get_baidu_access_token()
        
        # 读取图片并转为 base64
        with open(image_path, "rb") as f:
            image_data = f.read()
        image_base64 = base64.b64encode(image_data).decode("utf-8")
        
        # 调用百度 OCR API（通用文字识别-高精度版）
        url = "https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic"
        params = {"access_token": access_token}
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {"image": image_base64}
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, params=params, headers=headers, data=data)
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=500,
                    detail=f"百度 OCR 识别失败: {response.text}"
                )
            
            result = response.json()
            
            # 检查是否有错误
            if "error_code" in result:
                raise HTTPException(
                    status_code=500,
                    detail=f"百度 OCR 错误: {result.get('error_msg', 'Unknown error')}"
                )
            
            return result
    
    def parse_baidu_result(self, result: Dict) -> Tuple[str, float]:
        """
        解析百度 OCR 结果
        
        Args:
            result: 百度 OCR 原始结果
            
        Returns:
            (识别文本, 平均置信度)
        """
        if "words_result" not in result:
            return "", 0.0
        
        words_result = result["words_result"]
        
        if not words_result:
            return "", 0.0
        
        # 提取所有文本行
        lines = [item["words"] for item in words_result]
        text = "\n".join(lines)
        
        # 计算平均置信度（如果有）
        confidences = []
        for item in words_result:
            if "probability" in item:
                # 百度返回的是一个包含各字符置信度的对象
                prob = item["probability"]
                if isinstance(prob, dict) and "average" in prob:
                    confidences.append(prob["average"])
        
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.85
        
        return text, avg_confidence
    
    async def ocr_image(
        self,
        image_path: Path,
        engine: str = "baidu"
    ) -> Tuple[str, float, Dict]:
        """
        识别图片中的文字
        
        Args:
            image_path: 图片路径
            engine: OCR 引擎 (baidu, tencent, auto)
            
        Returns:
            (识别文本, 置信度, 原始结果)
        """
        start_time = time.time()
        
        # 根据引擎选择
        if engine == "baidu" or engine == "auto":
            if self.baidu_configured:
                raw_result = await self.ocr_baidu(image_path)
                text, confidence = self.parse_baidu_result(raw_result)
                processing_time = time.time() - start_time
                
                return text, confidence, {
                    "engine": "baidu",
                    "raw_result": raw_result,
                    "processing_time": processing_time
                }
        
        # 如果没有配置任何 OCR 服务
        raise HTTPException(
            status_code=500,
            detail="没有可用的 OCR 服务，请配置百度或腾讯 OCR"
        )
    
    async def ocr_with_math(
        self,
        image_path: Path,
        engine: str = "baidu"
    ) -> Tuple[str, float, Dict]:
        """
        识别包含数学公式的图片
        
        Args:
            image_path: 图片路径
            engine: OCR 引擎
            
        Returns:
            (识别文本, 置信度, 原始结果)
        """
        # TODO: 实现数学公式识别
        # 可以使用百度的公式识别 API 或其他专门的数学公式识别服务
        return await self.ocr_image(image_path, engine)


# 创建全局 OCR 服务实例
ocr_service = OCRService()

