from django.shortcuts import render
from django.http import Http404, JsonResponse, HttpResponseForbidden
import dateutil.parser
from datetime import datetime
import requests

from tool.models import Card


def tool(request, page_slug):
    """Tool."""
    try:
        return render(request, page_slug + ".html", dict(active_page=page_slug))
    except Exception:
        raise Http404


def worklogs(request):
    """Worklogs."""
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    current_date = datetime.today()

    response = requests.get(
        "https://yawavedev.atlassian.net/rest/api/latest/search?jql=worklogDate='{}' AND worklogAuthor='{}'&fields=worklog".format(
            current_date.strftime("%Y-%m-%d"),
            username
        ),
        auth=(username, password)
    )

    if response.status_code == 200:
        body = response.json()
        result = {
            'logs': [],
            'time': 0,
        }

        for issue in body['issues']:
            response = requests.get(issue['self'] + '/worklog', auth=(username, password))
            if response.status_code == 200:
                body = response.json()
                for log in body['worklogs']:
                    if log['author']['key'] == username and dateutil.parser.parse(log['created']).date() == current_date.date():
                        result['time'] += log['timeSpentSeconds'] / 3600
                        text = '{}{{{}}} {}'.format(
                            issue['key'],
                            (str(log['timeSpentSeconds'] / 3600)).rstrip('.0') + 'h',
                            log['comment']
                        )
                        result['logs'].append(text)

        return JsonResponse(result)

    return HttpResponseForbidden()


def flashcards(request):
    """Flashcards."""
    cards = []
    if request.user.is_authenticated:
        cards = Card.objects.filter(user=request.user).order_by('-id')

    return render(request, "flashcards.html", dict(cards=cards, active_page='flashcards'))
