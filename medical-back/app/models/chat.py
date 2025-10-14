from __future__ import annotations

from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Index
from .base import IDMixin, TimestampMixin, SoftDeleteMixin

# 聊天相关模型：会话与消息


class ChatSession(IDMixin, TimestampMixin, SoftDeleteMixin, SQLModel, table=True):
    __table_args__ = (
        Index("idx_chatsession_user_created", "user_id", "created_at"),
    )
    
    user_id: int = Field(foreign_key="user.id", index=True)  # 用户ID
    title: Optional[str] = None  # 会话标题（可选）

    messages: list["ChatMessage"] = Relationship(back_populates="session")


class ChatMessage(IDMixin, TimestampMixin, SoftDeleteMixin, SQLModel, table=True):
    __table_args__ = (
        Index("idx_chatmessage_session_created", "session_id", "created_at"),
    )

    session_id: int = Field(foreign_key="chatsession.id", index=True)  # 会话ID
    role: str = Field(index=True)  # 角色：user|assistant|tool
    content: str  # 消息内容
    tool_calls_json: Optional[str] = None  # 工具调用信息（JSON 字符串）
    related_ids: Optional[str] = None  # 关联实体ID（JSON 字符串）

    session: Optional[ChatSession] = Relationship(back_populates="messages")