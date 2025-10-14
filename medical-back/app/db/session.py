from typing import AsyncGenerator
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from app.core.settings import get_settings
from app.models.indicator import Indicator, IndicatorRecord
from app.models.indicator_detail import IndicatorDetail
from app.models.admission import AdmissionFolder, Admission, AdmissionFile
from app.models.medication import Medication, MedicationRecord
from app.models.user import User
from app.models.kb import KnowledgeDoc, KnowledgeChunk
from app.models.chat import ChatSession, ChatMessage
from app.models.ocr import OcrTask
from app.models.export import ExportTask
from app.models.system import SystemLog, AuditLog
from app.models.websearch import WebSearchQuery
from app.models.user_indicator import UserIndicator


settings = get_settings()
engine = create_async_engine(settings.sqlite_url, echo=False, future=True)
async_session_factory = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False, autoflush=False, autocommit=False
)


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session