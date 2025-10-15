from typing import Optional
from fastapi import Depends, Header, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from app.db.session import get_session
from app.models.user import User
from app.utils.jwt_util import verify_jwt_token


async def get_current_user(
    session: AsyncSession = Depends(get_session),
    authorization: Optional[str] = Header(None),
) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="未提供有效的认证信息")
    token = authorization.split(" ", 1)[1]
    try:
        payload = verify_jwt_token(token)
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Token无效")

    result = await session.execute(select(User).where(User.id == user_id, User.deleted_at.is_(None)))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在或已被删除")
    return user