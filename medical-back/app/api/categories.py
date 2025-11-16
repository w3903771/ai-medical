from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import func
from app.db.session import get_session
from app.api.auth.deps import get_current_user
from app.models.user import User
from app.models.indicator import Category, IndicatorCategoryLink, Indicator, IndicatorRecord
from app.models.user_indicator import UserIndicator

router = APIRouter()


@router.get("")
async def list_categories(
    page: int = 1,
    pageSize: int = 20,
    keyword: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    q = select(Category).where(Category.deleted_at.is_(None))
    if keyword:
        q = q.where(Category.name.contains(keyword))
    total_res = await session.exec(select(func.count()).select_from(q.subquery()))
    total = total_res.one() or 0
    res = await session.exec(q.order_by(Category.id).offset((page - 1) * pageSize).limit(pageSize))
    items = [
        {
            "id": c.id,
            "name": c.name,
            "description": c.description,
        }
        for c in res.all()
    ]
    return {"items": items, "total": total}


@router.get("/{id}")
async def get_category(
    id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    r = await session.exec(select(Category).where(Category.id == id, Category.deleted_at.is_(None)))
    c = r.scalar_one_or_none()
    if not c:
        raise HTTPException(status_code=404, detail="分类不存在")
    cnt_res = await session.exec(
        select(func.count()).where(IndicatorCategoryLink.category_id == id)
    )
    indicator_count = cnt_res.one() or 0
    return {
        "id": c.id,
        "name": c.name,
        "description": c.description,
        "indicatorCount": indicator_count,
    }


@router.get("/{id}/indicators")
async def get_category_indicators(
    id: int,
    page: int = 1,
    pageSize: int = 20,
    keyword: Optional[str] = None,
    favorites: Optional[bool] = None,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    link_q = select(IndicatorCategoryLink.indicator_id).where(IndicatorCategoryLink.category_id == id)
    ind_q = select(Indicator).where(Indicator.deleted_at.is_(None), Indicator.id.in_(link_q))
    if keyword:
        ind_q = ind_q.where(
            (Indicator.name_cn.contains(keyword)) | (Indicator.name_en.contains(keyword))
        )
    if favorites is True:
        fav_q = select(UserIndicator.indicator_id).where(
            UserIndicator.user_id == current_user.id, UserIndicator.favorite.is_(True)
        )
        ind_q = ind_q.where(Indicator.id.in_(fav_q))
    total_res = await session.exec(select(func.count()).select_from(ind_q.subquery()))
    total = total_res.one() or 0
    res = await session.exec(
        ind_q.order_by(Indicator.id).offset((page - 1) * pageSize).limit(pageSize)
    )
    inds = res.all()
    items = []
    for it in inds:
        rec_res = await session.exec(
            select(IndicatorRecord)
            .where(
                IndicatorRecord.indicator_id == it.id,
                IndicatorRecord.user_id == current_user.id,
                IndicatorRecord.deleted_at.is_(None),
            )
            .order_by(IndicatorRecord.measured_at.desc())
            .limit(1)
        )
        rec = rec_res.scalar_one_or_none()
        value = rec.value if rec else None
        unit = rec.unit if rec else it.unit
        measure_date = rec.measured_at.isoformat() if rec else None
        ref_low = rec.ref_low if rec else it.reference_min
        ref_high = rec.ref_high if rec else it.reference_max
        status = None
        if value is not None and ref_low is not None and ref_high is not None:
            try:
                v = float(value)
                status = "high" if v > float(ref_high) else ("low" if v < float(ref_low) else "normal")
            except Exception:
                status = "normal"
        fav_res = await session.exec(
            select(UserIndicator).where(
                UserIndicator.user_id == current_user.id,
                UserIndicator.indicator_id == it.id,
            )
        )
        fav = fav_res.scalar_one_or_none()
        items.append(
            {
                "id": it.id,
                "indicator": it.name_cn,
                "nameCn": it.name_cn,
                "nameEn": it.name_en,
                "type": it.type,
                "value": value,
                "unit": unit,
                "referenceRange": (
                    f"{ref_low}-{ref_high}" if ref_low is not None and ref_high is not None else None
                ),
                "status": status,
                "measureDate": measure_date,
                "categories": [],
                "source": rec.source if rec else None,
                "note": rec.note if rec else None,
                "isBuiltin": it.is_builtin,
                "loinc": it.loinc,
                "favorite": bool(fav.favorite) if fav else False,
            }
        )
    return {"items": items, "total": total}