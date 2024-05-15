# -*- coding: UTF-8 -*-

from enum import Enum
import os
from fastapi import Response, Request, Form, Body
from fastapi import FastAPI
import uvicorn
from starlette.responses import JSONResponse, RedirectResponse, FileResponse
from func.api.tg import Telegram
from func.function import Func
from func import middle
from func.router import Router
from func.const import *

app = FastAPI(
    title="SeoApi",
    description="seo网络服务api - by TG@seo888",
    version="1.0.0",
    openapi_tags=[
        {
            "name": "百度",
            "description": "百度相关api",
        },
        {
            "name": "谷歌",
            "description": "谷歌相关api",
        },
        {
            "name": "必应",
            "description": "必应相关api",
        },
        {
            "name": "米人",
            "description": "米人相关api",
        },
        {
            "name": "域名",
            "description": "域名相关api",
        },
        {
            "name": "telegram",
            "description": "telegram相关api",
        },
    ],
    docs_url="/",
    redoc_url=None,
    openapi_url="/api/v1/openapi.json",
)
func = Func()
# 路由引用
router = Router()


@app.middleware("http")
async def middleware(request: Request, call_next):
    """中间件 访问前后"""
    return await middle.middleware(request, call_next, func)


@app.get(
    "/telegram/send",
    tags=["telegram"],
    name="【telegram】Send Message",
    description="给指定telegram频道或用户发送消息",
)
async def telegram_send(request: Request, text=None, token=None, to_id=None):
    """给指定telegram频道或用户发送消息"""
    if text is None:
        return Response(content="【telegram】Send Message API",
                        media_type="text/html;charset=utf-8")
    if text is not None and token is not None and id is not None:
        return await router.tg_send(text, token, to_id)
    return JSONResponse({"error": "参数不全"})


@app.get("/scripts/{file_name}")
async def scriptPy(request: Request,
                   response: Response,
                   file_name: str = None):
    """返回脚本"""
    file_path = os.path.join("./scripts", file_name)
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            python_code = file.read()
        response.headers["Content-Type"] = "text/plain"
        return Response(status_code=200, content=python_code)
    return '没有文件'


@app.get("/tasks")
async def remoteTasks(request: Request,
                      do_user: str,
                      do_account: str,
                      count: int = 1,
                      limit: str = None):
    """获取pgsql中的任务数据"""
    count = 5 if count > 5 else count
    count = 1 if count < 1 else count
    return await router.getTasks(None, count, do_user, do_account, limit)


@app.get("/tasks/{user}")
async def tasks(request: Request,
                user: str,
                do_user: str,
                do_account: str,
                count: int = 1,
                limit: str = None):
    """获取pgsql中的任务数据"""
    count = 5 if count > 5 else count
    count = 1 if count < 1 else count
    return await router.getTasks(user, count, do_user, do_account, limit)


@app.get("/tasks_del/{user}")
async def delTask(request: Request, user: str, ids: str):
    """删除任务"""
    return await router.delTask(user, ids)


@app.get("/tasks_finish/{user}")
async def finishTasks(request: Request, user: str, tid: str, link: str):
    """完成了一个任务 更新"""
    return await router.finishTasks(user, tid, link)


@app.get("/tasks_past/{user}")
async def pastTimeTask(request: Request, user: str):
    """超时任务处理"""
    return await router.pastTimeTask(user)


@app.get("/task24log/{account}")
async def task24Log(request: Request, account: str):
    """获取24小时内任务发送数"""
    return await router.getLog24(account)


@app.get("/domains/{mode}")
async def domains(mode: DomainsAction, day=None):
    """展示扫描的可注册域名"""
    return await router.show_domains(mode, day)


@app.get("/s")
async def baidu_(wd: str = None, rn: int = 50):
    """百度接口 搜索输入跳转"""
    if wd is None:
        return JSONResponse(status_code=404, content={"error": "参数错误"})
    search_url = f"/baidu/source?q={wd}&num={rn}"
    return RedirectResponse(url=search_url, status_code=301)


@app.get("/baidu/{action}", tags=["百度"])
async def baidu(action: BaiduAction, q: str = None, num: int = 50):
    """百度接口"""
    if q is None:
        return JSONResponse(status_code=404, content={"error": "参数错误"})
    return await router.baidu(action, q, num=num)


@app.get("/search")
async def google_(request: Request, q: str = None, num: int = 50):
    """谷歌接口 搜索输入跳转"""
    if q is None:
        return JSONResponse(status_code=404, content={"error": "参数错误"})
    if "/bing/" in request.headers["referer"]:
        search_url = f"/bing/source?q={q}&num={num}"
    else:
        search_url = f"/google/source?q={q}&num={num}"
    return RedirectResponse(url=search_url, status_code=301)


@app.get("/google/{action}", tags=["谷歌"])
async def google(action: GoogleAction, q: str = None, num: int = 50):
    """谷歌接口"""
    if q is None:
        return JSONResponse(status_code=404, content={"error": "参数错误"})
    return await router.google(action, q, num=num)


@app.get("/url")
async def url(q: str = ""):
    """google 搜索结果url跳转"""
    if q[:len("http")] == "http":
        return RedirectResponse(url=q, status_code=301)
    return {"q": q}


@app.get("/bing/{action}", tags=["必应"])
async def bing(action: BingAction, q: str = None, num: int = 50):
    """必应接口"""
    if q is None:
        return JSONResponse(status_code=404, content={"error": "参数错误"})
    return await router.bing(action, q, num=num)


@app.get("/mir6/{action}", tags=["米人"])
async def mir6(action: Mir6Action, q: str = None):
    """米人mir6.com接口"""
    if q is None:
        return JSONResponse(status_code=404, content={"error": "参数错误"})
    return await router.mir6(action, q)


@app.get("/domain/{action}", tags=["域名"])
async def domain(action: DomainAction, q: str = None):
    """域名注册查询接口"""
    if q is None:
        return JSONResponse(status_code=404, content={"error": "参数错误"})
    return await router.domain(action, q)


@app.get("/ai/{action}", tags=["AI"])
async def ai(action: AiAction, q: str = None):
    """AI查询接口"""
    if q is None:
        return JSONResponse(status_code=404, content={"error": "参数错误"})
    return await router.geminiAI(action, q)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=17888)
