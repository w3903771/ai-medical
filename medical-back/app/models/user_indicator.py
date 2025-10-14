from __future__ import annotations

from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import UniqueConstraint
from .base import IDMixin, TimestampMixin

# 用户-指标映射：别名、阈值与收藏


class UserIndicator(IDMixin, TimestampMixin, SQLModel, table=True):
    __table_args__ = (UniqueConstraint("user_id", "indicator_id"),)

    user_id: int = Field(foreign_key="user.id", index=True)  # 用户ID
    indicator_id: int = Field(foreign_key="indicator.id", index=True)  # 指标ID
    alias: Optional[str] = None  # 自定义别名
    threshold_min: Optional[float] = None  # 自定义阈值下限
    threshold_max: Optional[float] = None  # 自定义阈值上限
    favorite: bool = Field(default=False, index=True)  # 是否收藏