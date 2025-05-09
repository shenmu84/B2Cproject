"""
搜索视图
"""
from typing import Dict, Any
from django.http import HttpRequest
from django.views import View
from django.core.cache import cache
from utils.response import APIResponse
from utils.decorators import log_api_call
from .serializers import SearchSerializer, SKUDocument
from apps.goods.models import SKU, GoodsCategory

class SearchView(View):
    """搜索视图"""
    
    @log_api_call
    def get(self, request: HttpRequest) -> APIResponse:
        """
        搜索商品
        
        Args:
            request: HTTP请求
            
        Returns:
            APIResponse: API响应
        """
        try:
            # 获取请求参数
            data = request.GET.dict()
            
            # 验证数据
            serializer = SearchSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            
            # 执行搜索
            result = serializer.search()
            
            return APIResponse.success(data=result)
            
        except Exception as e:
            return APIResponse.server_error(str(e))
            
class SearchSuggestView(View):
    """搜索建议视图"""
    
    @log_api_call
    def get(self, request: HttpRequest) -> APIResponse:
        """
        获取搜索建议
        
        Args:
            request: HTTP请求
            
        Returns:
            APIResponse: API响应
        """
        try:
            # 获取请求参数
            keyword = request.GET.get('keyword', '')
            
            if not keyword:
                return APIResponse.success(data=[])
                
            # 从缓存获取建议
            cache_key = f'search_suggest_{keyword}'
            suggestions = cache.get(cache_key)
            
            if suggestions is None:
                # 构建查询
                s = SKUDocument.search()
                s = s.suggest(
                    'name_suggest',
                    keyword,
                    completion={
                        'field': 'name_suggest',
                        'fuzzy': {
                            'fuzziness': 2
                        },
                        'size': 10
                    }
                )
                
                # 执行查询
                response = s.execute()
                
                # 获取建议
                suggestions = []
                if hasattr(response, 'suggest'):
                    for suggestion in response.suggest.name_suggest:
                        for option in suggestion.options:
                            suggestions.append(option.text)
                            
                # 缓存建议
                cache.set(cache_key, suggestions, 3600)
                
            return APIResponse.success(data=suggestions)
            
        except Exception as e:
            return APIResponse.server_error(str(e))
            
class SearchHotView(View):
    """热门搜索视图"""
    
    @log_api_call
    def get(self, request: HttpRequest) -> APIResponse:
        """
        获取热门搜索
        
        Args:
            request: HTTP请求
            
        Returns:
            APIResponse: API响应
        """
        try:
            # 从缓存获取热门搜索
            hot_searches = cache.get('hot_searches')
            
            if hot_searches is None:
                # 获取热门商品
                hot_skus = SKU.objects.filter(is_launched=True).order_by('-sales')[:10]
                
                # 构建热门搜索
                hot_searches = []
                for sku in hot_skus:
                    hot_searches.append({
                        'id': sku.id,
                        'name': sku.name,
                        'sales': sku.sales
                    })
                    
                # 缓存热门搜索
                cache.set('hot_searches', hot_searches, 3600)
                
            return APIResponse.success(data=hot_searches)
            
        except Exception as e:
            return APIResponse.server_error(str(e)) 