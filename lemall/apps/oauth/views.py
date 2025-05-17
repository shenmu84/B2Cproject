import http

from django.http import JsonResponse
from django_redis.serializers import json
from utils.util import makeToken,checkToken
from apps.users.models import User
from django.contrib.auth import login
from apps.oauth.models import OAuthGITEEUser
from django.views import View
import json
from lemall import settings
from apps.oauth.utils import OAuthGITEE
class GITEELoginURLView(View):
    def get(self, request):
        gitee=OAuthGITEE(client_id=settings.GITEE_CLIENT_ID,
                   client_secret=settings.GITEE_CLIENT_SECRET,
                   redirect_uri=settings.GITEE_REDIRECT_URI,
                   state=None)
        gitee_login_url = gitee.get_gitee_url()
        return JsonResponse({'code':0,'errmsg':'ok','login_url':gitee_login_url})



class OauthGITEEView(View):
    def get(self, request):
        # 1. 获取code  378a
        code = request.GET.get('code')
        if code is None:
            return JsonResponse({'code': 400, 'errmsg': '参数不全'})
        # 2. 通过code换取token
        gitee = OAuthGITEE(client_id=settings.GITEE_CLIENT_ID,
                     client_secret=settings.GITEE_CLIENT_SECRET,
                     redirect_uri=settings.GITEE_REDIRECT_URI,
                     state='xxxxx')

        token = gitee.get_access_token(code)
        # 3. 再通过token换取openid
        openid = gitee.get_open_id(token)
        # 4. 根据openid进行查询判断
        try:
            giteeuser = OAuthGITEEUser.objects.get(openid=openid)
        except OAuthGITEEUser.DoesNotExist:
            # 不存在
            # 5. 如果没有绑定过，则需要绑定
            access_token = makeToken(openid,3600)
            #前端拿着这个凭证去进行绑定
            response = JsonResponse({'code': 400, 'access_token': access_token})
            return response
        else:
            # 存在
            # 6. 如果绑定过，则直接登录
            # 6.1 设置session
            login(request, giteeuser.user)
            # 6.2 设置cookie
            response = JsonResponse({'code': 0, 'errmsg': 'ok'})
            response.set_cookie('username', giteeuser.user.username)
            return response
#绑定第三方信息和数据库中的
    def post(self,request):
        # 1. 接收请求
        data=json.loads(request.body.decode())
        # 2. 获取请求参数  openid
        mobile=data.get('mobile')
        password=data.get('password')
        sms_code=data.get('sms_code')
        access_token=data.get('access_token')
        #SIhushi6653*

        import re
        if not all([mobile, password, sms_code]):
            return JsonResponse({'code': 400, 'errmsg': '缺少必要参数'})
        # 判断手机号是否合格
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return JsonResponse({'code': 400,
                                      'errmsg': '请输入正确的手机号码'})

        # 判断密码是否合格
        if not re.match(r'^[0-9A-Za-z!@#$%^&*(),.?":{}|<>]{8,20}$', password):
            return JsonResponse({'code': 400,
                                      'errmsg': '请输入8-20位的密码'})
        from django_redis import get_redis_connection
        redis_conn = get_redis_connection('code')
        sms_code_client = redis_conn.get('sms_code_%s' % mobile)
        #这个数据库里面没有数据
        if sms_code_client is None:
            return JsonResponse({'code': 400, 'errmsg': '验证码失效'})
        if sms_code_client != sms_code_client:
            return JsonResponse({'code': 400, 'errmsg': '验证码错误'})
        from utils.util import checkToken
        # 添加对 access-token 解密
        openid=checkToken(access_token,3600)
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
        OAuthGITEEUser.objects.create(user=user,openid=openid)
        # 6. 完成状态保持
        login(request,user)
        # 7. 返回响应
        response=JsonResponse({'code':0,'errmsg':'ok'})

        response.set_cookie('username',user.username)

        return response


