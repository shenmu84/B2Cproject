from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views import View
from django_redis import get_redis_connection
from random import randint
from libs.yuntongxun.sms import CCP

class SmsCodeView(View):
   def get(self, request, mobile):
      # 1. 获取请求参数
      image_code = request.GET.get('image_code')
      uuid = request.GET.get('image_code_id')
      # 2. 验证参数
      if not all([image_code, uuid]):
         return JsonResponse({'code': 400, 'errmsg': '参数不全'})
      # 3. 验证图片验证码
      # 3.1 连接redis
      from django_redis import get_redis_connection
      redis_cli = get_redis_connection('code')
      # 3.2 获取redis数据
      redis_image_code = redis_cli.get(uuid)
      if redis_image_code is None:
         return JsonResponse({'code': 400, 'errmsg': '图片验证码已过期'})
      # 3.3 对比
      if redis_image_code.decode().lower() != image_code.lower():
         return JsonResponse({'code': 400, 'errmsg': '图片验证码错误'})
      send_flag=redis_cli.get('send_flag_%s' % mobile)
      if send_flag is not None:
         return JsonResponse({'code':400,'errmsg':'不要频繁发送短信'})
      # 4. 生成短信验证码
      sms_code = '%04d' % randint(0, 9999)
      # 5. 保存短信验证码
      pipline=redis_cli.pipeline()

      pipline.setex(mobile, 300, sms_code)
      pipline.setex('sms_code_%s' % mobile,300,sms_code)
      pipline.setex('send_flag_%s'%mobile,60,1)
      pipline.execute()
      # 6. 发送短信验证码
      from celery_tasks.sms.tasks import celery_send_sms_code
      celery_send_sms_code.delay(mobile,sms_code)
      #我怎么指导短信验证码是否正确 TODO
      # 7. 返回响应
      return JsonResponse({'code': 0, 'errmsg': 'ok'})

# Create your views here.
class ImageCodeView(View):
    def get(self,request,uuid):
       #接受路由中的UUID
       #生成图片验证码和图片二进制
       from libs.captcha.captcha import captcha
       #TEXT=图片验证码内容,IMAGE=图片二进制
       text,image = captcha.generate_captcha()
       #用redis保存验证码，返回图片二进制
       from django_redis import get_redis_connection
       #连接数据库，code是设置里配置好的
       redis_conn = get_redis_connection('code')
       #指令
       redis_conn.setex(uuid,100,text)
       return HttpResponse(image,content_type='image/jpeg')