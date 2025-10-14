from __future__ import annotations

from typing import Optional
from sqlmodel import SQLModel, Field
from .base import TimestampMixin, SoftDeleteMixin

# 导出任务模型：异步导出指标/住院/用药等数据


class ExportTask(TimestampMixin, SoftDeleteMixin, SQLModel, table=True):
    id: str = Field(primary_key=True)  # 任务ID（如 exp-1）
    user_id: int = Field(foreign_key="user.id", index=True)  # 用户ID
    format: str = Field(index=True)  # 导出格式：csv|json
    scope: str = Field(index=True)  # 导出范围：indicators|admissions|medications|all
    filters_json: Optional[str] = None  # 过滤条件（JSON 字符串）
    status: str = Field(default="queued", index=True)  # 状态：queued|running|done|failed
    download_url: Optional[str] = None  # 下载链接（完成后）