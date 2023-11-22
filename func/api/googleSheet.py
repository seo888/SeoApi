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
            "private_key_id": "3147454802b3a6e352ecee70c6461297491b11bc",
            "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDPz4tTeNiTTE6v\ngCZ/CyPgI00RTOjb1DwXtW30ULGzYl2dxCE0RHuEe6AGB3K/BZx9aVyayglqlSGO\nnTqpd8SKScSycs36MYYtFW1XHCA1fJkAO4wkod59gkicyNXO/5EaGC3RqdcrEjPr\nEUmZqbpkKDQrt3inCFbRxJ/uy5MfUFy4BAJNUNP0EK5CBtU+2DAj+/cA+Y9glWQI\ncsHmswmCdb5nCRpSQ9m3x4qm3vupZ5gG8ucgL9Hw7kZ9NUC/6J6Sf6wH/I+0hGdu\n97wfGhjxauBm0s6lrZ/IoWyzolxAmG7OhxiaimCkbeEg/bg278rte9POIkWndfYy\nrKb8lW1JAgMBAAECggEAAm9sMo43+4HpaiUWTmbTBM1lGc7M68aQ7bYyk6pearu8\nXRzvRq2GxQat2WQ89AAc1VtmummjspwMyJ8PEO1WYEh9BZpSz5vE9sJJhbvOpNHQ\n+S+5dLRw5wef0jaISuSzzpp57vsOinKsKRUKx8I1bPcLpXeA8nQmkE69kQ7RqoxB\nHmQXTyMkvZqKeIghxEF/zJ3NR0vwd6zF5gL0XLHjEfPgWNaunTleslSgSMgDj4si\nNXVpao72Mn/K4+C8Lok5H9PqruSlPl6Klb8FpQ+YCfonhqQOgZnY7FXPV6mzJgjm\nAUTIOvGAkHPZ9OF6wGTCzmSagwjSuK/kEW5rMCdMAQKBgQD3694Quhy1Wc3g/lGm\nx8/T2mjt7L4a9C7zIX2VVW1wPxb+wFbnzSwvXec4qCiz31Tfj1Aw0dfrKb4kHwHD\nJ1a2Sn4C2ogVnmYmiPb04nwsNgY0zIfF/YkXzCB/dBDBaOf3wZE55y3Wi05MBpOt\nsr2mw0pH+YPAm1J/CisjhzyRWwKBgQDWlRQLKmLTr9VxktcVAJxXlQpnYSjd4qc/\n+VcMrzBX+7imFFphN8OxHhodhpzVRSzNmm3A+4z7n9urz6jN1sSv7lN9kwMZFNtE\nzXel4DQ5iqmAq8P8GrEF7O0IweNVmQHI/rK0IB4JclFyMUTUjwZocmPpSNdEi0SM\nDQKj7y95KwKBgQChM5+Xtrv1+yeP1S1YSXHL6abylU3jDsT8V9llYT+gjZUxHfUk\nEddaES/IOicFFgEEwBW/OKKxiNnWeMbXktuh+fvHdTqo++6lvcb94coloRcV+6uI\nxFsAuzyiQuCmMcUq5pS8VqIKb1gAvQIHHkKMjUzeUdImSZgxfHYiSsvKIwKBgGMJ\nBOouUtROd91mHxxTXtTRNa8G2ZymqfhNtM5m4JIK3GrSQ/BQk2Hgeb8czK9lsMrn\ntjX2I1hSrEj8m3T85WQpQ6FWQ3zE8nortkf5VUElbRu0qsxk6UTJ15BOJATyjC9e\n1c1qcVJ8z3g7ov/TTurPuKsHckrxV96ndouArdFnAoGBALFHy6s2aHSLW8dqcb6T\nZCRuvULpadxXXaZHriyIj65vWsUg6zaPSPyhCHbmlqZMQEz81HHlr/MAdrUywPko\nKSvFiLBF45RE826+eCzFeLU2Q4W7D/kHB3RVbC//s3uj/rPlwtdl2+c5B1L/7XqN\ngIh0QCsIMwTeFKUqtdHxyCQq\n-----END PRIVATE KEY-----\n",
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
    



