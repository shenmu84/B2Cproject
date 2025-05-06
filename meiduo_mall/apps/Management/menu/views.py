# views.py
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import UmsMenu
from meiduo_mall.apps.Management.common.CommonResult import CommonResult
from .services import UmsMenuService  # 自定义服务层
from django.shortcuts import render
import json
# Create your views here.
# POST /menu/create/
class UmsMenuCreateView(APIView):
    """
    后台菜单创建接口（等价于 Java 的 @RequestMapping("/create")）
    """

    def post(self, request):
        # 解析请求体中的 JSON 数据
        data = json.loads(request.body)
        # 调用服务层逻辑（等价于 menuService.create(umsMenu)）
        count = UmsMenuService.create()
        if count:  # 模拟 count > 0 判断
            return JsonResponse(CommonResult.success(count).to_dict())
        else:
            return JsonResponse(CommonResult.failed().to_dict())

