"""域名可注册接口"""

from concurrent.futures import ThreadPoolExecutor
import os
import arrow
import tldextract
import httpx


class Register():
    """域名可注册接口"""

    def __init__(self,func):
        self.func = func
        self.executor = ThreadPoolExecutor(32)
        
    def idcqs(self, domain):
        """idcqs api"""
        url = 'http://idcqs.cn/domain/domainStatus'
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.62"
        tld = tldextract.extract(domain)
        root_domain = ".".join([tld.domain, tld.suffix]).strip(".").lower()
        data = {
            "domain": root_domain,
            "suffix": "."+tld.suffix,
        }
        headers = {"user-agent": user_agent,
                   'Host': 'idcqs.cn',
                   'Origin': 'http://idcqs.cn',
                   'Referer': f'http://idcqs.cn/domain/search?key={root_domain}&suffixes%5B%5D=.{tld.suffix}'}
        resp = httpx.post(url, data=data, headers=headers)
        # print(resp.text)
        if resp.json()['text'] == '域名可注册':
            return True
        return False

    def can_register(self, domain):
        """域名可注册"""
        register = self.idcqs(domain)
        return register

    def find_domain(self,config, domain, web, keyword, index, url,title, des):
        """扫域名"""
        path_dir = os.path.join("cache", arrow.now("Asia/Shanghai").format('YYYY-MM-DD'))
        os.makedirs(path_dir, exist_ok=True)
        register_path = os.path.join(path_dir, "register.txt")
        register_log = self.func.get_text(register_path)
        if f'‖{domain}‖' not in register_log:
            now_time = arrow.now("Asia/Shanghai").format('YYYY-MM-DD HH:mm:ss')
            if self.can_register(domain):
                print(mes:=f'{now_time}【{web}】‖{domain}‖✅‖{keyword}‖{index}‖{url}‖{title}‖{des}')
                if config['【功能开关】']['开启发送至telegram']:
                    url = f"http://{config['【网站信息】']['绑定域名']}/telegram/send"
                    params = {
                        "text": mes,
                        "token": config['【功能开关】']['telegram_token'],
                        "to_id": config['【功能开关】']['telegram_group_chat_id'],
                    }
                    resp = httpx.get(url,params=params)
                    print(resp.text)
            else:
                print(mes:=f'{now_time}【{web}】‖{domain}‖❌‖{keyword}‖{index}‖{url}‖{title}‖{des}')
            with open(register_path,'a',encoding='utf-8')as log_f:
                log_f.write(mes+'\n')
        else:
            print(f'[{web}]{domain}||已经存在，跳过查询')

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
