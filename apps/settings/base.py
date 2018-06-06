# coding=utf-8
#
# Created on 2016-11-25, by junn
#

####################################################################
#                        GLOBAL BASE SETTINGS
####################################################################

import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

DEBUG = False
TEMPLATE_DEBUG = DEBUG


# For this type session cache, Session data will be stored directly your cache,
# and session data may not be persistent
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = 'default'


ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
]


AUTH_USER_MODEL = 'users.User'
USER_PROFILE = 'staff'                  # user profile, it's a nmis.hospitals.Staff object

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',  # 默认backend
    'base.backends.CustomizedModelBackend',        # 各backend依次进行验证, 直到某一个验证通过
)

# use this later
# AUTH_PASSWORD_VALIDATORS = [
#     {
#         'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
#     },
# ]


TIME_ZONE = 'Asia/Shanghai'
LANGUAGE_CODE = 'zh-Hans'

SITE_ID = 1

USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
# USE_L10N = True  # comment this that make the DATETIME_FORMAT valid

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = False

# Absolute filesystem path to the directory that will hold user-uploaded files.
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media')
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')

MEDIA_URL = '/media/'
STATIC_URL = '/static/'


# ## 以下设置为相对路径

# 用户头像设置
USER_DEFAULT_AVATAR = 'user_avatar_default1.jpg'

# 用户头像存放目录
USER_AVATAR_DIR = {
    'original': 'img/avatar/originals',
    'thumb':    'img/avatar/thumbs'
}

# 其他图片存放目录
IMG_DIR = {
    'original': 'img/originals',    # 原图目录
    'thumb':    'img/thumbs',       # 缩略图目录
}

DEFAULT_THUMB_SIZE = (400, 400)     # 默认缩略图尺寸配置


STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',

)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '$^0#lv$kycl5!d-hq0yp*wsx90oytx'


MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',       # put this on the top

    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.locale.LocaleMiddleware',

    # 'base.middleware.GetTokenMiddleware',
]

ROOT_URLCONF = 'urls'

###########################################################
# #跨域请求白名单, 仅白名单中的域名可跨域请求后端服务
###########################################################

CORS_ORIGIN_WHITELIST = [
    '*.nmis.com',
    'localhost:8000',
    '127.0.0.1:8000',
]

TEMPLATES = [
{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [
        os.path.join(PROJECT_ROOT, 'templates'),
    ],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.contrib.auth.context_processors.auth',
            'django.template.context_processors.request',  # Make sure you have this line
            'django.template.context_processors.i18n',
            'django.template.context_processors.media',
            'django.template.context_processors.static',
            'django.template.context_processors.debug',
            'django.template.context_processors.csrf',
            'django.contrib.messages.context_processors.messages',
        ],
    },
},
]

# Additional locations of static files
STATICFILES_DIRS = (
    ("nmis",     os.path.join(STATIC_ROOT, 'nmis')),  # Added for local debug-env
    ("admin",    os.path.join(STATIC_ROOT, 'admin')),
)


INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'suit',
    'django.contrib.admin',

    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'captcha',
    'djcelery',

    'utils',
    'base',
    'users',
    'organs',
    'nmis.hospitals',
    'nmis.devices',
    'nmis.projects',

    'runtests',
]


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'base.backends.CustomizedModelBackend',
    ),

    # API接口默认访问权限配置, 默认需要登录
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),

    # 默认分页设置
    'DEFAULT_PAGINATION_CLASS': 'base.serializers.PlugPageNumberPagination',
    'MAX_PAGE_SIZE': 50,
    'PAGE_SIZE':     15  # default page size
}

FIXTURE_DIRS = [
    os.path.join(PROJECT_ROOT, "resources/fixtures"),

]

CSRF_FAILURE_VIEW = 'base.views.csrf_failure'


###########################################################
# ## SITE ADMIN SET
###########################################################

# django-suit settings
SUIT_CONFIG = {
    'ADMIN_NAME':           '管理后台',
    'HEADER_DATE_FORMAT':   'Y年m月d日 H:i',
    'HEADER_TIME_FORMAT':   '.',
}

# 设置admin的默认时间显示格式
DATE_FORMAT = 'Y-m-d'
DATETIME_FORMAT = 'Y-m-d H:i:s'

# 验证码
CAPTCHA_FOREGROUND_COLOR = '#1137D0'
CAPTCHA_TIMEOUT = 5
CAPTCHA_LENGTH = 4


# 邮件激活本地URL地址
LOCAL_DOMAIN_URL = 'http://127.0.0.1:8000/'

try:
    from .subs import *
except ImportError as e:
    print('Import Error in base settings')
    print(e)


