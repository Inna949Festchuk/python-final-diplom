"""
Django settings for netology_pd_diplom project.

Generated by 'django-admin startproject' using Django 5.0.

Более подробную информацию об этом файле см. на странице
https://docs.djangoproject.com/en/5.1/topics/settings/

Полный список настроек и их значений см. на странице
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

import os
from dotenv import load_dotenv # pip install python-dotenv

load_dotenv('.env')

# Обновление сертификата SSL (для почтового клиента)
import certifi 

# На macOS: Запустите скрипт установки сертификатов Python:
# bash
# /Applications/Python\ 3.10/Install\ Certificates.command
# (Замените 3.10 на вашу версию Python, если отличается.)

# Установите пакет certifi:
# pip install certifi

# В settings.py добавьте:
# Путь к доверенным обновленным сертификатам
os.environ['SSL_CERT_FILE'] = certifi.where() # Указываем Python использовать сертификаты из certifi

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG')

ALLOWED_HOSTS = [
    os.getenv('ALLOWED_HOSTS'),
]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'django_rest_passwordreset',
    'backend.apps.BackendConfig',
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

ROOT_URLCONF = 'netology_pd_diplom.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
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

WSGI_APPLICATION = 'netology_pd_diplom.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE'),
        'NAME': os.path.join(f"{BASE_DIR}", f"{os.getenv('DB_NAME')}")
    }
}

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'ru'  # Язык по умолчанию

USE_I18N = True  # Включение интернационализации

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'

AUTH_USER_MODEL = 'backend.User'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_USE_TLS = True
# EMAIL_HOST = 'smtp.mail.ru'
# EMAIL_HOST_USER = 'netology.diplom@mail.ru'
# EMAIL_HOST_PASSWORD = 'CLdm7yW4U9nivz9mbexu'
# EMAIL_PORT = '465'
# EMAIL_USE_SSL = True
# SERVER_EMAIL = EMAIL_HOST_USER

# # Настройки для mail.ru, справка https://help.mail.ru/mail/security/protection/external/
EMAIL_HOST = 'smtp.mail.ru' # SMTP-сервер
EMAIL_HOST_USER = 'festchuk@mail.ru'
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD') # Пароль приложения
EMAIL_PORT = '465' # Для SSL (или 587 для TLS)
EMAIL_USE_SSL = True # Для порта 465 (если используете 587 (более безопасно) → EMAIL_USE_TLS = True)
SERVER_EMAIL = EMAIL_HOST_USER # Для отправки системных писем


# # Проверка доступа к SMTP
# # python manage.py shell

# from django.core.mail import send_mail
# from django.conf import settings

# # Проверка параметров
# print("EMAIL_HOST:", settings.EMAIL_HOST)
# print("EMAIL_PORT:", settings.EMAIL_PORT)
# print("EMAIL_HOST_USER:", settings.EMAIL_HOST_USER)

# # Тест отправки
# send_mail(
#     'Тест аутентификации',
#     'Проверка доступа к SMTP.',
#     settings.EMAIL_HOST_USER,
#     ['dilmah949dilma@gmail.com'], # Список рассылки тестового письма
#     fail_silently=False,
# )



REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 40,

    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',

    ),

    'DEFAULT_AUTHENTICATION_CLASSES': (

        'rest_framework.authentication.TokenAuthentication',
    ),
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Celery
# Если Redis работает в другом контейнере, проверьте, правильно ли настроены сети в docker-compose.yml. 
# Необходимо использовать имя контейнера Redis в качестве адреса для подключения, а не localhost. 
# Например, если Redis запущен в контейнере с именем broker, то адрес должен выглядеть так:
CELERY_BROKER_URL = 'redis://broker:6379' # Бекенд задач (Если запускаем через docker-compose 'redis://broker:6379' 
                                                        # если локально то 'redis://localhost:6379')
CELERY_RESULT_BACKEND = 'redis://broker:6379' # Бекенд результатов
CELERY_ACCEPT_CONTENT = ['application/json'] # Допустимый формат
CELERY_RESULT_SERIALIZER = 'json' # Сериализатор результатов
CELERY_TASK_SERIALIZER = 'json' # Сериализатор задач
# В логе указано предупреждение о том, что настройка broker_connection_retry устареет в Celery 6.0. 
# Чтобы отключить это, в конфиг добавляется:
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True 
