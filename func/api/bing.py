# -*- coding: UTF-8 -*-
"""必应功能"""

import random
import os
import re
from urllib.parse import quote, unquote
from fake_useragent import UserAgent
from fastapi import Response
from starlette.responses import JSONResponse, RedirectResponse, FileResponse
import httpx
from lxml import etree
from tenacity import retry, stop_after_attempt
import aiofiles
import arrow
from func.api.ipTrans import IpTrans


class Bing():
    """必应功能"""
    def __init__(self, func):
        self.func = func
        self.config = self.func.get_yaml('config/config.yml')
        self.root = 'https://cn.bing.com'

    async def request_get(self, url, headers=None, params=None, use_ip='127.0.0.1',ip_trans=False):
        """异步访问"""
        try:
            url = url.replace('//www.bing','//cn.bing')
            if ip_trans or use_ip=='0.0.0.0':
                ip_trans_client = IpTrans(headers)
                if params is None:
                    resp = await ip_trans_client.request_get(url)
                    print(f'使用代理访问：{url}')
                else:
                    resp = await ip_trans_client.request_get(url, params=params)
                    print(f'使用代理访问：{url} {params}')
            else:
                transport = httpx.AsyncHTTPTransport(local_address=use_ip)
                if params is None:
                    async with httpx.AsyncClient(headers=headers, transport=transport) as client:
                        resp = await client.get(url)
                else:
                    async with httpx.AsyncClient(headers=headers, params=params, transport=transport) as client:
                        resp = await client.get(url)
                print(f'使用IP[{use_ip}]访问：{url}')
            return resp
        except Exception as err:
            print(err)
            return ''

    def get_headers(self,num):
        """生成headers"""
        user_agent = UserAgent().random
        headers = {
            "user-agent": user_agent,
            "referer": f"{self.root}/search",
            "cookie": """MUID=1577447F8A9B691E3D7557AD8B3268AB; _EDGE_V=1; MUIDB=1577447F8A9B691E3D7557AD8B3268AB; _UR=QS=0&TQS=0; _HPVN=CS=eyJQbiI6eyJDbiI6MSwiU3QiOjAsIlFzIjowLCJQcm9kIjoiUCJ9LCJTYyI6eyJDbiI6MSwiU3QiOjAsIlFzIjowLCJQcm9kIjoiSCJ9LCJReiI6eyJDbiI6MSwiU3QiOjAsIlFzIjowLCJQcm9kIjoiVCJ9LCJBcCI6dHJ1ZSwiTXV0ZSI6dHJ1ZSwiTGFkIjoiMjAyMy0xMS0yM1QwMDowMDowMFoiLCJJb3RkIjowLCJHd2IiOjAsIlRucyI6MCwiRGZ0IjpudWxsLCJNdnMiOjAsIkZsdCI6MCwiSW1wIjoxLCJUb2JicyI6MH0=; ipv6=hit=1700724335448&t=4; MicrosoftApplicationsTelemetryDeviceId=781d5c7c-3264-49c1-8282-fd3f730fbe6d; ai_session=eT5M0kXAgwBGKlFhWLMh2Q|1700720735889|1700720735889; _EDGE_S=F=1&SID=09FAA36D8110616A045AB0BF80B960C6&mkt=en-my; USRLOC=HS=1&ELOC=LAT=3.1411919593811035|LON=101.71832275390625|N=Bandar%20Kuala%20Lumpur%EF%BC%8C%E5%90%89%E9%9A%86%E5%9D%A1|ELT=4|; SRCHHPGUSR=SRCHLANG=zh-Hans&IG=598F117895BA401290C413D5F6F95E27&PV=15.0.0&BRW=HTP&BRH=T&CW=896&CH=1365&SCW=1196&SCH=7581&DPR=1.5&UTC=480&DM=0&HV=1700720799&PRVCW=2552&PRVCH=1365&EXLTT=4&EXLKNT=1&NRSLT=50&LSL=0&AS=1&ADLT=OFF&NNT=1&HAP=0&VSRO=1&CHTRSP=1&SRTOBRR=2&CIBV=1.1359.7"""
        }
        return headers

    # @retry(stop=stop_after_attempt(2))
    async def search(self, querry, num,ip_trans=True):
        """搜索查询"""
        text = unquote(querry)
        url = f'{self.root}/search'
        params = {
            "q": text,
            "qs": "n",
            "form": "QBRE",
            "sp": "-1",
            "lq": "0",
            "sc": "0-0",
            "ghsh": "0",
            "ghacc": "0",
            "mkt": "zh-CN", 
        }
        use_ip = await self.func.use_ip('bing')
        headers =self.get_headers(num)
        resp = await self.request_get(url, headers=headers, params=params, use_ip=use_ip,ip_trans=ip_trans)
        if resp=='':
            return ''

        if '<h1>没有与此相关的结果' in resp.text:
            resp_text = await self.search(querry,num,ip_trans=True)
            if use_ip!='0.0.0.0':
                print(f"{use_ip} bing被禁 删除")
                path_dir = os.path.join("cache", arrow.now("Asia/Shanghai").format('YYYY-MM-DD'))
                use_ips_path = os.path.join(path_dir, "bing_ips.txt")
                async with aiofiles.open(use_ips_path, "r", encoding='utf-8')as txt_f:
                    ips_text = await txt_f.read()
                new_ips_text = ips_text.replace(use_ip+"\n",'\n')
                async with aiofiles.open(use_ips_path, "w", encoding='utf-8')as txt_f:
                    await txt_f.write(new_ips_text)
            return resp_text
        return resp.text
        
    async def get_source(self, querry, num):
        """获取搜索结果源码"""
        try:
            result = await self.search(querry, num,ip_trans=True)
            return {'success': True, 'keyword': querry, 'result': result}
        except Exception as err:
            print(err)
            return {'success': False, 'keyword': querry, 'info': str(err)}

    async def get_data(self, querry, num):
        """获取搜索结果data数据"""
        resp_text = await self.search(querry, num,ip_trans=True)
        if resp_text=='':
            return {"keyword": querry, 'info': f'{querry} 代理访问失败', 'success': False}
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
            resp_text = await self.search(link,num,ip_trans=True)
            if '<h2>Object moved to' in resp_text:
                return {"querry": querry, 'success': False, 'info': 'Object moved to','from':self.config['【网站信息】']['程序名称']}
            include_ = re.findall('约 (.*?) 个结果',resp_text)+re.findall('共 (.*?) 条',resp_text)
            include = int(include_[0].replace(',','')) if len(include_)>0 else None
            if include is None:
                return {"querry": querry, 'success': False, 'info': '必应验证码','from':self.config['【网站信息】']['程序名称']}
            tree = etree.HTML(resp_text)
            next_url = tree.xpath('//a[@title="下一页"]/@href')
            next_url = quote(self.root+unquote(next_url[0])) if len(next_url)>0 else None
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
            return {"domain":full_domain,'querry': querry, 'include': include,"data": datas, 'next_url':next_url,'success': True}
        except Exception as err:
            print(err)
            return {'querry': querry, 'error': str(err), 'success': False,'from':self.config['【网站信息】']['程序名称']}
        
    async def get_include_next(self, querry,num):
        """获取下一页收录详情数据"""
        try:
            url = unquote(querry)
            headers = self.get_headers(num)
            use_ip = await self.func.use_ip('bing')
            resp = await self.request_get(url, headers=headers,use_ip=use_ip)
            # with open('1.html','w',encoding='utf-8')as f:
            #     f.write(resp.text)
            if '<h1>没有与此相关的结果' in resp.text:
                resp = await self.request_get(url, headers=headers,ip_trans=True)
            resp_text = resp.text
            if '<h2>Object moved to' in resp_text:
                return {"querry": querry, 'success': False, 'info': 'Object moved to','from':self.config['【网站信息】']['程序名称']}
            include_ = re.findall('约 (.*?) 个结果',resp_text)+re.findall('共 (.*?) 条',resp_text)
            include = int(include_[0].replace(',','')) if len(include_)>0 else None
            tree = etree.HTML(resp_text)
            next_url = tree.xpath('//a[@title="下一页"]/@href')
            next_url = quote(self.root+unquote(next_url[0])) if len(next_url)>0 else None
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
            return {"domain":full_domain,'querry': querry, 'include': include,"data": datas, 'next_url':next_url,'success': True}
        except Exception as err:
            print(err)
            return {'querry': querry, 'error': str(err), 'success': False,'from':self.config['【网站信息】']['程序名称']}


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

