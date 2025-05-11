import os
from pathlib import Path

def loadEnvironmentVariables():
    env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    if os.path.isfile(env_file):
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#') or '=' not in line:
                    continue
                key, value = line.split('=', 1)
                os.environ.setdefault(key, value)

loadEnvironmentVariables()

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def configureCoreSettings():
    return {
        'SECRET_KEY': os.getenv("DJANGO_SECRET_KEY", "replace-in-production-environment!"),
        
        'DEBUG': True,
        
        'ALLOWED_HOSTS': ['127.0.0.1', 'localhost', 'ogulcan-erdag.developerakademie.net'],
        
        'AUTH_USER_MODEL': 'auth_module.EmailBasedAuthenticationUser',
    }

def configureApplicationComponents():
    return {
        'INSTALLED_APPS': [
            'django.contrib.admin',
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.messages',
            'django.contrib.staticfiles',
            'rest_framework',
            'rest_framework.authtoken',
            'corsheaders',
            'core_api',
            'auth_module',
            'whitenoise.runserver_nostatic'    
        ],
        
        'MIDDLEWARE': [
            'django.middleware.security.SecurityMiddleware',
            'whitenoise.middleware.WhiteNoiseMiddleware',
            'corsheaders.middleware.CorsMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.common.CommonMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
            'django.middleware.clickjacking.XFrameOptionsMiddleware',
        ],
        
        'ROOT_URLCONF': 'server_config.urls',
        
        'TEMPLATES': [
            {
                'BACKEND': 'django.template.backends.django.DjangoTemplates',
                'DIRS': [PROJECT_ROOT / 'core_api' / 'templates'],
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
        ],
        
        'WSGI_APPLICATION': 'server_config.wsgi.application',
    }

def configureCrossSiteSettings():
    allowedOrigins = [
        'http://127.0.0.1:5500',
        'http://localhost:5500',
        'http://127.0.0.1:8000',
        'https://ogulcan-erdag.developerakademie.net',
        'file://',
    ]
    
    return {
        'CSRF_TRUSTED_ORIGINS': allowedOrigins,
        'CORS_ALLOWED_ORIGINS': allowedOrigins,
        'CORS_ALLOW_ALL_ORIGINS': True,
        'CORS_ALLOW_CREDENTIALS': True,
        'CORS_ALLOW_METHODS': [
            'DELETE',
            'GET',
            'OPTIONS',
            'PATCH',
            'POST',
            'PUT',
        ],
        'CORS_ALLOW_HEADERS': [
            'accept',
            'accept-encoding',
            'authorization',
            'content-type',
            'dnt',
            'origin',
            'user-agent',
            'x-csrftoken',
            'x-requested-with',
        ],
    }

def configureDatabaseSettings():
    return {
        'DATABASES': {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': PROJECT_ROOT / 'db.sqlite3',
            }
        },
        
        'DEFAULT_AUTO_FIELD': 'django.db.models.BigAutoField',
    }

def configureSecuritySettings():
    return {
        'AUTH_PASSWORD_VALIDATORS': [
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
        ],
    }

def configureInternationalization():
    return {
        'LANGUAGE_CODE': 'en-us',
        'TIME_ZONE': 'UTC',
        'USE_I18N': True,
        'USE_TZ': True,
    }

def configureStaticFiles():
    return {
        'STATIC_URL': '/static/',
        'STATIC_ROOT': PROJECT_ROOT / 'staticfiles',
        'STATICFILES_STORAGE': "whitenoise.storage.CompressedManifestStaticFilesStorage",
    }

def configureLogging():
    return {
        'LOGGING': {
            'version': 1,
            'disable_existing_loggers': False,
            'handlers': {
                'file': {
                    'level': 'ERROR',
                    'class': 'logging.FileHandler',
                    'filename': PROJECT_ROOT / 'errors.log',
                },
            },
            'loggers': {
                'django': {
                    'handlers': ['file'],
                    'level': 'ERROR',
                    'propagate': True,
                },
            },
        },
    }

def configureApiSettings():
    return {
        'REST_FRAMEWORK': {
            'DEFAULT_PERMISSION_CLASSES': [
                'rest_framework.permissions.IsAuthenticated',
            ],
            'DEFAULT_AUTHENTICATION_CLASSES': [
                'rest_framework.authentication.TokenAuthentication',
                'rest_framework.authentication.SessionAuthentication',
            ],    
        },
    }

def assembleConfiguration():
    configuration = {}
    
    configSections = [
        configureCoreSettings(),
        configureApplicationComponents(),
        configureCrossSiteSettings(),
        configureDatabaseSettings(),
        configureSecuritySettings(),
        configureInternationalization(),
        configureStaticFiles(),
        configureLogging(),
        configureApiSettings(),
    ]
    
    for section in configSections:
        configuration.update(section)
    
    return configuration

globals().update(assembleConfiguration())