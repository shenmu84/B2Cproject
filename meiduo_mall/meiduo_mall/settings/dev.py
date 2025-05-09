"""
开发环境配置文件
"""
import os
from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'nu@rt+zf*-g)iuc#rqf!&o**r^l@l-1ml0gt^nrh6)+o&zc4@$')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', 'www.meiduo.site', '127.0.0.1', '192.168.106.82']

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': os.getenv('DB_HOST', '127.0.0.1'),
        'PORT': os.getenv('DB_PORT', '3306'),
        'USER': os.getenv('DB_USER', 'root'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'root'),
        'NAME': os.getenv('DB_NAME', 'meiduo_mail'),
    },
    'slave': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': os.getenv('DB_SLAVE_HOST', '127.0.0.1'),
        'PORT': os.getenv('DB_SLAVE_PORT', '8306'),
        'USER': os.getenv('DB_SLAVE_USER', 'root'),
        'PASSWORD': os.getenv('DB_SLAVE_PASSWORD', 'mysql'),
        'NAME': os.getenv('DB_SLAVE_NAME', 'meiduo_mail'),
    },
    'mall': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': os.getenv('DB_MALL_HOST', '127.0.0.1'),
        'PORT': os.getenv('DB_MALL_PORT', '3306'),
        'USER': os.getenv('DB_MALL_USER', 'root'),
        'PASSWORD': os.getenv('DB_MALL_PASSWORD', 'root'),
        'NAME': os.getenv('DB_MALL_NAME', 'mall'),
    },
}

# 数据库路由配置
DATABASE_ROUTERS = ['common.db_router.MasterSlaveDBRouter']

# 邮件配置
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.163.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 25))
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
EMAIL_FROM = os.getenv('EMAIL_FROM', '') 