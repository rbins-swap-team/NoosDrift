"""
Django settings for noosDrift project.

Generated by 'django-admin startproject' using Django 2.1.1.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""
import datetime
import os
from requests.compat import urljoin
import socket

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

try:
    HOSTNAME = socket.gethostname()
except OSError as oserr:
    HOSTNAME = 'localhost'

# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

CENTRAL_ROLE = "Central"
NODE_ROLE = "Node"

NOOS_CENTRAL_ID = "NOOS_CENTRAL_ID"
NOOS_DEV = "DEV"
NOOS_ENV = "NOOS_ENV"
NOOS_MME_ID = "NOOS_MME_ID"
NOOS_MME_MODEL = "NOOS_MME_MODEL"
NOOS_NODE_ID = "NOOS_NODE_ID"
NOOS_PROD = "PROD"
NOOS_ROLE = "NOOS_ROLE"
NOOS_MME_CMD = ['python', './mme_code/noos-mme.py', '-i']
NOOS_MAPS_CMD = ['python', '/var/opt/noosdrift/Django/noosDrift/maps_code/copyMaps.py']
NOOS_NODE_PREPROCESSING_CMD = ['ssh', 'optos_v2_test@192.168.37.106', './cronrun', 'python3',
                               '/home/optos_v2_test/oserit/applications/noosdrift/procs/oserit_preproc.py']

# TODO replace with command to execute model software
NOOS_NODE_MODEL_CMD = ['ssh', 'optos_v2_test@192.168.37.106', './cronrun', 'python3',
                       '/home/optos_v2_test/oserit/applications/noosdrift/procs/oserit_proc.py']
NOOS_NODE_POSTPROCESSING_CMD = ['ssh', 'optos_v2_test@192.168.37.106', './cronrun', 'python3',
                                '/home/optos_v2_test/oserit/applications/noosdrift/procs/oserit_postproc.py']
NOOS_USERNAME = "NOOS_USERNAME"
NOOS_USERPWD = "NOOS_USERPWD"
NOOS_FTPDIR = os.path.join(BASE_DIR, 'requests')

ENV_VARS = (NOOS_NODE_ID, NOOS_USERNAME, NOOS_USERPWD, NOOS_ROLE, NOOS_CENTRAL_ID, NOOS_ENV)

ENV_DICT = {}

# USUAL variables, needed on Node and Central
for env_var_name in ENV_VARS:
    env_value = os.environ.get(env_var_name)
    if env_value is None:
        msg = "No {} defined and exported in bash environment".format(env_var_name)
        print(msg)
        assert env_value is not None, msg
    elif env_value in ["false", "False"]:
        env_value = bool(False)
    elif env_value in ["true", "True"]:
        env_value = bool(True)
    elif env_var_name in [NOOS_CENTRAL_ID, NOOS_NODE_ID]:
        env_value = int(env_value)

    ENV_DICT[env_var_name] = env_value

NOOS_USER = {"username": ENV_DICT[NOOS_USERNAME], "pwd": ENV_DICT[NOOS_USERPWD]}

mme_env_value = os.environ.get(NOOS_MME_ID)
if mme_env_value is not None:
    ENV_DICT[NOOS_MME_ID] = int(mme_env_value)
    if ENV_DICT[NOOS_MME_ID] == ENV_DICT[NOOS_NODE_ID]:
        ENV_DICT[NOOS_MME_MODEL] = 4

# Settings for a Node
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# Base URL des machines noos-drift chez les partenaires
BASE_URL = '/api/'

SCHEMA_URL = ""
schema_dict = {
    'nomDeMachine': 'https://versMachine'
}

SCHEMA_URL = urljoin(schema_dict[HOSTNAME], BASE_URL)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("NOOS_SECRET_KEY")
if SECRET_KEY is None:
    msg = "No NOOS_SECRET_KEY defined and exported in bash environment"
    print(msg)
    assert SECRET_KEY is not None, msg

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
if NOOS_DEV == ENV_DICT[NOOS_ENV]:
    DEBUG = True

ALLOWED_HOSTS = ['nomDeMachine', 'odnature.naturalsciences.be', 'localhost', '127.0.0.1']

CAPTCHA_CHALLENGE_FUNCT = 'captcha.helpers.math_challenge'

# Application definition

INSTALLED_APPS = [
    'captcha',
    'noos_services.apps.NoosServicesConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
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

ROOT_URLCONF = 'noosDrift.urls'

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
                'django.template.context_processors.media'
            ],
        },
    },
]

WSGI_APPLICATION = 'noosDrift.wsgi.application'

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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

TEMPLATE_DIRS = (os.path.join(BASE_DIR, 'templates'),)
TEMPLATE_URL = urljoin(BASE_URL, 'templates/')

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_DIR = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = [STATIC_DIR, ]
STATIC_URL = urljoin(BASE_URL, 'static/')

MEDIA_DIR = os.path.join(BASE_DIR, 'media')
MEDIA_ROOT = MEDIA_DIR
MEDIA_URL = urljoin(BASE_URL, 'media/')

# The dir where simulation data is sent by the Nodes
REQUESTS_DIR = os.path.join(BASE_DIR, 'requests')

# The dir where the analysis will be performed
NOOS_RESULTS_DIR = os.path.join(BASE_DIR, 'results')

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    # https://www.django-rest-framework.org/api-guide/throttling/
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ),
    'DEFAULT_THROTTLE_RATES': {
        'anon': '200/day',  # 50   for each node + central
        'user': '1000/day'  # 1000 request a day allowed by authenticated user
    }
}

# Configure the JWTs to expire after 1 hour, and allow users to refresh near-expiration tokens
JWT_AUTH = {
    'JWT_ENCODE_HANDLER': 'rest_framework_jwt.utils.jwt_encode_handler',
    'JWT_DECODE_HANDLER': 'rest_framework_jwt.utils.jwt_decode_handler',
    'JWT_PAYLOAD_HANDLER': 'rest_framework_jwt.utils.jwt_payload_handler',
    'JWT_PAYLOAD_GET_USER_ID_HANDLER': 'rest_framework_jwt.utils.jwt_get_user_id_from_payload_handler',
    'JWT_RESPONSE_PAYLOAD_HANDLER': 'rest_framework_jwt.utils.jwt_response_payload_handler',
    'JWT_SECRET_KEY': SECRET_KEY,
    'JWT_GET_USER_SECRET_KEY': None,
    'JWT_PUBLIC_KEY': None,
    'JWT_PRIVATE_KEY': None,
    'JWT_ALGORITHM': 'HS256',
    'JWT_VERIFY': True,
    'JWT_VERIFY_EXPIRATION': True,
    'JWT_LEEWAY': 0,
    'JWT_EXPIRATION_DELTA': datetime.timedelta(hours=1),
    'JWT_AUDIENCE': None,
    'JWT_ISSUER': None,
    'JWT_ALLOW_REFRESH': True,
    'JWT_REFRESH_EXPIRATION_DELTA': datetime.timedelta(hours=1),
    'JWT_AUTH_HEADER_PREFIX': 'JWT',
    'JWT_AUTH_COOKIE': None,
}

# Enables django-rest-auth to use JWT tokens instead of regular tokens.
REST_USE_JWT = True

LOGS_DIR = os.path.join(BASE_DIR, 'logs')

LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            # 'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
            'format': '%(levelname)s %(asctime)s %(module)s %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOGS_DIR, 'debug.log'),
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'noos_services.serializers': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'noos_services.views': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'noos_services.signals': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'noos_services.models': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'noos_services.helper': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'rest_framework.mixins': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'noos_services.tasks': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'noos_viewer.models': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'noos_viewer.views': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'noos_viewer.helper': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'noos_viewer.forms': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

ACTIVE_NODES = {}

APPUSERS_GROUP = 'appusers'

NOOS_ERROR_CODES = {
    0: ("Model simulation successfully completed (no error)", "FORCING-PROCESSED"),
    1: ("Initial position out of model domain", "FORCING-ERROR"),
    2: ("Initial position on land", "FORCING-ERROR"),
    3: ("Simulation start and/or end time are not in the forcing availability period  [today – 4 days, today + 4 days]", "FORCING-ERROR"),
    4: ("Release time of Lagrangian particle out of the simulation start time and end time windows", "FORCING-ERROR"),
    5: ("Drifter type unknown or not available in the model", "FORCING-ERROR"),
    6: ("Model cannot handle the requested set-up -> set-up has been adapted", "FORCING-ERROR"),
    7: ("Any other error in the model pre-processing", "FORCING-ERROR"),
    8: ("Any other error in the model processing", "FORCING-ERROR"),
    9: ("Any other error in the model post-processing : preparation of the model output", "FORCING-ERROR")
}

# Celery settings
BROKER_URL = os.environ.get("NOOS_BROKER_URL")
if BROKER_URL is None:
    msg = "No NOOS_BROKER_URL defined and exported in bash environment"
    print(msg)
    assert BROKER_URL is not None, msg
CELERY_RESULT_BACKEND = 'rpc://'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

# Security settings
# Only with certificate
if DEBUG is False and HOSTNAME in ['noos-drift-a-01', 'odin']:
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_HSTS_SECONDS = 3600
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# At all time
X_FRAME_OPTIONS = 'DENY'
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
