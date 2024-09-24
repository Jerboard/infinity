from pathlib import Path

import os
import redis


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('DJANGO_KEY')
DEBUG = bool(int(os.getenv('DEBUG')))

ALLOWED_HOSTS = ['*']


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'bot_manager',
    'django_ckeditor_5',
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

ROOT_URLCONF = 'admin_infinity.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'admin_infinity.wsgi.application'

# Подключаемся к Redis
redis_client = redis.Redis(host=os.getenv('REDIS_HOST'), port=int(os.getenv('REDIS_PORT')), db=0)
CHANNEL = os.getenv('CHANNEL')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB'),
        'USER': os.getenv('POSTGRES_USER'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }}


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

LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATIC_URL = '/static/'
if not os.path.exists(os.path.join(BASE_DIR, 'static')):
    os.mkdir(os.path.join(BASE_DIR, 'static'))

STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
if not os.path.exists(STATIC_ROOT):
    os.mkdir(STATIC_ROOT)

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
if not os.path.exists(MEDIA_ROOT):
    os.mkdir(MEDIA_ROOT)


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


LOG_DIR = os.path.join(BASE_DIR, 'logs')
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'WARNING',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'django.log'),
            'when': 'midnight',
            'backupCount': 7,
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            # 'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}


DJANGO_CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': 'full',
        'height': 500,
        'width': 'auto',
        # 'remove_plugins': 'stylesheetparser,FontColor,FontBackgroundColor',
        'remove_plugins': 'stylesheetparser',
        'extra_plugins': ','.join([
            'basicstyles',  # Простые стили (жирный, курсив)
            # Добавьте сюда дополнительные плагины, если нужно
        ]),
    },
}


# customColorPalette = [
#     {
#         'color': 'hsl(4, 90%, 58%)',
#         'label': 'Red'
#     },
#     {
#         'color': 'hsl(340, 82%, 52%)',
#         'label': 'Pink'
#     },
#     {
#         'color': 'hsl(291, 64%, 42%)',
#         'label': 'Purple'
#     },
#     {
#         'color': 'hsl(262, 52%, 47%)',
#         'label': 'Deep Purple'
#     },
#     {
#         'color': 'hsl(231, 48%, 48%)',
#         'label': 'Indigo'
#     },
#     {
#         'color': 'hsl(207, 90%, 54%)',
#         'label': 'Blue'
#     },
#     ]
# CK_EDITOR_5_UPLOAD_FILE_VIEW_NAME = "custom_upload_file"
# CKEDITOR_5_CUSTOM_CSS = 'path_to.css'  # optional
# CKEDITOR_5_FILE_STORAGE = "path_to_storage.CustomStorage"  # optional
CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar':
            ['bold', 'italic', 'link', 'underline', 'strikethrough', 'code'],
        # 'removePlugins': ['FontColor', 'FontBackgroundColor'],  # Убираем плагины, отвечающие за цвет текста
        'htmlSupport': {
            'allow': [{'name': 'strong'},],
            'disallow': [
                        {'name': 'p'}
                    ]
        }
    },
    'list': {
        'properties': {
            # 'styles': 'true',
            'startIndex': 'true',
            'reversed': 'true',
        }
    }
}
