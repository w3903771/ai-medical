"""
数据库引擎与会话管理模块

职责：
- 创建异步数据库引擎与会话工厂；提供 FastAPI 依赖的会话生成器；
- 应用启动事件中执行建表与种子数据导入（见 `init_db`）。
"""

from typing import AsyncGenerator
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from app.core.settings import get_settings
from app.core.logging import get_request_logger

# 导入所有涉及建表的模型，确保 `SQLModel.metadata.create_all` 能覆盖到联结表与所有业务表
from app.models.indicator import Indicator, IndicatorRecord, Category, IndicatorDetail, IndicatorCategoryLink
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


# 初始化异步引擎与会话工厂（DSN 来自 Settings.sqlite_url）
settings = get_settings()
engine = create_async_engine(settings.sqlite_url, echo=False, future=True)
async_session_factory = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False, autoflush=False, autocommit=False
)


async def init_db() -> None:
    """应用启动时创建所有数据表并执行种子导入。

    - 先执行 `create_all`，确保首次启动即可生成完整的数据库结构。
    - 再调用 `run_seeds()`，幂等导入内置字典与分类关联；异常被吞噬以避免影响服务启动。
    """
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    try:
        log = get_request_logger()
        log.info("db seeds:start")
        from app.db.seeds import run_seeds
        await run_seeds()
        log.info("db seeds:done")
    except Exception as e:
        log = get_request_logger()
        log.exception("db seeds:error")


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI 依赖：提供按请求生命周期管理的异步会话。"""
    async with async_session_factory() as session:
        yield session