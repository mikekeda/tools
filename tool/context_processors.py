from tool.models import SimplePage
from django.conf import settings
import os, sys


def categories(request):
    """Get all tools."""

    tools = []
    folders = settings.TEMPLATES[0]['DIRS']
    for folder in folders:
        if os.path.exists(folder + '/tools'):
            tools.extend([f for f in os.listdir(folder + '/tools') if (os.path.isfile(os.path.join(folder + '/tools', f)) and  f.endswith(".html"))])

    tools = [{'name': f[:-5].replace('-', ' '), 'slug': f[:-5]} for f in tools]

    return {'tools': tools}


def select_parent_template(request):
    """Check if it's ajax, if so no need to parent template."""
    parent_template = "dummy_parent.html" if request.is_ajax() else "base.html"
    return {'parent_template': parent_template}


def openshift(request):
    """Check if it's openshift."""
    if 'OPENSHIFT_APP_NAME' in os.environ:
        return {'OPENSHIFT': True}
    else:
        return {'OPENSHIFT': False}
