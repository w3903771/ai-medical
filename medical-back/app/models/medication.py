from __future__ import annotations

from typing import Optional
from datetime import date
from sqlmodel import SQLModel, Field, Relationship
from .base import IDMixin, TimestampMixin, SoftDeleteMixin

# 用药相关模型：药品与用药记录


class Medication(IDMixin, TimestampMixin, SoftDeleteMixin, SQLModel, table=True):
    name: str  # 药品名称
    generic_name: Optional[str] = None  # 通用名
    spec: Optional[str] = None  # 规格（剂型/浓度等）
    unit: Optional[str] = None  # 单位（mg、片等）
    records: list["MedicationRecord"] = Relationship(back_populates="medication")


class MedicationRecord(IDMixin, TimestampMixin, SoftDeleteMixin, SQLModel, table=True):
    medication_id: int = Field(foreign_key="medication.id", index=True)  # 药品ID
    user_id: int = Field(foreign_key="user.id", index=True)  # 用户ID
    start_date: Optional[date] = None  # 开始用药日期
    end_date: Optional[date] = None  # 结束用药日期
    dose: Optional[str] = None  # 剂量
    frequency: Optional[str] = None  # 频次（每日几次等）
    route: Optional[str] = None  # 给药途径（口服/静滴等）
    purpose: Optional[str] = None  # 用药目的
    notes: Optional[str] = None  # 备注
    is_current: bool = Field(default=True, index=True)  # 是否当前用药

    medication: Optional[Medication] = Relationship(back_populates="records")