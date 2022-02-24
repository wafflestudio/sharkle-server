"""
WSGI config for sharkle project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from dotenv import load_dotenv

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sharkle.settings.production') #default dev setting
load_dotenv(os.path.join("/home/ec2-user/build/sharkle", '.env'))
application = get_wsgi_application()
