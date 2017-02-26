#!/usr/bin/python
import os

# IMPORTANT: Put any additional includes below this line.  If placed above this
# line, it's possible required libraries won't be in your searchable path
#

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "toolssite.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
