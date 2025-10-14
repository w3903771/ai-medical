from __future__ import annotations

from typing import Optional
from datetime import datetime, date
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import UniqueConstraint, Index
from .base import IDMixin, TimestampMixin, SoftDeleteMixin
from .indicator_detail import IndicatorDetail

# 指标分类与指标模型


class Category(IDMixin, TimestampMixin, SoftDeleteMixin, SQLModel, table=True):
    name: str = Field(index=True, unique=True, nullable=False)  # 分类名称（唯一）
    description: Optional[str] = None  # 分类描述

    indicators: list["Indicator"] = Relationship(back_populates="category")


class Indicator(IDMixin, TimestampMixin, SoftDeleteMixin, SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("owner_user_id", "name_cn"),
    )
    owner_user_id: Optional[int] = Field(default=None, foreign_key="user.id", index=True)  # 指标所有者用户ID
    name_cn: str = Field(index=True)  # 指标中文名
    name_en: Optional[str] = Field(default=None, index=True)  # 指标英文名（可选）
    unit: str = Field(index=False, nullable=False)  # 单位（必填）
    category_id: Optional[int] = Field(default=None, foreign_key="category.id", index=True)  # 分类外键
    reference_min: Optional[float] = Field(default=None)  # 参考下限
    reference_max: Optional[float] = Field(default=None)  # 参考上限
    is_builtin: bool = Field(default=False, index=True)  # 是否内置指标
    
    category: Optional[Category] = Relationship(back_populates="indicators")
    records: list["IndicatorRecord"] = Relationship(back_populates="indicator")
    detail: Optional[IndicatorDetail] = Relationship(back_populates="indicator", sa_relationship_kwargs={"uselist": False})


class IndicatorRecord(IDMixin, TimestampMixin, SoftDeleteMixin, SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("user_id", "indicator_id", "measured_at", "source"),
        Index("idx_indicatorrecord_indicator_measured", "indicator_id", "measured_at"),
        Index("idx_indicatorrecord_user_measured", "user_id", "measured_at"),
        Index("idx_indicatorrecord_file", "admission_file_id"),
    )
    indicator_id: int = Field(foreign_key="indicator.id", index=True, nullable=False)  # 指标ID
    user_id: int = Field(foreign_key="user.id", index=True, nullable=False)  # 用户ID
    measured_at: date = Field(index=True, nullable=False)  # 测量日期
    value: float = Field(index=False, nullable=False)  # 指标值
    unit: str = Field(index=False, nullable=False)  # 单位（必填，避免跨表默认引用）
    ref_low: Optional[float] = Field(default=None, index=False)  # 参考下限（记录级覆盖）
    ref_high: Optional[float] = Field(default=None, index=False)  # 参考上限（记录级覆盖）
    ref_text: Optional[str] = Field(default=None, index=False)  # 参考文本（如“阴性/阳性”）
    source: Optional[str] = Field(default="manual")  # 数据来源（默认 manual）
    note: Optional[str] = None  # 备注
    admission_file_id: Optional[int] = Field(default=None, foreign_key="admissionfile.id", index=True)  # 关联住院文件ID

    indicator: Optional[Indicator] = Relationship(back_populates="records")