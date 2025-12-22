from fastapi import APIRouter
from .serp.router import router as serp_router
from .ai.router import router as ai_router
from .tg.router import router as tg_router

v1_router = APIRouter()

v1_router.include_router(serp_router, prefix="/serp", tags=["serp"])
v1_router.include_router(ai_router, prefix="/ai", tags=["ai"])
v1_router.include_router(tg_router, prefix="/tg", tags=["tg"])