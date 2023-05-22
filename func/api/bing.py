# -*- coding: UTF-8 -*-
"""必应功能"""

import random
import re
from urllib.parse import quote, unquote
from fake_useragent import UserAgent
import httpx
from lxml import etree
from tenacity import retry, stop_after_attempt


class Bing():
    """必应功能"""

    def __init__(self, func):
        self.func = func
        self.config = self.func.get_yaml('config/config.yml')

    async def request_get(self, url, headers=None, params=None, use_ip='127.0.0.1'):
        """异步访问"""
        transport = httpx.AsyncHTTPTransport(local_address=use_ip)
        print(url,use_ip)
        async with httpx.AsyncClient(
                headers=headers, params=params, http2=True, transport=transport) as client:
            resp = await client.get(url)
        return resp

    @retry(stop=stop_after_attempt(2))
    async def search(self, querry, num):
        """搜索查询"""
        text = unquote(querry)
        url = 'https://www.bing.com/search'
        # """&sk=&cvid=0054FD091D974C3085B871C05A447372&ghsh=0&ghacc=0&ghpl="""
        params = {
            "q": text,
            "qs": "n",
            "pq": "fges",
            "mkt": "zh-CN", 
            "cvid":"111828407a074e8d87ab05281b52b4c0",
            "aqs":"edge.0.69i64j69i64i450l7.21829j0j4",
            "FORM":"ANAB01",
            "PC":"HCTS",
        }

        use_ip = await self.func.use_ip('bing')
        # muid = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz'.upper()+"0123456789",k=32))
        # print(muid)
        # user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.62"
        # user_agent = "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm) Chrome/103.0.5060.134 Safari/537.36"
        user_agent = UserAgent().random
        headers = {
            "user-agent": user_agent,
            "referer": "https://www.bing.com/",
            # "cookie": f"f_EDGE_V=1; SRCHHPGUSR=NRSLT=50; MUID={muid}; SRCHD=AF=NOFORM; MUIDV=NU=1; SRCHUID=V=2&GUID={''.join(random.choices('abcdefghijklmnopqrstuvwxyz'.upper()+'0123456789',k=32))}&dmnchg=1;"
            # "cookie": f"f_EDGE_V=1; SRCHHPGUSR=NRSLT=50;"
            "cookie": f"""_EDGE_V=1; MUID=00419F979B86634206618D2D9AE062D5; SRCHD=AF=NOFORM; MUIDV=NU=1; SRCHUID=V=2&GUID=256205A9E4BE4D4A8DF6983319249A22&dmnchg=1; _UR=QS=0&TQS=0; MicrosoftApplicationsTelemetryDeviceId=2af9917a-270e-4f6e-964d-23cfb1d7a591; _tarLang=default=zh-Hans; _TTSS_IN=hist=WyJlbiIsImF1dG8tZGV0ZWN0Il0=; _TTSS_OUT=hist=WyJ6aC1IYW5zIl0=; MUIDB=00419F979B86634206618D2D9AE062D5; _clck=1gt3u0r|1|fah|0; Imported_MUID=3E162B4FADD96BE61E9839ACA9D96DB4; ANIMIA=FRE=1; ANON=A=363E8E1F42F56EBF1E2FA27CFFFFFFFF&E=1c52&W=2; KievRPSSecAuth=FAA6BBRaTOJILtFsMkpLVWSG6AN6C/svRwNmAAAEgAAACIy2ELJY4W7N+AMQjLMSWGbtmCyTrDlND5yxs7Zho4Ho/lxgSPu5c2JCACNQ0ntoSkxvwzRiAMRfeN+ktXw4fUVDKvmruBoTaKrRQNr6yqekmcDY35SwAfLyakhrMZWVM91Ny6LCcl0ShKrknudTsH94HanQZKYa75p5nnoXVwVc9W6E5IDVoa50iHdM/eEX/XPC70yDRMz9o0+nBBNwi9eYFRKTP5YBNB7pu+Rq2x/EFXWy7fWsM1laR6A5moRvuYy5jdxz1/O4gtEt6yhe/OVflSxDpGe66i8+1lG16fkMsDEKcGc37RW+3YBTHX5eBG/49/0LyRG3cvhWYxQOm48AX3FOfvCGPIy+mi8UHPEAXmp76PuB5SB7x1jS0pms/EvDex+XUddr90iByr8rJY5LpMd4yXyEAwagVxjH9F/zmnzKI7cXsctxIEo5AQPZhMzqF7omnM1eGo78MsDBHdBZoEjdHTIJdkCqNz5pgkyrvq6GqxdLhAUGgG17Hvl/qaWQ01PygtY5mLnS+I4W8J2APmqrMpbylI2apZipOPLmpf0zoyrcN1hel2pvO2jw0qb00eeS0FpQk7v7Tx4HMWaeOsOTPqtUOSxT5TuZ3pG987efWVOKzeMybOS/n+NgC0C0Nj2Lg5Xuu5baxlzCcUqwjC8Z0XHPIU7oxqg9kzYOX+a+jrpiEhECAqwRDoXhF6oeHHHzYUIV8ptCnWpt7MAGebI8mMs/ujuANsrN8XGkV19FzSb1rgjE5nUF6w7mtVkY0mrKbiRPLpO78ACvcOGALiVDBwwZUcLLUizToKHAVnhHLM7zsI3sPEReP3nA61symtU/tyF4ZWwdK/gQ5Cbr9go/ofbJfrEGLmT5+/+J0qsYKe2a/zeIJ+CmsjjLNYRB6SPK4aZX9oyl4j3xgm+9aMp5Tyzf6J3TtOe10gy8ASJK2WhMJPkc9zmcrdVXuw7yrI3HtpLUVP3q6dqGLKKlciB2xRbmTL16+At5sRdA/wFVng6kdwe1mfvqvNEN/hmv4vIc8NuXtdy0l9ihJ5+VZyYb/bHl27rFtZly2I4v4QlZcJqUDCd/zhFQZuQE2n68qORPC7yfS+jfcqOCjUGhSAW+WJ5T88cwa/Rc7RsG0ueuMz/guYsdAK6iv2X2X5ib5kE4GyCZYT+ugFz2TkVW2fWzPpzN8OAhSjg1hXRwE0B/MkBdDsl9PmeoS5I+E+7lhqhsGZR3YvRPPLv46heoAoQzxTk5pfAnMoHNzaNTTi2vEBBuvdjytAa+4YwYIk2GCrNEbaqsABjS/9E8Gv2JdsY4ZVOZFxw9PFX+JZp2ZQGVgMHmQCBuvAyshKpOCpznpwLDRwtuex1smc+kdgqvqRQA0X17csQ8QPST/kU40lL5AFEuSKA=; WLID=tHrtDXXyJq+VzfxRDyvEp8C1CUQyv2WPNe6NW15IyVkjDatCQxa+0dnTFFIGJ7Uv; SRCHS=PC=HCTS; msau=id=363E8E1F42F56EBF1E2FA27CFFFFFFFF&msa=1&aad=0; WLS=C=cf23b2cfcb4a25f9&N=%e5%be%b7%e5%8d%8e; SUID=A; _U=1Zr7buSeFCdGHH2BKOmZQdlWhlWRUhUPECM9t12p6KEoJBtpsk6lBUA8k8RQ09Ro-zazRCN1gWiWiXpLwCNAGMkWRj75upvo_72ZGvtGPjsT9fIoiM36lZQLBj0EP3Rvj2Cl48EQUwcFt2CYJhMntgEissvUNTgj-t11IrGRqjnb-dtSIe7NL5tIf3ODW6hABWUPkYGsJJrT88TGtKxed4CzqgA9bNgf2-L_vHrunRZQ; SRCHUSR=DOB=20230402&T=1684765118000&TPC=1684226723000; _EDGE_S=SID=38F0EE2B470460EE2724FD3D46DD613F&mkt=zh-cn&ui=zh-cn; ipv6=hit=1684769134971&t=4; _HPVN=CS=eyJQbiI6eyJDbiI6MTAsIlN0IjowLCJRcyI6MCwiUHJvZCI6IlAifSwiU2MiOnsiQ24iOjEwLCJTdCI6MCwiUXMiOjAsIlByb2QiOiJIIn0sIlF6Ijp7IkNuIjoxMCwiU3QiOjAsIlFzIjowLCJQcm9kIjoiVCJ9LCJBcCI6dHJ1ZSwiTXV0ZSI6dHJ1ZSwiTGFkIjoiMjAyMy0wNS0yMlQwMDowMDowMFoiLCJJb3RkIjowLCJHd2IiOjAsIkRmdCI6bnVsbCwiTXZzIjowLCJGbHQiOjAsIkltcCI6MTUzfQ==; USRLOC=HS=1&ELOC=LAT=28.09008026123047|LON=113.00614166259766|N=%E9%9B%A8%E8%8A%B1%E5%8C%BA%EF%BC%8C%E6%B9%96%E5%8D%97%E7%9C%81|ELT=2|&CLOC=LAT=28.090081063294967|LON=113.00614023251997|A=733.4464586120832|TS=230522141840|SRC=W; ABDEF=V=13&ABDV=13&MRNB=1684765555622&MRB=0; _RwBf=ilt=30&ihpd=1&ispd=1&rc=549&rb=549&gb=0&rg=0&pc=549&mtu=0&rbb=0.0&g=0&cid=&clo=0&v=4&l=2023-05-22T07:00:00.0000000Z&lft=0001-01-01T00:00:00.0000000&aof=0&o=0&p=bingcopilotwaitlist&c=MY00IA&t=2765&s=2023-04-02T13:31:40.2221847+00:00&ts=2023-05-22T14:25:56.2121178+00:00&rwred=0&wls=1&lka=0&lkt=0&TH=&mta=0&e=x0jWTre43ujbkgBQ-ShDq5afl2Tu4OZafOiuTC9qXxoHrCosYfkrgXvvuJXoAgyT53kBYXtOhuhyQ2Ok6n9rHQ&A=; _SS=SID=201EFC777B14642A305AEF797A1C6567&R=549&RB=549&GB=0&RG=0&RP=549&PC=HCTS; SRCHHPGUSR=SRCHLANG=zh-Hans&BRW=HTP&BRH=M&CW=893&CH=841&SCW=1164&SCH=4448&DPR=1.5&UTC=480&DM=1&WTS=63820015220&HV=1684765556&PV=14.0.0&PRVCW=893&PRVCH=841&NEWWND=0&NRSLT=50&LSL=0&AS=1&ADLT=DEMOTE&NNT=1&HAP=0&VSRO=1&CHTRSP=1&BZA=0&EXLTT=3"""
        }
        resp = await self.request_get(url, headers=headers, params=params, use_ip=use_ip)
        return resp.text

    async def get_source(self, querry, num):
        """获取搜索结果源码"""
        try:
            result = await self.search(querry, num)
            return {'success': True, 'keyword': querry, 'result': result}
        except Exception as err:
            print(err)
            return {'success': False, 'keyword': querry, 'info': str(err)}

    async def get_data(self, querry, num):
        """获取搜索结果data数据"""
        resp_text = await self.search(querry, num)
        count_ = re.findall('约 (.*?) 个结果', resp_text)
        count = int(count_[0].replace(',', '')) if len(count_) > 0 else None
        tree = etree.HTML(resp_text)
        lis = tree.xpath('//main/ol/li[@class="b_algo"]')
        datas = []
        for index, li in enumerate(lis):
            title = li.xpath('.//h2')[0].xpath('string(.)').strip()
            real_url = li.xpath('.//h2/a/@href')[0]
            full_domain, root_domain = self.func.get_domain_info(real_url)[1:]
            des = des_p[0].xpath('string(.)').strip() if len(des_p:=li.xpath('.//p'))>0 else ''
            des = des[2:] if des.startswith('网页') else des
            print(index+1, title, real_url,des)
            datas.append({"id": index + 1, "title": title, "full_domain": full_domain, "domain": root_domain, "link": real_url,'des': des})
        # 相关搜索 关键词
        related = tree.xpath('//div[@id="brsv3"]/ul/li/a/div[2]/text()')
        return {"keyword": querry, "count": count,"related": related, "data": datas, 'success': True}
    
    async def get_include(self, querry, num):
        """获取收录详情数据"""
        try:
            full_domain, domain = self.func.get_domain_info(querry)[1:]
            if "." not in domain:
                return {'querry': querry, 'info': f'{querry} 非法域名', 'success': False}
            # 查询site收录
            link = f"site:{full_domain}"
            resp_text = await self.search(link,num)
            include_ = re.findall('约 (.*?) 个结果',resp_text)
            include = int(include_[0].replace(',','')) if len(include_)>0 else None
            if include is None:
                return {"querry": querry, 'success': False, 'info': '必应验证码','from':self.config['【网站信息】']['程序名称']}
            tree = etree.HTML(resp_text)
            lis = tree.xpath('//main/ol/li[@class="b_algo"]')
            datas = []
            for index, li in enumerate(lis):
                title = li.xpath('.//h2')[0].xpath('string(.)').strip()
                real_url = li.xpath('.//h2/a/@href')[0]
                full_domain, root_domain = self.func.get_domain_info(real_url)[1:]
                des = li.xpath('.//p')[0].xpath('string(.)').strip()
                des = des[2:] if des.startswith('网页') else des
                print(index+1, title, real_url,des)
                datas.append({"id": index + 1, "title": title, "full_domain": full_domain, "domain": root_domain, "link": real_url,'des': des})
            return {"domain":full_domain,'querry': querry, 'include': include,"data": datas, 'success': True}
        except Exception as err:
            print(err)
            return {'querry': querry, 'info': str(err), 'success': False}


    async def get_pulldown(self, querry):
        """必应下拉词"""
        try:
            url = f"https://www.bing.com/AS/Suggestions?pt=page.home&mkt=zh-hk&qry={querry}&cvid=D23745981EC043668D16F70778716DD4"
            use_ip = await self.func.use_ip('bing')
            transport = httpx.AsyncHTTPTransport(local_address=use_ip)
            async with httpx.AsyncClient(transport=transport) as client:
                resp = await client.get(url, timeout=15)
            tree = etree.HTML(resp.text)
            pull_down_words = tree.xpath('//ul/li/@query')
            return {"keyword": querry, "pull_down_words": pull_down_words, 'success': True}
        except Exception as err:
            print(err)
            return {'keyword': querry, 'info': str(err), 'success': False}

