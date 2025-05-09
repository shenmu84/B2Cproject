import re
from django.http import JsonResponse, HttpResponse

from django.views import View
from django_redis import get_redis_connection
from apps.users.models import User
import json
from celery_tasks.email.tasks import celery_send_email
from utils.util import makeToken,checkToken
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
        from utils.carts import merge_cookie_to_redis
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
        from utils.util import checkToken
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
        verify_url = "http://www.meiduo.site:8000/success_verify_email.html?token=%s" % token
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
from utils.views import LoginRequiredJSONMixin
class CenterView(LoginRequiredJSONMixin, View):


    def get(self,request):
        info_data={
            'username':request.user.username,
            'email':request.user.email,
            'mobile':request.user.mobile,
            'email_active':request.user.email_active,
        }
        return JsonResponse({'code':0,'errmsg':'ok','info_data':info_data})

from apps.users.models import Address
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
from apps.goods.models import SKU
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
