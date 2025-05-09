from django.shortcuts import render
from django.views import View
from django.core.cache import cache
from utils.response import APIResponse
from utils.decorators import log_api_call, login_required
from .serializers import ContentSerializer, ContentCategorySerializer, IndexContentSerializer
from .models import Content, ContentCategory


# Create your views here.
class IndexView(View):
    def get(self, request):
        # 广告
        contents = {}
        content_categories = ContentCategory.objects.all()
        for cat in content_categories:
            contents[cat.key]=cat.content_set.filter(status=True).order_by('sequence')
        context = {
            'categories': content_categories,
            'contents': contents,
        }
        return render(request,'index.html',context)

class ContentView(View):
    """广告内容视图"""
    
    @log_api_call
    @login_required
    def post(self, request):
        """
        创建广告内容
        
        Args:
            request: HTTP请求
            
        Returns:
            APIResponse: API响应
        """
        try:
            # 获取请求数据
            data = request.POST.dict()
            
            # 验证数据
            serializer = ContentSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            
            # 创建广告内容
            content = serializer.save()
            
            # 清除缓存
            cache.delete('index_contents')
            
            return APIResponse.success(
                data=serializer.data,
                message="广告内容创建成功"
            )
            
        except Exception as e:
            return APIResponse.server_error(str(e))
            
    @log_api_call
    @login_required
    def get(self, request):
        """
        获取广告内容列表
        
        Args:
            request: HTTP请求
            
        Returns:
            APIResponse: API响应
        """
        try:
            # 获取请求参数
            category_id = request.GET.get('category_id')
            
            # 构建查询
            contents = Content.objects.all()
            
            if category_id:
                contents = contents.filter(category_id=category_id)
                
            # 序列化数据
            serializer = ContentSerializer(contents, many=True)
            
            return APIResponse.success(data=serializer.data)
            
        except Exception as e:
            return APIResponse.server_error(str(e))
            
    @log_api_call
    @login_required
    def put(self, request, content_id):
        """
        更新广告内容
        
        Args:
            request: HTTP请求
            content_id: 广告内容ID
            
        Returns:
            APIResponse: API响应
        """
        try:
            # 获取广告内容
            try:
                content = Content.objects.get(id=content_id)
            except Content.DoesNotExist:
                return APIResponse.not_found(message="广告内容不存在")
                
            # 获取请求数据
            data = request.PUT.dict()
            
            # 验证数据
            serializer = ContentSerializer(content, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            
            # 更新广告内容
            content = serializer.save()
            
            # 清除缓存
            cache.delete('index_contents')
            
            return APIResponse.success(
                data=serializer.data,
                message="广告内容更新成功"
            )
            
        except Exception as e:
            return APIResponse.server_error(str(e))
            
    @log_api_call
    @login_required
    def delete(self, request, content_id):
        """
        删除广告内容
        
        Args:
            request: HTTP请求
            content_id: 广告内容ID
            
        Returns:
            APIResponse: API响应
        """
        try:
            # 获取广告内容
            try:
                content = Content.objects.get(id=content_id)
            except Content.DoesNotExist:
                return APIResponse.not_found(message="广告内容不存在")
                
            # 删除广告内容
            content.delete()
            
            # 清除缓存
            cache.delete('index_contents')
            
            return APIResponse.success(message="广告内容删除成功")
            
        except Exception as e:
            return APIResponse.server_error(str(e))
            
class ContentCategoryView(View):
    """广告分类视图"""
    
    @log_api_call
    @login_required
    def post(self, request):
        """
        创建广告分类
        
        Args:
            request: HTTP请求
            
        Returns:
            APIResponse: API响应
        """
        try:
            # 获取请求数据
            data = request.POST.dict()
            
            # 验证数据
            serializer = ContentCategorySerializer(data=data)
            serializer.is_valid(raise_exception=True)
            
            # 创建广告分类
            category = serializer.save()
            
            # 清除缓存
            cache.delete('index_contents')
            
            return APIResponse.success(
                data=serializer.data,
                message="广告分类创建成功"
            )
            
        except Exception as e:
            return APIResponse.server_error(str(e))
            
    @log_api_call
    def get(self, request):
        """
        获取广告分类列表
        
        Args:
            request: HTTP请求
            
        Returns:
            APIResponse: API响应
        """
        try:
            # 获取广告分类
            categories = ContentCategory.objects.all()
            
            # 序列化数据
            serializer = ContentCategorySerializer(categories, many=True)
            
            return APIResponse.success(data=serializer.data)
            
        except Exception as e:
            return APIResponse.server_error(str(e))
            
class IndexContentView(View):
    """首页内容视图"""
    
    @log_api_call
    def get(self, request):
        """
        获取首页内容
        
        Args:
            request: HTTP请求
            
        Returns:
            APIResponse: API响应
        """
        try:
            # 从缓存获取首页内容
            contents = cache.get('index_contents')
            
            if contents is None:
                # 序列化首页内容
                serializer = IndexContentSerializer()
                contents = serializer.to_representation({})
                
                # 缓存首页内容
                cache.set('index_contents', contents, 3600)
                
            return APIResponse.success(data=contents)
            
        except Exception as e:
            return APIResponse.server_error(str(e))