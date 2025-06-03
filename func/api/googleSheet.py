import html
import re
import arrow
import httpx
import pygsheets
import tldextract
from google.oauth2 import service_account

class GoogleSheet():
    def __init__(self, target):
        self.client = self.getClient()
        self.sh = self.client.open(target)

    def getClient(self):
        secret = {
        "type": "service_account",
        "project_id": "virtual-cycling-388615",
        "private_key_id": "84c534a5cb3b80477f61c840d7057a157edd99a5",
        "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCdnULqdPozyUm+\njIvg70Oke9NZlE39BVdcrQ5ZY5VxgJs3FNp0gqBMxQ2dB/fnK+/28WN8DO3CLi8e\nmPRNM0vvShqIOLnVOisR3PDWIuH66WPJ7C37NiaB8qBUvx4SysTScBZn3tQiXdtE\nnoDuBWr3zDBQ0Bo7wMqCkgpn/EMz+bRChPtYpZ78MQZthG4v4znHmaSlOpfCueRi\nQc9E/bXJYj4X38bVlbQOQ9wLVFopSKVfV2jByWjPzfa9Sk59xgb1eDRanvX+JDRm\ns0hv1Qc0etIEQKBxJ0Zxn7zeNXaNlND5L6DjyaNnShjRZrRycGkXixPLsRNnf34S\n5+GgkvUvAgMBAAECggEAAefrbbthZSvrdN7tOBicmEoZCa3F7afZYRkEoecW4Qr9\nlYJui9ciihsd6Ya1pDl/StyrZ84eN+loD3YpCh/zLJ8YSAprkN0FtU8XKHe+hNK6\nrq/o9G84svyUnMG84txJ2gOZ+cKTjSDWbHOAOqCdJQb2lJuXnZ5ctIyAjLZbt66p\n8bDX7CnNxwUqtwih77ab4Xw0pglYUy3Py+cEdy6T3CPbU+RdIREROh7zNcR/KPKd\nzT04mB3JwwoX/RYB76j2nYyQZPhcnH9+KeZ9iJ10/ooVAat2thTPD1BRb18iKKk3\nFTMwG/smxizs5+Cy0TAv49j1tLYtRBgiLaubL8KfSQKBgQDefHfub4qhtM5TLMNf\nZ6EIKCmH3moIOjcquiJtsRI8vfzxQ2/ZpUd2Qb0C1E4L74HgZBCJAk8NZo+4o5L4\nqUqbP24gvAUjGN+fTD4YLNw8vlAw3rsMda8u/ssDwK+znMQp1CkwIGZbelhWkM+S\nKcUs1ZEKd3+L70GdY7mSH7WUmQKBgQC1WzJ8MRFRUrWkfYhgPDYMxGWSHoTa89+a\nk6uePiRP8xk8wnKA/yRQeUosfGiw7caHAbrlIWTA5dE2INLycdRTet4AY2dnsgjF\nG4niN1iIkKFT3Ibomeh1u7aZ4b15W0sp1kfA+y//n4O9yyLH31w6yv0/3YS3WhIu\nRkQpRIUtBwKBgCZOoAe5xNDa5LuFdY4ztZJF+ACg1vjbrSv6KHtihZVX0PlpdxSu\nVIOUBgs6qsV7U41jLUWp1BqmkhBkeaW+4E2iuj+AoBHO8pHm+roG31TGH+CKOQKI\nMMWSsTnQL3BpiYz6Lq1OptERW6xr+pFcB8sUaoi20osxgsaqqQTz2LvhAoGBAKzQ\nVFFHqIrn17MA9B1QAukzlN4iOtMxpJd1tAm8iXmt2xSs7dPCTOZqTaYKfvBqA83O\ndju1EH9H/44mxRzGH1/VKwsPrg9/9R9uWHu55aFswG5bLCslzf+yehQ0qgqkVgFt\n8T4RnfFmHXGTynbPfuF/YMek3LyjFcQGrRjt9EGtAoGBAIGRn33jppgUhAlVeb/1\n2RXXwFtcaXszah1WYIImwLlA44Q8ieIYm6DgYYDG47JquW6anUWYZe8Tnq/14VG3\nImgnHotRjTwoMk4sAJ4oGTnaCFbANlFeNg12zpNJw26dQyl1LMnJvF/85RzcBLwh\niZg5XEJhRW20vQ3Kgj/alF43\n-----END PRIVATE KEY-----\n",
        "client_email": "sheet-583@virtual-cycling-388615.iam.gserviceaccount.com",
        "client_id": "111341816615137395656",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/sheet-583%40virtual-cycling-388615.iam.gserviceaccount.com",
        "universe_domain": "googleapis.com"
        }
        SCOPES = ('https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive')
        service_account_info = secret
        my_credentials = service_account.Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
        client = pygsheets.authorize(custom_credentials=my_credentials)
        return client

    def getDomain(self, url):
        tld = tldextract.extract(url)
        full_domain = ".".join([tld.subdomain, tld.domain, tld.suffix]).strip('.').lower()
        only_domain = ".".join([tld.domain, tld.suffix]).lower()
        return tld.subdomain, only_domain, full_domain

    def getAllRows(self):
        wks = self.sh.worksheet_by_title("sheet")
        l_list = wks.get_values(f'A2', f'P99999')
        return l_list

    def insert_rows(self, datas):
        today = arrow.now("Asia/Shanghai").format('YYYY-MM-DD')
        try:
            wks = self.sh.worksheet_by_title(today)
        except:
            wks = self.sh.add_worksheet(today)
            first_lines = ["时间","搜索引擎","域名","关键词","排名","网址","网站类型","网址类型","标题","描述",'备注']
            wks.insert_rows(0, 1, first_lines)
        wks.insert_rows(1, 1, datas)

    def update_datas(self, index, datas):
        wks = self.sh.worksheet_by_title("sheet")
        wks.update_row(index, datas)

if __name__=="__main__":
    GS = GoogleSheet("必应扫域名")
    GS.insert_rows(['1','2','3'])
    



