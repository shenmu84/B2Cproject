import re
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views import View
from apps.users.models import User
import json
class UsernameCountView(View):
    def get(self,request,username):
        count=User.objects.filter(username=username).count()
        return JsonResponse({'code':0,'count':count,'errmsg':'ok'})
# Create your views here.

def log(request):
    import logging
    #创建日志器
    logger=logging.getLogger('django')
    logger.info('每个函数的信息不同')
    return HttpResponse('log')
def  post_json(request):
    json_bytes=request.body
    json_str=json_bytes.decode('utf-8')
    req_dict=json.loads(json_str)
    username=req_dict.get('username')
    password = req_dict.get('password')
    password2 = req_dict.get('password2')
    mobile = req_dict.get('mobile')
    allow = req_dict.get('allow')
    if not all([username,password,password2,mobile,allow]):
        return JsonResponse({'code':400,'errmsg':'参数不安全'})
    if not re.match('[a-zA-Z_-]{5,20}',username):
        return JsonResponse({'code':400,'errmsg':'命名不规范'})
    use=User.objects.create_user(username=username,password=password,mobile=mobile)
    # 状态保持
    from django.contrib.auth import login

    login(request, use)
    return JsonResponse({'code':0,'errmsg':'ok'})
class MobileCountView(View):
    def get(self,request,mobile):
        count = User.objects.filter(mobile=mobile).count()
        return JsonResponse({'code': 0, 'count': count, 'errmsg': 'ok'})
class LoginView(View):
    def post(self,request):
        #接收数据
        data=json.loads(request.body.decode())
        #处理数据
        username=data.get('username')
        password=data.get('password')
        remembered=data.get('remembered')
        # 验证用户名密码是否一致
        #多方验证
        if re.match('1[3-9]\d{9}',username):
            User.USERNAME_FIELD='mobile'
        else:
            User.USERNAME_FIELD='username'
        from django.contrib.auth import authenticate
        user=authenticate(username=username,password=password)
        if user is  None:
            return JsonResponse({'code':400,'errmsg':'账号或者密码错误'})
        # 设置SESSION存放数据库
        from django.contrib.auth import login
        login(request,user)
        #判断是否记住登陆
        if remembered:
            request.session.set_expiry(None)
        else:
            request.session.set_expiry(0)
        #返回json格式相应
        return JsonResponse({'code':0,'errmsg':'ok'})
