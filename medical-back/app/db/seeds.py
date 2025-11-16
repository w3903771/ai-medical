"""
种子数据导入模块（后端初始化）

功能：
- 在应用启动阶段，读取 `app/data/indicators.json` 与 `app/data/category.json`，幂等 upsert 指标、指标详情与分类，
  并建立 `IndicatorCategoryLink` 的多对多关联，同时写入系统日志。

说明：
- 设计对齐 `docs/design.md` 与 `docs/database_design.md`；支持缺失 `category.json` 的兼容回退。
- 类型推断：当指标 `type` 缺省时，按 `unit` 推断（`qualitative|n/a|na|none` → `text`）。
"""

from pathlib import Path
import json
from typing import Dict

from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import select

from app.core.settings import get_settings
from app.models.indicator import Category, Indicator, IndicatorDetail, IndicatorCategoryLink
from app.models.system import SystemLog


# 读取数据库设置，创建异步引擎与会话工厂（与应用一致的 DSN）
settings = get_settings()
_engine = create_async_engine(settings.sqlite_url, echo=False, future=True)
_session_factory = sessionmaker(
    bind=_engine, class_=AsyncSession, expire_on_commit=False, autoflush=False, autocommit=False
)

# 数据文件路径常量（定位到 app/data）
_DATA_DIR = Path(__file__).resolve().parents[1] / "data"
_IND_FILE_PATH = _DATA_DIR / "indicators.json"
_CAT_FILE_PATH = _DATA_DIR / "category.json"


async def run_seeds() -> None:
    """加载并导入内置指标/分类/详情，幂等执行。

    步骤：
    1. 读取 `indicators.json`（必需）与 `category.json`（可选）。
    2. upsert 分类并记录 {name → id} 映射。
    3. upsert 指标（优先按 `loinc`，否则按 `(owner_user_id IS NULL, name_cn)`），并维护 loinc/name 映射。
    4. upsert 指标详情（1:1）。
    5. 依据分类成员建立 `IndicatorCategoryLink` 多对多关联，幂等避免重复。
    6. 写入系统日志并提交事务。
    """

    # 读取指标数据（必须存在，否则直接返回）
    if not _IND_FILE_PATH.exists():
        return

    with _IND_FILE_PATH.open("r", encoding="utf-8") as f:
        ind_payload = json.load(f)

    indicators = ind_payload.get("indicators", [])
    ind_version = ind_payload.get("dataset_version", "unknown")

    # 读取分类数据（优先 category.json，缺失则兼容旧版 indicators.json）
    if _CAT_FILE_PATH.exists():
        with _CAT_FILE_PATH.open("r", encoding="utf-8") as f:
            cat_payload = json.load(f)
            categories = cat_payload.get("categories", [])
            cat_version = cat_payload.get("dataset_version", "unknown")
    else:
        categories = ind_payload.get("categories", [])
        cat_version = ind_version

    async with _session_factory() as session:
        # 映射用于后续快速建立分类-指标关联
        cat_id_map: Dict[str, int] = {}
        ind_by_loinc: Dict[str, int] = {}
        ind_by_name: Dict[str, int] = {}

        # 分类 upsert（name 唯一）
        for c in categories:
            name = c.get("name")
            if not name:
                continue
            existing = await session.execute(select(Category).where(Category.name == name))
            obj = existing.scalar_one_or_none()
            if obj:
                desc = c.get("description")
                if desc is not None:
                    obj.description = desc
            else:
                obj = Category(name=name, description=c.get("description"))
                session.add(obj)
                await session.flush()
                await session.refresh(obj)
            cat_id_map[name] = obj.id

        # 指标 upsert（对齐字段并设置 is_builtin）
        for it in indicators:
            name_cn = it.get("name_cn")
            unit = it.get("unit")
            if not name_cn or not unit:
                continue

            # 指标类型：优先读取，缺省依据 unit 推断
            ind_type = it.get("type")
            if not ind_type:
                u = (unit or "").lower()
                ind_type = "text" if u in {"qualitative", "n/a", "na", "none"} else "numeric"

            loinc = it.get("loinc")
            if loinc:
                res = await session.execute(select(Indicator).where(Indicator.loinc == loinc))
                ind = res.scalar_one_or_none()
            else:
                res = await session.execute(
                    select(Indicator)
                    .where(Indicator.name_cn == name_cn)
                    .where(Indicator.owner_user_id.is_(None))
                )
                ind = res.scalar_one_or_none()

            if ind:
                ind.name_en = it.get("name_en", ind.name_en)
                ind.unit = unit
                ind.reference_min = it.get("reference_min", ind.reference_min)
                ind.reference_max = it.get("reference_max", ind.reference_max)
                ind.is_builtin = True
                ind.type = ind_type or ind.type
                if loinc and not ind.loinc:
                    ind.loinc = loinc
            else:
                ind = Indicator(
                    owner_user_id=None,
                    name_cn=name_cn,
                    name_en=it.get("name_en"),
                    unit=unit,
                    type=ind_type,
                    reference_min=it.get("reference_min"),
                    reference_max=it.get("reference_max"),
                    is_builtin=True,
                    loinc=loinc,
                )
                session.add(ind)
                await session.flush()
                await session.refresh(ind)

            # 维护映射（供分类成员关联）
            if loinc:
                ind_by_loinc[loinc] = ind.id
            ind_by_name[name_cn] = ind.id

            # 指标详情 upsert（1:1）
            detail_data = it.get("detail")
            if detail_data:
                res = await session.execute(select(IndicatorDetail).where(IndicatorDetail.indicator_id == ind.id))
                detail = res.scalar_one_or_none()
                if detail:
                    for k, v in detail_data.items():
                        if v is not None:
                            setattr(detail, k, v)
                    if detail_data.get("unit") is None:
                        detail.unit = unit
                else:
                    detail = IndicatorDetail(
                        indicator_id=ind.id,
                        **{**detail_data, "unit": detail_data.get("unit", unit)}
                    )
                    session.add(detail)

        # 分类成员关联（幂等）
        for c in categories:
            cat_name = c.get("name")
            cat_id = cat_id_map.get(cat_name)
            if not cat_id:
                continue
            members = c.get("indicators", []) or []
            for m in members:
                # 成员可为字符串（按 loinc）或对象 { loinc | name_cn }
                m_loinc = m if isinstance(m, str) else (m.get("loinc") if isinstance(m, dict) else None)
                m_name = None if isinstance(m, str) else (m.get("name_cn") if isinstance(m, dict) else None)

                ind_id = None
                if m_loinc and m_loinc in ind_by_loinc:
                    ind_id = ind_by_loinc[m_loinc]
                elif m_name and m_name in ind_by_name:
                    ind_id = ind_by_name[m_name]
                else:
                    # 兜底查询（避免映射遗漏）
                    if m_loinc:
                        res = await session.execute(select(Indicator).where(Indicator.loinc == m_loinc))
                        row = res.scalar_one_or_none()
                        if row:
                            ind_id = row.id
                    elif m_name:
                        res = await session.execute(
                            select(Indicator)
                            .where(Indicator.name_cn == m_name)
                            .where(Indicator.owner_user_id.is_(None))
                        )
                        row = res.scalar_one_or_none()
                        if row:
                            ind_id = row.id

                if not ind_id:
                    continue

                # 幂等建立联结
                res = await session.execute(
                    select(IndicatorCategoryLink)
                    .where(IndicatorCategoryLink.indicator_id == ind_id)
                    .where(IndicatorCategoryLink.category_id == cat_id)
                )
                link = res.scalar_one_or_none()
                if not link:
                    session.add(IndicatorCategoryLink(indicator_id=ind_id, category_id=cat_id))

        # 写系统日志并提交
        log = SystemLog(
            level="info",
            message=f"seed_builtins:ind={ind_version};cat={cat_version}",
            context_json=json.dumps(
                {"categories": len(categories), "indicators": len(indicators)},
                ensure_ascii=False
            ),
        )
        session.add(log)
        await session.commit()