"""
OCR 识别相关的 API 端点
"""

import time
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import User, FileUpload
from app.schemas.file_upload import OCRRequest, OCRResponse
from app.services.ocr_service import ocr_service


router = APIRouter()


@router.post("/ocr", response_model=OCRResponse)
async def recognize_text(
    ocr_request: OCRRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    对上传的图片进行 OCR 识别
    
    - **file_id**: 文件ID
    - **ocr_engine**: OCR引擎选择 (baidu, tencent, auto)
    
    返回识别的文本和置信度
    """
    # 查询文件记录
    result = await db.execute(
        select(FileUpload).where(
            FileUpload.id == ocr_request.file_id,
            FileUpload.user_id == current_user.id
        )
    )
    file_upload = result.scalar_one_or_none()
    
    if not file_upload:
        raise HTTPException(status_code=404, detail="文件不存在")
    
    # 检查文件类型
    if not file_upload.mime_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="只支持图片文件的 OCR 识别")
    
    # 获取文件路径
    # 如果使用本地存储，从 file_url 解析路径
    if file_upload.file_url.startswith("/uploads/"):
        file_path = Path("uploads") / file_upload.file_url.replace("/uploads/", "")
    else:
        # 如果使用 OSS，需要先下载文件
        # TODO: 实现从 OSS 下载文件的逻辑
        raise HTTPException(status_code=501, detail="暂不支持 OSS 文件的 OCR 识别")
    
    # 检查文件是否存在
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="文件不存在于服务器")
    
    # 更新文件状态为处理中
    file_upload.status = "processing"
    await db.commit()
    
    try:
        # 执行 OCR 识别
        start_time = time.time()
        text, confidence, raw_result = await ocr_service.ocr_image(
            file_path,
            engine=ocr_request.ocr_engine
        )
        processing_time = time.time() - start_time
        
        # 更新文件记录
        file_upload.status = "completed"
        file_upload.processing_result = {
            "ocr_text": text,
            "confidence": confidence,
            "engine": raw_result.get("engine", ocr_request.ocr_engine),
            "processing_time": processing_time
        }
        await db.commit()
        
        return OCRResponse(
            file_id=file_upload.id,
            text=text,
            confidence=confidence,
            engine=raw_result.get("engine", ocr_request.ocr_engine),
            raw_result=raw_result.get("raw_result"),
            processing_time=processing_time
        )
    
    except Exception as e:
        # 更新文件状态为失败
        file_upload.status = "failed"
        file_upload.error_message = str(e)
        await db.commit()
        
        raise HTTPException(
            status_code=500,
            detail=f"OCR 识别失败: {str(e)}"
        )


@router.post("/ocr/math", response_model=OCRResponse)
async def recognize_math(
    ocr_request: OCRRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    对包含数学公式的图片进行 OCR 识别
    
    - **file_id**: 文件ID
    - **ocr_engine**: OCR引擎选择
    
    返回识别的文本（包含 LaTeX 格式的数学公式）
    """
    # 查询文件记录
    result = await db.execute(
        select(FileUpload).where(
            FileUpload.id == ocr_request.file_id,
            FileUpload.user_id == current_user.id
        )
    )
    file_upload = result.scalar_one_or_none()
    
    if not file_upload:
        raise HTTPException(status_code=404, detail="文件不存在")
    
    # 检查文件类型
    if not file_upload.mime_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="只支持图片文件的 OCR 识别")
    
    # 获取文件路径
    if file_upload.file_url.startswith("/uploads/"):
        file_path = Path("uploads") / file_upload.file_url.replace("/uploads/", "")
    else:
        raise HTTPException(status_code=501, detail="暂不支持 OSS 文件的 OCR 识别")
    
    # 检查文件是否存在
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="文件不存在于服务器")
    
    # 更新文件状态为处理中
    file_upload.status = "processing"
    await db.commit()
    
    try:
        # 执行数学公式 OCR 识别
        start_time = time.time()
        text, confidence, raw_result = await ocr_service.ocr_with_math(
            file_path,
            engine=ocr_request.ocr_engine
        )
        processing_time = time.time() - start_time
        
        # 更新文件记录
        file_upload.status = "completed"
        file_upload.processing_result = {
            "ocr_text": text,
            "confidence": confidence,
            "engine": raw_result.get("engine", ocr_request.ocr_engine),
            "processing_time": processing_time,
            "has_math": True
        }
        await db.commit()
        
        return OCRResponse(
            file_id=file_upload.id,
            text=text,
            confidence=confidence,
            engine=raw_result.get("engine", ocr_request.ocr_engine),
            raw_result=raw_result.get("raw_result"),
            processing_time=processing_time
        )
    
    except Exception as e:
        # 更新文件状态为失败
        file_upload.status = "failed"
        file_upload.error_message = str(e)
        await db.commit()
        
        raise HTTPException(
            status_code=500,
            detail=f"OCR 识别失败: {str(e)}"
        )

