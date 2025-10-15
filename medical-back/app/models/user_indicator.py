from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import UniqueConstraint, Index
from .base import IDMixin, TimestampMixin

# 用户-指标映射：别名、阈值与收藏


class UserIndicator(IDMixin, TimestampMixin, SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("user_id", "indicator_id"),
        Index("idx_userindicator_user_favorite", "user_id", "favorite"),
    )

    user_id: int = Field(foreign_key="user.id", index=True, nullable=False)  # 用户ID
    indicator_id: int = Field(foreign_key="indicator.id", index=True, nullable=False)  # 指标ID
    alias: Optional[str] = None  # 自定义别名
    threshold_min: Optional[float] = None  # 自定义阈值下限
    threshold_max: Optional[float] = None  # 自定义阈值上限
    favorite: bool = Field(default=False, index=True)  # 是否收藏

    # 说明：用户关注（favorite）用于前端筛选“我关注的指标”；不再支持用户自建分类