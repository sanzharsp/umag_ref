"""
Django settings for umag_backend project.

Generated by 'django-admin startproject' using Django 5.0.1.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path
from dotenv import load_dotenv
from django.templatetags.static import static
from django.urls import reverse_lazy
import os

load_dotenv()
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECKRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
INDOCKER = True
POSTGRES = True
PRODUCTION = True

ALLOWED_HOSTS = ['*']

if POSTGRES:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': str(os.getenv('POSTGRES_DB')),
            'USER': str(os.getenv('POSTGRES_USER')),
            'PASSWORD': str(os.getenv('POSTGRES_PASSWORD')),  # as a POSTGRES_PASSWORD
            'HOST': os.getenv('PG_HOST'),  # as the DB's service name in docker-compose.yml
            'PORT': '',  # default
            'SCHEMA': 'public',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Application definition

INSTALLED_APPS = [
    'main',
    'rest_framework',
    "unfold",  # before django.contrib.admin
    "unfold.contrib.filters",  # optional, if special filters are needed
    "unfold.contrib.forms",  # optional, if special form elements are needed
    "unfold.contrib.import_export",  # optional, if django-import-export package is used
    "unfold.contrib.guardian",  # optional, if django-guardian package is used
    "unfold.contrib.simple_history",  # optional, if django-simple-history package is used
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'import_export',
    'drf_yasg',
    'django_celery_beat',
]
REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly',
    ]
}
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'umag_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
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

WSGI_APPLICATION = 'umag_backend.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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

if INDOCKER:

    STATIC_URL = '/static/'
    STATIC_ROOT = '/var/www/static'
    MEDIA_URL = '/media/'
    MEDIA_ROOT = '/var/www/media'


else:
    STATIC_URL = '/static/'
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
    STATIC_ROOT = os.path.join(BASE_DIR, 'static')
# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'Asia/Qyzylorda'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/


# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
if PRODUCTION:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    CSRF_COOKIE_SECURE = True
    CSRF_TRUSTED_ORIGINS = [
        'http://34.88.104.128',
        'https://34.88.104.128',
        'https://jira-notifications.umag.kz',
        'http://jira-notifications.umag.kz',
        'http://localhost'
        'https://7de4-185-210-139-161.ngrok-free.app',
    ]
    CSRF_COOKIE_DOMAIN = '7de4-185-210-139-161.ngrok-free.app'

    # CORS_ALLOWED_ORIGINS = [
    #     'http://188.130.234.106',
    #     'https://188.130.234.106',
    #     'https://qazalem.ziz.kz',
    #     'http://qazalem.ziz.kz'
    #                         ]

    CORS_ALLOW_ALL_ORIGINS = True
    CORS_ALLOW_CREDENTIALS = True

CELERY_BROKER_URL = 'redis://redis:6379'

UNFOLD = {
    "SITE_TITLE": 'UMAG WEBHOOK SYSTEM',
    "SITE_HEADER": 'UMAG WEBHOOK SYSTEM',
    "SITE_URL": "/swagger",
    "SITE_ICON": lambda request: static("logo_.png"),
    "SITE_SYMBOL": "speed",  # symbol from icon set
    "LOGIN": {
        "image": lambda r: static("main.jpg"),
        "redirect_after": lambda r: reverse_lazy("admin:auth_user_changelist"),
    },

    "COLORS": {
        "primary": {
            "50": "250 245 255",
            "100": "243 232 255",
            "200": "233 213 255",
            "300": "216 180 254",
            "400": "192 132 252",
            "500": "168 85 247",
            "600": "147 51 234",
            "700": "126 34 206",
            "800": "107 33 168",
            "900": "88 28 135",
            "950": "59 7 100",
        },
    },
    "EXTENSIONS": {
        "modeltranslation": {
            "flags": {
                "en": "🇬🇧",
                "fr": "🇫🇷",
                "nl": "🇧🇪",
                "ru": "ru"
            },
        },
    },
    "SIDEBAR": {
        "show_search": True,  # Search in applications and models names
        "show_all_applications": True,  # Dropdown with all applications and models
        "navigation": [
            {
                "title": "Панель управление umag webhook",
                "separator": True,  # Top border
                "items": [
                    {
                        "title": "Панель",
                        "icon": "dashboard",  # Supported icon set: https://fonts.google.com/icons
                        "link": reverse_lazy("admin:index"),
                        "badge": "основное",
                        "permission": lambda request: request.user.is_superuser,
                    },

                    {
                        "title": "Webhook",
                        "icon": "Webhook",
                        "link": reverse_lazy("admin:main_webhookissuecreated_changelist"),
                    },
                    {
                        "title": "Администрация",
                        "icon": "Groups",
                        "link": reverse_lazy("admin:auth_user_changelist"),
                    },
                    {
                        "title": "Токен доступа и обновления AMO CRM",
                        "icon": "Token",
                        "link": reverse_lazy("admin:main_refreshaccesstoken_changelist"),
                    },
                    {
                        "title": "Настройки",
                        "icon": "Login",
                        "link": reverse_lazy("admin:main_settings_changelist"),
                    },

                    {
                        "title": "Данные из телеграм",
                        "icon": "Settings",
                        "link": reverse_lazy("admin:main_personaldata_changelist"),
                    },
                    {
                        "title": "Аналитика по запросам",
                        "icon": "Monitoring",
                        "link": reverse_lazy("analytics"),
                    },                    {
                        "title": "Аналитика оценки качества",
                        "icon": "Analytics",
                        "link": reverse_lazy("quality_control_analytics"),
                    },   {
                        "title": "Аналитика времени закрытия сделок",
                        "icon": "Query_Stats",
                        "link": reverse_lazy("analytics_lead"),
                    },
                    {
                        "title": "Открытые и закрытые сделок",
                        "icon": "Check_Circle",
                        "link": reverse_lazy("admin:main_responsetimecreate_changelist"),
                    },
                ],
            },
        ],
    },
    "TABS": [

        {
            "models": [
                "main.webhookissuecreated",
                "main.webhookissueupdated",
                "main.webhookissuedeleted",

            ],
            "items": [
                {
                    "title": "Созданные задачи",
                    "link": reverse_lazy("admin:main_webhookissuecreated_changelist"),

                },
                {
                    "title": "Обновленные задачи",
                    "link": reverse_lazy("admin:main_webhookissueupdated_changelist"),

                },
                {
                    "title": "Удаленные задачи",
                    "link": reverse_lazy("admin:main_webhookissuedeleted_changelist"),

                },

            ],
        },
        {
            "models": [
                "main.responsetimecreate",
                "main.responsetimedelete",

            ],
            "items": [
                {
                    "title": "Открытые сделки",
                    "link": reverse_lazy("admin:main_responsetimecreate_changelist"),

                },
                {
                    "title": "Закрытые сделки",
                    "link": reverse_lazy("admin:main_responsetimedelete_changelist"),

                },


            ],
        },

        {
            "models": [
                "main.personaldata",
                "main.supportconsultation",
                "main.supportbug",
                "main.supportsynchronization",
                "main.supportgetcourse",

            ],
            "items": [
                {
                    "title": "Персональные данные клиентов",
                    "link": reverse_lazy("admin:main_personaldata_changelist"),

                },
                {
                    "title": "Список консультации",
                    "link": reverse_lazy("admin:main_supportconsultation_changelist"),

                },
                {
                    "title": "Баги",
                    "link": reverse_lazy("admin:main_supportbug_changelist"),

                }, {
                    "title": "Синхранизаций",
                    "link": reverse_lazy("admin:main_supportsynchronization_changelist"),

                }, {
                    "title": "Get Course",
                    "link": reverse_lazy("admin:main_supportgetcourse_changelist"),

                },

            ],
        },
    ],
}