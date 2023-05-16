# -*- coding: UTF-8 -*-
"""路由解析器"""

import os
from fastapi import Response, Request, Form, Body
from starlette.responses import JSONResponse, RedirectResponse, FileResponse
from func.api.baidu import Baidu
from func.api.domain import Register
from func.api.google import Google
from func.api.bing import Bing
from func.const import *
from func.function import Func
from func.api.mir6 import Mir6


class Router():
    """路由解析器"""

    def __init__(self):
        self.func = Func()
        self.register = Register(self.func)
        if not os.path.exists('cache'):
            os.mkdir('cache')

    async def baidu(self, action, q,num=50):
        """百度接口"""
        baidu = Baidu(self.func)
        if action == BaiduAction.SOURCE:
            result = await baidu.get_source(q,num)
            return Response(content=result, media_type='text/html;charset=utf-8')
        elif action == BaiduAction.DATA:
            result = await baidu.get_data(q,num)
            # 查询域名是否可注册
            self.register.domain_can_register('baidu',result)
        elif action == BaiduAction.INCLUDED:
            result = await baidu.get_included(q,num)
        elif action == BaiduAction.INCLUDE:
            result = await baidu.get_include(q,num)
        elif action == BaiduAction.PULLDOWN:
            result = await baidu.get_pulldown(q)
        return JSONResponse(result)

    async def google(self, action, q,num=50):
        """谷歌接口"""
        google = Google(self.func)
        if action == GoogleAction.SOURCE:
            result = await google.get_source(q,num)
            return Response(content=result, media_type='text/html;charset=utf-8')
        elif action == GoogleAction.DATA:
            result = await google.get_data(q,num)
            # 查询域名是否可注册
            self.register.domain_can_register('google',result)
        elif action == GoogleAction.INCLUDE:
            result = await google.get_include(q,num)
        elif action == GoogleAction.PULLDOWN:
            result = await google.get_pulldown(q)
        return JSONResponse(result)
    
    async def bing(self, action, q,num=50):
        """必应接口"""
        bing = Bing(self.func)
        if action == BingAction.SOURCE:
            result = await bing.get_source(q,num)
            if result['success']:
                return Response(content=result['result'], media_type='text/html;charset=utf-8')
            else:
                return JSONResponse(result)
        elif action == BingAction.DATA:
            result = await bing.get_data(q,num)
            # 查询域名是否可注册
            self.register.domain_can_register('bing',result)
        elif action == BingAction.INCLUDE:
            result = await bing.get_include(q,num)
        elif action == BingAction.PULLDOWN:
            result = await bing.get_pulldown(q)
        return JSONResponse(result)

    async def mir6(self, action, q):
        """谷歌接口"""
        mir6 = Mir6(self.func)
        if action == Mir6Action.WEIGHT:
            result = await mir6.get_weight(q)
        return JSONResponse(result)
