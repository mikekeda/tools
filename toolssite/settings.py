"""
Django settings for tools site project.
"""

import os
import requests
from django.utils.translation import ugettext_lazy as _

SITE_ENV_PREFIX = 'TOOLS'


def get_env_var(name, default=''):
    """Get all sensitive data from google vm custom metadata."""
    try:
        name = '_'.join([SITE_ENV_PREFIX, name])
        res = os.environ.get(name)
        if res:
            # Check env variable (Jenkins build).
            return res
        else:
            res = requests.get(
                'http://metadata.google.internal/computeMetadata/'
                'v1/instance/attributes/{}'.format(name),
                headers={'Metadata-Flavor': 'Google'}
            )
            if res.status_code == 200:
                return res.text
    except requests.exceptions.ConnectionError:
        return default
    return default


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_env_var(
    'SECRET_KEY',
    'q-=(1t*%^5*c98%&_cj9vr56(3_(3@f^bj&bw)atj(yn_g)r0@'
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(get_env_var('DEBUG', 'True'))

INTERNAL_IPS = (
    '127.0.0.1',
)

ALLOWED_HOSTS = get_env_var('ALLOWED_HOSTS', '*').split(',')

ADMINS = [
    ('Mike', 'mriynuk@gmail.com')
]

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',

    'social_django',
    'widget_tweaks',
    'schedule',
    'easy_select2',
    'django_jenkins',
    'import_export',

    'tool',
)

MIDDLEWARE = (
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'social_django.middleware.SocialAuthExceptionMiddleware',
)

ROOT_URLCONF = 'toolssite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
            os.path.join(BASE_DIR, 'templates/tools')
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                'tool.context_processors.categories',
                'tool.context_processors.select_parent_template',
                'tool.context_processors.arrival_date',
                'tool.context_processors.user_profile',

                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]

WSGI_APPLICATION = 'toolssite.wsgi.application'


# Database

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': get_env_var('DB_NAME', 'tools'),
        'USER': get_env_var('DB_USER', 'tools_admin'),
        'PASSWORD': get_env_var('DB_PASSWORD', 'tools_local_pass'),
        'HOST': get_env_var('DB_HOST', '127.0.0.1'),
        'PORT': '',
    }
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://localhost:6379/3",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

# CELERY STUFF
CELERY_BROKER_URL = 'redis://localhost:6379/3'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/3'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

AUTHENTICATION_BACKENDS = (
    'social_core.backends.github.GithubOAuth2',
    'social_core.backends.facebook.FacebookOAuth2',

    'django.contrib.auth.backends.ModelBackend',
)

SOCIAL_AUTH_LOGIN_REDIRECT_URL = 'main'
SOCIAL_AUTH_FACEBOOK_KEY = get_env_var('SOCIAL_AUTH_FACEBOOK_KEY')
SOCIAL_AUTH_FACEBOOK_SECRET = get_env_var('SOCIAL_AUTH_FACEBOOK_SECRET')
SOCIAL_AUTH_GITHUB_KEY = get_env_var('SOCIAL_AUTH_GITHUB_KEY')
SOCIAL_AUTH_GITHUB_SECRET = get_env_var('SOCIAL_AUTH_GITHUB_SECRET')
LOGOUT_URL = 'logout'
LOGIN_REDIRECT_URL = '/'

EMAIL_HOST = 'smtp.mailgun.org'
EMAIL_PORT = 2525
EMAIL_HOST_USER = get_env_var('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = get_env_var('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = True
MAILGUN_SERVER_NAME = 'info.mkeda.me'
EMAIL_SUBJECT_PREFIX = '[Tools]'
SERVER_EMAIL = 'admin@info.mkeda.me'

# Internationalization

LANGUAGE_CODE = 'en-us'

LANGUAGES = [
    ('en', _('English')),
    ('es', _('Spanish')),
    ('uk', _('Ukrainian')),
    ('it', _('Italian')),
    ('fr', _('French')),
    ('ru', _('Russian')),
]

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

MEDIA_URL = '/media/'

LOGIN_URL = '/login'

# Static files (CSS, JavaScript, Images)

STATIC_ROOT = '/home/voron/sites/cdn/tools'

STATIC_URL = '/static/' if DEBUG else 'https://cdn.mkeda.me/tools/'

STATICFILES_DIRS = (
    ('', os.path.join(BASE_DIR, 'static')),
)

QPXEXPRESS_API_KEY = get_env_var('QPXEXPRESS_API_KEY')
QPXEXPRESS_URL = 'https://www.googleapis.com/qpxExpress/v1/trips/search?key='

JENKINS_TASKS = ('django_jenkins.tasks.run_pylint',
                 'django_jenkins.tasks.run_pep8',
                 'django_jenkins.tasks.run_pyflakes',)

PROJECT_APPS = ['tool', 'toolssite']

PYLINT_LOAD_PLUGIN = ['pylint_django']
