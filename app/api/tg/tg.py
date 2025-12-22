from telegram import Bot
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from typing import List, Dict, Any
import asyncio
import httpx
import tldextract
from parsel import Selector
import logging


class tg():
    """tg api"""

    def __init__(self, token, chat_id):
        self.bot = Bot(token=token)
        self.chat_id = chat_id
        self.chat_id = "-794028075"

    async def send_mes(self, text):
        """tg send message"""
        # pip install python-telegram-bot
        result = await self.bot.send_message(chat_id=self.chat_id,
                                             text=text,
                                             parse_mode="Markdown")
        print(
            mes :=
            f"{result['chat']['title']}@{result['from_user']['username']}：{result['text']}"
        )
        return mes