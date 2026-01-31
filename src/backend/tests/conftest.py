"""
pytest 配置文件
提供测试所需的 fixtures 和配置
"""

import asyncio
from typing import AsyncGenerator, Generator
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from main import app
from app.core.config import settings
from app.core.database import Base, get_db
from app.models import User, KnowledgeGraph, MemoryNode


# 测试数据库 URL（使用独立的测试数据库）
TEST_DATABASE_URL = (
    f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
    f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/neuralnote_test"
)


# 创建测试数据库引擎
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=NullPool,  # 测试时不使用连接池
    echo=False,
)

# 创建测试会话工厂
TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    创建测试数据库会话
    每个测试函数都会创建新的会话，测试结束后回滚
    """
    # 创建所有表
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # 创建会话
    session = TestSessionLocal()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()
    
    # 清理所有表
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    创建测试客户端
    覆盖应用的数据库依赖
    """
    async def override_get_db():
        try:
            yield db_session
        finally:
            pass  # 不要关闭会话，因为它由 db_session fixture 管理
    
    app.dependency_overrides[get_db] = override_get_db
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """创建测试用户"""
    from app.core.security import get_password_hash
    
    user = User(
        email="test@example.com",
        username="testuser",
        password_hash=get_password_hash("password123"),
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def auth_headers(test_user: User) -> dict:
    """获取认证请求头（直接生成token，不通过登录接口）"""
    from app.core.security import create_access_token
    
    # 直接生成 token（传入用户ID字符串）
    token = create_access_token(str(test_user.id))
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def test_graph(db_session: AsyncSession, test_user: User) -> KnowledgeGraph:
    """创建测试知识图谱"""
    graph = KnowledgeGraph(
        user_id=test_user.id,
        name="测试图谱",
        description="这是一个测试图谱",
        subject="math",
        is_public=False,
    )
    db_session.add(graph)
    await db_session.commit()
    await db_session.refresh(graph)
    return graph


@pytest.fixture
async def test_node(db_session: AsyncSession, test_graph: KnowledgeGraph, test_user: User) -> MemoryNode:
    """创建测试记忆节点"""
    node = MemoryNode(
        graph_id=test_graph.id,
        user_id=test_user.id,
        node_type="CONCEPT",
        title="测试节点",
        summary="这是一个测试节点",
        content_data={"test": "data"},
    )
    db_session.add(node)
    await db_session.commit()
    await db_session.refresh(node)
    return node


# 测试数据
TEST_USER_DATA = {
    "email": "newuser@example.com",
    "username": "newuser",
    "password": "password123"
}

TEST_GRAPH_DATA = {
    "name": "高等数学",
    "description": "高等数学知识图谱",
    "subject": "math",
    "is_public": False
}

TEST_NODE_DATA = {
    "node_type": "CONCEPT",
    "title": "导数的定义",
    "summary": "函数在某一点的导数是该点切线的斜率",
    "content_data": {
        "definition": "导数是函数变化率的度量",
        "formula": "f'(x) = lim(h->0) [f(x+h) - f(x)] / h"
    }
}
