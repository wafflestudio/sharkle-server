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

# CUSTOM LOGGING
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    "formatters": {
        "django.server": {
            "()": "django.utils.log.ServerFormatter",
            "format": "[{server_time}] {message}",
            "style": "{",
        }
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "filters": ["require_debug_true"],
            "class": "logging.StreamHandler",
        },
        "django.server": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "django.server",
        },
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        },
        # added for saving log files
        "file": {
            "level": "DEBUG",
            "filters": [
                "require_debug_false"
            ],  # later change to debug_false (only for server)
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "django.server",
            "encoding": "UTF-8",
            "filename": os.path.join(BASE_DIR, "logging/sharkle-server.log"),
            "maxBytes": 1024 * 1024 * 5,  # TODO 5 MB
            "backupCount": 5,
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "mail_admins", "file"],
            # 'level': 'INFO',
        },
        "django.server": {
            "handlers": ["django.server"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
