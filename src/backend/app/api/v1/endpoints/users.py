"""
用户管理相关的 API 端点
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.user import UserDetailResponse, UserUpdate

router = APIRouter()


@router.get("/me", response_model=UserDetailResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """
    获取当前用户信息
    
    需要提供有效的访问令牌
    """
    return current_user


@router.put("/me", response_model=UserDetailResponse)
async def update_current_user_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    更新当前用户信息
    
    - **username**: 用户名（可选）
    - **phone**: 手机号码（可选）
    - **avatar_url**: 头像URL（可选）
    - **timezone**: 时区（可选）
    - **language**: 语言（可选）
    """
    try:
        # 检查用户名是否已被使用（如果要更新用户名）
        if user_data.username and user_data.username != current_user.username:
            result = await db.execute(
                select(User).where(User.username == user_data.username)
            )
            if result.scalar_one_or_none() is not None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="该用户名已被使用"
                )
        
        # 检查手机号是否已被使用（如果要更新手机号）
        if user_data.phone and user_data.phone != current_user.phone:
            result = await db.execute(
                select(User).where(User.phone == user_data.phone)
            )
            if result.scalar_one_or_none() is not None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="该手机号已被使用"
                )
        
        # 更新字段
        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(current_user, field, value)
        
        await db.commit()
        await db.refresh(current_user)
        
        return current_user
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新用户信息失败: {str(e)}"
        )


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_current_user_account(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    删除当前用户账号
    
    注意：此操作不可逆，会删除所有相关数据
    """
    try:
        # 删除用户（级联删除所有相关数据）
        await db.delete(current_user)
        await db.commit()
        
        return None
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除用户账号失败: {str(e)}"
        )

