"""
AI 分析相关的 Pydantic Schemas
"""

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class AIAnalysisRequest(BaseModel):
    """AI 分析请求"""
    
    text: str = Field(..., description="要分析的文本内容")
    engine: Optional[str] = Field("auto", description="AI引擎: openai, deepseek, auto")
    include_embedding: bool = Field(False, description="是否生成向量嵌入")


class AIAnalysisResponse(BaseModel):
    """AI 分析响应"""
    
    subject: str = Field(..., description="学科分类")
    difficulty: str = Field(..., description="难度等级")
    question_type: str = Field(..., description="题目类型")
    answer: str = Field(..., description="详细解答")
    key_points: List[str] = Field(..., description="知识点列表")
    summary: str = Field(..., description="核心要点总结")
    tags: List[str] = Field(..., description="标签列表")
    engine: str = Field(..., description="使用的AI引擎")
    embedding: Optional[List[float]] = Field(None, description="向量嵌入（1536维）")


class KnowledgePointsRequest(BaseModel):
    """知识点提取请求"""
    
    content: str = Field(..., description="内容文本")
    engine: Optional[str] = Field("auto", description="AI引擎")


class KnowledgePointsResponse(BaseModel):
    """知识点提取响应"""
    
    knowledge_points: List[str] = Field(..., description="提取的知识点列表")
    engine: str = Field(..., description="使用的AI引擎")


class EmbeddingRequest(BaseModel):
    """向量嵌入请求"""
    
    text: str = Field(..., description="要生成嵌入的文本")


class EmbeddingResponse(BaseModel):
    """向量嵌入响应"""
    
    embedding: List[float] = Field(..., description="向量嵌入（1536维）")
    dimension: int = Field(..., description="向量维度")


class QuestionAnalysisRequest(BaseModel):
    """题目分析请求（基于文件）"""
    
    file_id: UUID = Field(..., description="文件ID（已OCR识别）")
    engine: Optional[str] = Field("auto", description="AI引擎")
    create_node: bool = Field(True, description="是否自动创建记忆节点")
    graph_id: Optional[UUID] = Field(None, description="目标知识图谱ID")


class QuestionAnalysisResponse(BaseModel):
    """题目分析响应"""
    
    file_id: UUID = Field(..., description="文件ID")
    analysis: AIAnalysisResponse = Field(..., description="分析结果")
    node_id: Optional[UUID] = Field(None, description="创建的记忆节点ID")

