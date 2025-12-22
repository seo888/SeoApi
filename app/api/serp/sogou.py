from starlette.responses import JSONResponse, RedirectResponse, FileResponse

async def sogou(action, q, num=50):
    # """获取用户积分及登录信息"""
    # ok, result = self.pgdb.getUserDataByUsername(user)
    # print(ok, result)
    ok = True
    result = action
    if ok:
        result_data = {"success": ok, "result": result}
    else:
        result_data = {"success": ok, "error_info": result}
    return JSONResponse(result_data)