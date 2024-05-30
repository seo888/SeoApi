# -*- coding: UTF-8 -*-
"""功能函数"""

import linecache
import os
import json
import random
import sys
from urllib.parse import quote
import aiofiles
import arrow
import tldextract
from ruamel import yaml


class Func():
    """功能函数"""

    def __init__(self):
        self.ips = self.get_ips()
        print('ips:')
        print(self.ips)

    def get_ips(self):
        """获取当前服务器所有IP"""
        nowsys = sys.platform
        if 'win' in nowsys:
            return []
        try:
            ips_list = os.popen('ip addr').readlines()
            ips = []
            for i in ips_list:
                if "inet " in i:
                    i = i.strip().split(' ')[1].split('/')[0]
                    ips.append(i)
            if "127.0.0.1" in ips:
                ips.remove('127.0.0.1')
            return ips
        except Exception as err:
            print(err)
            return []

    async def use_ip(self, name):
        """获取IP"""
        path_dir = os.path.join(
            "cache",
            arrow.now("Asia/Shanghai").format('YYYY-MM-DD'))
        os.makedirs(path_dir, exist_ok=True)
        use_ips_path = os.path.join(path_dir, f"{name}_ips") + ".txt"
        use_index_path = os.path.join(path_dir, f"{name}_index") + ".txt"
        if not os.path.exists(use_ips_path):
            ips = list(set(self.ips))
            async with aiofiles.open(use_ips_path, "w",
                                     encoding='utf-8') as txt_f:
                await txt_f.write("\n".join(ips) + "\n")
        if not os.path.exists(use_index_path):
            async with aiofiles.open(use_index_path, "a",
                                     encoding='utf-8') as txt_f:
                await txt_f.write("")
        use_ips = self.get_lines(use_ips_path)
        if use_ips == []:
            return '0.0.0.0'
        async with aiofiles.open(use_index_path, "r",
                                 encoding='utf-8') as txt_f:
            index_text = await txt_f.read()
        index = len(index_text)
        use_len = len(use_ips)
        if index < use_len:
            use_ip = use_ips[index]
        else:
            index = index % use_len
            use_ip = use_ips[index]
        print(index, use_ip)
        async with aiofiles.open(use_index_path, "a",
                                 encoding='utf-8') as txt_f:
            await txt_f.write("1")
        return use_ip

    async def geminiToken_useip(self):
        """获取IP"""
        name = "Gemini"
        path_dir = os.path.join(
            "cache",
            arrow.now("Asia/Shanghai").format('YYYY-MM-DD'))
        os.makedirs(path_dir, exist_ok=True)

        token_ips_path = os.path.join(path_dir, f"{name}_token_ips") + ".txt"
        use_index_path = os.path.join(path_dir, f"{name}_index") + ".txt"

        if not os.path.exists(token_ips_path):
            
            ips = sorted(list(set(self.ips)))
            print("ips", ips)
            tokens = self.get_lines("config/gemini_tokens.txt")
            token_ips = []
            for index, token in enumerate(tokens[:len(ips)]):
                token_ips.append(token + "|" + ips[index])

            async with aiofiles.open(token_ips_path, "w",
                                     encoding='utf-8') as txt_f:
                await txt_f.write("\n".join(token_ips))

        if not os.path.exists(use_index_path):
            async with aiofiles.open(use_index_path, "a",
                                     encoding='utf-8') as txt_f:
                await txt_f.write("")

        ips = self.get_lines(token_ips_path)
        if ips == []:
            return False, '0.0.0.0'
        async with aiofiles.open(use_index_path, "r",
                                 encoding='utf-8') as txt_f:
            index_text = await txt_f.read()
        index = len(index_text)
        use_len = len(ips)
        if index < use_len:
            token_ip = ips[index]
        else:
            index = index % use_len
            token_ip = ips[index]
        print(index, token_ip)
        async with aiofiles.open(use_index_path, "a",
                                 encoding='utf-8') as txt_f:
            await txt_f.write(".")
        return True, token_ip

    def get_domain_info(self, domain):
        """获取域名前后缀"""
        tld = tldextract.extract(domain)
        subdomain = tld.subdomain.lower()
        full_domain = ".".join([tld.subdomain, tld.domain,
                                tld.suffix]).strip(".").lower()
        root_domain = ".".join([tld.domain, tld.suffix]).strip(".").lower()
        return subdomain, full_domain, root_domain

    def is_domain(self, link):
        """判断是否为域名"""
        root_domain = self.get_domain_info(link)[-1]
        if '.' in root_domain:
            return True
        return False

    def get_yaml(self, path):
        """yaml文件解析"""
        linecache.checkcache(path)
        yml = "".join(linecache.getlines(path))
        result = yaml.load(yml, Loader=yaml.SafeLoader)
        return result

    def get_lines(self, path):
        """txt文件行数据"""
        linecache.checkcache(path)
        result = [
            i.strip() for i in linecache.getlines(path) if len(i.strip()) > 7
        ]
        return result

    def get_text(self, path):
        """文本文件解析"""
        linecache.checkcache(path)
        text = "".join(linecache.getlines(path))
        return text
