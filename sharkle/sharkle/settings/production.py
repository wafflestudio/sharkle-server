from sharkle.settings.base import *

DEBUG = False

ALLOWED_HOSTS = ['127.0.0.1', ]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': 'RDS',
        'PORT': 3306,
        'NAME': 'sharkle',
        'USER': 'sharkle-server',
        'PASSWORD': 'DB_PASSWORD',
        'OPTIONS': { # for emoji
            'charset': 'utf8mb4',
            'use_unicode': True,
        },
    }
}
