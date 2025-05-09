"""
API响应工具类
"""
from django.http import JsonResponse
from typing import Any, Dict, Optional, Union

class APIResponse:
    """API响应封装类"""
    
    @staticmethod
    def success(data: Any = None, message: str = "success", code: int = 200) -> JsonResponse:
        """
        成功响应
        
        Args:
            data: 响应数据
            message: 响应消息
            code: 响应状态码
            
        Returns:
            JsonResponse: JSON响应对象
        """
        return JsonResponse({
            'code': code,
            'message': message,
            'data': data
        })
    
    @staticmethod
    def error(message: str = "error", code: int = 400, data: Any = None) -> JsonResponse:
        """
        错误响应
        
        Args:
            message: 错误消息
            code: 错误状态码
            data: 错误详情
            
        Returns:
            JsonResponse: JSON响应对象
        """
        return JsonResponse({
            'code': code,
            'message': message,
            'data': data
        })
    
    @staticmethod
    def unauthorized(message: str = "unauthorized") -> JsonResponse:
        """
        未授权响应
        
        Args:
            message: 错误消息
            
        Returns:
            JsonResponse: JSON响应对象
        """
        return APIResponse.error(message=message, code=401)
    
    @staticmethod
    def forbidden(message: str = "forbidden") -> JsonResponse:
        """
        禁止访问响应
        
        Args:
            message: 错误消息
            
        Returns:
            JsonResponse: JSON响应对象
        """
        return APIResponse.error(message=message, code=403)
    
    @staticmethod
    def not_found(message: str = "not found") -> JsonResponse:
        """
        资源不存在响应
        
        Args:
            message: 错误消息
            
        Returns:
            JsonResponse: JSON响应对象
        """
        return APIResponse.error(message=message, code=404)
    
    @staticmethod
    def server_error(message: str = "server error") -> JsonResponse:
        """
        服务器错误响应
        
        Args:
            message: 错误消息
            
        Returns:
            JsonResponse: JSON响应对象
        """
        return APIResponse.error(message=message, code=500) 