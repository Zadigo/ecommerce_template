from django.utils.translation import gettext_lazy as _
import logging
import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', True)

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'mywebsite.fr',
                 '*.mywebsite.fr', '30f4e9938de6.ngrok.io', 'testserver']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.sitemaps',

    'social_django',
    'django_extensions',
    'django_celery_beat',
    'rest_framework',
    # 'debug_toolbar',

    'analytics',
    'lookbook',
    'accounts',
    'legal',
    'hero',
    'nodesplus',
    'shop',
    'discounts',
    'cart',
    'store',
    'dashboard',
    'subscribers',
    'customercare',
    'reviews',
    'imagekit',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # 'debug_toolbar.middleware.DebugToolbarMiddleware',
]

ROOT_URLCONF = 'mywebsite.urls'

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

                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',

                'cart.payment.stripe_context_processor',
                'mywebsite.context_processors.responsive'
            ],
            'libraries': {
                'aws_images': 'templatetags.aws_images',
                'table': 'templatetags.table',

                'share': 'templatetags.share',
                'navbar': 'templatetags.navbar',

                'carts': 'cart.templatetags.carts',
                'dropdowns': 'shop.templatetags.dropdowns',

                'dates': 'dashboard.templatetags.dates',
                'sidebar': 'dashboard.templatetags.sidebar',

                'sidemenu': 'accounts.templatetags.sidemenu',

                'nodes_plus': 'nodesplus.templatetags.nodes_plus',

                'shop_impressions': 'shop.templatetags.shop_impressions',
                'cart_impressions': 'cart.templatetags.cart_impressions',

                'shop': 'shop.templatetags.shop'
            },
        },
    },
]

WSGI_APPLICATION = 'mywebsite.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'princess_ecommerce'),
        'USER': os.environ.get('DB_USER', 'princess_ecommerce'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'princess_ecommerce'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': '5432',
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale')
]

LANGUAGES = [
    ('en', _('English')),
    ('fr', _('Français')),
]


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

USE_S3 = False

if USE_S3:
    STATICFILES_STORAGE = 'mywebsite.storage.StaticFilesStorage'

    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')

    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')

    AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    
    AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME')

    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com'

    AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}

    AWS_DEFAULT_ACL = 'public-read'

    AWS_LOCATION = 'mywebsite/static'

    STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_LOCATION}/'

    STATIC_ROOT = 'staticfiles'

    # MEDIA

    DEFAULT_FILE_STORAGE = 'mywebsite.storage.PublicMediaStorage'

    AWS_MEDIA_LOCATION = 'mywebsite/media'

    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_MEDIA_LOCATION}/'
    
    PUBLIC_MEDIA_LOCATION = 'mywebsite/media'
else:
    DEFAULT_FILE_STORAGE = 'mywebsite.storage.CustomeFileSystemStorage'

    STATIC_URL = '/static/'

    STATICFILES_DIRS = [
        os.path.join(BASE_DIR, 'static')
    ]

    STATIC_ROOT = os.path.join(BASE_DIR, 'allstatic')

    MEDIA_URL = '/media/'

    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

AWS_IMAGES_FOLDER = ''


# Authentication backends

AUTH_USER_MODEL = 'accounts.MyUser'

AUTHENTICATION_BACKENDS = [
    'social_core.backends.twitter.TwitterOAuth',
    # 'social_core.backends.open_id.OpenIdAuth',
    # 'social_core.backends.google.GoogleOpenId',
    'social_core.backends.google.GoogleOAuth2',
    'social_core.backends.facebook.FacebookOAuth2',
    'accounts.backends.EmailAuthenticationBackend'
]

LOGIN_URL = 'accounts:login'

LOGOUT_URL = 'accounts:logout'

LOGIN_REDIRECT_URL = 'accounts:profile'


# Social Django

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ.get('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY')

SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ.get('SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET')

SOCIAL_AUTH_TWITTER_KEY = os.environ.get('SOCIAL_AUTH_TWITTER_KEY')

SOCIAL_AUTH_TWITTER_SECRET = os.environ.get('SOCIAL_AUTH_TWITTER_SECRET')

# SOCIAL_AUTH_PIPELINE = [
#     'social_core.pipeline.social_auth.social_details',
#     'social_core.pipeline.social_auth.social_uid',
#     'social_core.pipeline.social_auth.social_user',
#     'social_core.pipeline.user.get_username',
#     'social_core.pipeline.social_auth.associate_by_email',
#     'social_core.pipeline.user.create_user',
#     'social_core.pipeline.social_auth.associate_user',
#     'social_core.pipeline.social_auth.load_extra_data',
#     'social_core.pipeline.user.user_details',
# ]

SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/'

SOCIAL_AUTH_LOGIN_ERROR_URL = '/accounts/login'

# SOCIAL_AUTH_USER_MODEL = 'accounts.MyUser'


# GMAIL

EMAIL_HOST = 'smtp.gmail.com'

EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')

EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')

EMAIL_USE_TLS = True

EMAIL_PORT = 587

EMAIL_USE_LOCALTIME = True


# SITE

SITE_ID = 1


# CELERY

# redis://redis:6379/0
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://127.0.0.1:6379')

CELERY_RESULT_BACKEND = os.environ.get('CELERY_BROKER', 'redis://127.0.0.1:6379')


# CELERY BEAT

CELERY_BEAT_SCHEDULE = {
    'send_email': {
        'task': 'shop.tasks.purchase_complete_email',
        'schedule': '',
    },
    'publish_product': {
        'task': 'shop.tasks.publish_product'
    }
}


# CACHE

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': os.environ.get('CACHE_FILE_LOCATION', os.path.join(BASE_DIR, 'cache'))
    },
    'inmemcache': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211'
    },
    'redis-cache': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient'
        },
        'KEY_PREFIX': 'mywebsite'
    }
}


INTERNAL_IPS = [
    '127.0.0.1'
]


# Use these global variables to dynamically
# import models within apps e.g. cart etc.

PRODUCT_MODEL = 'shop.Product'

PRODUCT_COLLECTION_MODEL = 'shop.Collection'

DISCOUNT_MODEL = 'discounts.Discount'

CART_MODEL = 'cart.Cart'


# Stripe

STRIPE_DEBUG = True

STRIPE_API_KEYS = {
    'test': {
        'publishable': '',
        'secret': ''
    },
    'live': {
        'publishable': '',
        'secret': ''
    }
}


# Payment

# PAYMENT_BACKEND = 'cart.payment.SessionPaymentBackend'


# Mailchimp

MAILCHIMP_API_KEY = None

MAILCHIMP_SERVER_KEY = None
