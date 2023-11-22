# -*- coding: UTF-8 -*-
"""谷歌功能"""

import random
import re
from urllib.parse import quote, unquote
from fake_useragent import UserAgent
import httpx
from lxml import etree
from tenacity import retry,stop_after_attempt



class Google():
    """谷歌功能"""

    def __init__(self,func):
        self.func = func
        self.config= self.func.get_yaml('config/config.yml')

    async def request_get(self, url, headers=None, params=None, use_ip='127.0.0.1'):
        """异步访问"""
        transport = httpx.AsyncHTTPTransport(local_address=use_ip)
        async with httpx.AsyncClient(
                headers=headers, params=params, http2=True, transport=transport) as client:
            resp = await client.get(url)
        return resp

    @retry(stop=stop_after_attempt(2))
    async def search(self, querry,num):
        """搜索查询"""
        text = unquote(querry)
        url = 'https://www.google.com/search'
        params = {"q": text,
                  "oq": text,
                  "source": "hp",
                  "sclient": "gws-wiz",
                  "newwindow": 1,
                  "hl": "zh-CN",
                #   "lr": "lang_zh-CN",
                  "num": num}
        use_ip = await self.func.use_ip('google')
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 APIs-Google (+https://developers.google.com/webmasters/APIs-Google.html)"
        headers = {
            "user-agent": user_agent,
            "referer": "https://www.google.com/",
        }
        resp = await self.request_get(url, headers=headers, params=params, use_ip=use_ip)
        return resp.text

    async def get_source(self, querry,num):
        """获取搜索结果源码"""
        try:
            result = await self.search(querry,num)
            result = result.replace('="/images/branding/googlelogo/2x/googlelogo_color_92x30dp.png"',
            '="https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_92x30dp.png"')
            return result
        except Exception as err:
            print(err)
            return {'keyword': querry, 'info': str(err)}
    
    async def get_data(self, querry,num):
        """获取搜索结果data数据"""
        try:
            resp_text = await self.search(querry,num)
            count_ = re.findall('找到约 (.*?) 条',resp_text)
            count = int(count_[0].replace(',','')) if len(count_)>0 else None
            if count is None:
                return {"querry": querry, 'success': False, 'info': '谷歌验证码','from':self.config['【网站信息】']['程序名称']}
            tree = etree.HTML(resp_text)
            divs = tree.xpath('//div[@class="yuRUbf"]')
            datas = []
            for index, div in enumerate(divs):
                try:
                    title = div.xpath('.//h3')[0].xpath('string(.)').strip()
                    print(title)
                    real_url = div.xpath('./div/span/a/@href')[0]
                    print(real_url)
                    full_domain, root_domain = self.func.get_domain_info(real_url)[1:]
                    des = div.xpath('../..//div[@data-snf="nke7rc"]')[0].xpath('string(.)').strip()
                    datas.append({"id": index + 1, "title": title,
                                    "full_domain": full_domain, "domain": root_domain, "link": real_url,'des': des})
                except Exception as err:
                    print(index, err)

            # 相关搜索 关键词
            related = tree.xpath('//div[@data-hveid="data-hveid"]/a//b/text()')
            related = tree.xpath('//div[@class="s75CSd OhScic AB4Wff"]//b/text()') if related == [] else related
            related = tree.xpath('//div[@class="wQiwMc related-question-pair"]//span/text()') if related == [] else related
            # 其他人搜
            more = tree.xpath('//span[@class="CSkcDe"]/text()')
            more = tree.xpath('//span[@class="JCzEY ZwRhJd"]/span/text()') if more == [] else more
            return {"keyword": querry,"count":count, "related": related, "more":more,"data": datas,'success': True}
        except Exception as err:
            print(err)
            return {'keyword': querry, 'info': str(err), 'success': False}

    async def get_include(self, querry, num):
        """获取收录详情数据"""
        try:
            full_domain, domain = self.func.get_domain_info(querry)[1:]
            if "." not in domain:
                return {'querry': querry, 'info': f'{querry} 非法域名', 'success': False}
            # 查询site收录
            link = f"site:{full_domain}"
            resp_text = await self.search(link,num)
            include_ = re.findall('找到约 (.*?) 条',resp_text)
            include = int(include_[0].replace(',','')) if len(include_)>0 else None
            if include is None:
                return {"querry": querry, 'success': False, 'info': '谷歌验证码','from':self.config['【网站信息】']['程序名称']}
            tree = etree.HTML(resp_text)
            divs = tree.xpath('//div[@class="yuRUbf"]')
            datas = []
            for index, div in enumerate(divs):
                try:
                    title = div.xpath('.//h3')[0].xpath('string(.)').strip()
                    real_url = div.xpath('./a/@href')[0]
                    full_domain_, root_domain_ = self.func.get_domain_info(real_url)[1:]
                    des = div.xpath('../..//div[@data-snf="nke7rc"]')[0].xpath('string(.)').strip()
                    datas.append({"id": index + 1, "title": title,
                                    "full_domain": full_domain_, "domain": root_domain_, "link": real_url,'des': des})
                except Exception as err:
                    print(index, err)
            return {"domain":full_domain,'querry': querry, 'include': include,"data": datas, 'success': True}
        except Exception as err:
            print(err)
            return {'querry': querry, 'info': str(err), 'success': False}

    async def get_pulldown(self, querry):
        """谷歌下拉词"""
        try:
            url = f"https://www.google.com/complete/search?q={querry}&client=gws-wiz-serp&xssi=t&hl=zh-CN&authuser=0"
            use_ip = await self.func.use_ip('google')
            transport = httpx.AsyncHTTPTransport(local_address=use_ip)
            async with httpx.AsyncClient(transport=transport) as client:
                resp = await client.get(url, timeout=15)
            pull_down_words = []
            result_list = eval(resp.text.split('\n')[1])[0]
            for i in result_list:
                pull_down_words.append(i[0])
            return {"keyword": querry, "pull_down_words": pull_down_words, 'success': True}
        except Exception as err:
            print(err)
            return {'keyword': querry, 'info': str(err), 'success': False}
