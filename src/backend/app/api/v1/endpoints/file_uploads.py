"""
文件上传相关的 API 端点
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Query, Request
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import User, FileUpload, KnowledgeGraph
from app.schemas.file_upload import (
    FileUploadResponse,
    FileUploadInfo,
    UploadResponse,
    FileUploadUpdate,
)
from app.schemas.common import PaginatedResponse
from app.services.file_storage import file_storage_service


router = APIRouter()


@router.post("/upload", response_model=UploadResponse, status_code=201)
async def upload_file(
    file: UploadFile = File(..., description="上传的文件"),
    graph_id: Optional[UUID] = Query(None, description="所属知识图谱ID"),
    request: Request = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    上传文件（图片）
    
    - **file**: 上传的文件（支持 JPEG, PNG）
    - **graph_id**: 可选，关联到特定知识图谱
    
    返回文件信息和访问 URL
    """
    # 验证知识图谱是否存在（如果提供了）
    if graph_id:
        result = await db.execute(
            select(KnowledgeGraph).where(
                KnowledgeGraph.id == graph_id,
                KnowledgeGraph.user_id == current_user.id
            )
        )
        graph = result.scalar_one_or_none()
        if not graph:
            raise HTTPException(status_code=404, detail="知识图谱不存在")
    
    # 保存文件
    stored_filename, file_url, file_size = await file_storage_service.save_file(
        file, current_user.id
    )
    
    # 获取客户端 IP
    client_ip = None
    if request:
        client_ip = request.client.host if request.client else None
    
    # 创建文件上传记录
    file_upload = FileUpload(
        user_id=current_user.id,
        graph_id=graph_id,
        original_filename=file.filename or "unknown",
        stored_filename=stored_filename,
        file_url=file_url,
        file_size=file_size,
        mime_type=file.content_type or "application/octet-stream",
        status="pending",
        uploaded_ip=client_ip,
    )
    
    db.add(file_upload)
    await db.commit()
    await db.refresh(file_upload)
    
    return UploadResponse(
        file_id=file_upload.id,
        file_url=file_upload.file_url,
        original_filename=file_upload.original_filename,
        file_size=file_upload.file_size,
        mime_type=file_upload.mime_type,
        message="文件上传成功"
    )


@router.get("/", response_model=PaginatedResponse[FileUploadInfo])
async def list_files(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    graph_id: Optional[UUID] = Query(None, description="筛选：知识图谱ID"),
    status: Optional[str] = Query(None, description="筛选：处理状态"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取文件上传列表（分页）
    
    - **page**: 页码（从1开始）
    - **page_size**: 每页数量（1-100）
    - **graph_id**: 可选，筛选特定图谱的文件
    - **status**: 可选，筛选特定状态的文件
    """
    # 构建查询
    query = select(FileUpload).where(FileUpload.user_id == current_user.id)
    
    # 应用筛选
    if graph_id:
        query = query.where(FileUpload.graph_id == graph_id)
    if status:
        query = query.where(FileUpload.status == status)
    
    # 排序
    query = query.order_by(FileUpload.created_at.desc())
    
    # 获取总数
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # 分页
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    
    # 执行查询
    result = await db.execute(query)
    files = result.scalars().all()
    
    return PaginatedResponse(
        items=[FileUploadInfo.model_validate(f) for f in files],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.get("/{file_id}", response_model=FileUploadResponse)
async def get_file(
    file_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取文件详情
    
    - **file_id**: 文件ID
    """
    result = await db.execute(
        select(FileUpload).where(
            FileUpload.id == file_id,
            FileUpload.user_id == current_user.id
        )
    )
    file_upload = result.scalar_one_or_none()
    
    if not file_upload:
        raise HTTPException(status_code=404, detail="文件不存在")
    
    return FileUploadResponse.model_validate(file_upload)


@router.patch("/{file_id}", response_model=FileUploadResponse)
async def update_file(
    file_id: UUID,
    file_update: FileUploadUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    更新文件记录
    
    - **file_id**: 文件ID
    - **file_update**: 更新的字段
    """
    result = await db.execute(
        select(FileUpload).where(
            FileUpload.id == file_id,
            FileUpload.user_id == current_user.id
        )
    )
    file_upload = result.scalar_one_or_none()
    
    if not file_upload:
        raise HTTPException(status_code=404, detail="文件不存在")
    
    # 更新字段
    update_data = file_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(file_upload, field, value)
    
    await db.commit()
    await db.refresh(file_upload)
    
    return FileUploadResponse.model_validate(file_upload)


@router.delete("/{file_id}", status_code=204)
async def delete_file(
    file_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    删除文件
    
    - **file_id**: 文件ID
    
    会同时删除数据库记录和存储的文件
    """
    result = await db.execute(
        select(FileUpload).where(
            FileUpload.id == file_id,
            FileUpload.user_id == current_user.id
        )
    )
    file_upload = result.scalar_one_or_none()
    
    if not file_upload:
        raise HTTPException(status_code=404, detail="文件不存在")
    
    # 删除存储的文件
    file_storage_service.delete_file(file_upload.stored_filename)
    
    # 删除数据库记录
    await db.delete(file_upload)
    await db.commit()
    
    return None

