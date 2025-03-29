from fastapi import status
from fastapi.responses import JSONResponse

def res_200(message = "请求成功", data = None):
    return JSONResponse(status_code=status.HTTP_200_OK, 
                        content={
                            "code": 200,
                            "status": 'success',
                            "message": message,
                            "data": data
                        })


def res_201(message = "创建成功", data = None):
    return JSONResponse(status_code=status.HTTP_201_CREATED, 
                        content={
                            "code": 201,
                            "status": 'success',
                            "message": message,
                            "data": data
                        })


def res_204(message = "删除成功", data = None):
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, 
                        content={
                            "code": 204,
                            "status": 'success',
                            "message": message,
                            "data": data
                        })


def res_400(message = "请求错误", data = None):
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, 
                        content={
                            "code": 400,
                            "status": 'failure',
                            "message": message,
                            "data": data
                        })


def res_401(message = "未获得授权", data = None):
    return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, 
                        headers={"WWW-Authenticate": "Bearer"},
                        content={
                            "code": 401,
                            "status": 'failure',
                            "message": message,
                            "data": data
                        })


def res_404(message = "未找到资源", data = None):
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, 
                        content={
                            "code": 404,
                            "status": 'failure',
                            "message": message,
                            "data": data
                        })