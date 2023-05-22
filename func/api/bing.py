# -*- coding: UTF-8 -*-
"""必应功能"""

import random
import os
import re
from urllib.parse import quote, unquote
from fake_useragent import UserAgent
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

    async def request_get(self, url, headers=None, params=None, use_ip='127.0.0.1'):
        """异步访问"""
        transport = httpx.AsyncHTTPTransport(local_address=use_ip)
        print(url,use_ip)
        async with httpx.AsyncClient(
                headers=headers, params=params, http2=True, transport=transport) as client:
            resp = await client.get(url)
        return resp

    @retry(stop=stop_after_attempt(2))
    async def search(self, querry, num,ip_trans=False):
        """搜索查询"""
        text = unquote(querry)
        url = 'https://www.bing.com/search'
        params = {
            "q": text,
            "qs": "n",
            "pq": "fges",
            "mkt": "zh-CN", 
        }
        use_ip = await self.func.use_ip('bing')
        # print(muid)
        # user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.62"
        # user_agent = "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm) Chrome/103.0.5060.134 Safari/537.36"
        user_agent = UserAgent().random
        muid = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz'.upper()+"0123456789",k=32))
        headers = {
            "user-agent": user_agent,
            "referer": "https://www.bing.com/",
            "cookie": f"f_EDGE_V=1; SRCHHPGUSR=NRSLT=50; MUID={muid};"
            # "cookie": f"f_EDGE_V=1; SRCHHPGUSR=NRSLT=50;"
        }
        if ip_trans or use_ip=='0.0.0.0':
            ip_trans_client = IpTrans(headers)
            resp = await ip_trans_client.request_get(url, params=params)
        else:
            resp = await self.request_get(url, headers=headers, params=params, use_ip=use_ip)
        print(resp.text)

        if '<h1>没有与此相关的结果' in resp.text:
            resp = await self.search(querry,num,ip_trans=True)
            # print(f"{use_ip} 被禁 删除")
            if use_ip!='0.0.0.0':
                print(f"{use_ip} bing被禁 删除")
                path_dir = os.path.join("cache", arrow.now("Asia/Shanghai").format('YYYY-MM-DD'))
                use_ips_path = os.path.join(path_dir, "bing_ips.txt")
                async with aiofiles.open(use_ips_path, "r", encoding='utf-8')as txt_f:
                    ips_text = await txt_f.read()
                new_ips_text = ips_text.replace(use_ip,'')
                async with aiofiles.open(use_ips_path, "w", encoding='utf-8')as txt_f:
                    await txt_f.write(new_ips_text)
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

