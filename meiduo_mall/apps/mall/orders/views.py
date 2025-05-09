import json

from django.db import transaction
from django.utils import timezone
from datetime import datetime
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django_redis import get_redis_connection
from rest_framework import status
from utils.response import APIResponse
from utils.decorators import log_api_call, login_required
from .serializers import OrderSerializer
from .models import OrderInfo

from apps.mall.goods.models import SKU
from apps.mall.users.models import Address
from utils.carts import getSkucount


#TODO 这里的结算后购物车被结算数据应该被清空
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
        result=getSkucount(user)
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
from apps.mall.orders.models import OrderInfo,OrderGoods
# 这段代码有bug，执行出错，明天debug检查哪里出错 TODO
class OrderCommitView(LoginRequiredMixin, View):
    def post(self,request):
        #获取数据
        user=request.user
        data=json.loads(request.body.decode())
        address_id=data.get('address_id')
        pay_method=data.get('pay_method')
        #验证数据
        if not all([address_id,pay_method]):
            return JsonResponse({'code':400,'errmsg':"参数不全"})
        try:
            address=Address.objects.get(id=address_id)
        except Address.DoesNotExist:
            return JsonResponse({'code':400,'errmsg':"参数不正确"})
        if pay_method not in [OrderInfo.PAY_METHODS_ENUM['CASH'],OrderInfo.PAY_METHODS_ENUM['ALIPAY']]:
            return JsonResponse({'code':400,'errmsg':'參數不正確'})

        #处理数据
        order_id=timezone.localtime().strftime('%Y%m%d%H%M%S%f')+'%09d'%user.id
        if pay_method == OrderInfo.PAY_METHODS_ENUM['CASH']:
            status=OrderInfo.ORDER_STATUS_ENUM['UNSEND']
        else:
            status=OrderInfo.ORDER_STATUS_ENUM['UNPAID']
            # 总数量，总金额， = 0
        total_count = 0
        from decimal import Decimal
        total_amount = Decimal('0')  # 总金额
        # 运费
        freight = Decimal('10.00')
        with transaction.atomic():
            point= transaction.savepoint()
            try:
                orderinfo = OrderInfo.objects.create(
                    order_id=order_id,
                    user=user,
                    address=address,
                    total_count=total_count,
                    total_amount=total_amount,
                    freight=freight,
                    pay_method=pay_method,
                    status=status
                )
            except:
                return JsonResponse({'code':400,'errmsg':'数据创建失败'})
            result = getSkucount(user)
            skuID_counts = result[0]  # {sku_id:count,sku_id:count}
            selected = result[1]
            carts={}
            for id in selected:
                carts[int(id)] = int(skuID_counts[id])
            for id,count in carts.items():
                for i in range(10):
                    sku=SKU.objects.get(pk=id)
                    if sku.stock < count:
                        transaction.savepoint_rollback(point)
                        return JsonResponse({'code':400,'errmsg':'库存不足'})
                    from time import sleep
                    sleep(7)
                    oldStock=sku.stock
                    #库存减少，销量增加
                    newStock=sku.stock  -count
                    newSales=sku.sales  +count
                    res=SKU.objects.filter(id=id,stock=oldStock).update(stock=newStock,sales=newSales)
                    if res==0:
                        sleep(0.7)
                        continue
                    else:
                        redis_cli=get_redis_connection('carts')
                        pipeline=redis_cli.pipeline()
                        for id in selected:
                            pipeline.hdel('carts_%s'%user.id,id)
                            pipeline.srem('selected_%s' % user.id,id)
                        pipeline.execute()
                    #订单总数量和总金额
                    orderinfo.total_count += count
                    orderinfo.total_amount += (count*sku.price)
                    OrderGoods.objects.create(
                        order=orderinfo,
                        sku=sku,
                        count=count,
                        price=sku.price
                    )
                    break
            orderinfo.save()
            transaction.savepoint_commit(point)
        return JsonResponse({'code':0,'errmsg':'ok','order_id':order_id})

class OrderView(View):
    """订单视图"""
    
    @log_api_call
    @login_required
    def post(self, request: HttpRequest) -> APIResponse:
        """
        创建订单
        
        Args:
            request: HTTP请求
            
        Returns:
            APIResponse: API响应
        """
        try:
            # 获取请求数据
            data = request.POST.dict()
            
            # 验证数据
            serializer = OrderSerializer(data=data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            
            # 创建订单
            order = serializer.save()
            
            return APIResponse.success(
                data=serializer.data,
                message="订单创建成功"
            )
            
        except Exception as e:
            return APIResponse.server_error(str(e))
            
    @log_api_call
    @login_required
    def get(self, request: HttpRequest) -> APIResponse:
        """
        获取订单列表
        
        Args:
            request: HTTP请求
            
        Returns:
            APIResponse: API响应
        """
        try:
            # 获取用户订单
            orders = OrderInfo.objects.filter(user=request.user).order_by('-create_time')
            
            # 序列化数据
            serializer = OrderSerializer(orders, many=True)
            
            return APIResponse.success(data=serializer.data)
            
        except Exception as e:
            return APIResponse.server_error(str(e))
            
class OrderDetailView(View):
    """订单详情视图"""
    
    @log_api_call
    @login_required
    def get(self, request: HttpRequest, order_id: str) -> APIResponse:
        """
        获取订单详情
        
        Args:
            request: HTTP请求
            order_id: 订单ID
            
        Returns:
            APIResponse: API响应
        """
        try:
            # 获取订单
            try:
                order = OrderInfo.objects.get(order_id=order_id, user=request.user)
            except OrderInfo.DoesNotExist:
                return APIResponse.not_found(message="订单不存在")
                
            # 序列化数据
            serializer = OrderSerializer(order)
            
            return APIResponse.success(data=serializer.data)
            
        except Exception as e:
            return APIResponse.server_error(str(e))
            
    @log_api_call
    @login_required
    def put(self, request: HttpRequest, order_id: str) -> APIResponse:
        """
        更新订单状态
        
        Args:
            request: HTTP请求
            order_id: 订单ID
            
        Returns:
            APIResponse: API响应
        """
        try:
            # 获取订单
            try:
                order = OrderInfo.objects.get(order_id=order_id, user=request.user)
            except OrderInfo.DoesNotExist:
                return APIResponse.not_found(message="订单不存在")
                
            # 获取请求数据
            data = request.PUT.dict()
            status = data.get('status')
            
            if not status:
                return APIResponse.error(message="订单状态不能为空")
                
            # 验证状态
            if status not in OrderInfo.ORDER_STATUS_ENUM.values():
                return APIResponse.error(message="订单状态不正确")
                
            # 更新订单状态
            order.status = status
            order.save()
            
            return APIResponse.success(message="订单状态更新成功")
            
        except Exception as e:
            return APIResponse.server_error(str(e))
            
    @log_api_call
    @login_required
    def delete(self, request: HttpRequest, order_id: str) -> APIResponse:
        """
        取消订单
        
        Args:
            request: HTTP请求
            order_id: 订单ID
            
        Returns:
            APIResponse: API响应
        """
        try:
            # 获取订单
            try:
                order = OrderInfo.objects.get(order_id=order_id, user=request.user)
            except OrderInfo.DoesNotExist:
                return APIResponse.not_found(message="订单不存在")
                
            # 检查订单状态
            if order.status != OrderInfo.ORDER_STATUS_ENUM['UNPAID']:
                return APIResponse.error(message="只能取消未支付的订单")
                
            # 恢复商品库存
            for order_goods in order.skus.all():
                sku = order_goods.sku
                sku.stock += order_goods.count
                sku.sales -= order_goods.count
                sku.save()
                
            # 删除订单
            order.delete()
            
            return APIResponse.success(message="订单取消成功")
            
        except Exception as e:
            return APIResponse.server_error(str(e))

