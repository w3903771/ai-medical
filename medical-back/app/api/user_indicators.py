from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import func
from app.db.session import get_session
from app.api.auth.deps import get_current_user
from app.models.user import User
from app.models.user_indicator import UserIndicator
from app.models.indicator import Indicator

router = APIRouter()


@router.get("")
async def list_user_indicators(
    page: int = 1,
    pageSize: int = 20,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    q = select(UserIndicator).where(UserIndicator.user_id == current_user.id)
    total_res = await session.exec(select(func.count()).select_from(q.subquery()))
    total = total_res.one() or 0
    res = await session.exec(q.order_by(UserIndicator.id).offset((page - 1) * pageSize).limit(pageSize))
    rows = res.all()
    items = [
        {
            "id": r.id,
            "indicatorId": r.indicator_id,
            "alias": r.alias,
            "thresholdMin": r.threshold_min,
            "thresholdMax": r.threshold_max,
            "favorite": r.favorite,
            "createdAt": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ]
    return {"items": items, "total": total}


@router.post("")
async def create_user_indicator(
    indicatorId: int,
    alias: Optional[str] = None,
    thresholdMin: Optional[float] = None,
    thresholdMax: Optional[float] = None,
    favorite: Optional[bool] = None,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    i_res = await session.exec(select(Indicator).where(Indicator.id == indicatorId))
    it = i_res.scalar_one_or_none()
    if not it:
        raise HTTPException(status_code=404, detail="指标不存在")
    r_res = await session.exec(
        select(UserIndicator).where(
            UserIndicator.user_id == current_user.id,
            UserIndicator.indicator_id == indicatorId,
        )
    )
    r = r_res.scalar_one_or_none()
    if r:
        if alias is not None:
            r.alias = alias
        if thresholdMin is not None:
            r.threshold_min = thresholdMin
        if thresholdMax is not None:
            r.threshold_max = thresholdMax
        if favorite is not None:
            r.favorite = favorite
        session.add(r)
        await session.commit()
        await session.refresh(r)
        return {"id": r.id}
    r = UserIndicator(
        user_id=current_user.id,
        indicator_id=indicatorId,
        alias=alias,
        threshold_min=thresholdMin,
        threshold_max=thresholdMax,
        favorite=bool(favorite) if favorite is not None else False,
    )
    session.add(r)
    await session.commit()
    await session.refresh(r)
    return {"id": r.id}


@router.put("")
async def update_user_indicator(
    indicatorId: int,
    alias: Optional[str] = None,
    thresholdMin: Optional[float] = None,
    thresholdMax: Optional[float] = None,
    favorite: Optional[bool] = None,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    r_res = await session.exec(
        select(UserIndicator).where(
            UserIndicator.user_id == current_user.id,
            UserIndicator.indicator_id == indicatorId,
        )
    )
    r = r_res.scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=404, detail="未关注该指标")
    if alias is not None:
        r.alias = alias
    if thresholdMin is not None:
        r.threshold_min = thresholdMin
    if thresholdMax is not None:
        r.threshold_max = thresholdMax
    if favorite is not None:
        r.favorite = favorite
    session.add(r)
    await session.commit()
    return {"code": 200}


@router.delete("/{id}")
async def delete_user_indicator(
    id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    r_res = await session.exec(
        select(UserIndicator).where(UserIndicator.id == id, UserIndicator.user_id == current_user.id)
    )
    r = r_res.scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=404, detail="不存在")
    await session.delete(r)
    await session.commit()
    return {"code": 200}