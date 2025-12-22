# api/v1/serp.py

from fastapi import APIRouter

router = APIRouter()

@router.get("/gemini")
async def ai_gemini():
    return [{"id": 1, "name": "gemini"}]

@router.get("/chatgpt")
async def ai_chatgpt():
    return [{"id": 1, "name": "chatgpt"}]

