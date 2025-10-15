from typing import Optional
from datetime import datetime, date
from sqlmodel import SQLModel, Field
from .base import IDMixin, TimestampMixin, SoftDeleteMixin

# 用户模型：包含用户名、密码哈希、邮箱、角色与最近登录时间


class User(IDMixin, TimestampMixin, SoftDeleteMixin, SQLModel, table=True):
    username: str = Field(index=True, unique=True, nullable=False)  # 用户名（唯一）
    name: str = Field(index=False, nullable=False)  # 姓名
    password_hash: str = Field(nullable=False)  # 密码哈希
    email: Optional[str] = Field(default=None, index=True, unique=True)  # 邮箱
    role: str = Field(default="user", index=True, nullable=False)  # 角色（默认 user）
    birth_date: Optional[date] = Field(default=None)  # 生日（YYYY-MM-DD）
    last_login: Optional[datetime] = Field(default=None)  # 最近登录时间
