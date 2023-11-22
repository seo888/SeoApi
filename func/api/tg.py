"""Telegram api"""
import asyncio
import telegram

class Telegram():
    """Telegram api"""
    def __init__(self,token):
        self.bot = telegram.Bot(token=token)

    def send_mes(self, text, to_id):
        """Telegram send message"""
        # pip install python-telegram-bot
        result = self.bot.send_message(chat_id=to_id, text=text, parse_mode="Markdown")
        print(mes:=f"{result['chat']['title']}@{result['from_user']['username']}：{result['text']}")
        return mes

async def run():
    tg = Telegram('5140222274:AAGadFsnBxxT4CoIfrMAtU5mYLylsxKuTjk')
    await tg.send_mes('test','-381608581')

if __name__=="__main__":
    asyncio.run(run())

#         self.telegram_token = "5140222274:AAGadFsnBxxT4CoIfrMAtU5mYLylsxKuTjk"
#         self.telegram_group_chat_id = "-321014615"
# tele_mes = mes.replace(f'【{web}】',webs[web]).replace(f'‖{keyword}‖',f'‖{keyword_dict[web]}‖')
#                         return_mes = Telegram(self.telegram_token).send_mes(tele_mes,self.telegram_group_chat_id)
#                         print(return_mes)
    