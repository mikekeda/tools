from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, JsonResponse
from django.core.exceptions import PermissionDenied
import dateutil.parser
from datetime import datetime
import requests
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
import json

from .models import Card, Word
from .forms import WordForm


def tool(request, slug):
    """Tool."""
    try:
        return render(request, slug + ".html", dict(active_page=slug))
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

    raise PermissionDenied


@login_required
def flashcards(request, username=None):
    """Flashcards."""
    if not request.user.is_superuser and username != request.user.username:
        raise PermissionDenied

    user = get_object_or_404(User, username=username) if username else request.user
    cards = Card.objects.filter(user=user).order_by('order')

    return render(request, "flashcards.html", dict(cards=cards, user=user, active_page='flashcards'))


@login_required
def card_order(request, username=None):
    """Change Flashcards order."""
    if request.is_ajax():
        if not request.user.is_superuser and username != request.user.username:
            raise JsonResponse(_("You can't change the order"), safe=False, status=403)

        user = get_object_or_404(User, username=username) if username else request.user
        cards = Card.objects.filter(user=user)
        order = request.POST.get('order', '')
        order = json.loads(order)
        for card in cards:
            if str(card.id) in order:
                card.order = order[str(card.id)]
                card.save()

        return JsonResponse(_("The order was changed"), safe=False)
    raise Http404


@login_required
def dictionary(request, username=None):
    """Dictionary."""
    if not request.user.is_superuser and username != request.user.username:
        raise PermissionDenied

    user = get_object_or_404(User, username=username) if username else request.user

    if request.method == 'POST':
        form = WordForm(data=request.POST)
        if form.is_valid():
            word = form.save(commit=False)
            word.user = user
            word.save()

            return redirect(reverse('dictionary'))
        else:
            print(form.errors)
    else:
        form = WordForm()

    words = Word.objects.filter(user=user).order_by('-id')

    return render(request, "dictionary.html", dict(
        words=words,
        languages=settings.LANGUAGES,
        form=form,
        active_page='dictionary'
    ))
