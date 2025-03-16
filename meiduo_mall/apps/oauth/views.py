from django.http import JsonResponse
from django_redis.serializers import json
from utils.util import makeToken,checkToken
from apps.oauth.models import OAuthQQUser
from apps.users.models import User
from django.contrib.auth import login
from QQLoginTool.QQtool import OAuthQQ
from django.views import View

from meiduo_mall import settings

#TODO 测试用户点开图标是否能跳转到QQ那里 07
class QQLoginURLView(View):
    def post(self, request):
        qq=OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                   client_secret=settings.QQ_CLIENT_SECRET,
                   redirect_uri=settings.QQ_REDIRECT_URI,
                   state=None)
        qq_login_url = qq.get_qq_url()
        return JsonResponse({'code':0,'errmsg':'ok','login_url':qq_login_url})
        pass


class OauthQQView(View):
    def get(self, request):
        # 1. 获取code
        code = request.GET.get('code')
        if code is None:
            return JsonResponse({'code': 400, 'errmsg': '参数不全'})
        # 2. 通过code换取token
        qq = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                     client_secret=settings.QQ_CLIENT_SECRET,
                     redirect_uri=settings.QQ_REDIRECT_URI,
                     state='xxxxx')
        # '5D52C8BAB528D363DBCD3FC0CEDA0BA7'
        token = qq.get_access_token(code)
        # 3. 再通过token换取openid
        # 'CBCF1AA40E417CD73880666C3D6FA1D6'
        openid = qq.get_open_id(token)
        # 4. 根据openid进行查询判断
        try:
            qquser = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            # 不存在
            # 5. 如果没有绑定过，则需要绑定

            access_token = makeToken(openid)
            #前端拿着这个凭证去进行绑定
            response = JsonResponse({'code': 400, 'access_token': access_token})
            return response
        else:
            # 存在
            # 6. 如果绑定过，则直接登录
            # 6.1 设置session
            login(request, qquser.user)
            # 6.2 设置cookie
            response = JsonResponse({'code': 0, 'errmsg': 'ok'})
            response.set_cookie('username', qquser.user.username)
            return response
        #TODO 测试是否能使用 13
    def post(self,request):
        # 1. 接收请求
        data=json.loads(request.body.decode())
        # 2. 获取请求参数  openid
        mobile=data.get('mobile')
        password=data.get('password')
        sms_code=data.get('sms_code')
        access_token=data.get('access_token')
        # 需要对数据进行验证（省略）

        # 添加对 access-token 解密
        openid=checkToken(access_token)
        if openid is None:
            return JsonResponse({'code':400,'errmsg':'参数缺失'})

        # 3. 根据手机号进行用户信息的查询
        try:
            user=User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            #手机号不存在
            # 5. 查询到用户手机号没有注册。我们就创建一个user信息。然后再绑定
            user=User.objects.create_user(username=mobile,mobile=mobile,password=password)

        else:
            #手机号存在
            # 4. 查询到用户手机号已经注册了。判断密码是否正确。密码正确就可以直接保存（绑定） 用户和openid信息
            if not user.check_password(password):
                return JsonResponse({'code':400,'errmsg':'账号或密码错误'})

        OAuthQQUser.objects.create(user=user,openid=openid)

        # 6. 完成状态保持
        login(request,user)
        # 7. 返回响应
        response=JsonResponse({'code':0,'errmsg':'ok'})

        response.set_cookie('username',user.username)

        return response
