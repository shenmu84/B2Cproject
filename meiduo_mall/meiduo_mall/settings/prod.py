"""
生产环境配置文件
"""
import os
from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'NAME': os.getenv('DB_NAME'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        }
    },
    'slave': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': os.getenv('DB_SLAVE_HOST'),
        'PORT': os.getenv('DB_SLAVE_PORT'),
        'USER': os.getenv('DB_SLAVE_USER'),
        'PASSWORD': os.getenv('DB_SLAVE_PASSWORD'),
        'NAME': os.getenv('DB_SLAVE_NAME'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        }
    },
    'mall': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': os.getenv('DB_MALL_HOST'),
        'PORT': os.getenv('DB_MALL_PORT'),
        'USER': os.getenv('DB_MALL_USER'),
        'PASSWORD': os.getenv('DB_MALL_PASSWORD'),
        'NAME': os.getenv('DB_MALL_NAME'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        }
    },
}

# 数据库路由配置
DATABASE_ROUTERS = ['common.db_router.MasterSlaveDBRouter']

# 邮件配置
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 25))
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
EMAIL_FROM = os.getenv('EMAIL_FROM')

# 安全配置
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# 静态文件配置
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles') 