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
