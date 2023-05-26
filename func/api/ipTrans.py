"""代理转发"""
#!/usr/bin/python3

import asyncio
import random
import time
import hashlib
import httpx
from fake_useragent import UserAgent


class IpTrans():
    """代理转发"""

    def __init__(self,headers):
        orderno = "ZF20235228137OCaZ4F"
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
            async with httpx.AsyncClient(headers=self.headers,http2=True, proxies=self.proxies,verify=False) as client:
                resp = await client.get(url)
        else:
            async with httpx.AsyncClient(headers=self.headers,http2=True, proxies=self.proxies,verify=False) as client:
                resp = await client.get(url,params=params)
        return resp

# async def run():
#     user_agent = UserAgent().random
#     muid = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz'.upper()+"0123456789",k=32))
#     headers = {
#             "user-agent": user_agent,
#             "referer": "https://www.bing.com/",
#             "cookie": f"f_EDGE_V=1; SRCHHPGUSR=NRSLT=50; MUID={muid};"
#             # "cookie": f"f_EDGE_V=1; SRCHHPGUSR=NRSLT=50;"
#     }
#     url = 'https://cn.bing.com/search'
#     params = {
#             "q": 'av online',
#             "qs": "n",
#             "pq": "fges",
#             "mkt": "zh-CN", 
#         }
#     ip_trans = IpTrans(headers=headers)
#     resp = await ip_trans.request_get(url,params)
#     # resp = await ip_trans.request_get("http://icanhazip.com/")
#     print(resp.text[:1000])

# if __name__ == "__main__":
#     asyncio.run(run())