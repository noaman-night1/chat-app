from pathlib import Path
import os
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# JDID: Kay9ra SECRET_KEY mn l'serveur, w ila ma kanch kaydir wa7ed par défaut
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-fallback-key-for-local')

# JDID: f l'internet kaykoun False, f PC dyalek kaykoun True
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

# JDID: Khelina ga3 les domaines y9dro ydkhelo (bach l'app tkhdem dghya)
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'channels',
    'chat',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # JDID: Bach l'fichiers ykhdmo f l'internet
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# JDID: Kay9ra Database mn l'serveur (Render), w ila knti f PC dyalek kaykhdem b l'9dima
DATABASES = {
    'default': dj_database_url.config(
        default='postgres://messaging_user:password123@localhost:5432/messaging_db',
        conn_max_age=600
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles') # JDID: Mohim l WhiteNoise

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# JDID: Redis bach l'WebSockets ykhdmo f l'internet (ila ma kanch Redis f l'PC, kaykhdem b InMemory)
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379')

if os.environ.get('RENDER'):
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {"hosts": [REDIS_URL]},
        },
    }
else:
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels.layers.InMemoryChannelLayer',
        },
    }

# JDID: Bach Django y9bel l'requêtes mn l'lien dyal Render
CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1:8000',
    'http://localhost:8000',
    'https://*.onrender.com',
]