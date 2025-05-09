import base64
import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django_redis import get_redis_connection
import pickle
from apps.goods.models import SKU

'''购物车获取数据
检验数据是否存在
登录的获取id放到redis
未登录放cookie里


'''
from utils.carts import *
from utils.response import APIResponse
from utils.decorators import log_api_call, login_required
from .serializers import CartSerializer, CartSKUSerializer

class CartView(View):
    """购物车视图"""
    
    @log_api_call
    def post(self, request: HttpRequest) -> APIResponse:
        """
        添加商品到购物车
        
        Args:
            request: HTTP请求
            
        Returns:
            APIResponse: API响应
        """
        try:
            # 获取请求数据
            data = request.POST.dict()
            
            # 验证数据
            serializer = CartSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            
            # 获取验证后的数据
            sku_id = serializer.validated_data['sku_id']
            count = serializer.validated_data['count']
            selected = serializer.validated_data['selected']
            
            # 获取Redis连接
            redis_conn = get_redis_connection('carts')
            
            # 获取用户ID
            user_id = request.user.id if request.user.is_authenticated else None
            
            if user_id:
                # 已登录用户，使用Redis Hash存储
                cart_key = f'cart_{user_id}'
                selected_key = f'selected_{user_id}'
                
                # 获取原有数量
                old_count = redis_conn.hget(cart_key, sku_id)
                if old_count:
                    count = int(old_count) + count
                    
                # 更新购物车
                redis_conn.hset(cart_key, sku_id, count)
                if selected:
                    redis_conn.sadd(selected_key, sku_id)
                else:
                    redis_conn.srem(selected_key, sku_id)
            else:
                # 未登录用户，使用Cookie存储
                cart_str = request.COOKIES.get('cart', '{}')
                cart_dict = json.loads(cart_str)
                
                # 更新购物车
                cart_dict[str(sku_id)] = {
                    'count': count,
                    'selected': selected
                }
                
                # 设置Cookie
                response = APIResponse.success(message="添加成功")
                response.set_cookie('cart', json.dumps(cart_dict))
                return response
            
            return APIResponse.success(message="添加成功")
            
        except Exception as e:
            return APIResponse.server_error(str(e))
            
    @log_api_call
    def get(self, request: HttpRequest) -> APIResponse:
        """
        获取购物车列表
        
        Args:
            request: HTTP请求
            
        Returns:
            APIResponse: API响应
        """
        try:
            # 获取Redis连接
            redis_conn = get_redis_connection('carts')
            
            # 获取用户ID
            user_id = request.user.id if request.user.is_authenticated else None
            
            if user_id:
                # 已登录用户，从Redis获取
                cart_key = f'cart_{user_id}'
                selected_key = f'selected_{user_id}'
                
                # 获取购物车数据
                cart_dict = redis_conn.hgetall(cart_key)
                selected_set = redis_conn.smembers(selected_key)
                
                # 构建购物车列表
                cart_list = []
                for sku_id, count in cart_dict.items():
                    sku_id = int(sku_id)
                    count = int(count)
                    selected = sku_id in selected_set
                    
                    try:
                        sku = SKU.objects.get(id=sku_id, is_launched=True)
                        cart_list.append({
                            'sku': sku,
                            'count': count,
                            'selected': selected
                        })
                    except SKU.DoesNotExist:
                        # 商品不存在，从购物车中删除
                        redis_conn.hdel(cart_key, sku_id)
                        redis_conn.srem(selected_key, sku_id)
            else:
                # 未登录用户，从Cookie获取
                cart_str = request.COOKIES.get('cart', '{}')
                cart_dict = json.loads(cart_str)
                
                # 构建购物车列表
                cart_list = []
                for sku_id, data in cart_dict.items():
                    sku_id = int(sku_id)
                    count = data['count']
                    selected = data['selected']
                    
                    try:
                        sku = SKU.objects.get(id=sku_id, is_launched=True)
                        cart_list.append({
                            'sku': sku,
                            'count': count,
                            'selected': selected
                        })
                    except SKU.DoesNotExist:
                        # 商品不存在，从购物车中删除
                        cart_dict.pop(str(sku_id))
                
                # 更新Cookie
                response = APIResponse.success(data=CartSKUSerializer(cart_list, many=True).data)
                response.set_cookie('cart', json.dumps(cart_dict))
                return response
            
            return APIResponse.success(data=CartSKUSerializer(cart_list, many=True).data)
            
        except Exception as e:
            return APIResponse.server_error(str(e))
            
    @log_api_call
    def put(self, request: HttpRequest) -> APIResponse:
        """
        更新购物车
        
        Args:
            request: HTTP请求
            
        Returns:
            APIResponse: API响应
        """
        try:
            # 获取请求数据
            data = request.PUT.dict()
            
            # 验证数据
            serializer = CartSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            
            # 获取验证后的数据
            sku_id = serializer.validated_data['sku_id']
            count = serializer.validated_data['count']
            selected = serializer.validated_data['selected']
            
            # 获取Redis连接
            redis_conn = get_redis_connection('carts')
            
            # 获取用户ID
            user_id = request.user.id if request.user.is_authenticated else None
            
            if user_id:
                # 已登录用户，更新Redis
                cart_key = f'cart_{user_id}'
                selected_key = f'selected_{user_id}'
                
                # 更新购物车
                redis_conn.hset(cart_key, sku_id, count)
                if selected:
                    redis_conn.sadd(selected_key, sku_id)
                else:
                    redis_conn.srem(selected_key, sku_id)
            else:
                # 未登录用户，更新Cookie
                cart_str = request.COOKIES.get('cart', '{}')
                cart_dict = json.loads(cart_str)
                
                # 更新购物车
                cart_dict[str(sku_id)] = {
                    'count': count,
                    'selected': selected
                }
                
                # 设置Cookie
                response = APIResponse.success(message="更新成功")
                response.set_cookie('cart', json.dumps(cart_dict))
                return response
            
            return APIResponse.success(message="更新成功")
            
        except Exception as e:
            return APIResponse.server_error(str(e))
            
    @log_api_call
    def delete(self, request: HttpRequest) -> APIResponse:
        """
        删除购物车商品
        
        Args:
            request: HTTP请求
            
        Returns:
            APIResponse: API响应
        """
        try:
            # 获取请求数据
            data = request.DELETE.dict()
            sku_id = data.get('sku_id')
            
            if not sku_id:
                return APIResponse.error(message="商品ID不能为空")
            
            # 获取Redis连接
            redis_conn = get_redis_connection('carts')
            
            # 获取用户ID
            user_id = request.user.id if request.user.is_authenticated else None
            
            if user_id:
                # 已登录用户，从Redis删除
                cart_key = f'cart_{user_id}'
                selected_key = f'selected_{user_id}'
                
                # 删除商品
                redis_conn.hdel(cart_key, sku_id)
                redis_conn.srem(selected_key, sku_id)
            else:
                # 未登录用户，从Cookie删除
                cart_str = request.COOKIES.get('cart', '{}')
                cart_dict = json.loads(cart_str)
                
                # 删除商品
                cart_dict.pop(str(sku_id), None)
                
                # 设置Cookie
                response = APIResponse.success(message="删除成功")
                response.set_cookie('cart', json.dumps(cart_dict))
                return response
            
            return APIResponse.success(message="删除成功")
            
        except Exception as e:
            return APIResponse.server_error(str(e))

class CartSelectView(View):
    """购物车选择视图"""
    
    @log_api_call
    def put(self, request: HttpRequest) -> APIResponse:
        """
        全选/取消全选
        
        Args:
            request: HTTP请求
            
        Returns:
            APIResponse: API响应
        """
        try:
            # 获取请求数据
            data = request.PUT.dict()
            selected = data.get('selected', True)
            
            # 获取Redis连接
            redis_conn = get_redis_connection('carts')
            
            # 获取用户ID
            user_id = request.user.id if request.user.is_authenticated else None
            
            if user_id:
                # 已登录用户，更新Redis
                cart_key = f'cart_{user_id}'
                selected_key = f'selected_{user_id}'
                
                # 获取购物车所有商品
                sku_ids = redis_conn.hkeys(cart_key)
                
                # 更新选中状态
                if selected:
                    redis_conn.sadd(selected_key, *sku_ids)
                else:
                    redis_conn.delete(selected_key)
            else:
                # 未登录用户，更新Cookie
                cart_str = request.COOKIES.get('cart', '{}')
                cart_dict = json.loads(cart_str)
                
                # 更新选中状态
                for sku_id in cart_dict:
                    cart_dict[sku_id]['selected'] = selected
                
                # 设置Cookie
                response = APIResponse.success(message="更新成功")
                response.set_cookie('cart', json.dumps(cart_dict))
                return response
            
            return APIResponse.success(message="更新成功")
            
        except Exception as e:
            return APIResponse.server_error(str(e))