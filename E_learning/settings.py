from pathlib import Path
from decouple import config
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '192.168.43.208', 'mysite.com']

# Application definition
CUSTOM_APPS = [
    'accounts.apps.AccountsConfig',
    'blog.apps.BlogConfig',
    'courses.apps.CoursesConfig',
    'quiz.apps.QuizConfig',
]

BUILT_IN_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.admin',
]

THIRD_PARTY_APPS = [
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'django_redis',
    'rest_framework',
    'paypal.standard.ipn',
    'dbbackup',
    'django_crontab',
    'django_email_verification',
    'taggit',
    'ckeditor',
    'ckeditor_uploader',
    'bootstrap_modal_forms',
    'widget_tweaks',
]

INSTALLED_APPS = CUSTOM_APPS + BUILT_IN_APPS + THIRD_PARTY_APPS

SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

DBBACKUP_STORAGE = 'django.core.files.storage.FileSystemStorage'
DBBACKUP_STORAGE_OPTIONS = {'location': os.path.join(BASE_DIR, 'backup')}

CRONJOBS = [
    ('*/45 * * * *', 'courses.cron.create_scheduled_backups')
]

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES':[
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
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

ROOT_URLCONF = 'E_learning.urls'

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
                'courses.context_processors.get_total_cart_items',
                'courses.context_processors.get_trashed_courses',
            ],
        },
    },
]

WSGI_APPLICATION = 'E_learning.wsgi.application'


CKEDITOR_CONFIGS = {
    'default': {
        'skin': 'moono-lisa',
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Styles', 'Format', 'Bold', 'Italic', 'Underline', 'Strike', 'SpellChecker', 'Undo', 'Redo'],
            ['Link', 'Unlink', 'Anchor'],
            ['Image', 'Table', 'HorizontalRule'],
            ['TextColor', 'BGColor'],
            ['Smiley', 'SpecialChar'], ['Source'],
            ['JustifyLeft', 'HorizontalRule' ,'JustifyCenter','JustifyRight','JustifyBlock'],
            ['NumberedList','BulletedList'],
            ['Indent','Outdent'],
            ['Maximize'],
        ],
        'tabSpaces': 4,
        'extraPlugins': ','.join(
            [
                'codesnippet',
                'uploadimage',
                'uploadwidget',
                'autoembed',
                'clipboard',
                'uicolor',
                'stylesheetparser',
                'tabletools',
                'templates',
            ]
        ),
        'removePlugins': 'exportpdf',
        'codeSnippet_theme': 'monokai_sublime',
        'height': 350,
        'width': 700
    },

    'my_ckeditor': {
        'toolbar': 'Basic',
    }
}

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# REDIS-SERVER FOR CACHING BACKEND-RESPONSE
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

AUTH_USER_MODEL = 'accounts.User'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

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

TIME_ZONE = 'Asia/Karachi'

USE_I18N = True

USE_L10N = True

USE_TZ = True

PAYPAL_TEST = True


STATIC_URL = '/static/'
MEDIA_URL = '/files/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static_builtin')
MEDIA_ROOT = os.path.join(BASE_DIR, 'static/files/')


STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static')
]

CKEDITOR_BASEPATH = '/static/ckeditor/ckeditor/'
CKEDITOR_UPLOAD_PATH = 'uploads/'

OPEN_WEATHER_API_KEY = config('OPEN_WEATHER_API_KEY')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'