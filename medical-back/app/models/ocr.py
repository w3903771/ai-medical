from __future__ import annotations

from typing import Optional
from sqlmodel import SQLModel, Field
from .base import TimestampMixin, SoftDeleteMixin

# OCR 任务模型：记录文件OCR处理的异步任务


class OcrTask(TimestampMixin, SoftDeleteMixin, SQLModel, table=True):
    id: str = Field(primary_key=True)  # 任务ID（如 ocr-123）
    user_id: Optional[int] = Field(default=None, foreign_key="user.id", index=True)  # 用户ID（可选）
    admission_id: Optional[int] = Field(default=None, foreign_key="admission.id", index=True)  # 关联住院记录
    file_id: int = Field(foreign_key="admissionfile.id", index=True)  # 关联文件ID
    status: str = Field(default="queued", index=True)  # 状态：queued|running|done|failed
    language: Optional[str] = None  # 语言：zh|en 等
    engine: Optional[str] = None  # OCR 引擎：paddleocr 等