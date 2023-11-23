# -*- coding: UTF-8 -*-
"""中间件 访问前后"""

import time
import os
import aiofiles
from starlette.responses import JSONResponse, RedirectResponse
from starlette.templating import Jinja2Templates
import tldextract
import arrow
from func.const import *


async def middleware(request, call_next, func):
    """中间件 访问前后"""
    # 请求处理前计时
    start_time = time.time()
    config = func.get_yaml('config/config.yml')
    # UA黑名单处理
    if 'user-agent' not in request.headers:
        return JSONResponse(status_code=403, content={"error": '10005'})
    real_ua = request.headers['user-agent']
    fuck_uas = config["【访问策略】"]["UA黑名单"]
    if fuck_uas != '' and any(i in real_ua for i in fuck_uas.split("|")):
        return JSONResponse(status_code=403, content={"error": '10002'})
    # IP黑名单处理
    real_ip = request.headers['x-real-ip']
    fuck_ips = config["【访问策略】"]["IP黑名单"]
    if fuck_ips != '' and any(i in real_ip for i in fuck_ips.split("|")):
        return JSONResponse(status_code=403, content={"error": '10001'})
    # ---------------
    response = await call_next(request)
    # ---------------
    # 请求处理后
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-From"] = config['【网站信息】']['程序名称']
    return response
