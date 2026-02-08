"""
AI 分析相关的 API 端点
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import User, FileUpload, MemoryNode, KnowledgeGraph
from app.schemas.ai_analysis import (
    AIAnalysisRequest,
    AIAnalysisResponse,
    KnowledgePointsRequest,
    KnowledgePointsResponse,
    EmbeddingRequest,
    EmbeddingResponse,
    QuestionAnalysisRequest,
    QuestionAnalysisResponse,
)
from app.services.ai_service import ai_service


router = APIRouter()


@router.post("/analyze", response_model=AIAnalysisResponse)
async def analyze_text(
    request: AIAnalysisRequest,
    current_user: User = Depends(get_current_user),
):
    """
    分析文本内容（题目）
    
    - **text**: 要分析的文本
    - **engine**: AI引擎选择 (openai, deepseek, auto)
    - **include_embedding**: 是否生成向量嵌入
    
    返回详细的分析结果
    """
    # 调用 AI 分析
    result = await ai_service.analyze_question(
        question_text=request.text,
        engine=request.engine
    )
    
    # 生成向量嵌入（如果需要）
    embedding = None
    if request.include_embedding:
        embedding = await ai_service.generate_embedding(request.text)
    
    return AIAnalysisResponse(
        subject=result.get("subject", "未知"),
        difficulty=result.get("difficulty", "未知"),
        question_type=result.get("question_type", "未知"),
        answer=result.get("answer", ""),
        key_points=result.get("key_points", []),
        summary=result.get("summary", ""),
        tags=result.get("tags", []),
        engine=result.get("engine", request.engine),
        embedding=embedding
    )


@router.post("/extract-knowledge", response_model=KnowledgePointsResponse)
async def extract_knowledge_points(
    request: KnowledgePointsRequest,
    current_user: User = Depends(get_current_user),
):
    """
    从内容中提取知识点
    
    - **content**: 内容文本
    - **engine**: AI引擎选择
    
    返回提取的知识点列表
    """
    knowledge_points = await ai_service.extract_knowledge_points(
        content=request.content,
        engine=request.engine
    )
    
    return KnowledgePointsResponse(
        knowledge_points=knowledge_points,
        engine=request.engine
    )


@router.post("/embedding", response_model=EmbeddingResponse)
async def generate_embedding(
    request: EmbeddingRequest,
    current_user: User = Depends(get_current_user),
):
    """
    生成文本的向量嵌入
    
    - **text**: 要生成嵌入的文本
    
    返回1536维的向量嵌入
    """
    embedding = await ai_service.generate_embedding(request.text)
    
    return EmbeddingResponse(
        embedding=embedding,
        dimension=len(embedding)
    )


@router.post("/analyze-question", response_model=QuestionAnalysisResponse)
async def analyze_question_from_file(
    request: QuestionAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    分析已上传并OCR识别的题目文件
    
    - **file_id**: 文件ID
    - **engine**: AI引擎选择
    - **create_node**: 是否自动创建记忆节点
    - **graph_id**: 目标知识图谱ID（如果创建节点）
    
    返回分析结果，并可选创建记忆节点
    """
    # 查询文件记录
    result = await db.execute(
        select(FileUpload).where(
            FileUpload.id == request.file_id,
            FileUpload.user_id == current_user.id
        )
    )
    file_upload = result.scalar_one_or_none()
    
    if not file_upload:
        raise HTTPException(status_code=404, detail="文件不存在")
    
    # 检查文件是否已完成 OCR
    if file_upload.status != "completed":
        raise HTTPException(status_code=400, detail="文件尚未完成 OCR 识别")
    
    # 获取 OCR 文本
    ocr_text = file_upload.processing_result.get("ocr_text", "")
    if not ocr_text:
        raise HTTPException(status_code=400, detail="文件没有 OCR 识别结果")
    
    # 调用 AI 分析
    analysis_result = await ai_service.analyze_question(
        question_text=ocr_text,
        engine=request.engine
    )
    
    # 生成向量嵌入（OpenAI 未配置时允许降级）
    embedding = None
    if ai_service.openai_configured:
        embedding = await ai_service.generate_embedding(ocr_text)
    
    # 创建记忆节点（如果需要）
    node_id = None
    if request.create_node:
        # 验证知识图谱
        if not request.graph_id:
            raise HTTPException(status_code=400, detail="创建节点需要指定 graph_id")
        
        graph_result = await db.execute(
            select(KnowledgeGraph).where(
                KnowledgeGraph.id == request.graph_id,
                KnowledgeGraph.user_id == current_user.id
            )
        )
        graph = graph_result.scalar_one_or_none()
        if not graph:
            raise HTTPException(status_code=404, detail="知识图谱不存在")
        
        # 创建记忆节点
        memory_node = MemoryNode(
            graph_id=request.graph_id,
            user_id=current_user.id,
            created_by=current_user.id,
            node_type="QUESTION",
            title=analysis_result.get("summary", "题目")[:100],
            summary=analysis_result.get("summary", ""),
            content_data={
                "question": ocr_text,
                "answer": analysis_result.get("answer", ""),
                "key_points": analysis_result.get("key_points", []),
                "difficulty": analysis_result.get("difficulty", "未知"),
                "question_type": analysis_result.get("question_type", "未知"),
                "file_id": str(file_upload.id),
                "file_url": file_upload.file_url,
            },
            content_embedding=embedding,
        )
        
        db.add(memory_node)
        await db.commit()
        await db.refresh(memory_node)
        
        node_id = memory_node.id
    
    return QuestionAnalysisResponse(
        file_id=file_upload.id,
        analysis=AIAnalysisResponse(
            subject=analysis_result.get("subject", "未知"),
            difficulty=analysis_result.get("difficulty", "未知"),
            question_type=analysis_result.get("question_type", "未知"),
            answer=analysis_result.get("answer", ""),
            key_points=analysis_result.get("key_points", []),
            summary=analysis_result.get("summary", ""),
            tags=analysis_result.get("tags", []),
            engine=analysis_result.get("engine", request.engine),
            embedding=embedding
        ),
        node_id=node_id
    )

