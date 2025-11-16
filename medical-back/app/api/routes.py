from fastapi import APIRouter
from .auth.auth import router as auth_router
from .auth.account import router as account_router
from .indicators import router as indicators_router
from .categories import router as categories_router
from .user_indicators import router as user_indicators_router


api_router = APIRouter()


@api_router.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}

# 子路由
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(account_router, prefix="/account", tags=["account"])
api_router.include_router(indicators_router, prefix="/indicators", tags=["indicators"])
api_router.include_router(categories_router, prefix="/categories", tags=["categories"])
api_router.include_router(user_indicators_router, prefix="/user-indicators", tags=["user-indicators"])