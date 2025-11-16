from typing import Optional, List
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import select, delete
from sqlalchemy import func
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.session import get_session
from app.api.auth.deps import get_current_user
from app.models.user import User
from app.models.indicator import Indicator, IndicatorRecord, IndicatorDetail, Category, IndicatorCategoryLink
from app.models.user_indicator import UserIndicator

router = APIRouter()


class CreateIndicatorRequest(BaseModel):
    nameCn: str
    nameEn: Optional[str] = None
    type: Optional[str] = None
    unit: str
    referenceMin: Optional[float] = None
    referenceMax: Optional[float] = None
    categories: Optional[List[str]] = None
    loinc: Optional[str] = None


class UpdateIndicatorRequest(CreateIndicatorRequest):
    pass


@router.get("")
async def list_indicators(
    page: int = 1,
    pageSize: int = 20,
    keyword: Optional[str] = None,
    category: Optional[str] = None,
    startDate: Optional[date] = None,
    endDate: Optional[date] = None,
    sortBy: Optional[str] = "measureDate",
    order: Optional[str] = "desc",
    favorites: Optional[bool] = None,
    builtin: Optional[bool] = None,
    owner: Optional[str] = "all",
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    q = select(Indicator).where(Indicator.deleted_at.is_(None))
    if builtin is True:
        q = q.where(Indicator.is_builtin.is_(True))
    if builtin is False:
        q = q.where(Indicator.is_builtin.is_(False))
    if owner == "me":
        q = q.where(
            (Indicator.owner_user_id == current_user.id) | (Indicator.is_builtin.is_(True))
        )
    if keyword:
        q = q.where((Indicator.name_cn.contains(keyword)) | (Indicator.name_en.contains(keyword)))
    if category:
        cat_res = await session.exec(select(Category).where(Category.name == category))
        cat = cat_res.scalar_one_or_none()
        if cat:
            link_q = select(IndicatorCategoryLink.indicator_id).where(IndicatorCategoryLink.category_id == cat.id)
            q = q.where(Indicator.id.in_(link_q))
    if favorites is True:
        fav_q = select(UserIndicator.indicator_id).where(
            UserIndicator.user_id == current_user.id, UserIndicator.favorite.is_(True)
        )
        q = q.where(Indicator.id.in_(fav_q))
    total_res = await session.exec(select(func.count()).select_from(q.subquery()))
    total = total_res.one() or 0
    res = await session.exec(q.order_by(Indicator.id).offset((page - 1) * pageSize).limit(pageSize))
    indicators = res.all()
    items = []
    for it in indicators:
        rec_q = select(IndicatorRecord).where(
            IndicatorRecord.indicator_id == it.id,
            IndicatorRecord.user_id == current_user.id,
            IndicatorRecord.deleted_at.is_(None),
        )
        if startDate:
            rec_q = rec_q.where(IndicatorRecord.measured_at >= startDate)
        if endDate:
            rec_q = rec_q.where(IndicatorRecord.measured_at <= endDate)
        if order == "asc":
            rec_q = rec_q.order_by(IndicatorRecord.measured_at.asc())
        else:
            rec_q = rec_q.order_by(IndicatorRecord.measured_at.desc())
        rec_q = rec_q.limit(1)
        rec_res = await session.exec(rec_q)
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
        cats_res = await session.exec(
            select(Category)
            .join(IndicatorCategoryLink, IndicatorCategoryLink.category_id == Category.id)
            .where(IndicatorCategoryLink.indicator_id == it.id)
        )
        cats = [c.name for c in cats_res.all()]
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
                "categories": cats,
                "source": rec.source if rec else None,
                "note": rec.note if rec else None,
                "isBuiltin": it.is_builtin,
                "loinc": it.loinc,
                "favorite": bool(fav.favorite) if fav else False,
            }
        )
    return {"items": items, "total": total}


@router.post("")
async def create_indicator(
    data: CreateIndicatorRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if not data.nameCn or not data.unit:
        raise HTTPException(status_code=400, detail="名称与单位必填")
    it = Indicator(
        owner_user_id=current_user.id,
        name_cn=data.nameCn,
        name_en=data.nameEn,
        unit=data.unit,
        type=data.type or "numeric",
        reference_min=data.referenceMin,
        reference_max=data.referenceMax,
        is_builtin=False,
        loinc=data.loinc,
    )
    session.add(it)
    await session.flush()
    await session.refresh(it)
    if data.categories:
        for name in data.categories:
            c_res = await session.exec(select(Category).where(Category.name == name))
            c = c_res.scalar_one_or_none()
            if c:
                session.add(IndicatorCategoryLink(indicator_id=it.id, category_id=c.id))
    await session.commit()
    return {"id": it.id}


@router.get("/{id}")
async def get_indicator(
    id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    res = await session.exec(select(Indicator).where(Indicator.id == id, Indicator.deleted_at.is_(None)))
    it = res.scalar_one_or_none()
    if not it:
        raise HTTPException(status_code=404, detail="指标不存在")
    cats_res = await session.exec(
        select(Category)
        .join(IndicatorCategoryLink, IndicatorCategoryLink.category_id == Category.id)
        .where(IndicatorCategoryLink.indicator_id == it.id)
    )
    cats = [c.name for c in cats_res.all()]
    return {
        "id": it.id,
        "nameCn": it.name_cn,
        "nameEn": it.name_en,
        "type": it.type,
        "unit": it.unit,
        "referenceMin": it.reference_min,
        "referenceMax": it.reference_max,
        "isBuiltin": it.is_builtin,
        "loinc": it.loinc,
        "categories": cats,
    }


@router.put("/{id}")
async def update_indicator(
    id: int,
    data: UpdateIndicatorRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    res = await session.exec(select(Indicator).where(Indicator.id == id, Indicator.deleted_at.is_(None)))
    it = res.scalar_one_or_none()
    if not it:
        raise HTTPException(status_code=404, detail="指标不存在")
    it.name_cn = data.nameCn or it.name_cn
    it.name_en = data.nameEn or it.name_en
    it.type = data.type or it.type
    it.unit = data.unit or it.unit
    it.reference_min = data.referenceMin if data.referenceMin is not None else it.reference_min
    it.reference_max = data.referenceMax if data.referenceMax is not None else it.reference_max
    it.loinc = data.loinc or it.loinc
    session.add(it)
    await session.flush()
    if data.categories is not None:
        await session.exec(
            delete(IndicatorCategoryLink).where(IndicatorCategoryLink.indicator_id == it.id)
        )
        if data.categories:
            for name in data.categories:
                c_res = await session.exec(select(Category).where(Category.name == name))
                c = c_res.scalar_one_or_none()
                if c:
                    session.add(IndicatorCategoryLink(indicator_id=it.id, category_id=c.id))
    await session.commit()
    return {"code": 200}


@router.delete("/{id}")
async def delete_indicator(
    id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    res = await session.exec(select(Indicator).where(Indicator.id == id, Indicator.deleted_at.is_(None)))
    it = res.scalar_one_or_none()
    if not it:
        raise HTTPException(status_code=404, detail="指标不存在")
    it.deleted_at = datetime.now()
    session.add(it)
    await session.commit()
    return {"code": 200}


class CreateRecordRequest(BaseModel):
    date: date
    value: str
    unit: str
    referenceMin: Optional[float] = None
    referenceMax: Optional[float] = None
    source: Optional[str] = None
    note: Optional[str] = None
    admissionFileId: Optional[int] = None


class UpdateRecordRequest(BaseModel):
    date: Optional[date] = None
    value: Optional[str] = None
    unit: Optional[str] = None
    referenceMin: Optional[float] = None
    referenceMax: Optional[float] = None
    source: Optional[str] = None
    note: Optional[str] = None
    admissionFileId: Optional[int] = None


@router.get("/{id}/records")
async def list_records(
    id: int,
    page: int = 1,
    pageSize: int = 20,
    startDate: Optional[date] = None,
    endDate: Optional[date] = None,
    admissionFileId: Optional[int] = None,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    q = select(IndicatorRecord).where(
        IndicatorRecord.indicator_id == id,
        IndicatorRecord.user_id == current_user.id,
        IndicatorRecord.deleted_at.is_(None),
    )
    if startDate:
        q = q.where(IndicatorRecord.measured_at >= startDate)
    if endDate:
        q = q.where(IndicatorRecord.measured_at <= endDate)
    if admissionFileId is not None:
        q = q.where(IndicatorRecord.admission_file_id == admissionFileId)
    total_res = await session.exec(select(func.count()).select_from(q.subquery()))
    total = total_res.one() or 0
    res = await session.exec(
        q.order_by(IndicatorRecord.measured_at.desc()).offset((page - 1) * pageSize).limit(pageSize)
    )
    rows = res.all()
    items = []
    for r in rows:
        status = None
        if r.value is not None and r.ref_low is not None and r.ref_high is not None:
            try:
                v = float(r.value)
                status = "high" if v > float(r.ref_high) else ("low" if v < float(r.ref_low) else "normal")
            except Exception:
                status = "normal"
        items.append(
            {
                "recordId": r.id,
                "date": r.measured_at.isoformat(),
                "value": r.value,
                "unit": r.unit,
                "status": status,
                "source": r.source,
                "note": r.note,
                "admissionFileId": r.admission_file_id,
            }
        )
    return {"items": items, "total": total}


@router.post("/{id}/records")
async def create_record(
    id: int,
    data: CreateRecordRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    it_res = await session.exec(select(Indicator).where(Indicator.id == id, Indicator.deleted_at.is_(None)))
    it = it_res.scalar_one_or_none()
    if not it:
        raise HTTPException(status_code=404, detail="指标不存在")
    r = IndicatorRecord(
        indicator_id=id,
        user_id=current_user.id,
        measured_at=data.date,
        value=str(data.value),
        unit=data.unit,
        ref_low=data.referenceMin,
        ref_high=data.referenceMax,
        source=data.source or "manual",
        note=data.note,
        admission_file_id=data.admissionFileId,
    )
    session.add(r)
    await session.commit()
    await session.refresh(r)
    return {"recordId": r.id}


@router.patch("/{id}/records/{recordId}")
async def update_record(
    id: int,
    recordId: int,
    data: UpdateRecordRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    res = await session.exec(
        select(IndicatorRecord).where(
            IndicatorRecord.id == recordId,
            IndicatorRecord.indicator_id == id,
            IndicatorRecord.user_id == current_user.id,
            IndicatorRecord.deleted_at.is_(None),
        )
    )
    r = res.scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=404, detail="记录不存在")
    if data.date is not None:
        r.measured_at = data.date
    if data.value is not None:
        r.value = str(data.value)
    if data.unit is not None:
        r.unit = data.unit
    if data.referenceMin is not None:
        r.ref_low = data.referenceMin
    if data.referenceMax is not None:
        r.ref_high = data.referenceMax
    if data.source is not None:
        r.source = data.source
    if data.note is not None:
        r.note = data.note
    if data.admissionFileId is not None:
        r.admission_file_id = data.admissionFileId
    session.add(r)
    await session.commit()
    return {"code": 200}


@router.delete("/{id}/records/{recordId}")
async def delete_record(
    id: int,
    recordId: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    res = await session.exec(
        select(IndicatorRecord).where(
            IndicatorRecord.id == recordId,
            IndicatorRecord.indicator_id == id,
            IndicatorRecord.user_id == current_user.id,
            IndicatorRecord.deleted_at.is_(None),
        )
    )
    r = res.scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=404, detail="记录不存在")
    r.deleted_at = datetime.now()
    session.add(r)
    await session.commit()
    return {"code": 200}


class UpdateDetailRequest(BaseModel):
    category: Optional[str] = None
    introductionText: Optional[str] = None
    measurementMethod: Optional[str] = None
    clinicalSignificance: Optional[str] = None
    referenceRange: Optional[str] = None
    unit: Optional[str] = None
    highMeaning: Optional[str] = None
    lowMeaning: Optional[str] = None
    highAdvice: Optional[str] = None
    lowAdvice: Optional[str] = None
    normalAdvice: Optional[str] = None
    generalAdvice: Optional[str] = None


@router.get("/{id}/detail")
async def get_indicator_detail(
    id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    res = await session.exec(select(Indicator).where(Indicator.id == id))
    it = res.scalar_one_or_none()
    if not it:
        raise HTTPException(status_code=404, detail="指标不存在")
    d_res = await session.exec(select(IndicatorDetail).where(IndicatorDetail.indicator_id == id, IndicatorDetail.deleted_at.is_(None)))
    d = d_res.scalar_one_or_none()
    if not d:
        return {}
    return {
        "indicatorName": it.name_cn,
        "introductionText": d.introduction_text,
        "measurementMethod": d.measurement_method,
        "clinicalSignificance": d.clinical_significance,
        "referenceRange": d.reference_range,
        "unit": d.unit,
        "highMeaning": d.high_meaning,
        "lowMeaning": d.low_meaning,
        "highAdvice": d.high_advice,
        "lowAdvice": d.low_advice,
        "normalAdvice": d.normal_advice,
        "generalAdvice": d.general_advice,
    }


@router.put("/{id}/detail")
async def update_indicator_detail(
    id: int,
    data: UpdateDetailRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in {"admin", "developer"}:
        raise HTTPException(status_code=403, detail="无权限")
    it_res = await session.exec(select(Indicator).where(Indicator.id == id))
    it = it_res.scalar_one_or_none()
    if not it:
        raise HTTPException(status_code=404, detail="指标不存在")
    d_res = await session.exec(select(IndicatorDetail).where(IndicatorDetail.indicator_id == id))
    d = d_res.scalar_one_or_none()
    if d:
        if data.introductionText is not None:
            d.introduction_text = data.introductionText
        if data.measurementMethod is not None:
            d.measurement_method = data.measurementMethod
        if data.clinicalSignificance is not None:
            d.clinical_significance = data.clinicalSignificance
        if data.highMeaning is not None:
            d.high_meaning = data.highMeaning
        if data.lowMeaning is not None:
            d.low_meaning = data.lowMeaning
        if data.highAdvice is not None:
            d.high_advice = data.highAdvice
        if data.lowAdvice is not None:
            d.low_advice = data.lowAdvice
        if data.normalAdvice is not None:
            d.normal_advice = data.normalAdvice
        if data.generalAdvice is not None:
            d.general_advice = data.generalAdvice
        if data.unit is not None:
            d.unit = data.unit
        if data.referenceRange is not None:
            d.reference_range = data.referenceRange
        d.updated_at = datetime.now()
        session.add(d)
    else:
        d = IndicatorDetail(
            indicator_id=id,
            introduction_text=data.introductionText,
            measurement_method=data.measurementMethod,
            clinical_significance=data.clinicalSignificance,
            high_meaning=data.highMeaning,
            low_meaning=data.lowMeaning,
            high_advice=data.highAdvice,
            low_advice=data.lowAdvice,
            normal_advice=data.normalAdvice,
            general_advice=data.generalAdvice,
            unit=data.unit,
            reference_range=data.referenceRange,
        )
        session.add(d)
    await session.commit()
    return {"code": 200}