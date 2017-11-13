import re
import json
from collections import OrderedDict
from datetime import datetime, timedelta
import requests
import pytz
import dateutil.parser
from schedule.models import Calendar, Event

from django.core.exceptions import PermissionDenied, ValidationError
from django.core.urlresolvers import reverse
from django.conf import settings
from django.http import Http404, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import ugettext
from django.utils import timezone
from django.views import View

from .models import (
    TIMEZONES,
    Card,
    Word,
    Profile,
    Task,
    Canvas,
    default_palette_colors
)
from .forms import (
    WordForm,
    EventForm,
    CardForm,
    AvatarForm,
    FlightsForm,
    TaskForm
)

User = get_user_model()


class GetUserMixin(object):
    def get_user(self, request, username: str):
        if not request.user.is_authenticated or (
                not request.user.is_superuser and
                username and username != request.user.username):
            raise PermissionDenied

        if username:
            return get_object_or_404(User, username=username)

        return request.user


def tool(request, slug, username=None):
    """Show needed tool."""
    try:
        user = request.user
        if username:
            user = get_object_or_404(User, username=username)

        return render(request, slug + ".html", dict(
            active_page=slug,
            profile_user=user
        ))
    except Exception:
        raise Http404


def worklogs(request):
    """Jira Worklogs."""
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    current_date = datetime.today()

    response = requests.get(
        "https://yawavedev.atlassian.net/rest/api/latest/search"
        "?jql=worklogDate='{}' "
        "AND worklogAuthor='{}'&fields=worklog".format(
            current_date.strftime("%Y-%m-%d"),
            username
        ),
        auth=(username, password)
    )

    if response.status_code == 200:
        date_today = current_date.date()
        body = response.json()
        result = {
            'logs': [],
            'time': 0,
        }

        for issue in body['issues']:
            response = requests.get(
                issue['self'] + '/worklog',
                auth=(username, password)
            )
            if response.status_code == 200:
                body = response.json()
                for log in body['worklogs']:
                    if (log['author']['key'] == username and
                            dateutil.parser.parse(
                                log['created']
                            ).date() == date_today):
                        result['time'] += log['timeSpentSeconds'] / 3600
                        text = '{}{{{}}} {}'.format(
                            issue['key'],
                            (
                                str(log['timeSpentSeconds'] / 3600)
                            ).rstrip('.0') + 'h',
                            log['comment']
                        )
                        result['logs'].append(text)

        return JsonResponse(result)

    raise PermissionDenied


@login_required
def flashcards(request, username=None):
    """Flashcards."""
    user = GetUserMixin().get_user(request, username)

    cards = Card.objects.filter(user=user).order_by('order')
    if user == request.user:
        form_action = reverse('flashcards')
    else:
        form_action = reverse('user_flashcards', args=[user.username])

    if request.method == 'POST':
        post_object = request.POST.copy()
        post_id = post_object.pop('id', [None])[0]
        if post_id:
            card = Card.objects.filter(id=post_id, user=user).first()
            if not card:
                raise PermissionDenied
        else:
            card = Card(user=user)

        form = CardForm(data=post_object, instance=card)
        if form.is_valid():
            form.save()

            return redirect(form_action)
    else:
        form = CardForm()

    return render(
        request,
        "flashcards.html",
        dict(
            cards=cards,
            profile_user=user,
            form=form,
            form_action=form_action,
            active_page=form_action.lstrip('/')
        )
    )


@login_required
def tasks_view(request, username=None):
    """Tasks."""
    tasks = []
    user = GetUserMixin().get_user(request, username)

    if user == request.user:
        form_action = reverse('tasks')
    else:
        form_action = reverse('user_tasks', args=[user.username])

    if request.method == 'POST':
        post_object = request.POST.copy()
        post_id = post_object.pop('id', [None])[0]
        if post_id:
            task = Task.objects.filter(id=post_id, user=user).first()
            if not task:
                raise PermissionDenied
        else:
            task = Task(user=user)
        form = TaskForm(data=post_object, instance=task)
        if form.is_valid():
            first_task = Task.objects.filter(
                user=user, status='todo').order_by('weight').first()
            task = form.save(commit=False)
            if not post_id:
                task.weight = first_task.weight - 1 if first_task else 0
            task.save()

            return redirect(form_action)
    else:
        tasks = Task.objects.filter(user=user).order_by('weight')
        form = TaskForm()

    profile, _ = Profile.objects.get_or_create(user=user)
    palette = {
        str(i): getattr(profile, 'palette_color_' + str(i), c)
        for i, c in enumerate(default_palette_colors, 1)
    }
    tasks_dict = OrderedDict([(k[0], []) for k in Task.STATUSES])
    for task in tasks:
        tasks_dict[task.status].append(task)

    form.fields['color'].widget.choices = [(i, k) for i, k in palette.items()]

    return render(
        request,
        "tasks.html",
        dict(
            tasks_dict=tasks_dict.items(),
            palette=palette,
            profile_user=user,
            form=form,
            form_action=form_action,
            active_page=form_action.lstrip('/')
        )
    )


@login_required
def calendar(request, username=None):
    """Calendar."""
    user = GetUserMixin().get_user(request, username)

    calendar_obj, _ = Calendar.objects.get_or_create(
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
            event.start = user_timezone.localize(
                event.start.replace(tzinfo=None)
            )
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
    profile, _ = Profile.objects.get_or_create(user=user)
    form = AvatarForm(data=request.POST)

    timezones = '['
    for val, text in TIMEZONES:
        timezones += '{value: "' + val + '", text: "' + text + '"},'
    timezones += ']'

    return render(request, 'profile.html', dict(
        profile_user=user,
        profile=profile,
        palette_colors=(
            getattr(profile, 'palette_color_' + str(i), c)
            for i, c in enumerate(default_palette_colors, 1)
        ),
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

                return JsonResponse(
                    ugettext("This value not allowed"),
                    safe=False,
                    status=403
                )
            elif field in ['first_name', 'last_name', 'email'] \
                    or field.startswith('palette_color_'):
                if field.startswith('palette_color_'):
                    current_obj = profile
                else:
                    current_obj = request.user

                setattr(current_obj, field, value)
                try:
                    current_obj.clean_fields()
                    current_obj.save()
                    return JsonResponse({'success': True})
                except ValidationError as e:
                    return JsonResponse(
                        ', '.join(e.message_dict[field]),
                        safe=False,
                        status=422
                    )

    return JsonResponse(
        ugettext("You can't change this field"),
        safe=False,
        status=403
    )


@login_required
def card_order(request, username=None):
    """Change Flashcards order callback."""
    if request.is_ajax():
        user = GetUserMixin().get_user(request, username)

        cards = Card.objects.filter(user=user)
        order = request.POST.get('order', '')
        order = json.loads(order)
        for card in cards:
            if str(card.id) in order:
                card.order = order[str(card.id)]
                card.save()

        return JsonResponse(ugettext('The order was changed'), safe=False)
    raise Http404


@login_required
def task_order(request, username=None):
    """Change Task order and status callback."""
    if request.is_ajax():
        user = GetUserMixin().get_user(request, username)
        order = request.POST.get('order', '')
        status = request.POST.get('status', '')
        if status in (status[0] for status in Task.STATUSES):
            tasks = Task.objects.filter(user=user)
            order = json.loads(order)
            for task in tasks:
                if str(task.id) in order:
                    task.weight = order[str(task.id)]
                    task.status = status
                    task.save()

        return JsonResponse(ugettext('The order was changed'), safe=False)
    raise Http404


@login_required
def user_events(request):
    """Get today's events."""
    if request.is_ajax():
        start = timezone.now()
        end = start + timezone.timedelta(days=1)
        events = Event.objects.filter(
            start__gt=start,
            start__lte=end,
            creator=request.user
        ).select_related('creator')

        user_events_list = []
        for event in events:
            local_time = timezone.localtime(
                event.start,
                pytz.timezone(event.creator.profile.timezone)
            ).strftime('%H:%M')
            user_events_list.append(local_time + ' ' + event.title)
        return JsonResponse(' and '.join(user_events_list), safe=False)

    raise Http404


@login_required
def dictionary(request, username=None):
    """Dictionary."""
    user = GetUserMixin().get_user(request, username)

    # it could be current user that open a page by his username
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


class FlightsView(LoginRequiredMixin, View):
    def get(self, request):
        """Get form."""
        form = FlightsForm()

        return render(request, 'flights.html', dict(
            form=form,
        ))

    def post(self, request):
        """Form submit."""
        form = FlightsForm(data=request.POST)

        if form.is_valid():
            params = {
                'request': {
                    'slice': [
                        {
                            'origin': form.cleaned_data['origin'],
                            'destination': form.cleaned_data['destination'],
                            'date': str(form.cleaned_data['date_start'])
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

            if form.cleaned_data['round_trip']:
                date_back = form.cleaned_data['date_back']

                params['request']['slice'].append({
                    'origin': form.cleaned_data['destination'],
                    'destination': form.cleaned_data['origin'],
                    'date': str(date_back)
                })

            response = requests.post(
                settings.QPXEXPRESS_URL + settings.QPXEXPRESS_API_KEY,
                data=json.dumps(params),
                headers={'content-type': 'application/json'}
            )
            data = response.json()

            # Handle an error.
            if response.status_code != 200:
                return JsonResponse({
                    'status': response.status_code,
                    'statusText': data['error']['message']
                }, safe=False)

            result = []
            for fly in data['trips'].get('tripOption', []):
                slice_data = []
                for item in fly['slice']:
                    route = item['segment'][0]['leg'][0]['origin']
                    for seg in item['segment']:
                        route += '->' + seg['leg'][0]['destination']

                    slice_data.append({
                        'stops': len(item['segment']) - 1,
                        'slice': route,
                        'duration': str(timedelta(
                            minutes=item['duration']
                        ))[:-3]
                    })

                result.append({
                    'price': float(re.sub(
                        r'[^0-9.]',
                        '',
                        fly['saleTotal']
                    )),
                    'slice': slice_data
                })

            return JsonResponse(result, safe=False)

        return render(request, 'flights.html', dict(
            form=form,
        ))


def log_in(request):
    """User login page."""
    if request.user.is_authenticated():
        return redirect(settings.LOGIN_REDIRECT_URL)
    form = AuthenticationForm()
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect(reverse('main'))

    return render(request, 'login.html', {'form': form})


class CanvasView(View, GetUserMixin):
    def get(self, request, slug):
        """Get canvas by slug."""
        canvas = get_object_or_404(Canvas.objects.values_list('canvas'),
                                   slug=slug)

        return JsonResponse(canvas[0], safe=False)


class CanvasesView(View, GetUserMixin):
    def get(self, request, username=None):
        """Get list of user canvases."""
        user = get_object_or_404(User, username=username)
        canvases = Canvas.objects.filter(user=user).order_by('-pk')\
            .values_list('slug', 'canvas')

        return JsonResponse(dict(canvases), safe=False)

    def post(self, request, username=None):
        """Save or create canvas."""
        user = self.get_user(request, username)
        data = request.POST.get('imgBase64', '')
        slug = request.POST.get('slug', '')

        if slug:
            # Change existing canvas.
            canv = Canvas.objects.filter(slug=slug).first()
            if canv:
                canv.canvas = data
                canv.save()
                message = ugettext("The Canvas wasn't changed")
            else:
                message = ugettext('The Canvas was changed')

            return JsonResponse(message, safe=False)

        # Create a new canvas.
        obj = Canvas(user=user, canvas=data)
        obj.save()

        return JsonResponse(ugettext('The Canvas was created'), safe=False)


@login_required
def log_out(request):
    """User logout callback."""
    logout(request)
    return redirect(reverse('login'))
