from __future__ import annotations

from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field
from .base import IDMixin, TimestampMixin, SoftDeleteMixin

# 用户模型：包含用户名、密码哈希、邮箱、角色与最近登录时间


class User(IDMixin, TimestampMixin, SoftDeleteMixin, SQLModel, table=True):
    username: str = Field(index=True, unique=True)  # 用户名（唯一）
    password_hash: str  # 密码哈希
    email: Optional[str] = Field(default=None, index=True)  # 邮箱
    role: Optional[str] = Field(default="user", index=True)  # 角色（默认 user）
    last_login: Optional[datetime] = None  # 最近登录时间