from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, JsonResponse, HttpResponseRedirect
from django.core.exceptions import PermissionDenied, ValidationError
import dateutil.parser
from datetime import datetime, timedelta
import requests
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.utils import timezone
import json
from schedule.models import Calendar, Event
import pytz
import re

from .models import TIMEZONES, Card, Word, Profile
from .forms import WordForm, EventForm, CardForm, AvatarForm, FlightsForm

User = get_user_model()


def tool(request, slug):
    """Show needed tool."""
    try:
        return render(request, slug + ".html", dict(active_page=slug))
    except Exception:
        raise Http404


def worklogs(request):
    """Jira Worklogs."""
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
    if user == request.user:
        form_action = reverse('flashcards')
    else:
        form_action = reverse('user_flashcards', args=[user.username])

    if request.method == 'POST':
        form = CardForm(data=request.POST)
        if form.is_valid():
            card = form.save(commit=False)
            card.user = user
            card.save()

            return redirect(form_action)
    else:
        form = CardForm()

    return render(request, "flashcards.html", dict(
        cards=cards,
        user=user,
        form=form,
        form_action=form_action,
        active_page=form_action.lstrip('/'))
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
    if user == request.user:
        form_action = reverse('calendar')
    else:
        form_action = reverse('user_calendar', args=[user.username])

    if request.method == 'POST':
        form = EventForm(data=request.POST)
        if form.is_valid():
            user_timezone = pytz.timezone(request.user.profile.timezone)

            event = form.save(commit=False)
            event.creator = user
            event.calendar = calendar_obj
            event.start = user_timezone.localize(event.start.replace(tzinfo=None))
            event.end = user_timezone.localize(event.end.replace(tzinfo=None))
            event.color_event = '#' + event.color_event
            event.save()

            return redirect(form_action)
    else:
        form = EventForm()

    return render(request, "calendar.html", dict(
        profile_user=user,
        form=form,
        form_action=form_action,
        active_page=form_action.lstrip('/')
    ))


@login_required
def profile_view(request, username):
    """User profile."""
    user = get_object_or_404(User, username=username)
    profile, created = Profile.objects.get_or_create(user=user)
    form = AvatarForm(data=request.POST)

    timezones = '['
    for val, text in TIMEZONES:
        timezones += '{value: "' + val + '", text: "' + text + '"},'
    timezones += ']'

    return render(request, 'profile.html', dict(
        profile_user=user,
        profile=profile,
        is_current_user=user == request.user,
        form=form,
        timezones=timezones
    ))


@staff_member_required
def users_list(request):
    """Users list."""
    users = User.objects.all()

    return render(request, 'user_list.html', dict(
        users=users,
        active_page=users
    ))


@login_required
def update_profile(request):
    """Update user callback."""
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
    """Change Flashcards order callback."""
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
def user_events(request):
    """Get today's events."""
    if request.is_ajax():
        start = timezone.now()
        end = start + timezone.timedelta(days=1)
        events = Event.objects.filter(start__gt=start, start__lte=end, creator=request.user).select_related('creator')

        user_events = []
        for event in events:
            local_time = timezone.localtime(
                event.start,
                pytz.timezone(event.creator.profile.timezone)
            ).strftime('%H:%M')
            user_events.append(local_time + ' ' + event.title)
        return JsonResponse(' and '.join(user_events), safe=False)

    raise Http404


@login_required
def dictionary(request, username=None):
    """Dictionary."""
    if not request.user.is_superuser and username and username != request.user.username:
        raise PermissionDenied

    user = get_object_or_404(User, username=username) if username else request.user
    if user == request.user:
        form_action = reverse('dictionary')
    else:
        form_action = reverse('user_dictionary', args=[user.username])

    if request.method == 'POST':
        form = WordForm(data=request.POST)
        if form.is_valid():
            word = form.save(commit=False)
            word.user = user
            word.save()

            return redirect(form_action)
    else:
        form = WordForm()

    words = Word.objects.filter(user=user).order_by('-id')

    return render(request, "dictionary.html", dict(
        words=words,
        languages=settings.LANGUAGES,
        form=form,
        form_action=form_action,
        active_page=form_action.lstrip('/')
    ))


@login_required
def flights_view(request):
    """Check tickets."""
    if request.method == 'POST':
        form = FlightsForm(data=request.POST)

        if form.is_valid():
            url = settings.QPXEXPRESS_URL + settings.QPXEXPRESS_API_KEY
            headers = {'content-type': 'application/json'}

            origin = form.cleaned_data['origin']
            destination = form.cleaned_data['destination']
            round_trip = form.cleaned_data['round_trip']
            date_start = form.cleaned_data['date_start']

            params = {
                'request': {
                    'slice': [
                        {
                            'origin': origin,
                            'destination': destination,
                            'date': str(date_start)
                        }
                    ],
                    'passengers': {
                        'adultCount': 1,
                        'infantInLapCount': 0,
                        'infantInSeatCount': 0,
                        'childCount': 0,
                        'seniorCount': 0
                    },
                    'solutions': 10,
                    'refundable': False
                }
            }

            if round_trip:
                date_back = form.cleaned_data['date_back']

                params['request']['slice'].append({
                    'origin': destination,
                    'destination': origin,
                    'date': str(date_back)
                })

            response = requests.post(url, data=json.dumps(params), headers=headers)
            data = response.json()
            result = []

            if response.status_code == 200:
                if 'tripOption' in data['trips']:
                    for fly in data['trips']['tripOption']:
                        slice_data = []
                        for slice in fly['slice']:
                            route = slice['segment'][0]['leg'][0]['origin']
                            for segment in slice['segment']:
                                route += '->' + segment['leg'][0]['destination']

                            slice_data.append({
                                'stops': len(slice['segment']) - 1,
                                'slice': route,
                                'duration': str(timedelta(minutes=slice['duration']))[:-3]
                            })

                            result.append({
                                'price (USD)': float(re.sub(r'[^0-9.]', '', fly['saleTotal'])),
                                'slice': slice_data
                            })
            else:
                result = {
                    'status': response.status_code,
                    'statusText': data['error']['message']
                }

            return JsonResponse(result, safe=False)
    else:
        form = FlightsForm()

    return render(request, 'flights.html', dict(
        form=form,
    ))


def log_in(request):
    """User login page."""
    form = AuthenticationForm()
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect(reverse('main'))

    return render(request, 'login.html', {'form': form})


@login_required
def log_out(request):
    """User logout callback."""
    logout(request)
    return redirect(reverse('login'))
