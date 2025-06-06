"""
WSGI config for sps_project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sps_project.settings.local')
if 'DJANGO_PRODUCTION' in os.environ:
    os.environ['DJANGO_SETTINGS_MODULE'] = 'sps_project.settings.production'

application = get_wsgi_application()
