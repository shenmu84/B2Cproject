import re
from django.http import JsonResponse, HttpResponse

from django.views import View
from django_redis import get_redis_connection
from meiduo_mall.apps.mall.users.models import User
import json
from meiduo_mall.celery_tasks.email.tasks import celery_send_email
from meiduo_mall.utils.util import makeToken,checkToken
#todo SIhushi6653*
class tentative(View):
    def get(self,request):
        return JsonResponse({'code': 0, 'errmsg': 'ok'})
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
    def options(self, request, *args, **kwargs):
        # 手动处理 OPTIONS 请求，返回必要的 CORS 头部
        response = JsonResponse({"message": "OPTIONS request"})
        response["Access-Control-Allow-Origin"] = "*"  # 允许所有来源
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"  # 允许的请求方法
        response["Access-Control-Allow-Headers"] = "Content-Type, Authorization"  # 允许的请求头
        return response
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
        #登录后合并cookie的购物车和redis里的
        from meiduo_mall.utils.carts import merge_cookie_to_redis
        response = merge_cookie_to_redis(request,response)
        return response

#实现退出功能
from django.contrib.auth import logout
class LogoutView(View):
    def delete(self,request):
        #清除SEESION
        logout(request)
        response= JsonResponse({'code':0,'errmsg':'ok'})
        #清除前端的cookie缓存
        response.delete_cookie('username')
        return response
from django.core.mail import send_mail
class Browse_histories(View):
    def get(self,request):
        return JsonResponse({'code':0,'errmsg':'ok'})
class EmailVerifyView(View):
    def put(self,request):
        data=request.GET
        token=data.get('token')
        if token is None:
            return JsonResponse({'code':400,'errmsg':'ok'})
        from meiduo_mall.utils.util import checkToken
        userId=checkToken(token,3600)
        if userId is None:
            return JsonResponse({'code':400,'errmsg':'ok'})
        user=User.objects.get(id=userId)
        user.email_active=True
        user.save()
        return JsonResponse({'code':0,'errmsg':'ok'})
class EmailView(View):
    def put(self,request):
        data=json.loads(request.body.decode())
        email=data.get('email')
        user=request.user
        user.email=email
        user.save()
        #django的发送邮件类
        token=makeToken(request.user.id,3600)
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
from meiduo_mall.utils.views import LoginRequiredJSONMixin
class CenterView(LoginRequiredJSONMixin, View):


    def get(self,request):
        info_data={
            'username':request.user.username,
            'email':request.user.email,
            'mobile':request.user.mobile,
            'email_active':request.user.email_active,
        }
        return JsonResponse({'code':0,'errmsg':'ok','info_data':info_data})

from meiduo_mall.apps.mall.users.models import Address
class AddressCreateView(LoginRequiredJSONMixin,View):

    def post(self,request):
        user=request.user
        #判断地址上限
        count=user.addresses.count()
        if count>=20:
            return JsonResponse({'code':400,'errmsg':'地址数量超过上线'})
        # 1.接收请求
        data=json.loads(request.body.decode())
        # 2.获取参数，验证参数
        receiver=data.get('receiver')
        province_id=data.get('province_id')
        city_id=data.get('city_id')
        district_id=data.get('district_id')
        place=data.get('place')
        mobile=data.get('mobile')
        tel=data.get('tel')
        email=data.get('email')
        # 验证参数
        # 2.1 验证必传参数
        if not all([receiver,province_id,city_id,district_id,place,mobile]):
            return JsonResponse({'code':400,'errmsg':'缺少必传参数'})
        # 2.2 省市区的id 是否正确
        # 2.3 详细地址的长度
        if len(place)>20:
            return JsonResponse({'code':400,'errmsg':'地址太长'})
        # 2.4 手机号
        if not re.match(r'^1[3-9]\d{9}$',mobile):
            return JsonResponse({'code':400,'errmsg':'请输入合法手机号'})

        # 2.5 固定电话
        if tel:
            if not re.match(r'^1[3-9]\d{9}$',tel):
                return  JsonResponse({'code':400,'errmsg':'请输入合法手机号'})

        # 2.6 邮箱
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$',email):
                return JsonResponse({'code':400,'errmsg':'请输入合法邮箱'})
        # 3.数据入库
        try:
            address=Address.objects.create(
                user=user,
                title=receiver,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email
            )
        except Exception as e:
            return JsonResponse({'code':400,'errmsg':'请输入合法数据'})
        address_dict = {
            'id':address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }

        # 4.返回响应
        return JsonResponse({'code':0,'errmsg':'ok','address':address_dict})
class AddressView(LoginRequiredJSONMixin, View):
        def get(self, request):
            # 1.查询指定数据
            user = request.user
            # addresses=user.addresses
            addresses = Address.objects.filter(user=user, is_deleted=False)
            # 2.将对象数据转换为字典数据
            address_list = []
            for address in addresses:
                address_list.append({
                    "id": address.id,
                    "title": address.title,
                    "receiver": address.receiver,
                    "province": address.province.name,
                    "city": address.city.name,
                    "district": address.district.name,
                    "place": address.place,
                    "mobile": address.mobile,
                    "tel": address.tel,
                    "email": address.email
                })
            # 3.返回响应
            return JsonResponse({'code': 0, 'errmsg': 'ok', 'addresses': address_list})
from meiduo_mall.apps.mall.goods.models import SKU
class UserHistoryView(LoginRequiredJSONMixin, View):
    def post(self, request):
        user = request.user

        # 1. 接收请求
        data = json.loads(request.body.decode())
        # 2. 获取请求参数
        sku_id = data.get('sku_id')
        # 3. 验证参数
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return JsonResponse({'code': 400, 'errmsg': '没有此商品'})
        # 4. 连接redis    list
        redis_cli = get_redis_connection('history')
        # 5. 去重(先删除 这个商品id 数据，再添加就可以了)
        redis_cli.lrem('history_%s' % user.id, 0, sku_id)
        # 6. 保存到redsi中
        redis_cli.lpush('history_%s' % user.id, sku_id)
        # 7. 只保存5条记录
        redis_cli.ltrim("history_%s" % user.id, 0, 4)
        # 8. 返回JSON
        return JsonResponse({'code': 0, 'errmsg': 'ok'})

    def get(self, request):
        # 1. 连接redis
        redis_cli = get_redis_connection('history')
        # 2. 获取redis数据（[1,2,3]）
        ids = redis_cli.lrange('history_%s' % request.user.id, 0, 4)
        # [1,2,3]
        # 3. 根据商品id进行数据查询
        history_list = []
        for sku_id in ids:
            sku = SKU.objects.get(id=sku_id)
            # 4. 将对象转换为字典
            history_list.append({
                'id': sku.id,
                'name': sku.name,
                'default_image_url': sku.default_image.url,
                'price': sku.price
            })

        # 5. 返回JSON
        return JsonResponse({'code': 0, 'errmsg': 'ok', 'skus': history_list})

"""
用户相关API视图
"""
from typing import Any, Dict
from django.http import HttpRequest
from django.views import View
from django.contrib.auth import login, logout, authenticate
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django_redis import get_redis_connection
from django.contrib.auth import get_user_model

from utils.response import APIResponse
from utils.decorators import login_required, rate_limit, log_api_call, cache_response
from .models import User, Address
from .serializers import UserSerializer, AddressSerializer

User = get_user_model()

class UserRegisterView(View):
    """用户注册视图"""
    
    @log_api_call
    @rate_limit(limit=5, period=300)  # 5分钟内最多注册5次
    def post(self, request: HttpRequest) -> APIResponse:
        """
        用户注册
        
        Args:
            request: HTTP请求
            
        Returns:
            APIResponse: API响应
        """
        try:
            # 获取请求数据
            data = request.POST.dict()
            
            # 验证数据
            self._validate_register_data(data)
            
            # 检查用户名是否已存在
            if User.objects.filter(username=data['username']).exists():
                return APIResponse.error(message="用户名已存在")
                
            # 检查手机号是否已存在
            if data.get('mobile') and User.objects.filter(mobile=data['mobile']).exists():
                return APIResponse.error(message="手机号已被注册")
                
            # 检查邮箱是否已存在
            if data.get('email') and User.objects.filter(email=data['email']).exists():
                return APIResponse.error(message="邮箱已被注册")
            
            # 创建用户
            user = User.objects.create_user(
                username=data['username'],
                password=data['password'],
                email=data.get('email', ''),
                mobile=data.get('mobile', '')
            )
            
            # 自动登录
            login(request, user)
            
            # 序列化用户数据
            user_data = UserSerializer(user).data
            
            return APIResponse.success(
                data=user_data,
                message="注册成功"
            )
            
        except ValidationError as e:
            return APIResponse.error(message=str(e))
        except Exception as e:
            return APIResponse.server_error(str(e))
            
    def _validate_register_data(self, data: Dict[str, Any]) -> None:
        """
        验证注册数据
        
        Args:
            data: 注册数据
            
        Raises:
            ValidationError: 验证错误
        """
        # 验证用户名
        if not data.get('username'):
            raise ValidationError("用户名不能为空")
        if len(data['username']) < 3 or len(data['username']) > 20:
            raise ValidationError("用户名长度必须在3-20个字符之间")
            
        # 验证密码
        if not data.get('password'):
            raise ValidationError("密码不能为空")
        if len(data['password']) < 6 or len(data['password']) > 20:
            raise ValidationError("密码长度必须在6-20个字符之间")
            
        # 验证邮箱
        if data.get('email'):
            try:
                validate_email(data['email'])
            except ValidationError:
                raise ValidationError("邮箱格式不正确")
                
        # 验证手机号
        if data.get('mobile'):
            if not data['mobile'].isdigit() or len(data['mobile']) != 11:
                raise ValidationError("手机号格式不正确")

class UserLoginView(View):
    """用户登录视图"""
    
    @log_api_call
    @rate_limit(limit=10, period=300)  # 5分钟内最多登录10次
    def post(self, request: HttpRequest) -> APIResponse:
        """
        用户登录
        
        Args:
            request: HTTP请求
            
        Returns:
            APIResponse: API响应
        """
        try:
            # 获取请求数据
            data = request.POST.dict()
            
            # 验证数据
            if not data.get('username') or not data.get('password'):
                return APIResponse.error(message="用户名和密码不能为空")
                
            # 验证用户
            user = authenticate(
                username=data['username'],
                password=data['password']
            )
            
            if not user:
                return APIResponse.error(message="用户名或密码错误")
                
            if not user.is_active:
                return APIResponse.error(message="账号已被禁用")
                
            # 登录用户
            login(request, user)
            
            # 更新最后登录时间
            user.save()
            
            # 序列化用户数据
            user_data = UserSerializer(user).data
            
            return APIResponse.success(
                data=user_data,
                message="登录成功"
            )
            
        except Exception as e:
            return APIResponse.server_error(str(e))

class UserLogoutView(View):
    """用户登出视图"""
    
    @log_api_call
    @login_required
    def post(self, request: HttpRequest) -> APIResponse:
        """
        用户登出
        
        Args:
            request: HTTP请求
            
        Returns:
            APIResponse: API响应
        """
        try:
            # 清除用户会话
            logout(request)
            
            # 清除Redis中的用户数据
            redis_conn = get_redis_connection('default')
            redis_conn.delete(f'user:{request.user.id}:*')
            
            return APIResponse.success(message="登出成功")
        except Exception as e:
            return APIResponse.server_error(str(e))

class UserProfileView(View):
    """用户资料视图"""
    
    @log_api_call
    @login_required
    @cache_response(timeout=300)  # 缓存5分钟
    def get(self, request: HttpRequest) -> APIResponse:
        """
        获取用户资料
        
        Args:
            request: HTTP请求
            
        Returns:
            APIResponse: API响应
        """
        try:
            # 序列化用户数据
            user_data = UserSerializer(request.user).data
            
            return APIResponse.success(data=user_data)
            
        except Exception as e:
            return APIResponse.server_error(str(e))
            
    @log_api_call
    @login_required
    def put(self, request: HttpRequest) -> APIResponse:
        """
        更新用户资料
        
        Args:
            request: HTTP请求
            
        Returns:
            APIResponse: API响应
        """
        try:
            # 获取请求数据
            data = request.PUT.dict()
            
            # 验证数据
            self._validate_profile_data(data)
            
            # 更新用户资料
            user = request.user
            for key, value in data.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            user.save()
            
            # 清除缓存
            redis_conn = get_redis_connection('default')
            redis_conn.delete(f'user:{user.id}:*')
            
            # 序列化用户数据
            user_data = UserSerializer(user).data
            
            return APIResponse.success(
                data=user_data,
                message="更新成功"
            )
            
        except ValidationError as e:
            return APIResponse.error(message=str(e))
        except Exception as e:
            return APIResponse.server_error(str(e))
            
    def _validate_profile_data(self, data: Dict[str, Any]) -> None:
        """
        验证用户资料数据
        
        Args:
            data: 用户资料数据
            
        Raises:
            ValidationError: 验证错误
        """
        # 验证邮箱
        if data.get('email'):
            try:
                validate_email(data['email'])
            except ValidationError:
                raise ValidationError("邮箱格式不正确")
                
        # 验证手机号
        if data.get('mobile'):
            if not data['mobile'].isdigit() or len(data['mobile']) != 11:
                raise ValidationError("手机号格式不正确")

class UserAddressView(View):
    """用户地址视图"""
    
    @log_api_call
    @login_required
    def get(self, request: HttpRequest) -> APIResponse:
        """
        获取用户地址列表
        
        Args:
            request: HTTP请求
            
        Returns:
            APIResponse: API响应
        """
        try:
            # 获取用户地址列表
            addresses = Address.objects.filter(user=request.user, is_deleted=False)
            
            # 序列化地址数据
            address_data = AddressSerializer(addresses, many=True).data
            
            return APIResponse.success(data=address_data)
            
        except Exception as e:
            return APIResponse.server_error(str(e))
            
    @log_api_call
    @login_required
    def post(self, request: HttpRequest) -> APIResponse:
        """
        创建用户地址
        
        Args:
            request: HTTP请求
            
        Returns:
            APIResponse: API响应
        """
        try:
            # 获取请求数据
            data = request.POST.dict()
            
            # 验证数据
            self._validate_address_data(data)
            
            # 检查地址数量限制
            if Address.objects.filter(user=request.user, is_deleted=False).count() >= 20:
                return APIResponse.error(message="地址数量已达上限")
            
            # 创建地址
            address = Address.objects.create(
                user=request.user,
                **data
            )
            
            # 序列化地址数据
            address_data = AddressSerializer(address).data
            
            return APIResponse.success(
                data=address_data,
                message="创建成功"
            )
            
        except ValidationError as e:
            return APIResponse.error(message=str(e))
        except Exception as e:
            return APIResponse.server_error(str(e))
            
    def _validate_address_data(self, data: Dict[str, Any]) -> None:
        """
        验证地址数据
        
        Args:
            data: 地址数据
            
        Raises:
            ValidationError: 验证错误
        """
        # 验证必填字段
        required_fields = ['receiver', 'province', 'city', 'district', 'place', 'mobile']
        for field in required_fields:
            if not data.get(field):
                raise ValidationError(f"{field}不能为空")
                
        # 验证手机号
        if not data['mobile'].isdigit() or len(data['mobile']) != 11:
            raise ValidationError("手机号格式不正确")
            
        # 验证固定电话
        if data.get('tel'):
            if not data['tel'].isdigit() or len(data['tel']) < 5:
                raise ValidationError("固定电话格式不正确")
                
        # 验证邮箱
        if data.get('email'):
            try:
                validate_email(data['email'])
            except ValidationError:
                raise ValidationError("邮箱格式不正确")
