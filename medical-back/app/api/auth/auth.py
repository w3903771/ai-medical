import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.session import get_session
from app.models.user import User
from app.utils.jwt_util import create_jwt_token
from .deps import get_current_user


router = APIRouter()


def _hash_password(password: str) -> str:
    import hashlib
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


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


class RegisterRequest(BaseModel):
    username: str
    name: str
    password: str
    email: Optional[EmailStr] = None


@router.post("/register")
async def register(data: RegisterRequest, session: AsyncSession = Depends(get_session)):
    # 检查必填字段
    if not data.username or not data.password:
        raise HTTPException(status_code=400, detail="用户名与密码必填")

    # 检查用户名唯一性
    if data.username:
        existing = await session.exec(select(User).where(User.username == data.username))
        if existing.first():
            raise HTTPException(status_code=400, detail="用户名已存在")
    # 检查邮箱唯一性
    if data.email:
        existing_email = await session.exec(select(User).where(User.email == data.email))
        if existing_email.first():
            raise HTTPException(status_code=400, detail="邮箱已被使用")

    user = User(
        username=data.username,
        name=data.name,
        password_hash=_hash_password(data.password),
        email=data.email,
    )

    try:
        session.add(user)
        await session.commit()
        await session.refresh(user)
    except Exception as e:
        # 针对常见数据库异常进行分类反馈
        from sqlalchemy.exc import IntegrityError, OperationalError
        await session.rollback()
        if isinstance(e, IntegrityError):
            # 唯一约束或其他完整性约束冲突
            raise HTTPException(status_code=400, detail="唯一约束冲突：用户名或邮箱已存在或字段不合法")
        if isinstance(e, OperationalError):
            # 典型如表不存在/数据库未初始化
            raise HTTPException(status_code=500, detail="数据库未初始化或表不存在，请检查后端启动日志与数据库文件")
        # 其他未分类异常
        raise HTTPException(status_code=500, detail="服务器内部错误，请查看后端日志")
    return {"id": user.id, "username": user.username}


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login")
async def login(data: LoginRequest, session: AsyncSession = Depends(get_session)):
    result = await session.exec(select(User).where(User.username == data.username, User.deleted_at.is_(None)))
    user = result.first()
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")

    if _hash_password(data.password) != user.password_hash:
        raise HTTPException(status_code=401, detail="密码错误")

    user.last_login = datetime.datetime.now(datetime.timezone.utc)
    await session.commit()

    token = create_jwt_token(user_id=user.id, expire_minutes=10)
    return {
        "token": token,
        "expiresIn": 600,
        "user": _user_to_profile(user),
    }


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    # 目前为无状态登出：前端删除令牌即可；此处保留接口以便前端统一调用
    # 若未来支持令牌撤销/版本号提升，可在此实现服务端状态更新
    return {"success": True}