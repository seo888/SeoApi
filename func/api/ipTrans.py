"""代理转发"""
#!/usr/bin/python3

import time
import hashlib
import httpx


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

    async def request_get(self,url,params):
        """代理访问"""
        async with httpx.AsyncClient(headers=self.headers,http2=True, proxies=self.proxies) as client:
            resp = await client.get(url,params=params)
        return resp
