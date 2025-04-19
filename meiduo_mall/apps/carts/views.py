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
            #redis是byte数据，需转换
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
                # 5.未登录用户更新cookie
                #     5.1 先读取购物车数据
                cookie_cart=request.COOKIES.get('carts')
                #         判断有没有。
                if cookie_cart is not None:
                    #         如果有则解密数据
                    carts=pickle.loads(base64.b64decode(cookie_cart))
                else:
                    #         如果没有则初始化一个空字典
                    carts={}
                #     5.2 更新数据
                # {sku_id: {count:xxx,selected:xxx}}
                if sku_id in carts:
                    carts[sku_id]={
                        'count':count,
                        'selected':selected
                    }
                #     5.3 重新最字典进行编码和base64加密
                new_carts=base64.b64encode(pickle.dumps(carts))
                #     5.4 设置cookie
                response = JsonResponse({'code':0,'errmsg':'ok','cart_sku':{'count':count,'selected':selected}})
                response.set_cookie('carts',new_carts.decode(),max_age=14*24*3600)
                #     5.5 返回响应
                return response
    def delete(self,request):
        #获取数据
        content=request.body
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
            # 5.未登录用户操作cookie
            #     5.1 读取cookie中的购物车数据
            cookie_cart = request.COOKIES.get('carts')
            #     判断数据是否存在
            if cookie_cart is not None:
                #     存在则解码
                carts = pickle.loads(base64.b64decode(cookie_cart))
                #     5.2 删除数据 {}
                del carts[sku_id]
            else:
                #     不存在则初始化字典
                carts = {}
            #     5.3 我们需要对字典数据进行编码和base64的处理
            new_carts = base64.b64encode(pickle.dumps(carts))
            #     5.4 设置cookie
            response = JsonResponse({'code': 0, 'errmsg': 'ok'})
            response.set_cookie('carts', new_carts.decode(), max_age=14 * 24 * 3600)
            #     5.5 返回响应
            return response