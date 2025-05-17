import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lemall.settings')
#导入操作系统

# 为“celery”程序设置默认的 Django 设置模块。
#创建实例
app = Celery('celery_tasks')

# 在此处使用字符串意味着工作器不必将配置对象序列化为子进程。
# - namespace='CELERY' 表示所有与 celery 相关的配置键
# 应具有 `CELERY_` 前缀。
app.config_from_object('django.conf:settings',namespace='CELERY' )
# 从所有已注册的 Django 应用加载任务模块。
app.autodiscover_tasks(['celery_tasks.sms','celery_tasks.email'])

