from __future__ import annotations

from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from .base import IDMixin, TimestampMixin, SoftDeleteMixin


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
    updated_at: Optional[datetime] = Field(default=datetime.now(), index=True, nullable=False)

    indicator: Optional["Indicator"] = Relationship(back_populates="detail")