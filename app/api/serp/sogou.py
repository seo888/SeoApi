from fastapi import HTTPException
from fastapi.responses import JSONResponse
from typing import List, Dict, Any
import asyncio
import httpx
import tldextract
from parsel import Selector
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== 配置区 ====================
PAGES_TO_CRAWL = lambda num: max(1, (num // 10) + 1)  # 每页约10个结果
MAX_CONCURRENCY = 5
REQUEST_DELAY = 0.1

PROXY_URL = "http://13187255005:ibNgXVXT@t128.juliangip.cc:32686/"  # 建议改为环境变量

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Referer": "https://www.sogou.com/",
}

BAD_SUFFIXES = {"gov.cn", "edu.cn", "gov.mo", "edu"}
BAD_DOMAINS = {
    "sogou.com", "baidu.com", "qq.com", "weibo.com", "360.cn", "haosou.com",
    "cctv.com", "163.com", "ce.cn", "cntv.cn", "people.cn", "ifeng.com",
    "sohu.com", "xinhuanet.com", "chinadaily.com.cn", "sina.com.cn", "toutiao.com",
}

WHOIS_API = "https://v2.xxapi.cn/api/whois"
extract = tldextract.extract
# ================================================

async def fetch_page(client: httpx.AsyncClient, keyword: str, page: int) -> str:
    """获取搜狗搜索单页 HTML"""
    params = {"query": keyword, "page": page}
    try:
        response = await client.get(
            "https://www.sogou.com/web",
            params=params,
            timeout=15.0,
        )
        response.raise_for_status()
        await asyncio.sleep(REQUEST_DELAY)
        return response.text
    except httpx.TimeoutException:
        logger.warning(f"搜狗请求超时: {keyword} 第{page}页")
        return ""
    except httpx.HTTPStatusError as e:
        logger.error(f"搜狗返回错误状态码: {e.response.status_code} - {keyword} 第{page}页")
        return ""
    except httpx.RequestError as e:
        logger.error(f"搜狗网络请求失败: {e} - {keyword} 第{page}页")
        return ""

def extract_serp_results(html: str, keyword: str, page: int) -> List[Dict[str, Any]]:
    """
    从搜狗搜索结果页提取专业 SERP 条目（包含标题、链接、摘要、域名、排名）
    """
    if not html:
        return []

    sel = Selector(text=html)
    results = []
    base_rank = (page - 1) * 10 + 1

    # 搜狗有机结果的主要容器
    for rank_offset, result in enumerate(sel.css("div.results>div.fb"), start=base_rank):
        title_elem = result.css("h3 a::text, h3::text").get()
        link_elem = result.css("h3 a::attr(href)").get()
        snippet_elem = result.css("p.text-abstr::text, div.f000::text").get()
        cite_elem = result.css("div.citeurl span::text, div.citeurl > span::text").get()

        if not (title_elem and link_elem):
            continue

        title = title_elem.strip()
        link = link_elem.strip()
        snippet = (snippet_elem or "").strip()
        cite = (cite_elem or "").strip() if cite_elem else ""

        # 提取域名
        host = ""
        if cite:
            host_part = cite.split(" ")[-1].replace("http://", "").replace("https://", "").split("/")[0]
        else:
            # 从链接中提取
            try:
                host_part = httpx.URL(link).host or ""
            except:
                host_part = ""

        ext = extract(host_part)
        domain = f"{ext.domain}.{ext.suffix}".lower() if ext.domain and ext.suffix else None

        if not domain:
            continue
        if ext.suffix.lower() in BAD_SUFFIXES:
            continue
        if domain in BAD_DOMAINS:
            continue

        results.append({
            "rank": rank_offset,
            "title": title,
            "url": link,
            "snippet": snippet,
            "cite": cite,
            "domain": domain,
        })

    return results

async def check_whois(domain: str) -> bool:
    """检查域名是否可注册"""
    try:
        async with httpx.AsyncClient(timeout=12.0) as client:
            resp = await client.get(WHOIS_API, params={"domain": domain})
            if resp.status_code != 200:
                return False
            return '"domain_status":""' in resp.text
    except Exception as e:
        logger.debug(f"Whois 检查失败 {domain}: {e}")
        return False


async def sogou_search(keyword: str, num: int = 50):
    """
    搜狗 SERP 域名挖掘 API（专业版）
    
    返回结构化搜索结果，并标注可注册域名
    """
    keyword = keyword.strip()
    if not keyword:
        raise HTTPException(status_code=400, detail="keyword 参数不能为空")

    if num < 1 or num > 200:
        raise HTTPException(status_code=400, detail="num 参数必须在 1-200 之间")

    pages_needed = PAGES_TO_CRAWL(num)
    sem = asyncio.Semaphore(MAX_CONCURRENCY)

    limits = httpx.Limits(max_keepalive_connections=20, max_connections=50)
    transport = httpx.AsyncHTTPTransport(proxy=httpx.Proxy(url=PROXY_URL))

    all_results: List[Dict] = []
    domain_set = set()

    try:
        async with httpx.AsyncClient(
            headers=HEADERS,
            http2=True,
            limits=limits,
            transport=transport,
            timeout=15.0,
        ) as client:
            tasks = [
                asyncio.create_task(fetch_page(client, keyword, page))
                for page in range(1, pages_needed + 1)
            ]

            for future in asyncio.as_completed(tasks):
                html = await future
                # 找出是哪一页（通过 task 匹配）
                page_idx = tasks.index(future)
                page_num = page_idx + 1

                page_results = extract_serp_results(html, keyword, page_num)
                for item in page_results:
                    domain = item["domain"]
                    if domain not in domain_set:
                        domain_set.add(domain)
                        all_results.append(item)

    except Exception as e:
        logger.exception("搜狗爬取过程发生未知错误")
        raise HTTPException(status_code=500, detail="搜索过程发生内部错误")

    if not all_results:
        return JSONResponse({
            "success": True,
            "keyword": keyword,
            "requested_num": num,
            "total_results": 0,
            "available_domains": 0,
            "message": "未找到有效搜索结果（可能被反爬或代理失效）",
            "results": []
        })

    # 并发检查域名可用性
    whois_tasks = [check_whois(item["domain"]) for item in all_results]
    availabilities = await asyncio.gather(*whois_tasks, return_exceptions=False)

    available_count = 0
    for item, available in zip(all_results, availabilities):
        item["available"] = bool(available)
        if available:
            available_count += 1
        if available_count >= num:
            break

    # 按排名排序
    all_results.sort(key=lambda x: x["rank"])

    return JSONResponse({
        "success": True,
        "keyword": keyword,
        "requested_num": num,
        "total_results": len(all_results),
        "available_domains": available_count,
        "search_url": f"https://www.sogou.com/web?query={keyword}",
        "results": all_results
    })