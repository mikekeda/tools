from django.shortcuts import render
from django.http import Http404, JsonResponse, HttpResponseForbidden
import dateutil.parser
from datetime import datetime
import requests


def main(request):
    """Main page."""

    return render(request, "slider.html", dict(active_page="home"))


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
    call = []

    response = requests.get(
        "https://yawavedev.atlassian.net/rest/api/latest/search?jql=worklogDate='{}' AND worklogAuthor='{}'&fields=worklog".format(current_date.strftime("%Y-%m-%d"), username),
        auth=(username, password)
    )

    if response.status_code == 200:
        body = response.json()
        result = {
            'logs': [],
        }

        for issue in body['issues']:
            response = requests.get(issue['self'] + '/worklog', auth=(username, password))
            body = response.json()
            call.append(issue['self'] + '/worklog')
            logs = list(filter(lambda w:
                w['author']['key'] == username and dateutil.parser.parse(w['created']).date() == current_date.date(),
                body['worklogs']
            ))
            for log in logs:
                text = '{}{{{}}} {}'.format(issue['key'], (str(log['timeSpentSeconds'] / 3600)).rstrip('.0') + 'h', log['comment'])
                result['logs'].append(text)

        return JsonResponse(result)

    return HttpResponseForbidden()
