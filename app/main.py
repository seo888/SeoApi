# -*- coding: UTF-8 -*-

import time
from fastapi import Request
from fastapi import FastAPI
from function import Func
import uvicorn
from starlette.responses import JSONResponse
from api import v1_router


app = FastAPI(
    title="SeoApi",
    description="seo网络服务api - by TG@seo888",
    version="0.0.1",
    openapi_tags=[
        {
            "name": "serp",
            "description": "搜索引擎结果api",
        },
        {
            "name": "ai",
            "description": "AI接口",
        },
        {
            "name": "tg",
            "description": "tg接口",
        },
    ],
    docs_url="/",
    redoc_url=None,
    openapi_url="/api/v1/openapi.json",
)

func = Func()

@app.middleware("http")
async def middleware(request: Request, call_next):
    """中间件 访问前后"""
    return await middleware(request, call_next, func)

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


# @app.get(
#     "/tg/send",
#     tags=["tg"],
#     name="【tg】Send Message",
#     description="给指定tg频道或用户发送消息",
# )
# async def tg_send(request: Request, text=None, token=None, to_id=None):
#     """给指定tg频道或用户发送消息"""
#     if text is None:
#         return Response(content="【tg】Send Message API",
#                         media_type="text/html;charset=utf-8")
#     if text is not None and token is not None and id is not None:
#         return await router.tg_send(text, token, to_id)
#     return JSONResponse({"error": "参数不全"})

# @app.get("/ai/{action}", tags=["AI"])
# async def ai(action: AiAction, q: str = None):
#     """AI查询接口"""
#     if q is None:
#         return JSONResponse(status_code=404, content={"error": "参数错误"})
#     return await router.geminiAI(action, q)

# 挂载 v1 版本，路径前缀为 /rest/v1
app.include_router(
    v1_router,
    prefix="/api",   # 这里就是你的 rest/v1
    # tags=["v1"]          # 在 Swagger UI 中分组显示
)

# 可选：根路径或非版本路由
@app.get("/")
async def root():
    return {"message": "Welcome to SeoApi! Visit /docs for API docs."}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=17888)
