import os

AUTH_USER_MODEL = 'users.User'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECRET_KEY
with open(os.path.join(BASE_DIR, 'secret_key.txt')) as f:
    SECRET_KEY = f.read().strip()

DEBUG = False

ALLOWED_HOSTS = ['https://evafilm.stream', 'http://evafilm.stream', 'evafilm.stream', '185.239.104.26', 'evafilm.ir', ]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'widget_tweaks',
    'users',
    'accounts',
    'movies',
    'payments',
    'api',
    'admin_panel',
    'imdb_scraper',
    'send_message.apps.SendMessageConfig',
    'extensions',
    'giftcard.apps.GiftcardConfig',
    'rest_framework',
    'django.contrib.sitemaps',
    'django.contrib.sites',
    'sitemap.apps.SitemapConfig',
    'discount_app.apps.DiscountAppConfig',
    'cnsr.apps.EshopOrderConfig',
    'robots_txt.apps.RobotsTxtConfig',
    'invitor',
    'dbbackup',
    'slider',
    'videoposition',

]

DBBACKUP_STORAGE = 'django.core.files.storage.FileSystemStorage'
DBBACKUP_STORAGE_OPTIONS = {'location': '/home/ubuntu/evafilm/backups'}
DBBACKUP_CONNECTORS = {
    'superstream': {
        'NAME': 'superstream',
        'USER': 'evafilmuser',
        'PASSWORD': 'amir#$1372',
        'HOST': 'localhost'
    }
}

SITE_ID = 4

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

]

LOGIN_URL = '/login'

ROOT_URLCONF = 'evafilm.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates')
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

WSGI_APPLICATION = 'evafilm.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'evafilm',
        'USER': 'evafilm_user',
        'PASSWORD': 'evafilm@2021evafilm',
        'HOST': 'localhost',
        'PORT': '',
    }
}

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

RENDERER = ('rest_framework.renderers.JSONRenderer',)
if DEBUG:
    RENDERER += ('rest_framework.renderers.BrowsableAPIRenderer',)

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAuthenticated',),
    # 'rest_framework.permissions.IsAdminUser',
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',
                                'rest_framework.filters.SearchFilter',
                                'rest_framework.filters.OrderingFilter',
                                ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_RENDERER_CLASSES': RENDERER
}

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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Tehran'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
# STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

CONTENT_URL = 'https://ss.evafilm.stream/'
SITE_URL = 'https://evafilm.stream/'

LOGOUT_REDIRECT_URL = 'Home'
LOGIN_REDIRECT_URL = 'Home'

# Celery Config
BROKER_TRANSPORT = 'redis'
CELERY_BROKER_URL = 'redis://localhost:6379'
CELERY_RESULT_BACKEND = 'redis://localhost:6379'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

EMAIL_HOST = "smtp-kilitac792.alwaysdata.net"
EMAIL_HOST_USER = 'eva.master@evafilm.ir'
EMAIL_HOST_PASSWORD = "omu_+xj1"
EMAIL_PORT = 465
EMAIL_USE_SSL = True
DEFAULT_FROM_EMAIL = "eva.master@evafilm.ir"

# HTTPS setting
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True
# SECURE_SSL_REDIRECT = True

# HSTS setting
# SECURE_HSTS_SECONDS = 31536000  # 1 year
# SECURE_HSTS_PRELOAD = True
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
