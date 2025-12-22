# api/serp/router.py

from api.serp.sogou import sogou
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

@router.get("/sogou/{action}")
async def serp_sogou(action: str, q: str = None, num: int = 50):
    """谷歌接口"""
    if q is None:
        return JSONResponse(status_code=404, content={"error": "参数错误"})
    return await sogou(action, q, num=num)