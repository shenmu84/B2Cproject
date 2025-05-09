from django.http import JsonResponse
from django.views import View
from apps.orders.models import OrderInfo
from apps.mall.payment.models import Payment
from meiduo_mall import settings
from alipay import AliPay,AliPayConfig
from typing import Dict, Any
from django.http import HttpRequest
from django.db import transaction
from utils.response import APIResponse
from utils.decorators import log_api_call, login_required
from .serializers import PaymentSerializer

class PayUrlView(View):
    def get(self,request,order_id):
        user=request.user
        try:
            order=OrderInfo.objects.get(order_id=order_id,user=user,status=OrderInfo.ORDER_STATUS_ENUM["UNPAID"])
        except:
            return JsonResponse({'code':400,'errmsg':'此订单不存在'})
        app_private_key_string = open(settings.APP_PRIVATE_KEY_PATH).read()
        alipay_public_key_string = open(settings.ALIPAY_PUBLIC_KEY_PATH).read()
        # 4. 创建支付宝实例
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,  # 默认回调url
            app_private_key_string=app_private_key_string,
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_string=alipay_public_key_string,
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=settings.ALIPAY_DEBUG,  # 默认False
            config=AliPayConfig(timeout=15)  # 可选, 请求超时时间
        )
        subject = "美多商城测试订单"

        # 电脑网站支付，需要跳转到https://openapi.alipay.com/gateway.do? + order_string
        # https://openapi.alipay.com/gateway.do 这个是线上的
        # 'https://openapi.alipaydev.com/gateway.do' 这个是沙箱的
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,
            total_amount=str(order.total_amount),  # 一定要进行类型转换,因为decimal不是基本数据类型
            subject=subject,
            return_url=settings.ALIPAY_RETURN_URL,  # 支付成功之后,跳转的页面
            notify_url="https://example.com/notify"  # 可选, 不填则使用默认notify url
        )
        # 6.  拼接连接
        pay_url = 'https://openapi-sandbox.dl.alipaydev.com/gateway.do?' + order_string
        # 7. 返回响应
        return JsonResponse({'code': 0, 'errmsg': 'ok', 'alipay_url': pay_url})
    #用户在支付宝支付后查看订单状态
class PaymentStatusView(View):
    def put(self,request):
        data=request.GET
       # out_trade_no 唯一标识商户自己的订单
        #trade_no 唯一标识支付宝的交易记录
        # 2. 查询字符串转换为字典 验证数据
        data = data.dict()
        # 3. 验证没有问题获取支付宝交易流水号
        signature = data.pop("sign")
        app_private_key_string = open(settings.APP_PRIVATE_KEY_PATH).read()
        alipay_public_key_string = open(settings.ALIPAY_PUBLIC_KEY_PATH).read()
        # 创建支付宝实例
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,  # 默认回调url
            app_private_key_string=app_private_key_string,
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_string=alipay_public_key_string,
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=settings.ALIPAY_DEBUG,  # 默认False
            config=AliPayConfig(timeout=15)  # 可选, 请求超时时间
        )
        success = alipay.verify(data, signature)
        if success:
            # 获取 trade_no	String	必填	64	支付宝交易号
            trade_no = data.get('trade_no')
            order_id = data.get('out_trade_no')
            Payment.objects.create(
                trade_id=trade_no,
                order_id=order_id
            )
            # 4. 改变订单状态
            OrderInfo.objects.filter(order_id=order_id).update(status=OrderInfo.ORDER_STATUS_ENUM['UNSEND'])

            return JsonResponse({'code': 0, 'errmsg': 'ok', 'trade_id': trade_no})
        else:

            return JsonResponse({'code': 400, 'errmsg': '请到个人中心的订单中查询订单状态'})

class PaymentView(View):
    """支付视图"""
    
    @log_api_call
    @login_required
    def post(self, request: HttpRequest) -> APIResponse:
        """
        创建支付
        
        Args:
            request: HTTP请求
            
        Returns:
            APIResponse: API响应
        """
        try:
            # 获取请求数据
            data = request.POST.dict()
            order_id = data.get('order_id')
            
            if not order_id:
                return APIResponse.error(message="订单ID不能为空")
                
            # 获取订单
            try:
                order = OrderInfo.objects.get(order_id=order_id, user=request.user)
            except OrderInfo.DoesNotExist:
                return APIResponse.not_found(message="订单不存在")
                
            # 验证订单状态
            if order.status != OrderInfo.ORDER_STATUS_ENUM['UNPAID']:
                return APIResponse.error(message="订单状态不正确")
                
            # 创建支付记录
            payment_data = {
                'order': order,
                'payment_method': data.get('payment_method'),
                'amount': order.total_amount + order.freight
            }
            
            serializer = PaymentSerializer(data=payment_data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            
            with transaction.atomic():
                payment = serializer.save()
                
                # 调用支付接口
                if payment.payment_method == Payment.PAYMENT_METHODS_ENUM['ALIPAY']:
                    # 调用支付宝接口
                    trade_id = self._create_alipay_order(payment)
                else:
                    # 调用微信支付接口
                    trade_id = self._create_wechat_order(payment)
                    
                # 更新支付记录
                payment.trade_id = trade_id
                payment.save()
                
            return APIResponse.success(
                data=serializer.data,
                message="支付创建成功"
            )
            
        except Exception as e:
            return APIResponse.server_error(str(e))
            
    @log_api_call
    @login_required
    def get(self, request: HttpRequest) -> APIResponse:
        """
        获取支付状态
        
        Args:
            request: HTTP请求
            
        Returns:
            APIResponse: API响应
        """
        try:
            # 获取请求参数
            trade_id = request.GET.get('trade_id')
            
            if not trade_id:
                return APIResponse.error(message="交易ID不能为空")
                
            # 获取支付记录
            try:
                payment = Payment.objects.get(trade_id=trade_id, order__user=request.user)
            except Payment.DoesNotExist:
                return APIResponse.not_found(message="支付记录不存在")
                
            # 查询支付状态
            if payment.payment_method == Payment.PAYMENT_METHODS_ENUM['ALIPAY']:
                # 查询支付宝支付状态
                status = self._query_alipay_status(payment)
            else:
                # 查询微信支付状态
                status = self._query_wechat_status(payment)
                
            # 更新支付状态
            if status != payment.status:
                payment.status = status
                payment.save()
                
                # 更新订单状态
                if status == Payment.PAYMENT_STATUS_ENUM['SUCCESS']:
                    payment.order.status = OrderInfo.ORDER_STATUS_ENUM['UNSEND']
                    payment.order.save()
                    
            return APIResponse.success(data={'status': status})
            
        except Exception as e:
            return APIResponse.server_error(str(e))
            
    def _create_alipay_order(self, payment: Payment) -> str:
        """创建支付宝订单"""
        # TODO: 实现支付宝支付接口
        return f"ALIPAY_{payment.id}"
        
    def _create_wechat_order(self, payment: Payment) -> str:
        """创建微信支付订单"""
        # TODO: 实现微信支付接口
        return f"WECHAT_{payment.id}"
        
    def _query_alipay_status(self, payment: Payment) -> int:
        """查询支付宝支付状态"""
        # TODO: 实现支付宝支付状态查询
        return Payment.PAYMENT_STATUS_ENUM['PENDING']
        
    def _query_wechat_status(self, payment: Payment) -> int:
        """查询微信支付状态"""
        # TODO: 实现微信支付状态查询
        return Payment.PAYMENT_STATUS_ENUM['PENDING']