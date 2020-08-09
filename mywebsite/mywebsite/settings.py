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
DEBUG = True

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

    'django_celery_beat',
    'accounts',
    'rest_framework',
    'django_extensions',
    'shop',
    'dashboard',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
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
                'shop.payment.stripe_context_processor',
                'mywebsite.responsive.responsive_context_processor'
            ],
            'libraries': {
                'aws_images': 'templatetags.aws_images',
                'general_tags': 'templatetags.general_tags',
                'table': 'templatetags.table',

                'share': 'templatetags.share',
                'navbar': 'templatetags.navbar',

                'carts': 'shop.templatetags.carts',
                'delivery': 'shop.templatetags.delivery',
                'prices': 'shop.templatetags.prices',
                'seo': 'shop.templatetags.seo',

                'dates': 'dashboard.templatetags.dates',
                'sidebar': 'dashboard.templatetags.sidebar',
            },
        },
    },
]

WSGI_APPLICATION = 'mywebsite.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
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

STATIC_URL = '/static/'

# STATIC_ROOT = 'static'

MEDIA_URL = 'media/'

MEDIA_ROOT = 'media'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static')
]


# AUTHENTICATION BACKENDS

AUTH_USER_MODEL = 'accounts.MyUser'

AUTHENTICATION_BACKENDS = (
#     'social_core.backends.twitter.TwitterOAuth',
#     'social_core.backends.open_id.OpenIdAuth',
#     'social_core.backends.google.GoogleOpenId',
#     'social_core.backends.google.GoogleOAuth2',
#     'social_core.backends.facebook.FacebookOAuth2',
    'accounts.backends.EmailAuthenticationBackend',
)


# SOCIAL DJANGO

LOGIN_URL = 'accounts:login'

LOGOUT_URL = 'accounts:logout'

LOGIN_REDIRECT_URL = 'accounts:profile'

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ.get('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY')

SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ.get('SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET')


# GMAIL

EMAIL_HOST = 'smtp.gmail.com'

EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')

EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')

EMAIL_USE_TLS = True

EMAIL_PORT = 587

EMAIL_USE_LOCALTIME = True


# AMAZON S3

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY')

AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_KEY')

AWS_STORAGE_BUCKET_NAME = ''

AWS_S3_REGION_NAME = ''

AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com'

AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400'
}

AWS_QUERYSTRING_AUTH = False

AWS_DEFAULT_ACL = None

if not DEBUG:
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

    AWS_LOCATION = ''

    STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_LOCATION}/'

    STATIC_ROOT = 'staticfiles'

    AWS_MEDIA_LOCATION = ''

    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_MEDIA_LOCATION}/'

    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

    PRODUCTS_FOLDER_LOCATION = ''

    PRODUCTS_FOLDER_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{PRODUCTS_FOLDER_LOCATION}'

AWS_IMAGES_FOLDER = ''


# SITE

SITE_ID = 1


# STRIPE

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

APPLE_PAY_DOMAIN = 'mywebsite.fr'


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
    }
}
