"""
用户序列化器
"""
from typing import Dict, Any
from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Address

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """用户序列化器"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'mobile', 'date_joined', 'last_login']
        read_only_fields = ['id', 'date_joined', 'last_login']
        
    def to_representation(self, instance: User) -> Dict[str, Any]:
        """
        自定义序列化输出
        
        Args:
            instance: 用户实例
            
        Returns:
            Dict[str, Any]: 序列化后的数据
        """
        data = super().to_representation(instance)
        # 添加额外的字段
        data['is_active'] = instance.is_active
        return data

class AddressSerializer(serializers.ModelSerializer):
    """地址序列化器"""
    
    class Meta:
        model = Address
        fields = [
            'id', 'receiver', 'province', 'city', 'district',
            'place', 'mobile', 'tel', 'email', 'is_default'
        ]
        read_only_fields = ['id']
        
    def to_representation(self, instance: Address) -> Dict[str, Any]:
        """
        自定义序列化输出
        
        Args:
            instance: 地址实例
            
        Returns:
            Dict[str, Any]: 序列化后的数据
        """
        data = super().to_representation(instance)
        # 添加省市区名称
        data['province_name'] = instance.province.name
        data['city_name'] = instance.city.name
        data['district_name'] = instance.district.name
        return data 