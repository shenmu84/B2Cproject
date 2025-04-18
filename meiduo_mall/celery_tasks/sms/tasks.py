from libs.yuntongxun.sms import CCP
from celery import shared_task
@shared_task
def celery_send_sms_code(mobile,code):
    # 注意： 测试的短信模板编号为1

    CCP().send_template_sms(mobile, [code, 5], 1)