import jwt
import logging
from django.contrib.auth import get_user_model, authenticate
from django.utils import timezone
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django_redis import get_redis_connection
from rest_framework.exceptions import AuthenticationFailed
import datetime
from meiduo_mall.meiduo_mall.settings import REDIS_KEY_ADMIN, REDIS_KEY_RESOURCE_LIST, REDIS_EXPIRE_COMMON
from .models import UmsAdminLoginLog, UmsAdmin,UmsAdminRoleRelation

logger = logging.getLogger(__name__)

User = get_user_model()

class JwtTokenUtil:
    @staticmethod
    def generate_token(user):
        # 使用用户的 ID 生成一个 JWT token，设置过期时间为 1 天
        payload = {
            'user_id': user.id,
            'username': user.username,
            'exp': timezone.now() + timezone.timedelta(days=1)
        }
        return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm='HS256')

class UserDetails:
    def __init__(self, user):
        self.username = user.username
        self.password = user.password
        self.is_enabled = user.is_active
        self.user_id = user.id

    def get_password(self):
        return self.password

    def get_authorities(self):
        return []  # 此处可根据需求返回用户的权限角色列表

    def is_enabled(self):
        return self.is_enabled
import json

class UserService:
    def getAdminByUsername(username):
        userDetails=[]
        """
        1.获取账户信息
        """
        # 使用 get_redis_connection 获取 history 数据库连接
        redis_cli = get_redis_connection('ums')  # 获取名为 'history' 的 Redis 连接

        # Redis 缓存 key
        key = f"{REDIS_KEY_ADMIN}:{username}"

        # 先从 Redis 缓存中获取数据
        adminID = redis_cli.get(key)

        if adminID:
            # 如果缓存中存在，返回从缓存中获取的 admin 数据
            userDetails.append(adminID)  # 假设 UmsAdmin 有 from_json 方法来解析缓存数据
        # Redis 缓存中没有，从数据库查询
        else:
            try:
                admin = UmsAdmin.objects.get(username=username)
                #存入缓存
                key = f"{REDIS_KEY_ADMIN}:{admin.username}"
                redis_cli.setex(key, REDIS_EXPIRE_COMMON, str(admin.id)) # 写入缓存
                userDetails.append(str(admin.id))
            except :
                return None
        # 2.获取ResourceList

        key = f"{REDIS_KEY_RESOURCE_LIST}:{userDetails[0]}"
        cached_data = redis_cli.get(key)
        if cached_data:
            resource_list = json.loads(cached_data)
        else:
            # 缓存未命中，查数据库
            resource_list =UmsAdminRoleRelation.objects.get(userDetails[0])
            if resource_list:
                #存入缓存
                key = f"{REDIS_KEY_RESOURCE_LIST}:{userDetails[0].id}"
                data = [res.to_dict() for res in resource_list]
                redis_cli.setex(key, REDIS_EXPIRE_COMMON, json.dumps(data, cls=DjangoJSONEncoder))
            userDetails.append(resource_list)
        return userDetails


    def generate_token(user):
        """
        根据用户对象生成 JWT Token
        """
        payload = {
            'username': user.username,
            'created': datetime.datetime.utcnow().isoformat(),
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7),  # 设置过期时间（7天）
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS512')
        return token


from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from django.contrib.auth import login as django_login
def login(self, request,username, password):
    token = None
    userDetails = self.getAdminByUsername(username)
    user=UmsAdmin.objects.get(id=userDetails[0])
    resource=userDetails[1]
    # 使用 Django 自带的认证系统验证密码
    if not user.check_password(password):
        raise AuthenticationFailed("密码不正确")

    # 检查用户是否被禁用
    if not user.active:
        raise AuthenticationFailed("帐号已被禁用")
    # 权限列表（等效 userDetails.getAuthorities()）
    authorities = [f"{res.id}:{res.name}" for res in resource.objects.filter(id=user.id).all()]
    #  将权限挂载到 request.user 上，供后续视图访问
    request.user.authorities = authorities
    #request.user.authorities 只在这个请求中有效（不会持久化）
    # 登录用户，设置 session 等（Django 相当于 SecurityContextHolder）
    django_login(request, user)

    # 可选：更新用户的登录时间
    update_last_login(None, user)

    # 生成 JWT token
    token = self.generate_token(user)
    return token





    def update_login_time(self, username):
        # 更新登录时间（此处是示例，您可以根据需求修改）
        user = self.get_user_by_username(username)
        if user:
            user.last_login = timezone.now()
            user.save()
