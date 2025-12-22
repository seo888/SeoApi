# api/v1/serp.py

from fastapi import APIRouter

router = APIRouter()

@router.get("/gemini")
async def gemini():
    return [{"id": 1, "name": "gemini"}]

@router.get("/chatgpt")
async def chatgpt():
    return [{"id": 1, "name": "chatgpt"}]

