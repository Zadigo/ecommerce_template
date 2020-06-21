import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'lh^a_lltkll9r+)5o53ac1m*!tcbb#2s@69kw@=&*%%_9l@ymh'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',
    'rest_framework',
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

ROOT_URLCONF = 'ecommerce.urls'

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
            'libraries': {
                'aws_images': 'templatetags.aws_images',
                'general_tags': 'templatetags.general_tags',
                'table': 'templatetags.table'
            },
        },
    },
]

WSGI_APPLICATION = 'ecommerce.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'template_ecommerce'),
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

LOGIN_URL = 'login'

LOGOUT_URL = 'logout'

LOGIN_REDIRECT_URL = 'profile'

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ.get('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY')

SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ.get('SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET')


# GMAIL

EMAIL_HOST = 'smtp.gmail.com'

EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')

EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')

EMAIL_USE_TLS = True

EMAIL_PORT = 587

EMAIL_USE_LOCALTIME = True