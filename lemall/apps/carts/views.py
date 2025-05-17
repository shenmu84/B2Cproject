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
from utils.carts import *
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
            carts=getCartFromCook(request)
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
            return setCartToCookie(response, carts)
    def get(self,request):
        user=request.user
        if user.is_authenticated:
            redis_cli=get_redis_connection("carts")
            sku_id_count=redis_cli.hgetall("carts_%s" % user.id)
            selected_ids=redis_cli.smembers("selected_%s" % user.id)
            carts={}
            for sku_id,count in sku_id_count.items():
                carts[int(sku_id)] = {
                    'count': int(count),
                    'selected': sku_id in selected_ids
                }
        else:
            carts=getCartFromCook(request)
        #根据已经有的信息，创建商品信息，用列表传递除去
        sku_ids = carts.keys()
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

    def put(self,request):
            # 1.获取用户信息
            user=request.user
            # 2.接收数据
            data=json.loads(request.body.decode())
            sku_id=data.get('sku_id')
            count=data.get('count')
            selected=data.get('selected')
            # 3.验证数据
            if not all([sku_id,count]):
                return JsonResponse({'code':400,'errmsg':'参数不全'})
            try:
                SKU.objects.get(id=sku_id)
            except SKU.DoesNotExist:
                return JsonResponse({'code':400,'errmsg':'没有此商品'})
            try:
                count=int(count)
            except Exception:
                count=1

            if user.is_authenticated:
                # 4.登录用户更新redis
                #     4.1 连接redis
                redis_cli=get_redis_connection('carts')
                #     4.2 hash
                redis_cli.hset('carts_%s'%user.id,sku_id,count)
                #     4.3 set
                if selected:
                    redis_cli.sadd('selected_%s'%user.id,sku_id)
                else:
                    redis_cli.srem('selected_%s'%user.id,sku_id)

                #     4.4 返回响应
                return JsonResponse({'code':0,'errmsg':'ok','cart_sku':{'count':count,'selected':selected}})

            else:
                carts=getCartFromCook(request)
                #     5.2 更新数据
                # {sku_id: {count:xxx,selected:xxx}}
                if sku_id in carts:
                    carts[sku_id]={
                        'count':count,
                        'selected':selected
                    }
                response = JsonResponse({'code':0,'errmsg':'ok','cart_sku':{'count':count,'selected':selected}})
                return setCartToCookie(response, carts)
    def delete(self,request):
        #获取数据
        decode=request.body.decode()
        data=json.loads(decode)
        sku_id=data.get('sku_id')
        #验证数据
        try:
            SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return JsonResponse({'code':400,'errmsg':'没有此商品'})
        #处理数据
        user=request.user
        if user.is_authenticated:
            redis_cli=get_redis_connection('carts')
            pipeline = redis_cli.pipeline()
            pipeline.hdel('carts_%s'%user.id,sku_id)
            pipeline.srem('selected_%s'%user.id,sku_id)
            pipeline.execute()
            return  JsonResponse({'code': 0, 'errmsg': 'ok'})
        else:
            carts=getCartFromCook(request)
            if carts:
                del carts[sku_id]
            response = JsonResponse({'code': 0, 'errmsg': 'ok'})

            return setCartToCookie(response,carts)