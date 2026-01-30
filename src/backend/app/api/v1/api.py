"""
API v1 路由聚合
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    health,
    knowledge_graphs,
    memory_nodes,
    users,
    file_uploads,
    ocr,
    ai_analysis,
)

api_router = APIRouter()

# 包含各个端点路由
api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(knowledge_graphs.router, prefix="/graphs", tags=["Knowledge Graphs"])
api_router.include_router(memory_nodes.router, prefix="/nodes", tags=["Memory Nodes"])
api_router.include_router(file_uploads.router, prefix="/files", tags=["File Uploads"])
api_router.include_router(ocr.router, prefix="/ocr", tags=["OCR"])
api_router.include_router(ai_analysis.router, prefix="/ai", tags=["AI Analysis"])

