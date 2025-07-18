'''
Django settings for heltour project.

Generated by 'django-admin startproject' using Django 1.9.7.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
'''

import os
from datetime import timedelta
from celery.schedules import crontab

ADMINS = []

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'gje)lme+inrew)s%@2mvhj+0$vip^n500i22-o23lm$t1)aq8e'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

ALLOWED_HOSTS = [
    'www.lichess4545.tv',
    'lichess4545.tv',
    'www.lichess4545.com',
    'lichess4545.com',
    'heltour.lakin.ca',
    'heltour.lakin.ca',
    'localhost',
]
CSRF_TRUSTED_ORIGINS = [
    'https://www.lichess4545.tv',
    'https://lichess4545.tv',
    'https://www.lichess4545.com',
    'https://lichess4545.com',
    'http://localhost',
]
LINK_PROTOCOL = 'https'

# Application definition

if 'HELTOUR_APP' in os.environ and os.environ['HELTOUR_APP'] == 'API_WORKER':
    HELTOUR_APP = 'api_worker'
else:
    HELTOUR_APP = 'tournament'

INSTALLED_APPS = [
    'cacheops',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'heltour.%s' % HELTOUR_APP,
    'reversion',
    'bootstrap3',
    'ckeditor',
    'ckeditor_uploader',
    'debug_toolbar',
    'django_comments',
    'heltour.comments',
    'impersonate',
    'static_precompiler',
]

COMMENTS_APP = 'heltour.comments'

API_WORKER_HOST = 'http://localhost:8880'

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'impersonate.middleware.ImpersonateMiddleware',
    'heltour.tournament.middlewares.RejectNullMiddleware',
]

ROOT_URLCONF = 'heltour.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'heltour.tournament.context_processors.common_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'heltour.wsgi.application'

SITE_ID = 1

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}

# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': 'localhost',
        'NAME': 'heltour_lichess4545',
        'USER': 'heltour_lichess4545',
        'PASSWORD': 'sown shuts combiner chattels',
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

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

AUTHENTICATION_BACKENDS = ['django.contrib.auth.backends.ModelBackend',
                           'heltour.tournament.auth.LeagueAuthBackend']

IMPERSONATE_REDIRECT_URL = '/'

# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Email
# https://docs.djangoproject.com/en/1.10/topics/email/

DEFAULT_FROM_EMAIL = 'noreply@lichess.org'

# Celery (tasks)

BROKER_URL = 'redis://localhost:6379/1'
CELERY_DEFAULT_QUEUE = 'heltour.live'

CELERYBEAT_SCHEDULE = {
    'update-ratings': {
        'task': 'heltour.tournament.tasks.update_player_ratings',
        'schedule': timedelta(minutes=60),
        'args': ()
    },
    'update-tv-state': {
        'task': 'heltour.tournament.tasks.update_tv_state',
        'schedule': timedelta(minutes=5),
        'args': ()
    },
    'update-slack-users': {
        'task': 'heltour.tournament.tasks.update_slack_users',
        'schedule': timedelta(minutes=30),
        'args': ()
    },
    'populate-historical-ratings': {
        'task': 'heltour.tournament.tasks.populate_historical_ratings',
        'schedule': timedelta(minutes=60),
        'args': ()
    },
    'run_scheduled_events': {
        'task': 'heltour.tournament.tasks.run_scheduled_events',
        'schedule': timedelta(minutes=10),
        'args': ()
    },
    'alternates_manager_tick': {
        'task': 'heltour.tournament.tasks.alternates_manager_tick',
        'schedule': timedelta(minutes=2),
        'args': ()
    },
    'update_lichess_presence': {
        'task': 'heltour.tournament.tasks.update_lichess_presence',
        'schedule': timedelta(minutes=1),
        'args': ()
    },
    'validate_pending_registrations': {
        'task': 'heltour.tournament.tasks.validate_pending_registrations',
        'schedule': timedelta(minutes=5),
        'args': ()
    },
    'celery_is_up': {
        'task': 'heltour.tournament.tasks.celery_is_up',
        'schedule': timedelta(minutes=5),
        'args': ()
    },
    'start_games': {
        'task': 'heltour.tournament.tasks.start_games',
        'schedule': crontab(minute='*/5'), # run every 5 minutes
        'args': ()
    },
}

CELERY_TIMEZONE = 'UTC'

# Django-Redis

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_PRECOMPILER_OUTPUT_DIR = '../heltour/tournament/static/'
STATIC_PRECOMPILER_COMPILERS = (
    ('static_precompiler.compilers.SCSS', {
        'sourcemap_enabled': True,
        'output_style': 'compact'
    }),
)
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'
    },
}

BOOTSTRAP3 = {
    'set_placeholder': False
}

CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
        'width': 930,
        'height': 300,
    },
}
CKEDITOR_UPLOAD_PATH = 'uploads/'
MEDIA_ROOT = 'media'
MEDIA_URL = '/media/'
CKEDITOR_ALLOW_NONIMAGE_FILES = True

LOGIN_URL = '/admin/login/'
SESSION_COOKIE_AGE = 4838400  # 8 weeks

DEBUG_TOOLBAR_PATCH_SETTINGS = False
INTERNAL_IPS = ['127.0.0.1', '::1']

CACHEOPS_REDIS = {
    'host': 'localhost',
    'port': 6379,
    'db': 1,
}
CACHEOPS_DEGRADE_ON_FAILURE = True
CACHEOPS_DEFAULTS = {
    'timeout': 60*60
}
CACHEOPS = {
    'admin.*': {'ops': 'all'},
    'auth.*': {'ops': 'all'},
    'heltour.*': {'ops': 'all'},
    'tournament.*': {'ops': 'all'},
    '*.*': {},
}

CACHEOPS_ENABLED = True

SLEEP_UNIT = 1 # time to sleep, mostly used to avoid slack rate limiting; hopefully removable in the future

TEAMGEN_PROCESSES_NUMBER = 8

GOOGLE_SERVICE_ACCOUNT_KEYFILE_PATH = '/home/lichess4545/etc/heltour/gspread.conf'
SLACK_API_TOKEN_FILE_PATH = '/home/lichess4545/etc/heltour/slack-token.conf'
SLACK_CHANNEL_BUILDER_TOKEN_FILE_PATH = '/home/lichess4545/etc/heltour/slack-channel-builder-token.conf'
SLACK_WEBHOOK_FILE_PATH = '/home/lichess4545/etc/heltour/slack-webhook.conf'
LICHESS_API_TOKEN_FILE_PATH = '/home/lichess4545/etc/heltour/lichess-api-token.conf'
JAVAFO_COMMAND = 'java -jar /home/lichess4545/etc/heltour/javafo.jar'
FCM_API_KEY_FILE_PATH = '/home/lichess4545/etc/heltour/fcm-key.conf'

SLACK_APP_TOKEN = ''
SLACK_ANNOUNCE_CHANNEL = 'C2UP34BCZ'
SLACK_TEAM_ID = 'T0CSGMP0R'
CHESSTER_USER_ID = 'U020MSB1FV0'

LICHESS_NAME = 'lichess'
LICHESS_TOPLEVEL = 'org'
LICHESS_DOMAIN = f'https://{LICHESS_NAME}.{LICHESS_TOPLEVEL}/'
LICHESS_OAUTH_ACCOUNT_URL = f'{LICHESS_DOMAIN}api/account'
LICHESS_OAUTH_EMAIL_URL = f'{LICHESS_DOMAIN}api/email'
LICHESS_OAUTH_AUTHORIZE_URL = f'{LICHESS_DOMAIN}oauth'
LICHESS_OAUTH_TOKEN_URL = f'{LICHESS_DOMAIN}api/token'
LICHESS_OAUTH_REDIRECT_SCHEME = 'https://'
LICHESS_OAUTH_CLIENTID = 'heltour'

DATA_UPLOAD_MAX_MEMORY_SIZE = 26214400 # 25MB - we'll let nginx otherwise restrict it.
