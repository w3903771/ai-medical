from __future__ import annotations

from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import UniqueConstraint, Index
from .base import IDMixin, TimestampMixin, SoftDeleteMixin

# 知识库相关模型：文档与分块


class KnowledgeDoc(IDMixin, TimestampMixin, SoftDeleteMixin, SQLModel, table=True):
    __table_args__ = (
        Index("idx_knowledgedoc_source", "source_type"),
    )
    title: str = Field(index=True)  # 文档标题
    source_type: str = Field(default="pdf", index=True)  # 来源类型：pdf|url
    url: Optional[str] = None  # 若来源为 URL
    oss_key: Optional[str] = None  # 若来源为本地/云存储路径
    meta_json: Optional[str] = None  # 元数据（JSON 字符串）
    uploaded_at: datetime = Field(default_factory=datetime.utcnow, index=True, nullable=False)  # 上传/引入时间（非空，默认当前 UTC）

    chunks: list["KnowledgeChunk"] = Relationship(back_populates="doc")


class KnowledgeChunk(IDMixin, TimestampMixin, SoftDeleteMixin, SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("doc_id", "chunk_index"),
    )
    
    doc_id: int = Field(foreign_key="knowledgedoc.id", index=True)  # 关联文档ID
    chunk_index: int = Field(index=True)  # 分块序号
    chunk_text: str  # 分块文本
    embedding_ref: Optional[str] = None  # 向量或引用（JSON 字符串）

    doc: Optional[KnowledgeDoc] = Relationship(back_populates="chunks")