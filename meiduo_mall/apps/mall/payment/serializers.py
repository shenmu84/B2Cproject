"""
支付序列化器
"""
from typing import Dict, Any
from rest_framework import serializers
from .models import Payment
from apps.orders.models import OrderInfo

class PaymentSerializer(serializers.ModelSerializer):
    """支付序列化器"""
    
    class Meta:
        model = Payment
        fields = ['id', 'order', 'trade_id', 'payment_method', 'amount', 'status', 'create_time']
        read_only_fields = ['id', 'trade_id', 'status', 'create_time']
        
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """验证支付数据"""
        # 验证订单
        order = attrs.get('order')
        if not order:
            raise serializers.ValidationError('订单不能为空')
            
        # 验证订单状态
        if order.status != OrderInfo.ORDER_STATUS_ENUM['UNPAID']:
            raise serializers.ValidationError('订单状态不正确')
            
        # 验证支付方式
        payment_method = attrs.get('payment_method')
        if payment_method not in [Payment.PAYMENT_METHODS_ENUM['ALIPAY'], Payment.PAYMENT_METHODS_ENUM['WECHAT']]:
            raise serializers.ValidationError('支付方式不正确')
            
        # 验证支付金额
        amount = attrs.get('amount')
        if amount != order.total_amount + order.freight:
            raise serializers.ValidationError('支付金额不正确')
            
        return attrs
        
    def create(self, validated_data: Dict[str, Any]) -> Payment:
        """创建支付记录"""
        # 获取当前用户
        user = self.context['request'].user
        
        # 验证订单所属用户
        order = validated_data['order']
        if order.user != user:
            raise serializers.ValidationError('无权操作此订单')
            
        # 创建支付记录
        payment = Payment.objects.create(
            order=order,
            payment_method=validated_data['payment_method'],
            amount=validated_data['amount'],
            status=Payment.PAYMENT_STATUS_ENUM['PENDING']
        )
        
        return payment 