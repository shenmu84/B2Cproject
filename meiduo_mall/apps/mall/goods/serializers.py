"""
商品序列化器
"""
from typing import Dict, Any
from rest_framework import serializers
from .models import GoodsCategory, GoodsChannel, SKU, SKUSpecification, SpecificationOption

class GoodsCategorySerializer(serializers.ModelSerializer):
    """商品分类序列化器"""
    
    class Meta:
        model = GoodsCategory
        fields = ['id', 'name', 'parent', 'level']
        read_only_fields = ['id']
        
    def to_representation(self, instance: GoodsCategory) -> Dict[str, Any]:
        """
        自定义序列化输出
        
        Args:
            instance: 商品分类实例
            
        Returns:
            Dict[str, Any]: 序列化后的数据
        """
        data = super().to_representation(instance)
        # 添加子分类
        if instance.level < 3:  # 只获取三级分类
            children = GoodsCategory.objects.filter(parent=instance)
            data['children'] = GoodsCategorySerializer(children, many=True).data
        return data

class GoodsChannelSerializer(serializers.ModelSerializer):
    """商品频道序列化器"""
    
    category = GoodsCategorySerializer()
    
    class Meta:
        model = GoodsChannel
        fields = ['id', 'category', 'url', 'sequence']
        read_only_fields = ['id']

class SKUSpecificationSerializer(serializers.ModelSerializer):
    """SKU规格序列化器"""
    
    option = serializers.StringRelatedField()
    spec = serializers.StringRelatedField()
    
    class Meta:
        model = SKUSpecification
        fields = ['spec', 'option']

class SKUSerializer(serializers.ModelSerializer):
    """SKU序列化器"""
    
    specs = SKUSpecificationSerializer(many=True)
    category = GoodsCategorySerializer()
    
    class Meta:
        model = SKU
        fields = [
            'id', 'name', 'caption', 'price', 'cost_price',
            'market_price', 'stock', 'sales', 'comments',
            'category', 'specs', 'default_image_url'
        ]
        read_only_fields = ['id', 'sales', 'comments']
        
    def to_representation(self, instance: SKU) -> Dict[str, Any]:
        """
        自定义序列化输出
        
        Args:
            instance: SKU实例
            
        Returns:
            Dict[str, Any]: 序列化后的数据
        """
        data = super().to_representation(instance)
        # 添加商品详情
        data['detail'] = instance.detail
        # 添加商品图片
        data['images'] = [image.url for image in instance.images.all()]
        return data

class SpecificationOptionSerializer(serializers.ModelSerializer):
    """规格选项序列化器"""
    
    class Meta:
        model = SpecificationOption
        fields = ['id', 'value']
        read_only_fields = ['id']

class GoodsSpecificationSerializer(serializers.ModelSerializer):
    """商品规格序列化器"""
    
    options = SpecificationOptionSerializer(many=True)
    
    class Meta:
        model = SpecificationOption
        fields = ['id', 'name', 'options']
        read_only_fields = ['id'] 