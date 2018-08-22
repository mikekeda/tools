"""
WSGI config for Tools site project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "toolssite.settings")

application = get_wsgi_application()
