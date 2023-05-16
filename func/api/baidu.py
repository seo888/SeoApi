# -*- coding: UTF-8 -*-
"""百度功能"""

import json
import linecache
import os
import random
import re
from urllib.parse import unquote
import aiofiles
import arrow
from fake_useragent import UserAgent
import httpx
from lxml import etree
from tenacity import retry,stop_after_attempt


class Baidu():
    """百度功能"""

    def __init__(self, func):
        self.func = func
        self.config= self.func.get_yaml('config/config.yml')
        os.makedirs("cookie_cache", exist_ok=True)

    async def request_get(self, url, headers=None, params=None, use_ip='127.0.0.1'):
        """异步访问"""
        transport = httpx.AsyncHTTPTransport(local_address=use_ip)
        async with httpx.AsyncClient(
                headers=headers, params=params, http2=True, transport=transport) as client:
            resp = await client.get(url)
        return resp

    async def get_cookie(self, use_ip):
        """获取cookie"""
        url = 'http://www.baidu.com'
        user_agent = UserAgent().random
        user_agent = f"{user_agent} (compatible; baidumib;mip; + https://www.mipengine.org)"
        headers = {'User-Agent': user_agent}
        transport = httpx.AsyncHTTPTransport(local_address=use_ip)
        async with httpx.AsyncClient(http2=True, transport=transport) as client:
            resp = await client.get(url, headers=headers)
        cookie = resp.headers['set-cookie'].strip()
        return {"cookie": cookie, "User-Agent": user_agent, 'use_ip': use_ip}

    @retry(stop=stop_after_attempt(2))
    async def search(self, querry, num):
        """搜索查询"""
        text = unquote(querry)
        url = "http://www.baidu.com/s"
        params = {"wd": text,
                  "rn": num,
                  "ie": "UTF-8"}
        use_ip = await self.func.use_ip('baidu')
        ip_path_dir = os.path.join("cookie_cache", arrow.now(
            "Asia/Shanghai").format('YYYY-MM-DD'))
        os.makedirs(ip_path_dir, exist_ok=True)
        ip_path = os.path.join(ip_path_dir, use_ip)+".json"
        if not os.path.exists(ip_path):
            # 生成cookie并写入本地
            cache = await self.get_cookie(use_ip)
            async with aiofiles.open(ip_path, "w", encoding='utf-8')as json_f:
                await json_f.write(json.dumps(cache))
        else:
            linecache.checkcache(ip_path)
            cache_text = "".join(linecache.getlines(ip_path))
            cache = json.loads(cache_text)
        headers = {'User-Agent': cache["User-Agent"],
                   'Accept': 'text/html,application/xhtml+xml,application/xml;'
                   'q=0.9,image/avif,image/webp,image/apng,*/*;'
                   'q=0.8,application/signed-exchange;v=b3;q=0.7',
                   'Accept-Encoding': 'gzip, deflate',
                   'Accept-Language': 'zh-CN,zh;q=0.9',
                   'Connection': 'keep-alive',
                   'Cookie': cache['cookie'],
                   'Host': 'www.baidu.com',
                   'Referer': 'http://www.baidu.com/',
                   'Upgrade-Insecure-Requests': '1'}
        resp = await self.request_get(url, headers=headers, params=params, use_ip=use_ip)
        return resp.text

    async def get_source(self, querry, num):
        """获取搜索结果源码"""
        try:
            resp_text = await self.search(querry, num)
            return resp_text
        except Exception as err:
            print(err)
            return {'keyword': querry, 'info': str(err)}

    async def get_data(self, querry, num):
        """获取搜索结果data数据"""
        try:
            resp_text = await self.search(querry, num)
            if "</title>" not in resp_text:
                return {"keyword": querry, 'success': False, 'info': '百度验证码','from':self.config['【网站信息】']['程序名称']}
            count_ = re.findall('找到相关结果约(.*?)个',resp_text)
            count = int(count_[0].replace(',','')) if len(count_)>0 else None
            tree = etree.HTML(resp_text)
            others_source = tree.xpath(
                "//div[@class='c-font-medium list_1V4Yg']//a/text()")
            more = []
            if len(others_source) > 0:
                more = [i.strip() for i in others_source]
            related_source = tree.xpath(
                "//table[@class='rs-table_3RiQc']//a/text()")
            related = []
            if len(related_source) > 0:
                related = [i.strip() for i in related_source]
            results = tree.xpath(
                "//div[contains(concat(' ', @class, ' '), 'result')]")
            datas = []
            for index, result in enumerate(results):
                srcid_ = result.xpath("@srcid")
                srcid = srcid_[0] if len(srcid_) > 0 else ""
                id_ = result.xpath("@id")
                index_id = id_[0] if len(id_) > 0 else ""
                mu_ = result.xpath("@mu")
                real_url = mu_[0] if len(mu_) > 0 else ""
                title = result.xpath("string(div//h3/a)")
                if len(title.strip()) > 1:
                    if srcid == "1599":
                        des = result.xpath(
                            "string(div//span[@class='content-right_8Zs40'])")
                        origin = result.xpath(
                            "string(div//span[@aria-hidden='true'])")
                        full_domain, domain = self.func.get_domain_info(real_url)[
                            1:]
                        datas.append({'id': index_id, 'title': title, 'origin': origin,
                                    "full_domain": full_domain, "domain": domain, "link": real_url, 'des': des})
            return {"keyword": querry,"count":count, "related": related, "more": more, "data": datas, 'success': True}
        except Exception as err:
            print(err)
            return {'keyword': querry, 'info': str(err), 'success': False}

    async def get_included(self, querry, num):
        """获取收录数据"""
        try:
            link = querry.replace('http://', '').replace('https://', '')
            full_domain, domain = self.func.get_domain_info(link)[1:]
            if "." not in domain:
                return {'url': querry, 'info': f'{querry} 非url链接', 'success': False}
            # 查询链接自身收录
            resp_text = await self.search(link, num)
            if "</title>" not in resp_text:
                return {"keyword": querry, 'success': False, 'info': '百度验证码','from':self.config['【网站信息】']['程序名称']}
            if 'http://zhanzhang.baidu.com/sitesubmit/index?sitename=' in resp_text:
                included = False
                return {'url': querry, 'included': included, 'success': True}
            included = True
            tree = etree.HTML(resp_text)
            results = tree.xpath(
                "//div[contains(concat(' ', @class, ' '), 'result')]")
            for result in results:
                srcid_ = result.xpath("@srcid")
                srcid = srcid_[0] if len(srcid_) > 0 else ""
                id_ = result.xpath("@id")
                index_id = id_[0] if len(id_) > 0 else ""
                title = result.xpath("string(div//h3/a)")
                if len(title.strip()) > 1:
                    if srcid == "1599" and index_id == "1":
                        des = result.xpath(
                            "string(div//span[@class='content-right_8Zs40'])")
                        origin = result.xpath(
                            "string(div//span[@aria-hidden='true'])")
                        break
            return {'url': querry, 'included': included, 'title': title, 'origin': origin, "full_domain": full_domain, "domain": domain, 'des': des, 'success': True}
        except Exception as err:
            print(err)
            return {'url': querry, 'info': str(err), 'success': False}
        
    async def get_include(self, querry, num):
        """获取收录详情数据"""
        try:
            full_domain, domain = self.func.get_domain_info(querry)[1:]
            if "." not in domain:
                return {'querry': querry, 'info': f'{querry} 非法域名', 'success': False}
            # 查询site收录
            link = f"site:{full_domain}"
            resp_text = await self.search(link, num)
            if "</title>" not in resp_text:
                return {"keyword": querry, 'success': False, 'info': '百度验证码','from':self.config['【网站信息】']['程序名称']}
            if 'http://zhanzhang.baidu.com/sitesubmit/index?sitename=' in resp_text:
                include = 0
                return {'querry': querry, 'include': include, 'success': True}
            tree = etree.HTML(resp_text)
            include_ = tree.xpath("//p[3]/span/b")
            include = int(include_[0].replace(',','')) if len(include_)>0 else None
            if include is None:
                include_ = re.findall('找到相关结果数约(.*?)个',resp_text)
                include = int(include_[0].replace(',','')) if len(include_)>0 else None
            results = tree.xpath(
                "//div[contains(concat(' ', @class, ' '), 'result')]")
            datas = []
            for index, result in enumerate(results):
                srcid_ = result.xpath("@srcid")
                srcid = srcid_[0] if len(srcid_) > 0 else ""
                id_ = result.xpath("@id")
                index_id = id_[0] if len(id_) > 0 else ""
                mu_ = result.xpath("@mu")
                real_url = mu_[0] if len(mu_) > 0 else ""
                title = result.xpath("string(div//h3/a)")
                if len(title.strip()) > 1:
                    if srcid == "1599":
                        des = result.xpath(
                            "string(div//span[@class='content-right_8Zs40'])")
                        origin = result.xpath(
                            "string(div//span[@aria-hidden='true'])")
                        full_domain_, domain_ = self.func.get_domain_info(real_url)[1:]
                        datas.append({'id': index_id, 'title': title, 'origin': origin,
                                    "full_domain": full_domain_, "domain": domain_, "link": real_url, 'des': des})
            return {"domain":full_domain,'querry': querry, 'include': include,"data": datas, 'success': True}
        except Exception as err:
            print(err)
            return {'querry': querry, 'info': str(err), 'success': False}

    async def get_pulldown(self, querry):
        """百度下拉词"""
        try:
            url = f"https://www.baidu.com/sugrec?pre=1&p=3&ie=utf-8&json=1&prod=pc&from=pc_web&sugsid=34647,34068,34749,34654,34711,34597,34584,34107,26350,34502,34423,22157,34691&cb=jQuery11020383424710195859_1632731774592&_=1632731774608&wd={querry}"
            use_ip = await self.func.use_ip('baidu')
            transport = httpx.AsyncHTTPTransport(local_address=use_ip)
            async with httpx.AsyncClient(transport=transport) as client:
                resp = await client.get(url, timeout=15)
            pull_down_words = []
            h_text = resp.text
            h_text = re.sub('jQuery.*?\(', '', h_text).strip(')')
            if '"g":[{' in resp.text:
                pull_down_words.extend(i["q"] for i in json.loads(h_text)["g"])
            return {"keyword": querry, "pull_down_words": pull_down_words}
        except Exception as err:
            print(err)
            return {'keyword': querry, 'info': str(err), 'success': False}
