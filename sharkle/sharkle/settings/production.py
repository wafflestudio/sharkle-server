from sharkle.settings.base import *

DEBUG = False

ALLOWED_HOSTS = ["127.0.0.1", "sharkle-server.kro.kr"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "HOST": os.environ.get(("DB_HOST")),
        "PORT": 3306,
        "NAME": "sharkle",
        "USER": os.environ.get(("DB_USER")),
        "PASSWORD": os.environ.get("DB_PASSWORD"),
        "OPTIONS": {  # for emoji
            "charset": "utf8mb4",
            "use_unicode": True,
        },
    }
}
