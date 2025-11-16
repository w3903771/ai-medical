from typing import Optional
from datetime import datetime, date
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy.orm import Mapped
from sqlalchemy import UniqueConstraint, Index
from .base import IDMixin, TimestampMixin, SoftDeleteMixin

# 指标分类与指标模型


class Category(IDMixin, TimestampMixin, SoftDeleteMixin, SQLModel, table=True):
    name: str = Field(index=True, unique=True, nullable=False)  # 分类名称（唯一）
    description: Optional[str] = None  # 分类描述

    indicators: list["Indicator"] = Relationship(
        back_populates="categories",
        link_model=IndicatorCategoryLink
    )


class Indicator(IDMixin, TimestampMixin, SoftDeleteMixin, SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("owner_user_id", "name_cn"),
    )

    owner_user_id: Optional[int] = Field(default=None, foreign_key="user.id", index=True)
    name_cn: str = Field(nullable=False, index=True)
    name_en: Optional[str] = Field(default=None, index=True)
    unit: str = Field(index=False, nullable=False)
    type: str = Field(default="numeric", index=True, description="指标类型：numeric|text")
    reference_min: Optional[float] = Field(default=None)
    reference_max: Optional[float] = Field(default=None)
    is_builtin: bool = Field(default=False, index=True)
    loinc: Optional[str] = Field(default=None, index=True, unique=True, description="LOINC编码（唯一，可选）")
    
    records: Mapped[list["IndicatorRecord"]] = Relationship(back_populates="indicator")
    detail: Mapped[Optional["IndicatorDetail"]] = Relationship(back_populates="indicator", sa_relationship_kwargs={"uselist": False})
    users: Mapped[list["User"]] = Relationship(
        back_populates="indicators",
        link_model=UserIndicator
    )
    categories: Mapped[list["Category"]] = Relationship(
        back_populates="indicators",
        link_model=IndicatorCategoryLink
    )


class IndicatorRecord(IDMixin, TimestampMixin, SoftDeleteMixin, SQLModel, table=True):
    __table_args__ = (
        Index("idx_indicatorrecord_indicator_measured", "indicator_id", "measured_at"),
        Index("idx_indicatorrecord_user_measured", "user_id", "measured_at"),
    )

    indicator_id: int = Field(foreign_key="indicator.id", index=True, nullable=False)  # 指标ID
    user_id: int = Field(foreign_key="user.id", index=True, nullable=False)  # 用户ID
    measured_at: date = Field(index=True, nullable=False)  # 测量日期
    value: str = Field(index=False, nullable=False)  # 指标值（字符串，兼容文本与数值）
    unit: str = Field(index=False, nullable=False)  # 单位（必填，避免跨表默认引用）
    ref_low: Optional[float] = Field(default=None, index=False)  # 参考下限（记录级覆盖）
    ref_high: Optional[float] = Field(default=None, index=False)  # 参考上限（记录级覆盖）
    ref_text: Optional[str] = Field(default=None, index=False)  # 参考文本（如“阴性/阳性”）
    source: Optional[str] = Field(default="manual")  # 数据来源（默认 manual）
    note: Optional[str] = None  # 备注
    admission_file_id: Optional[int] = Field(default=None, foreign_key="admissionfile.id", index=True)  # 关联住院文件ID

    indicator: Optional[Indicator] = Relationship(back_populates="records")


class IndicatorDetail(IDMixin, TimestampMixin, SoftDeleteMixin, SQLModel, table=True):
    indicator_id: int = Field(foreign_key="indicator.id", index=True, unique=True)
    introduction_text: Optional[str] = None
    measurement_method: Optional[str] = None
    clinical_significance: Optional[str] = None
    high_meaning: Optional[str] = None
    low_meaning: Optional[str] = None
    high_advice: Optional[str] = None
    low_advice: Optional[str] = None
    normal_advice: Optional[str] = None
    general_advice: Optional[str] = None
    unit: Optional[str] = None
    reference_range: Optional[str] = None
    updated_at: Optional[datetime] = Field(default_factory=datetime.now, index=True, nullable=False)

    indicator: Mapped["Indicator"] = Relationship(back_populates="detail")


class IndicatorCategoryLink(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("indicator_id", "category_id"),
    )

    indicator_id: int = Field(foreign_key="indicator.id", primary_key=True, index=True)
    category_id: int = Field(foreign_key="category.id", primary_key=True, index=True)
