"""代理转发"""
#!/usr/bin/python3

import asyncio
import random
import time
import hashlib
from urllib.parse import unquote
import httpx
from fake_useragent import UserAgent


class IpTrans():
    """代理转发"""

    def __init__(self,headers):
        orderno = "ZF20235265897ukIela"
        secret = "177062c03c7a4669ad4a2822584fe07c"
        ip_port = "forward.xdaili.cn:80"
        timestamp = str(int(time.time()))
        string = f"orderno={orderno},secret={secret},timestamp={timestamp}".encode()
        md5_string = hashlib.md5(string).hexdigest()                
        sign = md5_string.upper()                             
        auth = "sign=" + sign + "&" + "orderno=" + orderno + "&" + "timestamp=" + timestamp
        self.headers = headers
        self.headers["Proxy-Authorization"]= auth
        self.proxies = {
            'http://': f'http://{ip_port}',  # 代理1
            'https://': f'http://{ip_port}',  # 代理2
        }

    async def request_get(self,url,params=None):
        """代理访问"""
        if params is None:
            async with httpx.AsyncClient(headers=self.headers, proxies=self.proxies,verify=False) as client:
                resp = await client.get(url)
        else:
            print(url,self.headers)
            async with httpx.AsyncClient(headers=self.headers, proxies=self.proxies,verify=False) as client:
                resp = await client.get(url,params=params)
        return resp