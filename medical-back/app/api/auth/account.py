from typing import Optional
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from app.db.session import get_session
from app.models.user import User
from .deps import get_current_user


router = APIRouter()


def _user_to_profile(user: User) -> dict:
    return {
        "id": user.id,
        "username": user.username,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "birthDate": user.birth_date.isoformat() if user.birth_date else None,
        "gender": user.gender,
        "createdAt": user.created_at.isoformat() if user.created_at else None,
        "lastLogin": user.last_login.isoformat() if user.last_login else None,
    }


@router.get("/profile")
async def get_profile(current_user: User = Depends(get_current_user)):
    return _user_to_profile(current_user)


class UpdateProfileRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    gender: Optional[int] = None
    birthDate: Optional[date] = None

@router.put("/profile")
async def update_profile(
    data: UpdateProfileRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    changed = False

    if data.name and data.name != current_user.name:
        current_user.name = data.name
        changed = True

    if data.email and data.email != (current_user.email or None):
        # 检查邮箱唯一
        exists = await session.exec(select(User).where(User.email == data.email))
        if exists.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="邮箱已被使用")
        current_user.email = data.email
        changed = True

    if data.gender is not None and data.gender != current_user.gender:
        current_user.gender = data.gender
        changed = True

    if data.birthDate is not None and data.birthDate != current_user.birth_date:
        current_user.birth_date = data.birthDate
        changed = True

    if changed:
        session.add(current_user)
        await session.commit()
    return {"success": True}


class ChangePasswordRequest(BaseModel):
    oldPassword: str
    newPassword: str


def _hash_password(password: str) -> str:
    import hashlib
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


@router.put("/password")
async def change_password(
    data: ChangePasswordRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if _hash_password(data.oldPassword) != current_user.password_hash:
        raise HTTPException(status_code=400, detail="旧密码不正确")
    if not data.newPassword:
        raise HTTPException(status_code=400, detail="新密码不能为空")

    current_user.password_hash = _hash_password(data.newPassword)
    session.add(current_user)
    await session.commit()
    return {"success": True}