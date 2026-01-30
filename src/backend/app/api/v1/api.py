"""
API v1 路由聚合
"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, health

api_router = APIRouter()

# 包含各个端点路由
api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# 后续添加更多路由
# api_router.include_router(users.router, prefix="/users", tags=["Users"])
# api_router.include_router(graphs.router, prefix="/graphs", tags=["Knowledge Graphs"])

