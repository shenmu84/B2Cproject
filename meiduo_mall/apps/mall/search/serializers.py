"""
搜索序列化器
"""
from typing import Dict, Any, List
from rest_framework import serializers
from apps.goods.models import SKU, GoodsCategory
from elasticsearch_dsl import Document, Text, Keyword, Integer, Float, Date, Nested
from elasticsearch_dsl.connections import connections

# 创建Elasticsearch连接
connections.create_connection(hosts=['localhost'])

class SKUDocument(Document):
    """SKU文档"""
    
    id = Integer()
    name = Text(analyzer='ik_max_word')
    caption = Text(analyzer='ik_max_word')
    price = Float()
    stock = Integer()
    sales = Integer()
    comments = Integer()
    default_image_url = Keyword()
    category_id = Integer()
    category_name = Text(analyzer='ik_max_word')
    brand_id = Integer()
    brand_name = Text(analyzer='ik_max_word')
    create_time = Date()
    
    class Index:
        name = 'skus'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }
        
class SearchSerializer(serializers.Serializer):
    """搜索序列化器"""
    
    keyword = serializers.CharField(required=False, allow_blank=True)
    category_id = serializers.IntegerField(required=False)
    brand_id = serializers.IntegerField(required=False)
    min_price = serializers.FloatField(required=False)
    max_price = serializers.FloatField(required=False)
    sort = serializers.CharField(required=False)
    page = serializers.IntegerField(default=1)
    page_size = serializers.IntegerField(default=20)
    
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """验证搜索参数"""
        # 验证价格范围
        min_price = attrs.get('min_price')
        max_price = attrs.get('max_price')
        
        if min_price and max_price and min_price > max_price:
            raise serializers.ValidationError('最低价格不能大于最高价格')
            
        # 验证排序方式
        sort = attrs.get('sort')
        if sort and sort not in ['price', '-price', 'sales', '-sales', 'create_time', '-create_time']:
            raise serializers.ValidationError('排序方式不正确')
            
        # 验证分页参数
        page = attrs.get('page', 1)
        page_size = attrs.get('page_size', 20)
        
        if page < 1:
            raise serializers.ValidationError('页码不能小于1')
            
        if page_size < 1 or page_size > 100:
            raise serializers.ValidationError('每页数量必须在1-100之间')
            
        return attrs
        
    def search(self) -> Dict[str, Any]:
        """执行搜索"""
        # 构建查询
        s = SKUDocument.search()
        
        # 关键词搜索
        keyword = self.validated_data.get('keyword')
        if keyword:
            s = s.query('multi_match', query=keyword, fields=['name', 'caption', 'category_name', 'brand_name'])
            
        # 分类过滤
        category_id = self.validated_data.get('category_id')
        if category_id:
            s = s.filter('term', category_id=category_id)
            
        # 品牌过滤
        brand_id = self.validated_data.get('brand_id')
        if brand_id:
            s = s.filter('term', brand_id=brand_id)
            
        # 价格范围过滤
        min_price = self.validated_data.get('min_price')
        max_price = self.validated_data.get('max_price')
        
        if min_price is not None or max_price is not None:
            price_range = {}
            if min_price is not None:
                price_range['gte'] = min_price
            if max_price is not None:
                price_range['lte'] = max_price
            s = s.filter('range', price=price_range)
            
        # 排序
        sort = self.validated_data.get('sort')
        if sort:
            s = s.sort(sort)
        else:
            s = s.sort('-create_time')
            
        # 分页
        page = self.validated_data.get('page', 1)
        page_size = self.validated_data.get('page_size', 20)
        start = (page - 1) * page_size
        
        s = s[start:start + page_size]
        
        # 执行搜索
        response = s.execute()
        
        # 构建结果
        results = []
        for hit in response:
            results.append({
                'id': hit.id,
                'name': hit.name,
                'caption': hit.caption,
                'price': hit.price,
                'stock': hit.stock,
                'sales': hit.sales,
                'comments': hit.comments,
                'default_image_url': hit.default_image_url,
                'category_id': hit.category_id,
                'category_name': hit.category_name,
                'brand_id': hit.brand_id,
                'brand_name': hit.brand_name,
                'create_time': hit.create_time
            })
            
        return {
            'count': response.hits.total.value,
            'results': results
        } 