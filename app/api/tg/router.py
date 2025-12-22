# api/tg/router.py

from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import JSONResponse
from api.tg.tg import tg  # 假设你的 Telegram 发送类在这里


router = APIRouter()


@router.get("/send_mes")
async def tg_send_mes(
    text: str = Query(..., description="要发送的消息内容"),
    token: str = Query(..., description="Telegram Bot Token"),
    chat_id: int = Query(..., description="目标聊天 ID（用户、群组或频道 ID）")
):
    """
    发送 Telegram 消息

    - text: 消息内容（必填，不能为空字符串）
    - token: Bot Token（必填）
    - chat_id: 接收者 chat_id（必填）
    """
    # 1. 基础参数校验
    if not text or not text.strip():
        raise HTTPException(
            status_code=400,
            detail="消息内容（text）不能为空"
        )

    if not token or not token.strip():
        raise HTTPException(
            status_code=400,
            detail="Bot Token（token）不能为空"
        )

    if chat_id == 0:
        raise HTTPException(
            status_code=400,
            detail="chat_id 不能为 0，请提供有效的聊天 ID"
        )

    # 2. 初始化 Telegram 发送器
    try:
        tg_bot = tg(token=token, chat_id=chat_id)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"初始化 Telegram Bot 失败: {str(e)}"
        )

    # 3. 发送消息并捕获所有可能异常
    try:
        success = await tg_bot.send_mes(text.strip())
        if success:
            return JSONResponse({
                "success": True,
                "message": "消息发送成功",
                "text": text.strip(),
                "chat_id": chat_id
            })
        else:
            raise HTTPException(
                status_code=500,
                detail="消息发送失败（Bot 返回失败）"
            )

    except HTTPException:
        # 让上面主动抛出的异常直接传递
        raise
    except Exception as e:
        # 捕获网络错误、Telegram API 错误、权限问题等
        error_msg = str(e)
        if "Forbidden" in error_msg or "blocked" in error_msg.lower():
            detail = "Bot 被用户屏蔽或无权限发送消息"
        elif "chat not found" in error_msg.lower():
            detail = "聊天 ID 不存在或 Bot 未加入群组/频道"
        elif "Unauthorized" in error_msg:
            detail = "Bot Token 无效或已失效"
        elif "timeout" in error_msg.lower():
            detail = "发送超时，请检查网络或代理"
        else:
            detail = f"发送失败: {error_msg}"

        raise HTTPException(status_code=502, detail=detail)