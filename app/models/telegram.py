from telegram import Bot


class Telegram():
    """Telegram api"""

    def __init__(self, token):
        self.bot = Bot(token=token)
        self.chat_id = "-794028075"

    async def send_mes(self, text):
        """Telegram send message"""
        # pip install python-telegram-bot
        result = await self.bot.send_message(chat_id=self.chat_id,
                                             text=text,
                                             parse_mode="Markdown")
        print(
            mes :=
            f"{result['chat']['title']}@{result['from_user']['username']}：{result['text']}"
        )
        return mes