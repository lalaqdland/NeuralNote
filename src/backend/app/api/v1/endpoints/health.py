"""
健康检查端点
"""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db

router = APIRouter()


@router.get("/ping")
async def ping():
    """简单的 ping 检查"""
    return {"message": "pong"}


@router.get("/status")
async def status():
    """服务状态检查"""
    return {
        "status": "running",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": "development" if settings.DEBUG else "production",
    }


@router.get("/database")
async def database_check(db: AsyncSession = Depends(get_db)):
    """数据库连接检查"""
    try:
        # 执行简单查询
        result = await db.execute(text("SELECT version()"))
        version = result.scalar()
        
        # 检查表是否存在
        result = await db.execute(
            text(
                "SELECT COUNT(*) FROM information_schema.tables "
                "WHERE table_schema = 'public'"
            )
        )
        table_count = result.scalar()
        
        return {
            "status": "connected",
            "database": settings.POSTGRES_DB,
            "host": settings.POSTGRES_HOST,
            "port": settings.POSTGRES_PORT,
            "version": version,
            "table_count": table_count,
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
        }


@router.get("/redis")
async def redis_check():
    """Redis 连接检查"""
    try:
        import redis.asyncio as redis
        
        client = redis.from_url(settings.redis_url)
        await client.ping()
        await client.close()
        
        return {
            "status": "connected",
            "host": settings.REDIS_HOST,
            "port": settings.REDIS_PORT,
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
        }

