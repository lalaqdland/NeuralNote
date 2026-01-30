"""
通用响应 Schemas
"""

from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel, Field

DataT = TypeVar("DataT")


class Response(BaseModel, Generic[DataT]):
    """统一响应格式"""
    
    code: int = Field(default=0, description="状态码，0表示成功")
    message: str = Field(default="success", description="响应消息")
    data: Optional[DataT] = Field(default=None, description="响应数据")


class ErrorResponse(BaseModel):
    """错误响应"""
    
    code: int = Field(..., description="错误码")
    message: str = Field(..., description="错误消息")
    detail: Optional[Any] = Field(None, description="错误详情")


class PaginationParams(BaseModel):
    """分页参数"""
    
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=20, ge=1, le=100, description="每页数量")


class PaginatedResponse(BaseModel, Generic[DataT]):
    """分页响应"""
    
    items: list[DataT] = Field(..., description="数据列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
    total_pages: int = Field(..., description="总页数")
    
    @classmethod
    def create(
        cls,
        items: list[DataT],
        total: int,
        page: int,
        page_size: int
    ) -> "PaginatedResponse[DataT]":
        """创建分页响应"""
        total_pages = (total + page_size - 1) // page_size
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )

