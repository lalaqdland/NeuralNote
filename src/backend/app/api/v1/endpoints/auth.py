"""
用户认证相关的 API 端点
"""

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
    verify_token,
)
from app.models.user import User
from app.schemas.user import (
    PasswordChange,
    RefreshTokenRequest,
    TokenResponse,
    UserDetailResponse,
    UserLogin,
    UserRegister,
    UserResponse,
)

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db)
):
    """
    用户注册
    
    - **email**: 邮箱地址（必填，唯一）
    - **username**: 用户名（必填，唯一，3-50字符）
    - **password**: 密码（必填，至少6位）
    - **phone**: 手机号码（可选）
    """
    try:
        # 检查邮箱是否已存在
        result = await db.execute(
            select(User).where(User.email == user_data.email)
        )
        if result.scalar_one_or_none() is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该邮箱已被注册"
            )
        
        # 检查用户名是否已存在
        result = await db.execute(
            select(User).where(User.username == user_data.username)
        )
        if result.scalar_one_or_none() is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该用户名已被使用"
            )
        
        # 检查手机号是否已存在（如果提供）
        if user_data.phone:
            result = await db.execute(
                select(User).where(User.phone == user_data.phone)
            )
            if result.scalar_one_or_none() is not None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="该手机号已被注册"
                )
        
        # 创建新用户
        new_user = User(
            email=user_data.email,
            username=user_data.username,
            password_hash=get_password_hash(user_data.password),
            phone=user_data.phone,
            is_active=True,
            is_verified=False,  # 需要邮箱验证
        )
        
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        
        # TODO: 发送验证邮件
        
        return new_user
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        print(f"注册错误: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"注册失败: {str(e)}"
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    """
    用户登录
    
    - **email**: 邮箱地址
    - **password**: 密码
    
    返回访问令牌和刷新令牌
    """
    # 查询用户
    result = await db.execute(
        select(User).where(User.email == login_data.email)
    )
    user = result.scalar_one_or_none()
    
    # 验证用户和密码
    if user is None or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 检查用户是否激活
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账号已被禁用，请联系管理员"
        )
    
    # 更新最后登录时间
    user.last_login_at = datetime.utcnow()
    await db.commit()
    
    # 生成 Token
    access_token = create_access_token(subject=str(user.id))
    refresh_token = create_refresh_token(subject=str(user.id))
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    """
    刷新访问令牌
    
    使用刷新令牌获取新的访问令牌
    """
    # 验证刷新令牌
    user_id_str = verify_token(refresh_data.refresh_token, token_type="refresh")
    
    if user_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的刷新令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 查询用户
    from uuid import UUID
    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的用户ID"
        )
    
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在"
        )
    
    # 检查用户是否激活
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账号已被禁用"
        )
    
    # 生成新的 Token
    access_token = create_access_token(subject=str(user.id))
    new_refresh_token = create_refresh_token(subject=str(user.id))
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.get("/me", response_model=UserDetailResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    获取当前登录用户信息
    
    需要提供有效的访问令牌
    """
    return current_user


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    修改密码
    
    需要提供旧密码和新密码
    """
    # 验证旧密码
    if not verify_password(password_data.old_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="旧密码错误"
        )
    
    # 检查新密码是否与旧密码相同
    if password_data.old_password == password_data.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="新密码不能与旧密码相同"
        )
    
    # 更新密码
    current_user.password_hash = get_password_hash(password_data.new_password)
    await db.commit()
    
    return {"message": "密码修改成功"}


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    用户登出
    
    注意：JWT Token 是无状态的，实际的登出需要在客户端删除 Token
    这个接口主要用于记录登出日志或执行其他清理操作
    """
    # TODO: 可以在这里记录登出日志
    # TODO: 如果使用 Redis 存储 Token 黑名单，可以在这里将 Token 加入黑名单
    
    return {"message": "登出成功"}

