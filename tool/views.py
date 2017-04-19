from django.shortcuts import render, redirect
from django.http import Http404, JsonResponse, HttpResponseForbidden
import dateutil.parser
from datetime import datetime
import requests
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

from .models import Card, Word
from .forms import WordForm


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


@login_required
def flashcards(request):
    """Flashcards."""
    cards = []
    if request.user.is_authenticated:
        cards = Card.objects.filter(user=request.user).order_by('-id')

    return render(request, "flashcards.html", dict(cards=cards, active_page='flashcards'))


@login_required
def dictionary(request):
    """Dictionary."""
    if request.method == 'POST':
        form = WordForm(data=request.POST)
        if form.is_valid():
            word = form.save(commit=False)
            word.user = request.user
            word.save()

            return redirect(reverse('dictionary'))
        else:
            print(form.errors)
    else:
        form = WordForm()

    words = Word.objects.filter(user=request.user).order_by('-id')

    return render(request, "dictionary.html", dict(
        words=words,
        languages=settings.LANGUAGES,
        form=form,
        active_page='dictionary'
    ))
