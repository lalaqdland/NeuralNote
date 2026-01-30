"""
FastAPI 应用主入口
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.api import api_router
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """应用生命周期管理"""
    # 启动时执行
    print("🚀 NeuralNote API 启动中...")
    print(f"📦 版本: {settings.APP_VERSION}")
    print(f"🔧 调试模式: {settings.DEBUG}")
    print(f"🗄️  数据库: {settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}")
    
    yield
    
    # 关闭时执行
    print("👋 NeuralNote API 关闭中...")


# 创建 FastAPI 应用实例
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="NeuralNote - 智能学习管理工具 API",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 根路由
@app.get("/", tags=["Root"])
async def root():
    """根路由 - API 欢迎信息"""
    return {
        "message": "Welcome to NeuralNote API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
    }


# 健康检查路由
@app.get("/health", tags=["Health"])
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


# 数据库健康检查
@app.get("/health/db", tags=["Health"])
async def database_health_check():
    """数据库健康检查接口"""
    try:
        from sqlalchemy import text
        from app.core.database import async_engine
        
        async with async_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        
        return {
            "status": "healthy",
            "database": "connected",
            "host": settings.POSTGRES_HOST,
            "port": settings.POSTGRES_PORT,
            "database": settings.POSTGRES_DB,
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e),
            },
        )


# 包含 API 路由
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )

