from __future__ import annotations

from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Index
from .base import IDMixin, TimestampMixin

# 系统与审计日志模型


class SystemLog(IDMixin, TimestampMixin, SQLModel, table=True):
    level: str = Field(index=True)  # 日志级别：info|warn|error
    message: str  # 日志消息
    context_json: Optional[str] = None  # 上下文（JSON 字符串）


class AuditLog(IDMixin, TimestampMixin, SQLModel, table=True):
    __table_args__ = (
        Index("idx_auditlog_entity_entityid", "entity", "entity_id"),
        Index("idx_auditlog_user_created", "user_id", "created_at"),
    )

    user_id: Optional[int] = Field(default=None, foreign_key="user.id", index=True)  # 用户ID
    action: str = Field(index=True)  # 动作
    entity: str = Field(index=True)  # 实体类型（Indicator/Admission/...）
    entity_id: Optional[str] = Field(default=None, index=True)  # 实体ID（字符串或数字）
    payload_json: Optional[str] = None  # 载荷（JSON 字符串）