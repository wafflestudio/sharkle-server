from sharkle.settings.base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

if DEBUG:
    INSTALLED_APPS.append("debug_toolbar")
    MIDDLEWARE.append("debug_toolbar.middleware.DebugToolbarMiddleware")
    INTERNAL_IPS = ["127.0.0.1"]

ALLOWED_HOSTS = []

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "HOST": "127.0.0.1",
        "PORT": 3306,
        "NAME": "sharkle",
        "USER": os.environ.get(("DB_USER")),
        "PASSWORD": os.environ.get(("DB_PASSWORD")),
        "OPTIONS": {  # for emoji
            "charset": "utf8mb4",
            "use_unicode": True,
        },
    }
}

# 한국 시간
# https://goodthings4me.tistory.com/536
TIME_ZONE = 'Asia/Seoul'  # 한국 시간 적용
USE_I18N = True
USE_L10N = True
USE_TZ = False