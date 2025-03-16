import re
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views import View
from apps.users.models import User
import json
from celery_tasks.email.tasks import celery_send_email
from utils.util import makeToken,checkToken


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
        response= JsonResponse({'code':0,'errmsg':'ok'})
        #为了让前端获取cookie中的用户信息
        response.set_cookie('username',username)
        return response

#实现退出功能
from django.contrib.auth import logout
class LogoutView(View):
    def get(self,request):
        #清除SEESION
        logout(request)
        response= JsonResponse({'code':0,'errmsg':'ok'})
        #清除前端的cookie缓存
        response.delete_cookie('username')
        return response
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
class Browse_histories(View):
    def get(self,request):
        return JsonResponse({'code':0,'errmsg':'ok'})
class EmailView(View):
    def put(self,request):
        data=json.loads(request.body.decode())
        email=data.get('email')
        user=request.user
        user.email=email
        user.save()
        #django的发送邮件类
        token=makeToken(request.user.id)
        verify_url = "http://www.meiduo.site:8080/success_verify_email.html?token=%s" % token
        # 4.2 组织我们的激活邮件
        html_message='<p>尊敬的用户您好！</p>' \
                       '<p>感谢您使用美多商城。</p>' \
                       '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
                       '<p><a href="%s">%s<a></p>'% (email, verify_url, verify_url)

        subject='这是主题'
        message='Here is the message.'
        from_email='shenmu_ovo@163.com'
        recipient_list=['htt656264405.q@qq.com']
        html_message=html_message
        celery_send_email.delay(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list,
            html_message=html_message
        )
        return JsonResponse({'code':0,'errmsg':'ok'})
class CenterView(LoginRequiredMixin, View):

    def handle_no_permission(self):
        return JsonResponse({'code':400,'errmsg':'没有登录'})
    def get(self,request):
        info_data={
            'username':request.user.username,
            'email':request.user.email,
            'mobile':request.user.mobile,
            'email_active':request.user.email_active,
        }
        return JsonResponse({'code':0,'errmsg':'ok','info_data':info_data})