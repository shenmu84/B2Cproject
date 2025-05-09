"""
订单序列化器
"""
from typing import Dict, Any
from rest_framework import serializers
from .models import OrderInfo, OrderGoods
from apps.goods.models import SKU
from apps.users.models import Address

class OrderSKUSerializer(serializers.ModelSerializer):
    """订单商品序列化器"""
    
    class Meta:
        model = SKU
        fields = ['id', 'name', 'price', 'default_image_url', 'stock']
        
class OrderGoodsSerializer(serializers.ModelSerializer):
    """订单商品详情序列化器"""
    
    sku = OrderSKUSerializer()
    
    class Meta:
        model = OrderGoods
        fields = ['id', 'sku', 'count', 'price']
        
class OrderSerializer(serializers.ModelSerializer):
    """订单序列化器"""
    
    skus = OrderGoodsSerializer(many=True, read_only=True)
    
    class Meta:
        model = OrderInfo
        fields = ['id', 'order_id', 'user', 'address', 'total_count', 'total_amount', 
                 'freight', 'pay_method', 'status', 'create_time', 'skus']
        read_only_fields = ['id', 'order_id', 'user', 'total_count', 'total_amount', 
                          'freight', 'status', 'create_time']
        
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """验证订单数据"""
        # 验证收货地址
        address = attrs.get('address')
        if not address:
            raise serializers.ValidationError('收货地址不能为空')
            
        # 验证支付方式
        pay_method = attrs.get('pay_method')
        if pay_method not in [OrderInfo.PAY_METHODS_ENUM['CASH'], OrderInfo.PAY_METHODS_ENUM['ALIPAY']]:
            raise serializers.ValidationError('支付方式不正确')
            
        return attrs
        
    def create(self, validated_data: Dict[str, Any]) -> OrderInfo:
        """创建订单"""
        # 获取当前用户
        user = self.context['request'].user
        
        # 获取购物车数据
        redis_conn = get_redis_connection('carts')
        cart_key = f'cart_{user.id}'
        selected_key = f'selected_{user.id}'
        
        # 获取选中的商品
        sku_ids = redis_conn.smembers(selected_key)
        if not sku_ids:
            raise serializers.ValidationError('请选择要购买的商品')
            
        # 获取商品数量
        cart_dict = redis_conn.hgetall(cart_key)
        
        # 创建订单
        order = OrderInfo.objects.create(
            user=user,
            address=validated_data['address'],
            total_count=0,
            total_amount=0,
            freight=10,
            pay_method=validated_data['pay_method'],
            status=OrderInfo.ORDER_STATUS_ENUM['UNPAID']
        )
        
        # 创建订单商品
        total_count = 0
        total_amount = 0
        
        for sku_id in sku_ids:
            sku_id = int(sku_id)
            count = int(cart_dict[sku_id])
            
            # 获取商品信息
            try:
                sku = SKU.objects.get(id=sku_id, is_launched=True)
            except SKU.DoesNotExist:
                raise serializers.ValidationError('商品不存在')
                
            # 检查库存
            if sku.stock < count:
                raise serializers.ValidationError(f'商品 {sku.name} 库存不足')
                
            # 创建订单商品
            OrderGoods.objects.create(
                order=order,
                sku=sku,
                count=count,
                price=sku.price
            )
            
            # 更新库存和销量
            sku.stock -= count
            sku.sales += count
            sku.save()
            
            # 更新订单总数量和总金额
            total_count += count
            total_amount += sku.price * count
            
        # 更新订单总数量和总金额
        order.total_count = total_count
        order.total_amount = total_amount
        order.save()
        
        # 清除购物车中已下单的商品
        redis_conn.hdel(cart_key, *sku_ids)
        redis_conn.srem(selected_key, *sku_ids)
        
        return order 