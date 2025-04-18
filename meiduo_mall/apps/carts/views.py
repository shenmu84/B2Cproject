import base64
import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django_redis import get_redis_connection
import pickle
from apps.goods.models import SKU

'''购物车获取数据
检验数据是否存在
登录的获取id放到redis
未登录放cookie里


'''
class CartsView(View):
    def post(self,request):
        data=json.loads(request.body.decode())
        sku_id=data.get('sku_id')
        count = data.get('count')
        # 2.验证数据
        try:
            sku =SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return JsonResponse({'code': 400, 'errmsg': '查无此商品'})
        user=request.user
        if user.is_authenticated:
            redis_cli=get_redis_connection("carts")
            pipeline = redis_cli.pipeline()
            #     4.2 操作hash
            # redis_cli.hset(key,field,value)
            # 1. 先获取之前的数据，然后累加
            # 2.
            # redis_cli.hset('carts_%s'%user.id,sku_id,count)
            # hincrby
            # 会进行累加操作
            pipeline.hincrby('carts_%s' % user.id, sku_id, count)
            #     4.3 操作set
            # 默认就是选中
            pipeline.sadd('selected_%s' % user.id, sku_id)

            # 一定要执行！！！
            pipeline.execute()
            #     4.4 返回响应
            return JsonResponse({'code': 0, 'errmsg': 'ok'})
        else:
            cookie_carts = request.COOKIES.get('carts')
            if cookie_carts:
                # 对加密的数据解密
                carts = pickle.loads(base64.b64decode(cookie_carts))
            else:
                #5.1 先有cookie字典
                carts = {}
            # 判断新增的商品 有没有在购物车里
            if sku_id in carts:
                # 购物车中 已经有该商品id
                # 数量累加
                origin_count = carts[sku_id]['count']
                count += origin_count
            carts[sku_id] = {
                'count': count,
                'selected': True
            }
            response=JsonResponse({'code': 0, 'errmsg': 'ok'})
            response.set_cookie('carts', base64.b64encode(pickle.dumps(carts)).decode(), max_age=3600)
            return response
    def get(self,request):
        user=request.user
        if user.is_authenticated:
            redis_cli=get_redis_connection("carts")
            # hgetall把Redis 的 Hash 类型数据读取出来，并转为 Python 能用的格式。
            sku_id_count=redis_cli.hgetall("carts_%s" % user.id)
            selected_ids=redis_cli.smembers("selected_%s" % user.id)
            #将redis的数据格式转换成cookie的字典
            carts={}
            for sku_id,count in sku_id_count.items():
                carts[int(sku_id)] = {
                    'count': int(count),
                    'selected': sku_id in selected_ids
                }
        else:
            cookie=request.COOKIES.get('carts')
            if cookie is not None:
                carts=pickle.loads(base64.b64decode(cookie))
            else:
                carts={}
        #根据已经有的信息，创建商品信息，用列表传递除去
        sku_ids = carts.keys()
        # [1,2,3,4,5]
        # 可以遍历查询
        # 也可以用 in
        skus = SKU.objects.filter(id__in=sku_ids)

        sku_list = []
        for sku in skus:
            # 5 将对象数据转换为字典数据
            sku_list.append({
                'id': sku.id,
                'price': sku.price,
                'name': sku.name,
                'default_image_url': sku.default_image.url,
                'selected': carts[sku.id]['selected'],  # 选中状态
                'count': int(carts[sku.id]['count']),  # 数量 强制转换一下
                'amount': sku.price * carts[sku.id]['count']  # 总价格
            })
        # 6 返回响应
        return JsonResponse({'code': 0, 'errmsg': 'ok', 'cart_skus': sku_list})

