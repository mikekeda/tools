import re
import json
from collections import OrderedDict
from datetime import timedelta
import requests
import pytz
from schedule.models import Calendar, Event

from django.core.exceptions import PermissionDenied, ValidationError
from django.conf import settings
from django.db import transaction
from django.db.utils import IntegrityError
from django.http import Http404, JsonResponse, HttpResponseRedirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.translation import ugettext
from django.utils import timezone
from django.views import View

from .models import (TIMEZONES, Card, Word, Profile, Task, Canvas, Code,
                     default_palette_colors)
from .forms import (WordForm, EventForm, CardForm, AvatarForm, FlightsForm,
                    TaskForm, CodeForm)

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


class FlashcardsView(LoginRequiredMixin, View, GetUserMixin):
    def get(self, request, username=None):
        """Get form."""
        user = self.get_user(request, username)
        cards = Card.objects.filter(user=user).order_by('order')
        if user == request.user:
            form_action = reverse('flashcards')
        else:
            form_action = reverse('user_flashcards', args=[user.username])
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

    def post(self, request, username=None):
        """Form submit."""
        user = self.get_user(request, username)
        cards = Card.objects.filter(user=user).order_by('order')
        if user == request.user:
            form_action = reverse('flashcards')
        else:
            form_action = reverse('user_flashcards', args=[user.username])
        post_object = request.POST.copy()
        post_id = post_object.pop('id', [None])[0]
        if post_id:
            card = Card.objects.filter(id=post_id, user=user).first()
            if not card:
                raise Http404
        else:
            card = Card(user=user)

        form = CardForm(data=post_object, instance=card)
        if form.is_valid():
            flashcard = form.save(commit=False)
            try:
                with transaction.atomic():
                    flashcard.save()
                return redirect(form_action)
            except IntegrityError:
                form.add_error(
                    'word',
                    'Card with word "{}" already exists.'.format(
                        flashcard.word
                    )
                )

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

    def delete(self, request, pk, username=None):
        """Delete the flashcard."""
        self.get_user(request, username)
        flashcard = get_object_or_404(Card, pk=pk)
        flashcard.delete()

        return JsonResponse(
            {'redirect': reverse('flashcards'), 'success': True}
        )


class TasksView(LoginRequiredMixin, View, GetUserMixin):
    def get(self, request, username=None):
        """Get form."""
        user = self.get_user(request, username)

        if user == request.user:
            form_action = reverse('tasks')
        else:
            form_action = reverse('user_tasks', args=[user.username])

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

        form.fields['color'].widget.choices = [(i, k) for i, k in
                                               palette.items()]

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

    def post(self, request, username=None):
        """Form submit."""
        user = self.get_user(request, username)

        if user == request.user:
            form_action = reverse('tasks')
        else:
            form_action = reverse('user_tasks', args=[user.username])

        profile, _ = Profile.objects.get_or_create(user=user)
        palette = {
            str(i): getattr(profile, 'palette_color_' + str(i), c)
            for i, c in enumerate(default_palette_colors, 1)
        }
        tasks_dict = OrderedDict([(k[0], []) for k in Task.STATUSES])

        post_object = request.POST.copy()
        post_id = post_object.pop('id', [None])[0]
        if post_id:
            task = Task.objects.filter(id=post_id, user=user).first()
            if not task:
                raise Http404
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

    def delete(self, request, pk, username=None):
        """Delete the task."""
        self.get_user(request, username)
        task = get_object_or_404(Task, pk=pk)
        task.delete()

        return JsonResponse(
            {'redirect': reverse('tasks'), 'success': True}
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
    if request.user.is_authenticated:
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
        canvas = get_object_or_404(Canvas.objects.values_list(
            'canvas', flat=True), slug=slug)

        return JsonResponse(canvas, safe=False)


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
        else:
            # Create a new canvas.
            Canvas(user=user, canvas=data).save()

        canvases = Canvas.objects.filter(user=user).order_by('-pk')\
            .values_list('slug', 'canvas')

        return JsonResponse(dict(canvases), safe=False)


class CodeView(View, GetUserMixin):
    def get(self, request, slug=None, username=None):
        """Get list of user code snippets or user snippet."""
        save_btn = True
        code_snippet = None
        code_snippets = ()
        if slug:
            # Show single code snippet and edit form.
            code_snippet = get_object_or_404(Code, slug=slug)
            try:
                self.get_user(request, username)
            except PermissionDenied:
                save_btn = False  # the user can't edit this snippet
        else:
            # Show all code snippets and create form.
            try:
                user = self.get_user(request, username)
            except PermissionDenied:
                return redirect(reverse('login') + '?next=' + request.path)
            code_snippets = Code.objects.filter(user=user).order_by('-pk') \
                .values_list('title', 'slug')

        form = CodeForm(instance=code_snippet)

        return render(request, 'code.html', {
            'form': form,
            'codes': code_snippets,
            'save_btn': save_btn,
            'delete_btn': save_btn and slug,
            'active_page': 'code'
        })

    def post(self, request, slug=None, username=None):
        """Save or create code snippet."""
        user = self.get_user(request, username)
        code_snippet = None
        code_snippets = []
        if slug:
            code_snippet = get_object_or_404(Code, slug=slug)

        form = CodeForm(data=request.POST, instance=code_snippet)

        if form.is_valid():
            code = form.save(commit=False)
            code.user = user
            try:
                with transaction.atomic():
                    code.save()
            except IntegrityError:
                form.add_error(
                    'title',
                    'Code snippet with title "{}" already exists.'.format(
                        code.title
                    )
                )
            else:
                return redirect(reverse('code'))
        elif slug:
            code_snippets = Code.objects.filter(user=user).order_by('-pk') \
                .values_list('title', 'slug')

        return render(request, 'code.html', {
            'form': form,
            'codes': code_snippets,
            'save_btn': True,  # only privileged user will have access to post
            'delete_btn': bool(slug),
            'active_page': 'code'
        })

    def delete(self, request, slug, username=None):
        """Delete code snippet."""
        self.get_user(request, username)
        code_snippet = get_object_or_404(Code, slug=slug)
        code_snippet.delete()

        return JsonResponse({'redirect': reverse('code'), 'success': True})


@login_required
def log_out(request):
    """User logout callback."""
    logout(request)
    return redirect(reverse('login'))
