"""
内容序列化器
"""
from typing import Dict, Any, List
from rest_framework import serializers
from .models import Content, ContentCategory

class ContentSerializer(serializers.ModelSerializer):
    """广告内容序列化器"""
    
    class Meta:
        model = Content
        fields = ['id', 'category', 'title', 'url', 'image', 'text', 'sequence', 'status', 'create_time']
        read_only_fields = ['id', 'create_time']
        
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """验证广告内容"""
        # 验证标题
        title = attrs.get('title')
        if not title:
            raise serializers.ValidationError('标题不能为空')
            
        # 验证图片
        image = attrs.get('image')
        if not image:
            raise serializers.ValidationError('图片不能为空')
            
        # 验证排序
        sequence = attrs.get('sequence')
        if sequence is not None and sequence < 0:
            raise serializers.ValidationError('排序不能小于0')
            
        return attrs
        
class ContentCategorySerializer(serializers.ModelSerializer):
    """广告分类序列化器"""
    
    contents = ContentSerializer(many=True, read_only=True)
    
    class Meta:
        model = ContentCategory
        fields = ['id', 'name', 'key', 'contents']
        read_only_fields = ['id']
        
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """验证广告分类"""
        # 验证名称
        name = attrs.get('name')
        if not name:
            raise serializers.ValidationError('名称不能为空')
            
        # 验证键名
        key = attrs.get('key')
        if not key:
            raise serializers.ValidationError('键名不能为空')
            
        # 验证键名唯一性
        if ContentCategory.objects.filter(key=key).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError('键名已存在')
            
        return attrs
        
class IndexContentSerializer(serializers.Serializer):
    """首页内容序列化器"""
    
    def to_representation(self, instance: Dict[str, Any]) -> Dict[str, Any]:
        """序列化首页内容"""
        # 获取所有广告分类
        categories = ContentCategory.objects.all()
        
        # 构建首页内容
        contents = {}
        for category in categories:
            # 获取分类下的广告内容
            category_contents = Content.objects.filter(
                category=category,
                status=Content.STATUS_ENUM['ONLINE']
            ).order_by('sequence')
            
            # 序列化广告内容
            contents[category.key] = ContentSerializer(category_contents, many=True).data
            
        return contents 