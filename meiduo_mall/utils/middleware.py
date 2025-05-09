"""
API中间件
"""
import json
import logging
from typing import Any, Callable
from django.http import HttpRequest, HttpResponse
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import Http404
from .response import APIResponse
from django.views.generic import TemplateView
from django.conf import settings

logger = logging.getLogger('django')

class APIExceptionMiddleware:
    """
    API异常处理中间件
    """
    
    def __init__(self, get_response: Callable) -> None:
        self.get_response = get_response
        
    def __call__(self, request: HttpRequest) -> HttpResponse:
        return self.get_response(request)
        
    def process_exception(self, request: HttpRequest, exception: Exception) -> HttpResponse:
        """
        处理异常
        
        Args:
            request: HTTP请求
            exception: 异常对象
            
        Returns:
            HttpResponse: HTTP响应
        """
        # 只处理API请求
        if not request.path.startswith('/api/'):
            return None
            
        # 记录异常日志
        logger.error(f"API异常: {str(exception)}", exc_info=True)
        
        # 处理不同类型的异常
        if isinstance(exception, Http404):
            return APIResponse.not_found()
        elif isinstance(exception, PermissionDenied):
            return APIResponse.forbidden()
        elif isinstance(exception, ValidationError):
            return APIResponse.error(message=str(exception))
        else:
            return APIResponse.server_error()

class APILoggingMiddleware:
    """
    API日志中间件
    """
    
    def __init__(self, get_response: Callable) -> None:
        self.get_response = get_response
        
    def __call__(self, request: HttpRequest) -> HttpResponse:
        # 只处理API请求
        if not request.path.startswith('/api/'):
            return self.get_response(request)
            
        # 记录请求信息
        self.log_request(request)
        
        # 获取响应
        response = self.get_response(request)
        
        # 记录响应信息
        self.log_response(request, response)
        
        return response
        
    def log_request(self, request: HttpRequest) -> None:
        """
        记录请求信息
        
        Args:
            request: HTTP请求
        """
        log_data = {
            'method': request.method,
            'path': request.path,
            'query_params': dict(request.GET.items()),
            'headers': dict(request.headers),
        }
        
        if request.method in ['POST', 'PUT', 'PATCH']:
            try:
                log_data['body'] = json.loads(request.body)
            except:
                log_data['body'] = request.body.decode()
                
        logger.info(f"API请求: {json.dumps(log_data, ensure_ascii=False)}")
        
    def log_response(self, request: HttpRequest, response: HttpResponse) -> None:
        """
        记录响应信息
        
        Args:
            request: HTTP请求
            response: HTTP响应
        """
        log_data = {
            'status_code': response.status_code,
            'headers': dict(response.headers),
        }
        
        if hasattr(response, 'content'):
            try:
                log_data['body'] = json.loads(response.content)
            except:
                log_data['body'] = response.content.decode()
                
        logger.info(f"API响应: {json.dumps(log_data, ensure_ascii=False)}")

class FrontendRoutingMiddleware:
    """前端路由中间件"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request: HttpRequest) -> HttpResponse:
        # 如果是API请求，直接返回
        if request.path.startswith('/api/'):
            return self.get_response(request)
            
        # 如果是静态文件请求，直接返回
        if request.path.startswith('/static/') or request.path.startswith('/media/'):
            return self.get_response(request)
            
        # 如果是HTML文件请求，直接返回
        if request.path.endswith('.html'):
            return self.get_response(request)
            
        # 其他请求返回index.html
        try:
            return TemplateView.as_view(template_name='index.html')(request)
        except Exception as e:
            logger.error(f"Frontend routing error: {str(e)}")
            return self.get_response(request) 