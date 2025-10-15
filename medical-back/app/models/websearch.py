from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Index
from .base import TimestampMixin

# 网络搜索查询模型：记录搜索参数与结果快照


class WebSearchQuery(TimestampMixin, SQLModel, table=True):
    __table_args__ = (
        Index("idx_websearchquery_user_created", "user_id", "created_at"),
    )

    id: str = Field(primary_key=True)  # 查询ID
    user_id: int = Field(foreign_key="user.id", index=True)  # 用户ID
    query: str  # 查询文本
    provider: Optional[str] = None  # 提供方：bing|google|custom
    results_json: Optional[str] = None  # 结果（JSON 字符串）