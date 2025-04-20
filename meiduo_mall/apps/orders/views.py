from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django_redis import get_redis_connection
from redis.asyncio.utils import pipeline

from apps.users.models import Address


# Create your views here.
class OrderSettlementView(View):
    def get(self,request):
        user=request.user
        addresses=Address.objects.filter(user=user)
        addresses_list = []
        for address in addresses:
            addresses_list.append({
                'id': address.id,
                'province': address.province.name,
                'city': address.city.name,
                'district': address.district.name,
                'place': address.place,
                'receiver': address.receiver,
                'mobile': address.mobile
            })
        redis_cli=get_redis_connection('carts')
        pipeline=redis_cli.pipeline()
        pipeline.hgetall('carts_%s' % user.id)
        #     3.3 set         [1,2]
        pipeline.smembers('selected_%s' % user.id)
        # 我们接收 管道统一执行之后，返回的结果
        result = pipeline.execute()
        sku_id_counts = result[0]  # {sku_id:count,sku_id:count}
        selected_ids = result[1]
        selected_info={}
        for id in selected_ids:
            selected_info[int(id)]=int(sku_id_counts[id])
        from apps.goods.models import SKU
        sku_list = []
        for sku_id, count in selected_info.items():
            sku = SKU.objects.get(pk=sku_id)
            #     3.6 需要将对象数据转换为字典数据
            sku_list.append({
                'id': sku.id,
                'name': sku.name,
                'count': count,
                'default_image_url': sku.default_image.url,
                'price': sku.price
            })

        # 运费
        from decimal import Decimal
        freight = Decimal('10')
        content = {
            'skus': sku_list,
            'addresses': addresses_list,
            'freight': freight  # 运费
        }

        return JsonResponse({'code': 0, 'errmsg': 'ok', 'context': content})
