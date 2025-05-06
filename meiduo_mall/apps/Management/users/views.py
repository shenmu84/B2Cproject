from django.conf import settings
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import json
from . import services
from meiduo_mall.apps.Management.common import CommonResult

# 假设有一个admin_service来处理业务逻辑

''''
注册和登录
'''
class UmsAdminRegisterView(APIView):
    def post(self, request):
        # 获取 JSON 数据并反序列化
       pass
class UmsAdminLoginView(APIView):
    def options(self, request, *args, **kwargs):
        # 手动处理 OPTIONS 请求，返回必要的 CORS 头部
        response = JsonResponse({"message": "OPTIONS request"})
        response["Access-Control-Allow-Origin"] = "*"  # 允许所有来源
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"  # 允许的请求方法
        response["Access-Control-Allow-Headers"] = "Content-Type, Authorization"  # 允许的请求头
        return response
    def post(self, request):
        token_head = settings.JWT_TOKEN_HEAD
        data=json.loads(request.body)
        username=data.get('username')
        password=data.get('password')
        token = services.login(username,password)
        if token is None:
                return JsonResponse(CommonResult.validate_failed("用户名或密码错误").to_dict())
                # 登录成功，封装 token 返回
        token_map = {
            "token": token,
            "tokenHead": token_head
        }

        result = CommonResult.success(token_map)
        return JsonResponse(result.to_dict())

'''
第二部分：刷新 Token 和获取当前用户信息
'''
class UmsAdminRefreshTokenView(APIView):
    def get(self, request):
        pass
'''
第三部分：用户信息和登出功能
'''


class UmsAdminInfoView(APIView):
    def get(self, request):
        pass


class UmsAdminLogoutView(APIView):
    def post(self, request):
        pass
'''第四部分：用户列表和用户更新'''
from rest_framework.pagination import PageNumberPagination


class UmsAdminListView(APIView):
    def get(self, request):
        pass

class UmsAdminUpdateView(APIView):
    def post(self, request, id):
        pass