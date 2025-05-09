"""
基础配置文件，包含所有环境共享的配置
"""
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Application definition
INSTALLED_APPS = [
    'corsheaders',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'apps.mall.users',
    'apps.mall.verifications',
    'apps.mall.oauth',
    'apps.mall.areas',
    'apps.mall.goods',
    'apps.mall.contents',
    'haystack',
    'django_crontab',
    'apps.mall.carts',
    'apps.mall.orders',
    'apps.mall.payment',
    'apps.Management.common',
    'apps.Management.users',
    'apps.Management.menu',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'utils.middleware.FrontendRoutingMiddleware',
    'utils.middleware.APIExceptionMiddleware',
    'utils.middleware.APILoggingMiddleware',
]

ROOT_URLCONF = 'meiduo_mall.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'static'),
            os.path.join(BASE_DIR, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'meiduo_mall.wsgi.application'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# 媒体文件设置
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# 替换系统的USER模型
AUTH_USER_MODEL = 'users.User'

# 跨域配置
CORS_ALLOWED_ORIGINS = [
    'http://127.0.0.1:8090/',
    'http://127.0.0.1:8080',
    'http://www.meiduo.site:8080',
]
CORS_ALLOW_CREDENTIALS = True

# JWT配置
JWT_TOKEN_HEAD = 'Bearer'

# Redis配置
REDIS_CONFIG = {
    'default': {
        'host': os.getenv('REDIS_HOST', '127.0.0.1'),
        'port': int(os.getenv('REDIS_PORT', 6379)),
        'db': 0,
    },
    'session': {
        'host': os.getenv('REDIS_HOST', '127.0.0.1'),
        'port': int(os.getenv('REDIS_PORT', 6379)),
        'db': 1,
    },
    'code': {
        'host': os.getenv('REDIS_HOST', '127.0.0.1'),
        'port': int(os.getenv('REDIS_PORT', 6379)),
        'db': 2,
    },
    'history': {
        'host': os.getenv('REDIS_HOST', '127.0.0.1'),
        'port': int(os.getenv('REDIS_PORT', 6379)),
        'db': 3,
    },
    'carts': {
        'host': os.getenv('REDIS_HOST', '127.0.0.1'),
        'port': int(os.getenv('REDIS_PORT', 6379)),
        'db': 4,
    },
    'ums': {
        'host': os.getenv('REDIS_HOST', '127.0.0.1'),
        'port': int(os.getenv('REDIS_PORT', 6379)),
        'db': 5,
    }
}

# 使用配置生成CACHES
CACHES = {
    name: {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{config['host']}:{config['port']}/{config['db']}",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {
                "max_connections": 100,
            },
        }
    }
    for name, config in REDIS_CONFIG.items()
}

# Session配置
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "session"

# Celery配置
CELERY_BROKER_URL = f"redis://{REDIS_CONFIG['default']['host']}:{REDIS_CONFIG['default']['port']}/15"
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_TASK_TRACK_STARTED = True

# 日志配置
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "filters": {
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "filters": ["require_debug_true"],
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(BASE_DIR, "logs/meiduo.log"),
            "maxBytes": 300 * 1024 * 1024,
            "backupCount": 10,
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "propagate": True,
        },
    },
} 