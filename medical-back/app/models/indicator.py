from __future__ import annotations

from typing import Optional
from datetime import datetime, date
from sqlmodel import SQLModel, Field, Relationship
from .base import IDMixin, TimestampMixin, SoftDeleteMixin

# 指标模型：定义各类医学指标的基础信息


class Indicator(IDMixin, TimestampMixin, SoftDeleteMixin, SQLModel, table=True):
    code: Optional[str] = Field(default=None, index=True)  # 指标编码（可选）
    owner_user_id: Optional[int] = Field(default=None, foreign_key="user.id", index=True)  # 指标所有者用户ID
    name_cn: str = Field(index=True)  # 指标中文名
    name_en: Optional[str] = Field(default=None, index=True)  # 指标英文名（可选）
    unit: str  # 单位（必填）
    category: Optional[str] = Field(default=None, index=True)  # 类别（例如生命体征/检验等）
    reference_min: Optional[float] = Field(default=None)  # 参考下限
    reference_max: Optional[float] = Field(default=None)  # 参考上限
    is_builtin: bool = Field(default=False, index=True)  # 是否内置指标
    records: list["IndicatorRecord"] = Relationship(back_populates="indicator")


class IndicatorRecord(IDMixin, TimestampMixin, SoftDeleteMixin, SQLModel, table=True):
    indicator_id: int = Field(foreign_key="indicator.id", index=True)  # 指标ID
    user_id: int = Field(foreign_key="user.id", index=True)  # 用户ID
    measured_at: date = Field(index=True)  # 测量日期
    value: float  # 指标值
    unit: str  # 单位（可与指标基础信息一致）
    ref_low: Optional[float] = None  # 参考下限（记录级覆盖）
    ref_high: Optional[float] = None  # 参考上限（记录级覆盖）
    ref_text: Optional[str] = None  # 参考文本（如“阴性/阳性”）
    source: Optional[str] = Field(default="manual")  # 数据来源（默认 manual）
    note: Optional[str] = None  # 备注
    admission_file_id: Optional[int] = Field(default=None, foreign_key="admissionfile.id", index=True)  # 关联住院文件ID

    indicator: Optional[Indicator] = Relationship(back_populates="records")