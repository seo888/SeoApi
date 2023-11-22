"""域名可注册接口"""
from concurrent.futures import ThreadPoolExecutor
import os
import random
import asyncio
import arrow
import tldextract
import httpx
from func.api.tg import Telegram
from func.api.googleSheet import GoogleSheet


class Register():
    """域名可注册接口"""

    def __init__(self,func):
        self.GS_bing = GoogleSheet("必应扫域名")
        self.GS_baidu = GoogleSheet("谷歌扫域名")
        self.GS_google = GoogleSheet("百度扫域名")
        self.func = func
        self.executor = ThreadPoolExecutor(32)
        # self.telegram_token = "6323574779:AAG-bLmHVcfrfIpg5IMaQF0Q2FDFxtClJYs"
        # self.telegram_group_chat_id = "-794028075"
        
    def net_cn(self,domain):
        url = f"http://panda.www.net.cn/cgi-bin/check.cgi?area_domain={domain}"
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.62"
        headers = {"user-agent": user_agent,}
        use_ip = random.choice(self.func.ips)
        client = httpx.Client(transport=httpx.HTTPTransport(local_address=use_ip))
        resp = client.get(url,headers=headers)
        # print(resp.text)
        if 'Domain name is available' in resp.text:
            return True
        return False

    def sedo_com(self,domain):
        url = f"https://sedo.com/brokerage/acquisition.php?domain={domain}&origin=partner"
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.62"
        headers = {"user-agent": user_agent,}
        use_ip = random.choice(self.func.ips)
        client = httpx.Client(transport=httpx.HTTPTransport(local_address=use_ip))
        resp = client.get(url,headers=headers)
        # print(resp.text)
        if 'can be registered' in resp.text:
            return True
        return False

    def idcqs(self, domain):
        """idcqs api"""
        url = 'http://idcqs.cn/domain/domainStatus'
        tld = tldextract.extract(domain)
        root_domain = ".".join([tld.domain, tld.suffix]).strip(".").lower()
        data = {
            "domain": root_domain,
            "suffix": "."+tld.suffix,
        }
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.62"
        headers = {"user-agent": user_agent,
                   'Host': 'idcqs.cn',
                   'Origin': 'http://idcqs.cn',
                   'Referer': f'http://idcqs.cn/domain/search?key={root_domain}&suffixes%5B%5D=.{tld.suffix}'}
        use_ip = random.choice(self.func.ips)
        client = httpx.Client(transport=httpx.HTTPTransport(local_address=use_ip))
        resp = client.post(url, data=data, headers=headers)
        if resp.json()['text'] == '域名可注册':
            return True
        return False

    def can_register(self, domain):
        """域名可注册"""
        try: 
            # register_ok = self.net_cn(domain)
            register_ok = self.sedo_com(domain)
        except:
            # register_ok = self.sedo_com(domain)
            register_ok = self.net_cn(domain)
        return register_ok

    def write_gsheet(self,web,datas):
        if web=='bing':
            self.GS_bing.insert_rows(datas)
        elif web=='google':
            self.GS_google.insert_rows(datas)
        elif web=='baidu':
            self.GS_baidu.insert_rows(datas)

    def send_tg(self,tele_mes,telegram_token,telegram_group_chat_id):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(Telegram(telegram_token).send_mes(tele_mes,telegram_group_chat_id))
        loop.close()


    def find_domain(self,config, domain, web, keyword, index, url,title, des):
        """扫域名"""
        # try:
        if True:
            path_dir = os.path.join("cache", arrow.now("Asia/Shanghai").format('YYYY-MM-DD'))
            os.makedirs(path_dir, exist_ok=True)
            register_path = os.path.join(path_dir, "register.txt")
            register_log = self.func.get_text(register_path)
            if f'‖{domain}‖' not in register_log and not any(domain.endswith(i) for i in ['.edu.cn','.gov.cn']):
                now_time = arrow.now("Asia/Shanghai").format('YYYY-MM-DD HH:mm:ss')
                if self.can_register(domain):
                    print(mes:=f'{now_time}【{web}】‖{domain}‖✅‖{keyword}‖{index}‖{url}‖{title}‖{des}')
                    if config['【功能开关】']['开启发送至telegram']:
                        if int(index) <= int(config['【功能开关】']['排名大于限制发送']):
                            webs = {
                                'bing':f'[【bing】](https://www.bing.com/search?q=site:{domain})',
                                'google':f'[【google】](https://www.google.com/search?q=site:{domain})',
                                'baidu':f'[【baidu】](https://www.baidu.com/s?wd=site:{domain})',
                            }
                            keyword_dict = {
                                'bing':f'[{keyword}](https://www.bing.com/search?q={keyword})',
                                'google':f'[{keyword}](https://www.google.com/search?q={keyword})',
                                'baidu':f'[{keyword}](https://www.baidu.com/s?wd={keyword})',
                            }
                            # 发送到telegram群组
                            tele_mes = mes.replace(f'【{web}】',webs[web]).replace(f'‖{keyword}‖',f'‖{keyword_dict[web]}‖')
                            telegram_token = config['【机器人配置】']['telegram_token']
                            telegram_group_chat_id = config['【机器人配置】']['telegram_group_chat_id']
                            if telegram_token!='' and telegram_group_chat_id!='':
                                self.send_tg(tele_mes,telegram_token,telegram_group_chat_id)
                            # 数据写入谷歌表格
                            subdomain, full_domain, root_domain = self.func.get_domain_info(url)
                            is_main = "主站" if subdomain in ['','www'] else "泛站"
                            is_index = "首页" if (url_split:=url.split(full_domain,1))[1] in ['/',''] else "内页"
                            info = f"{config['【网站信息】']['绑定域名']} | {str(arrow.now('Asia/Shanghai').format('YYYY-MM-DD HH:mm:ss'))}"
                            self.executor.submit(self.write_gsheet,web,[now_time,web,domain,keyword,index,url,is_main,is_index,title,des,info])
                else:
                    print(mes:=f'{now_time}【{web}】‖{domain}‖❌‖{keyword}‖{index}‖{url}‖{title}')
                with open(register_path,'a',encoding='utf-8')as log_f:
                    log_f.write(mes+'\n')
            else:
                print(f'[{web}]{domain}||已经存在，跳过查询')
        # except Exception as err:
        #     print('扫域名报错：',domain,err)

    def domain_can_register(self,web,result):
        """查询域名data结果是否有可以注册的域名"""
        config = self.func.get_yaml('config/config.yml')
        if config['【功能开关】']['开启域名可注册查询'] and result['success'] and len(datas:=result['data'])>0:
            query_dict = {}
            for i in datas:
                domain = i['domain']
                keyword = result['keyword']
                index = i['id']
                url = i['link']
                title = i['title']
                des = i['des']
                if domain not in query_dict:
                    query_dict[domain] = [web,keyword,index,url,title,des]
            for domain,v in query_dict.items():
                self.executor.submit(self.find_domain,config,domain,*v)
