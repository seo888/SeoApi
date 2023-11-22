"""Telegram api"""
import asyncio
import telegram

class Telegram():
    """Telegram api"""
    def __init__(self,token):
        self.bot = telegram.Bot(token=token)

    async def send_mes(self, text, to_id):
        """Telegram send message"""
        # pip install python-telegram-bot
        result = await self.bot.send_message(chat_id=to_id, text=text, parse_mode="Markdown")
        print(mes:=f"{result['chat']['title']}@{result['from_user']['username']}：{result['text']}")
        return mes

# async def run():
#     tg = Telegram('5140222274:AAGadFsnBxxT4CoIfrMAtU5mYLylsxKuTjk')
#     await tg.send_mes('test123455556','-381608581')

# if __name__=="__main__":
#     asyncio.run(run())
    