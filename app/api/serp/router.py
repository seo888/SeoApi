# api/serp/router.py

from .sogou import sogou_search
from fastapi import APIRouter

router = APIRouter()

@router.get("/google")
async def serp_google():
    return [{"id": 1, "name": "google"}]

@router.get("/bing")
async def serp_bing():
    return [{"id": 1, "name": "google"}]

@router.get("/baidu")
async def serp_baidu():
    return [{"id": 1, "name": "google"}]

@router.get("/sogou/search")
async def serp_sogou_search(q: str = None, num: int = 50):
    """谷歌接口"""
    if q is None:
        return JSONResponse(status_code=404, content={"error": "参数错误"})
    return await sogou_search(q, num=num)