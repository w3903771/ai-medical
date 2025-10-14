from __future__ import annotations

from typing import Optional
from datetime import date, datetime
from sqlmodel import SQLModel, Field, Relationship
from .base import IDMixin, TimestampMixin, SoftDeleteMixin

# 住院档案相关模型：目录/住院记录/住院文件


class AdmissionFolder(IDMixin, SQLModel, table=True):
    user_id: int = Field(foreign_key="user.id", index=True)  # 用户ID
    year: int = Field(index=True)  # 年
    month: int = Field(index=True)  # 月
    admissions: list["Admission"] = Relationship(back_populates="folder")


class Admission(IDMixin, TimestampMixin, SoftDeleteMixin, SQLModel, table=True):
    folder_id: int = Field(foreign_key="admissionfolder.id", index=True)  # 所属目录ID
    user_id: int = Field(foreign_key="user.id", index=True)  # 用户ID
    hospital: str  # 医院
    department: Optional[str] = None  # 科室
    diagnosis: Optional[str] = None  # 诊断
    admission_date: date  # 入院日期
    discharge_date: Optional[date] = None  # 出院日期
    tags_json: Optional[str] = None  # 标签（JSON 字符串）
    notes: Optional[str] = None  # 备注

    folder: Optional[AdmissionFolder] = Relationship(back_populates="admissions")
    files: list["AdmissionFile"] = Relationship(back_populates="admission")


class AdmissionFile(IDMixin, TimestampMixin, SoftDeleteMixin, SQLModel, table=True):
    admission_id: int = Field(foreign_key="admission.id", index=True)  # 关联住院记录ID
    user_id: int = Field(foreign_key="user.id", index=True)  # 用户ID
    filename: str  # 文件名
    oss_key: Optional[str] = None  # 云存储 Key（如使用 OSS/S3）
    url: Optional[str] = None  # 文件访问 URL
    pages: Optional[int] = None  # 页数
    ocr_done: bool = Field(default=False)  # OCR 是否完成
    extracted_text: Optional[str] = None  # OCR 提取文本
    meta_json: Optional[str] = None  # 元数据（JSON 字符串）
    uploaded_at: Optional[datetime] = Field(default=None, index=True)  # 上传时间

    admission: Optional[Admission] = Relationship(back_populates="files")