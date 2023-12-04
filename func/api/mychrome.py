import os
import linecache

import aiofiles
from DrissionPage import ChromiumPage
from DrissionPage.easy_set import set_paths
from DrissionPage import ChromiumOptions
from DrissionPage.easy_set import set_headless, set_paths,use_auto_port
from DrissionPage import SessionPage, SessionOptions
from DrissionPage.common import ActionChains
from DrissionPage.common import Keys
import arrow
import time
import hashlib
from urllib.parse import unquote


class MyChrome():
    def getBingCookie(self):
        try:
            set_headless(True)
            use_auto_port(True)
            set_paths(browser_path=r'/opt/google/chrome/google-chrome')
            # set_paths(browser_path=r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe')
            page = ChromiumPage()
            # 跳转到登录页面
            page.get('http://www.bing.com/account/general')
            #选择点击事件 可以使用 xpath: 后面的是xpath路径
            page.ele('xpath://*[@id="rpp"]').click()
            time.sleep(1)
            ac = ActionChains(page)
            ac.type('5')
            page.ele('xpath://*[@id="sv_btn"]').click()
            #这里为input的输入的内容 根据xpath
            # print(page.get_cookies())
            time.sleep(1)
            cookie = "".join([i['name'] + "=" + i['value'] + ";" for i in page.get_cookies()])
            print(cookie)
            #关闭浏览器
            # page.close_tabs()
            return cookie
        except Exception as e:
            print(e)
            return ''
    
    async def getTxtCookie(self):
        now_time = arrow.now("Asia/Shanghai")
        cache_dir = f"cache/{now_time.format('YYYY-MM-DD')}"
        name = now_time.format('YYYY-MM-DD HH')
        file_name = f"{cache_dir}/{name}.txt"
        if os.path.exists(file_name):
            linecache.checkcache(file_name)
            cookie = "".join(linecache.getlines(file_name)).strip()
        else:
            cookie = self.getBingCookie().strip()
            async with aiofiles.open(file_name,'w',encoding='utf-8')as f:
                await f.write(cookie)
        return cookie
