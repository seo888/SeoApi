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
        async with httpx.AsyncClient(
                headers=headers, params=params, http2=True, transport=transport) as client:
            resp = await client.get(url)
        return resp

    @retry(stop=stop_after_attempt(2))
    async def search(self, querry, num):
        """搜索查询"""
        text = unquote(querry)
        url = 'https://www.bing.com/search'
        params = {
            "q": text,
            "qs": "n",
            "from": 'QBRE',
            "sp": '-1',
            "lq": '0',
            "pq": 'python',
            "setlang": "zh-Hans", }
        use_ip = await self.func.use_ip('bing')
        # user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.62"
        user_agent = "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm) Chrome/103.0.5060.134 Safari/537.36"
        headers = {
            "user-agent": user_agent,
            "referer": "https://www.bing.com/",
            "cookie": 'SRCHHPGUSR=NRSLT=50;'
            # "cookie": f"""cookie: _EDGE_V=1; MUID=00419F979B86634206618D2D9AE062D5; SRCHD=AF=NOFORM; MUIDV=NU=1; SRCHUID=V=2&GUID=256205A9E4BE4D4A8DF6983319249A22&dmnchg=1; MicrosoftApplicationsTelemetryDeviceId=cce78f19-63b8-4542-bec9-2cf7f30f88b4; _UR=QS=0&TQS=0; _tarLang=default=zh-Hans; _TTSS_IN=hist=WyJlbiIsImF1dG8tZGV0ZWN0Il0=; _TTSS_OUT=hist=WyJ6aC1IYW5zIl0=; _clck=1gt3u0r|1|fah|0; Imported_MUID=3E162B4FADD96BE61E9839ACA9D96DB4; MUIDB=00419F979B86634206618D2D9AE062D5; ABDEF=V=13&ABDV=13&MRNB=1683385093529&MRB=0; .AspNet.ExternalCookie=LOj52DvTo_ltkhiuYyQb4cagxBdy8ALO0zO5hc-tqXkRVs9sMCpfPcygkfYOoMSE9-0v-euw4Wph3MsTGA93a0hNWuK1YtABX-DEFOaqA-TYvR6C8GnD81b3cNzsd1ONxbaXE1g8caDMoF4BONGRykQxoBlccLQV22vFLhq_ky6UWaq3H5Ofw_mNM9r1b3B0dMr5Vz8PmaV6L-UVsFBW5R883saKkyOV4pr48Pfuqh_ADesG5mzCC6yOUVdJ4dmQUqsAKA69wyl1jE9ILJs2_6jbraiLIpF0Gmj378Se1evPFsxi_jtdG5-vOZjvYS9Q_yHenBuOSpGdXGlQVoyFz5zruK7tI-F-GlfnyMTZ17taWaBKzkqpKKDvEDywrMwouH7H9d7pt_Dd2MpBHyZJXWN3IlbjDURTOzNZL_luvKYIhewiR_YtDUBGsNizG1YVW_DY_xb35q1Bjb3RYsu_SO79mZfbic_qBE9D4r-I0IsdcHsDvOFYis39pEz2IqBkkKXAyMvm6VV-PeYy3fbH8JljT6nBiZSkgkCLBXK4epx6CJeAwGawJIDlCQLsWBdZozgesHh436oX61yqcbhOqI1cz-1_NnoFiiA4sN32ZoyXhjUVDHXHYzEuDB_O0ZRrpiLYfIKobiaf4Y6foKu1-ULa_8-pJ1vueqUvtJi4IiFnhmHxJ6WpaSAFewmtpXVwjpEiJfkld7uMpiDA4KjbnnZUtqNGJgAGcVvOqvGZU5I2WxG1fbr-2duBD9z9mD6sxPPPtf3c_Q7_QQYzNCp4Ogw5YgbHYBfzxu2ULa3yMTR0scqBBZW8mK5xHEItr3rljTgyGXcDEIEn3Q3VlkrqCiUCOZ_jkiV_Qg5WyCHFLCQpsyq8anJqriaa5bdqywaQRInqEdV2Znh6AZv4dN35WnKdl7n-jkOg1Nmr6myqtvM&BWTUserCookie=AAEAAMqcu0XfV4EUB99HvL0jnU49TNxaNJAc2871MIOKaSyEJKVNSCuHXHTFiUSVZO2K1QMjqYp0WgaB+lHuS6aBqbkjRMpoO7fJxbIV0AWIednxBO7EYkkMqi8SlYkLyZyZAyIl3t+AsQXfe8cg5gepGl5E+QY/NK4iSj1/PUZj3MiK7MWJZC1MBhKAn3+Rawv1Kmz0VkhermtmtUGNcmogxY7cL/GfKYvhY5oe/3pKQ5BRTXOprMGWyCf/BQNzo9dzswKUMGQqZsp6vbxUF0q4GMgXKc+w0+yWLp0bX+KCZXL4cTlZRnfgOJI9trnhRPS/9BB8i4RMRA1TyV3geXvWJmKQ6U9HbPvIccBf8IYN+pt/z9i6UaH0q5JTFGz1neJSqQABAAB65WGR/6qDS/UkXCYiaM840hdO9+T9HppUtrVLkO7dBpK5hIQW5m5pCq3m9SwpO7h+jr0bGB67YfGkbrkO2oYhgkSdz9iFz2JLU+rnffbTo5CV5fWyk/MKrAzFjwmIjtGnX6nvBca/8mk8CRb6bPaw5SPLKYfiklyxlfGFjetYBmucu90gRJK7wuHhknH3sTA3yWW1blAhiwc/FoiqQX2+FRlgNW9hyEfE9N+7QLzrmO3fX3GFplvtxaX3uiKuDYD9/D+nWlcI8xYTxAXkWGclqnXep+fJ95D3YBulW/UdQ+rfgSA7xwI8SX0mKr6CywIswVe0UEKVmi6dkOkcQgZLUAIAAOsDUgj1/llKJBYX9nucJW8vCTKeByjDIZhXhXHarJRLwN6NAr1djRSVT0QqMpR8mOehRi3F3NlpeClayHWk1q7HUz/yem+ixDgfKcrn9DbLQQqegFJWz9N3JNT1GRkUqcnemTQcX/aBx6H9vvpGnyDj9cw8eKfQ0u02wOtSKmmxc4irnu0nphgZMxY9dOxTeOJ0KkRprMOJXTHBQ7GFqyNPxEJ5ASLXME0lk2n/AjjuDbWUhIFO8oju356G2fKSoN4z0tHP8aaKG/LT+ChPyvYPbLcW9hrmcPcK4FddcS3tBwVQrr4e3OBoub2Sd2lbQjQqD76mefawMaFOraWyGm2N+TU55Tr+DrQTrRsVVu2QTGMI+US6BFx7WSJYETxbE5NtW8XyN0/oLYHOOoYvDyUE0ElP3PgD3CXCd4zU75nRWZTw7euLZE2I7m7nW5K93xqkrQO3Wx/IL7+hCvQu9KvC/EKscRKZEe/mWi1Embcqu7nyPqr5zgrAz/jTL32GGopczaB8csJfYIkHEGoOg+DxPLf2ueAZ+7QOxwQZIKlu6vQgkubMPozjMr0vTcjNPUJXYNOz22wwTbhBD9bHeYTbkEgNrgOLc/AlOX1rGvvuUBV+tE5eSdcoRGW2zz3Z5x5C7tfAguRshSCmEc36nJozRjT65Cpladl4Wz5YYx0BJBqW5x9NeBtePHrhYNHMtyohpzaFOL1cvWw5a/TylIEdTOVP2jlJxrX2GpKL25pEbKGMSTlDVgGnACza9L4ic9GKOp4/U7xJN0WKhMzokwk=; ai_user=hFINA4XcTaMZWXFiIQYmBY|2023-05-08T12:35:09.310Z; ANIMIA=FRE=1; WLID=3I7fPft1JxlCQNOtHUBOgyIoHIlMvPjOO7nMr1/qjTMGKAIN0De5Rx6Wo7LaxDdByh/tjfTQSTPA+DhRYRY27Wj9GIxTNH3mW00BJHGCSKY=; ANON=A=363E8E1F42F56EBF1E2FA27CFFFFFFFF&E=1c52&W=2; WLS=C=cf23b2cfcb4a25f9&N=%e5%be%b7%e5%8d%8e; SUID=A; _U=1PtLDYBzDvDjv3vSruRuk96aRTH5crDIZwmYE_2WnRGBGKa7wJICkOLuBAb_VEErEJKCJk0wqs5UfprKhOpgNXOZ4AOsgy_95Oq05k1SrexUxuWSt4XAJLU28X1aWbJdFIORZClo4F3oK1nsgWezISRVLaNcKzwIWL1jrwdp6EA5YP8Gw3pGBPoJqTJMiDXEgxRKMNsU0PvFhMd6fCrKeILqyAfFFNvAqnnogR6uks7I; SRCHUSR=DOB=20230402&T=1684316670000&TPC=1684226723000&POEX=W; ipv6=hit=1684320271048&t=4; USRLOC=HS=1&ELOC=LAT=28.090974807739258|LON=113.00442504882812|N=%E9%9B%A8%E8%8A%B1%E5%8C%BA%EF%BC%8C%E6%B9%96%E5%8D%97%E7%9C%81|ELT=2|&CLOC=LAT=28.090974940390414|LON=113.0044224201238|A=733.4464586120832|TS=230516171008|SRC=W; SRCHS=PC=HCTS; CSRF=QUFFQUFGOWc4OXZkR09hMC9wT0huSVFRUnFDMnozejF5TUU3YlRqdTd4TjdoYWVobWxwYU1SaytwLzMzT2xMZzZwdGVBbkxkNDkvQS9qdk0ydUoxcUhtMVJOWWxWZjl5eUwvOFV3dC9VOFUzV3NLSGVYbnNOZy9obmxHbUh4TmlxNmg1enJTZFdQWDEvMDlZVXNlUk1KdjdhZTRtVnJ2c1JUbGMrWnZjMzNxTkkvYVlHczljeEFTSUFyNUVXaDZnQWs1WFNQSmd1YWpJY21hVGlGenhtdkk1RVNNTTA3Ri9JRWl5VkxCdnVCSWpQdTlldTlzR2lqeXp1UldYRlBBaFN1Qy9CNGdVVU9zUk9rd0hGWjAxczFaalAxWktHSnEzNFpyMjhUMzBtYVEzd2NNS1lnME5uYzhSS3NjZm5xdldpbkZmVDg3Vmg5Vk1rRW1kOVJFNURaSUZmYitRNlU5SGJQdkljY0JmOElZTitwdC96OWk2VWFIMHE1SlRGR3oxbmVKU3FRQUJBQUJHN3A0V0FQT2ZCSVFrcUMvd29INGRmdzQ2eVNIbDlkMmx3WDdIT3VaWktuTjNrYlBKSEsycFNrQVJLRjB5aVk0MFVDRm5XUlBHQ1RiNHl1QmpGa1pSUlVuZEwwcmpoNGltSFAvZVg3cVpQQ05GZ0tPSmt3SUdKTjA5ajhnd01JYWczczMyd0RuUnBnVEpXbzVMVDlJV3BEMVluUmtzV3IzTjhkN3VRSDQ3eU8wNitwQUZydEd5ME1WQTRYQjgwVHJPZWc1VHJQS1NMTVA5ellxbUE2Z1B1eWZuRDdzcXl5THZFQ0VmWFErNTArZG9QR1BNVUJBcFYrU0xhbFdUdG1TKzFmL2c1bVNHeUlRZElKeDlUTmw1TitTZmZiZnZ4MmlXSGVmSVQ1U1BkN0FvNElnb291cjB4dTUyWWxjL2t4R0E0RkxJWVRNU1lpWHYrNEp5M1FXNVVBQUFBRmlrTit3Y3A0dlkwN3c1TnRRUWFubUhHM2N0UmNCRWJLb2tvYStEaTd2TTF0U2NHYit2cGJJeXR5NTdiRXc3QjF0dUdxS3ZaTmVSalkvNnQ2MnhSYWt6dWJIL1I2MzZsY3U4c3NhNFBqcGU%3D; _HPVN=CS=eyJQbiI6eyJDbiI6OSwiU3QiOjAsIlFzIjowLCJQcm9kIjoiUCJ9LCJTYyI6eyJDbiI6OSwiU3QiOjAsIlFzIjowLCJQcm9kIjoiSCJ9LCJReiI6eyJDbiI6OSwiU3QiOjAsIlFzIjowLCJQcm9kIjoiVCJ9LCJBcCI6dHJ1ZSwiTXV0ZSI6dHJ1ZSwiTGFkIjoiMjAyMy0wNS0xN1QwMDowMDowMFoiLCJJb3RkIjowLCJHd2IiOjAsIkRmdCI6bnVsbCwiTXZzIjowLCJGbHQiOjAsIkltcCI6MTUzfQ==; SRCHHPGUSR=SRCHLANG=zh-Hans&BRW=HTP&BRH=M&CW=885&CH=841&SCW=885&SCH=841&DPR=1.5&UTC=480&DM=1&WTS=63819823516&HV=1684317826&PV=14.0.0&PRVCW=1707&PRVCH=841&NEWWND=0&NRSLT={num}&LSL=0&AS=1&ADLT=DEMOTE&NNT=1&HAP=0&VSRO=1&CHTRSP=1&BZA=0&EXLTT=3; _RwBf=ilt=28&ihpd=2&ispd=4&rc=519&rb=519&gb=0&rg=0&pc=519&mtu=0&rbb=0.0&g=0&cid=&clo=0&v=5&l=2023-05-17T07:00:00.0000000Z&lft=0001-01-01T00:00:00.0000000&aof=0&o=0&p=bingcopilotwaitlist&c=MY00IA&t=2765&s=2023-04-02T13:31:40.2221847+00:00&ts=2023-05-17T10:03:46.6312518+00:00&rwred=0&wls=1&lka=0&lkt=0&TH=&mta=0&e=x0jWTre43ujbkgBQ-ShDq5afl2Tu4OZafOiuTC9qXxoHrCosYfkrgXvvuJXoAgyT53kBYXtOhuhyQ2Ok6n9rHQ&A=; _SS=SID=201EFC777B14642A305AEF797A1C6567&R=519&RB=519&GB=0&RG=0&RP=519&PC=HCTS; _EDGE_S=SID=0F751F5E3D3464F906310C4D3C3C65B5&mkt=zh-cn; ai_session=azvatMXHsvesceJiRw4J9R|1684316671089|1684317826367"""
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

