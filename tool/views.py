from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, JsonResponse, HttpResponseRedirect
from django.core.exceptions import PermissionDenied, ValidationError
import dateutil.parser
from datetime import datetime
import requests
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
import json
from schedule.models import Calendar, CalendarRelation, Event, Rule

from .models import TIMEZONES, Card, Word, Profile
from .forms import WordForm, EventForm, CardForm, AvatarForm

User = get_user_model()


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
    if not request.user.is_superuser and username and username != request.user.username:
        raise PermissionDenied

    user = get_object_or_404(User, username=username) if username else request.user
    cards = Card.objects.filter(user=user).order_by('order')

    if request.method == 'POST':
        form = CardForm(data=request.POST)
        if form.is_valid():
            card = form.save(commit=False)
            card.user = user
            card.save()

            return redirect(reverse('flashcards'))
    else:
        form = CardForm()

    return render(request, "flashcards.html", dict(
        cards=cards,
        user=user,
        form=form,
        active_page='flashcards')
    )


@login_required
def calendar(request, username=None):
    """Calendar."""
    if not request.user.is_superuser and username and username != request.user.username:
        raise PermissionDenied

    user = get_object_or_404(User, username=username) if username else request.user
    calendar_obj, created = Calendar.objects.get_or_create(
        slug=user.username,
        defaults={'name': '{} Calendar'.format(user.username)},
    )

    if request.method == 'POST':
        form = EventForm(data=request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.creator = user
            event.calendar = calendar_obj
            event.color_event = '#' + event.color_event
            event.save()

            return redirect(reverse('calendar'))
    else:
        form = EventForm()

    return render(request, "calendar.html", dict(
        form=form,
        active_page='calendar'
    ))


@login_required
def profile_view(request, username):
    """User profile."""
    user = get_object_or_404(User, username=username)
    form = AvatarForm(data=request.POST)

    timezones = '['
    for val, text in TIMEZONES:
        timezones += '{value: "' + val + '", text: "' + text + '"},'
    timezones += ']'

    return render(request, 'profile.html', {
        'profile_user': user,
        'is_current_user': user == request.user,
        'form': form,
        'timezones': timezones,
    })


@login_required
def update_profile(request):
    """Update user."""
    if request.method == 'POST':
        profile = get_object_or_404(Profile, user=request.user)
        avatar = request.FILES.get('avatar', '')
        if avatar:
            form = AvatarForm(request.POST, request.FILES, instance=profile)
            if form.is_valid():
                form.save()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            field = request.POST.get('name', '')
            value = request.POST.get('value', '')

            if field == 'timezone':
                if value in [t for t, _ in TIMEZONES]:
                    profile.timezone = value
                    profile.save()
                    return JsonResponse({'success': True})
                else:
                    return JsonResponse(_("This value not allowed"), safe=False, status=403)
            elif field in ['first_name', 'last_name', 'email']:
                setattr(request.user, field, value)
                try:
                    request.user.clean_fields()
                    request.user.save()
                    return JsonResponse({'success': True})
                except ValidationError as e:
                    return JsonResponse(', '.join(e.message_dict[field]), safe=False, status=422)

    return JsonResponse(_("You can't change this field"), safe=False, status=403)


@login_required
def card_order(request, username=None):
    """Change Flashcards order."""
    if request.is_ajax():
        if not request.user.is_superuser and username and username != request.user.username:
            raise JsonResponse(_("You can't change the order"), safe=False, status=403)

        user = get_object_or_404(User, username=username) if username else request.user
        cards = Card.objects.filter(user=user)
        order = request.POST.get('order', '')
        order = json.loads(order)
        for card in cards:
            if str(card.id) in order:
                card.order = order[str(card.id)]
                card.save()

        return JsonResponse(_('The order was changed'), safe=False)
    raise Http404


@login_required
def dictionary(request, username=None):
    """Dictionary."""
    if not request.user.is_superuser and username and username != request.user.username:
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
        form = WordForm()

    words = Word.objects.filter(user=user).order_by('-id')

    return render(request, "dictionary.html", dict(
        words=words,
        languages=settings.LANGUAGES,
        form=form,
        active_page='dictionary'
    ))


def log_in(request):
    form = AuthenticationForm()
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect(reverse('main'))

    return render(request, 'login.html', {'form': form})


@login_required
def log_out(request):
    logout(request)
    return redirect(reverse('login'))
