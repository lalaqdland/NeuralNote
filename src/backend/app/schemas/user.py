"""
用户相关的 Pydantic Schemas
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator


# ==================== 用户注册 ====================

class UserRegister(BaseModel):
    """用户注册请求"""
    
    email: EmailStr = Field(..., description="邮箱地址")
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=100, description="密码")
    phone: Optional[str] = Field(None, max_length=20, description="手机号码")
    
    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        """验证用户名只包含字母、数字、下划线"""
        if not v.replace("_", "").isalnum():
            raise ValueError("用户名只能包含字母、数字和下划线")
        return v
    
    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        """验证密码强度"""
        if len(v) < 6:
            raise ValueError("密码长度至少为6位")
        return v


# ==================== 用户登录 ====================

class UserLogin(BaseModel):
    """用户登录请求"""
    
    email: EmailStr = Field(..., description="邮箱地址")
    password: str = Field(..., description="密码")


class TokenResponse(BaseModel):
    """Token 响应"""
    
    access_token: str = Field(..., description="访问令牌")
    refresh_token: str = Field(..., description="刷新令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    expires_in: int = Field(..., description="过期时间（秒）")


class RefreshTokenRequest(BaseModel):
    """刷新 Token 请求"""
    
    refresh_token: str = Field(..., description="刷新令牌")


# ==================== 用户信息 ====================

class UserBase(BaseModel):
    """用户基础信息"""
    
    email: EmailStr
    username: str
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    timezone: str = "Asia/Shanghai"
    language: str = "zh-CN"
    subscription_plan: str = "free"


class UserResponse(UserBase):
    """用户响应（公开信息）"""
    
    id: UUID
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}


class UserDetailResponse(UserResponse):
    """用户详细信息响应（包含订阅信息）"""
    
    subscription_expires_at: Optional[datetime] = None
    updated_at: datetime
    
    model_config = {"from_attributes": True}


# ==================== 用户更新 ====================

class UserUpdate(BaseModel):
    """用户信息更新请求"""
    
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    phone: Optional[str] = Field(None, max_length=20)
    avatar_url: Optional[str] = Field(None, max_length=500)
    timezone: Optional[str] = Field(None, max_length=50)
    language: Optional[str] = Field(None, max_length=10)
    
    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v: Optional[str]) -> Optional[str]:
        """验证用户名只包含字母、数字、下划线"""
        if v is not None and not v.replace("_", "").isalnum():
            raise ValueError("用户名只能包含字母、数字和下划线")
        return v


class PasswordChange(BaseModel):
    """修改密码请求"""
    
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., min_length=6, max_length=100, description="新密码")
    
    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        """验证密码强度"""
        if len(v) < 6:
            raise ValueError("密码长度至少为6位")
        return v


# ==================== 邮箱验证 ====================

class EmailVerificationRequest(BaseModel):
    """邮箱验证请求"""
    
    token: str = Field(..., description="验证令牌")


class PasswordResetRequest(BaseModel):
    """密码重置请求"""
    
    email: EmailStr = Field(..., description="邮箱地址")


class PasswordResetConfirm(BaseModel):
    """密码重置确认"""
    
    token: str = Field(..., description="重置令牌")
    new_password: str = Field(..., min_length=6, max_length=100, description="新密码")
    
    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        """验证密码强度"""
        if len(v) < 6:
            raise ValueError("密码长度至少为6位")
        return v

