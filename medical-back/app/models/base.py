from __future__ import annotations

from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field

# 通用混入（Mixin）定义：统一 ID、时间戳、软删除字段


class TimestampMixin(SQLModel):
    """时间戳字段：创建时间/更新时间"""
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: Optional[datetime] = Field(default=None, nullable=True)


class SoftDeleteMixin(SQLModel):
    """软删除字段：删除时间，非空表示记录已被软删除"""
    deleted_at: Optional[datetime] = Field(default=None, nullable=True)


class IDMixin(SQLModel):
    """主键 ID 字段"""
    id: Optional[int] = Field(default=None, primary_key=True)