from django.conf import settings
from datetime import date
import os


def categories(request=None):
    """Get all tools."""
    tools = []
    folders = settings.TEMPLATES[0]['DIRS']
    for folder in folders:
        if os.path.exists(folder + '/tools'):
            tools.extend([f for f in os.listdir(folder + '/tools') if (os.path.isfile(os.path.join(folder + '/tools', f)) and f.endswith(".html"))])

    tools = [{'name': f[:-5].replace('-', ' ').capitalize(), 'slug': f[:-5]} for f in tools]
    tools = sorted(tools, key=lambda k: k['name'])

    return {'tools': tools}


def select_parent_template(request):
    """Check if it's ajax, if so no need to parent template."""
    parent_template = "dummy_parent.html" if request.is_ajax() else "base.html"
    return {'parent_template': parent_template}


def arrival_date(request):
    """Arrival date."""
    return {'today': date.today(), 'arrival_date': date(2017, 9, 24)}
