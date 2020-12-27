import json
import re
from collections import OrderedDict, defaultdict

import pytz
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.gis.geoip2 import GeoIP2
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.serializers import serialize
from django.db import transaction
from django.db.utils import IntegrityError
from django.http import Http404, HttpResponseRedirect, JsonResponse, QueryDict
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext
from django.views import View
from geoip2.errors import AddressNotFoundError
from schedule.models import Calendar, Event

from tool.forms import (AvatarForm, CardForm, CodeForm, EventForm, LinkForm,
                        TaskForm, WordForm)
from tool.models import (TIMEZONES, Canvas, Card, Code, Label, Link, Profile,
                         Task, Word, default_palette_colors)
from tool.tasks import get_occurrences
from tool.utils import check_news

User = get_user_model()


class GetUserMixin:
    @staticmethod
    def get_user(request, username: str):
        """ Get user by username and check access. """
        if not request.user.is_authenticated or (
                not request.user.is_superuser and
                username and username != request.user.username):
            raise PermissionDenied

        if username:
            return get_object_or_404(User, username=username)

        return request.user


def tool(request, slug, username=None):
    """ Show needed tool. """
    try:
        user = request.user
        if username:
            user = get_object_or_404(User, username=username)

        return render(request, slug + ".html", dict(
            active_page=slug,
            profile_user=user
        ))
    except Exception as e:
        raise Http404 from e


def about_page(request):
    """ About page. """
    return render(request, 'about.html', {'active_page': 'about'})


class FlashcardsView(LoginRequiredMixin, View, GetUserMixin):
    def get(self, request, username=None):
        """ Get form. """
        user = self.get_user(request, username)
        cards = Card.objects.filter(user=user).order_by('order')
        if user == request.user:
            form_action = reverse('flashcards')
        else:
            form_action = reverse('user_flashcards', args=[user.username])
        form = CardForm()

        return render(request, "flashcards.html", dict(
            cards=cards,
            profile_user=user,
            form=form,
            form_action=form_action,
            active_page=form_action.lstrip('/')
        ))

    def post(self, request, username=None):
        """ Form submit. """
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

        return render(request, "flashcards.html", dict(
            cards=cards,
            profile_user=user,
            form=form,
            form_action=form_action,
            active_page=form_action.lstrip('/')
        ))

    def delete(self, request, pk, username=None):
        """ Delete the flashcard. """
        self.get_user(request, username)
        flashcard = get_object_or_404(Card, pk=pk)
        flashcard.delete()

        return JsonResponse(
            {'redirect': reverse('flashcards'), 'success': True}
        )


class TasksView(LoginRequiredMixin, View, GetUserMixin):
    def get(self, request, username=None):
        """ Get form. """
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

        form.fields['color'].widget.choices = list(palette.items())

        return render(request, "tasks.html", dict(
            tasks_dict=tasks_dict.items(),
            palette=palette,
            profile_user=user,
            form=form,
            form_action=form_action,
            active_page=form_action.lstrip('/')
        ))

    def post(self, request, username=None):
        """ Form submit. """
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

        return render(request, "tasks.html", dict(
            tasks_dict=tasks_dict.items(),
            palette=palette,
            profile_user=user,
            form=form,
            form_action=form_action,
            active_page=form_action.lstrip('/')
        ))

    def delete(self, request, pk, username=None):
        """ Delete the task. """
        self.get_user(request, username)
        task = get_object_or_404(Task, pk=pk)
        task.delete()

        return JsonResponse({'redirect': reverse('tasks'), 'success': True})


class CalendarView(LoginRequiredMixin, View, GetUserMixin):
    def get(self, request, username=None):
        """ Get form. """
        user = self.get_user(request, username)

        return render(request, "calendar.html", dict(
            profile_user=user,
            form=EventForm()
        ))

    def post(self, request, username=None):
        """ Form submit. """
        user = self.get_user(request, username)

        calendar_obj, _ = Calendar.objects.get_or_create(
            slug=user.username,
            defaults={'name': '{} Calendar'.format(user.username)},
        )

        post_object = request.POST.copy()
        post_id = post_object.pop('id', [None])[0]
        if post_id:
            event = Event.objects.filter(id=post_id, creator=user).first()
            if not event:
                raise Http404
        else:
            event = Event(creator=user)

        form = EventForm(data=post_object, instance=event)
        if form.is_valid():
            user_timezone = 'UTC'
            if hasattr(user, 'profile') and user.profile.timezone:
                user_timezone = user.profile.timezone
            user_timezone = pytz.timezone(user_timezone)

            event = form.save(commit=False)
            event.calendar = calendar_obj
            event.start = user_timezone.localize(
                event.start.replace(tzinfo=None)
            )
            event.end = user_timezone.localize(event.end.replace(tzinfo=None))
            event.color_event = '#' + event.color_event
            event.save()

            return redirect(request.path)

        return render(request, "calendar.html", dict(
            profile_user=user,
            form=form
        ))

    def delete(self, request, pk, username=None):
        """ Delete the event. """
        user = self.get_user(request, username)
        event = get_object_or_404(Event, pk=pk, creator=user)
        event.delete()

        if user == request.user:
            form_action = reverse('calendar')
        else:
            form_action = reverse('user_calendar', args=[user.username])

        return JsonResponse({'redirect': form_action, 'success': True})


class ProfileView(LoginRequiredMixin, View, GetUserMixin):
    def get(self, request, username):
        """ User profile. """
        user = self.get_user(request, username)
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
            is_current_user=True,
            form=form,
            timezones=timezones
        ))

    def post(self, request, username=None):
        """ Update user callback. """
        user = self.get_user(request, username)
        profile = get_object_or_404(Profile, user=user)
        avatar = request.FILES.get('avatar', '')
        if avatar:
            form = AvatarForm(request.POST, request.FILES, instance=profile)
            if form.is_valid():
                form.save()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

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

        if any([
                field in ['first_name', 'last_name', 'email', 'phone_number'],
                field.startswith('palette_color_')
        ]):
            if field == 'phone_number' or \
                    field.startswith('palette_color_'):
                current_obj = profile
            else:
                current_obj = user

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


@staff_member_required
def users_list(request):
    """ Users list. """
    users = User.objects.all()

    return render(request, 'user_list.html', dict(
        users=users,
        active_page=users
    ))


@login_required
def card_order(request, username=None):
    """ Change Flashcards order callback. """
    if request.is_ajax():
        user = GetUserMixin().get_user(request, username)

        cards = Card.objects.filter(user=user)
        order = json.loads(request.POST.get('order', ''))
        with transaction.atomic():
            for card in cards:
                if str(card.id) in order:
                    card.order = order[str(card.id)]
                    card.save()

        return JsonResponse(ugettext('The order was changed'), safe=False)
    raise Http404


@login_required
def task_order(request, username=None):
    """ Change Task order and status callback. """
    if request.is_ajax():
        user = GetUserMixin().get_user(request, username)
        serialized_task = {}
        status = request.POST.get('status', '')
        try:
            task_id = int(str(request.POST.get('id')))
        except ValueError:
            task_id = None

        if status in (status[0] for status in Task.STATUSES):
            tasks = Task.objects.filter(user=user)
            order = json.loads(request.POST.get('order', ''))
            with transaction.atomic():
                for task in tasks:
                    if str(task.id) in order:
                        task.weight = order[str(task.id)]
                        task.status = status

                        # Adjust progress and resolution.
                        if status == 'todo':
                            task.progress = 0
                        elif status == 'done':
                            task.resolution = task.resolution or 'done'
                            task.progress = 100

                        task.save()

                        if task.pk == task_id:
                            serialized_task = serialize('json', [task])[1:-1]

        return JsonResponse({'task': serialized_task})
    raise Http404


@login_required
def link_order(request, username=None):
    """ Change Links order callback. """
    if request.is_ajax():
        user = GetUserMixin().get_user(request, username)

        links = Link.objects.filter(user=user)
        order = json.loads(request.POST.get('order', ''))
        with transaction.atomic():
            for link in links:
                if str(link.id) in order:
                    link.weight = order[str(link.id)]
                    link.save()

        return JsonResponse(ugettext('The order was changed'), safe=False)
    raise Http404


@login_required
def user_events(request):
    """ Get today's events. """
    if request.is_ajax():
        start = timezone.now()
        end = start + timezone.timedelta(days=1)
        events = get_occurrences(start, end, request.user)

        user_events_list = []
        for event in events:
            user_timezone = pytz.utc
            if event.creator.profile.timezone:
                user_timezone = pytz.timezone(event.creator.profile.timezone)
            local_time = timezone.localtime(event.start,
                                            user_timezone).strftime('%H:%M')
            user_events_list.append(local_time + ' ' + event.title)
        return JsonResponse(' and '.join(user_events_list), safe=False)

    raise Http404


class DictionaryView(View, GetUserMixin):
    def get(self, request, username=None):
        """ Get form. """
        try:
            user = self.get_user(request, username)
        except PermissionDenied:
            return redirect(reverse('login') + '?next=' + request.path)
        form = WordForm()
        words = Word.objects.filter(user=user).order_by('-id')

        return render(request, "dictionary.html", dict(
            profile_user=user,
            words=words,
            languages=settings.LANGUAGES,
            form=form,
            form_action=request.path,
            active_page=request.path.lstrip('/')
        ))

    def post(self, request, username=None):
        """ Form submit. """
        user = self.get_user(request, username)

        form = WordForm(data=request.POST)
        if form.is_valid():
            word = form.save(commit=False)
            word.user = user
            word.save()

            return redirect(request.path)

        words = Word.objects.filter(user=user).order_by('-id')

        return render(request, "dictionary.html", dict(
            profile_user=user,
            words=words,
            languages=settings.LANGUAGES,
            form=form,
            form_action=request.path,
            active_page=request.path.lstrip('/')
        ))

    def put(self, request, username=None):
        """ Word edit. """
        put = QueryDict(request.body)
        field = put.get('lang', '')

        if field in [lang[0] for lang in settings.LANGUAGES]:
            self.get_user(request, username)
            pk = put.get('pk', '')
            word = get_object_or_404(Word, pk=pk)
            value = put.get('value', '')
            setattr(word, field, value)
            word.save()
            return JsonResponse({'redirect': request.path, 'success': True})

        return JsonResponse(
            ugettext("You can't change this field"),
            safe=False,
            status=403
        )


def log_in(request):
    """ User login page. """
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
    # noinspection PyMethodMayBeStatic
    def get(self, _, slug):
        """ Get canvas by slug. """
        canvas = get_object_or_404(Canvas.objects.values_list(
            'canvas', flat=True), slug=slug)

        return JsonResponse(canvas, safe=False)


class CanvasesView(View, GetUserMixin):
    # noinspection PyMethodMayBeStatic
    def get(self, _, username=None):
        """ Get list of user canvases. """
        user = get_object_or_404(User, username=username)
        canvases = Canvas.objects.filter(user=user).order_by('-pk')\
            .values_list('slug', 'canvas')

        return JsonResponse(dict(canvases), safe=False)

    def post(self, request, username=None):
        """ Save or create canvas. """
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


class TracerouteView(LoginRequiredMixin, View):
    # noinspection PyMethodMayBeStatic
    def get(self, request):
        """ Get list of user code snippets or user snippet. """
        return render(request, 'traceroute.html', {})

    # noinspection PyMethodMayBeStatic
    def post(self, request):
        result = defaultdict(int)
        g = GeoIP2()
        traceroute = request.POST.get('traceroute', '')
        traceroute = traceroute.splitlines()
        s = [row.split() for row in traceroute if row]
        for i, row in enumerate(s):
            try:
                if row[1][0] == '(' and row[1][-1] == ')':
                    ip = row[1][1:-1]
                else:
                    ip = row[2][1:-1]

                lon, lat = g.lon_lat(ip)
            except (AddressNotFoundError, TypeError, OSError, IndexError):
                continue  # skip invalid ip

            result[(lon, lat)] = i + 1

            traceroute[i].rstrip()
            traceroute[i] += f" ({lat}, {lon})"

        return render(request, 'traceroute.html', {
            'traceroute': '\n'.join(traceroute),
            'result': [(lat, lon, t) for (lon, lat), t in result.items()]
        })


class CodeView(View, GetUserMixin):
    def get(self, request, slug=None, username=None):
        """ Get list of user code snippets or user snippet. """
        save_btn = True
        active_page = 'code'
        code_snippet = None
        code_snippets = ()
        page_title = ugettext('Code snippets')
        if slug:
            # Show single code snippet and edit form.
            code_snippet = get_object_or_404(Code, slug=slug)
            active_page = 'code/{}'.format(code_snippet.title)
            page_title = code_snippet.title
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
            params = request.GET.copy()
            label = params.get('label')
            code_snippets = Code.get_code_snippets_with_labels(user, label)

        form = CodeForm(instance=code_snippet)

        return render(request, 'code.html', {
            'form': form,
            'codes': code_snippets,
            'save_btn': save_btn,
            'delete_btn': save_btn and slug,
            'active_page': active_page,
            'page_title': page_title,
        })

    def post(self, request, slug=None, username=None):
        """ Save or create code snippet. """
        user = self.get_user(request, username)
        code_snippet = None
        active_page = 'code'
        page_title = ugettext('Code snippets')
        if slug:
            code_snippet = get_object_or_404(Code, slug=slug)
            active_page = 'code/{}'.format(code_snippet.title)
            page_title = code_snippet.title

        form = CodeForm(data=request.POST, instance=code_snippet)

        if form.is_valid():
            code = form.save(commit=False)
            code.user = user
            try:
                with transaction.atomic():
                    code.save()

                form.save_m2m()

                # Save used programming languages as labels.
                langs = set(re.findall('<code class="language-(.*?)">',
                                       code.text, re.DOTALL))
                labels = Label.objects.filter(category='programing')
                filtered_labels = []
                for label in labels:
                    # Need to fit 'C++', 'C#', ' Objective-C'.
                    if label.title.lower().replace('-', '').replace('#', 's')\
                            .replace('+', 'p', 2) in langs:
                        filtered_labels.append(label)
                code.labels.add(*filtered_labels)
            except IntegrityError:
                form.add_error(
                    'title',
                    'Code snippet with title "{}" already exists.'.format(
                        code.title
                    )
                )
            else:
                return redirect(reverse('code'))

        return render(request, 'code.html', {
            'form': form,
            'codes': [] if slug else Code.get_code_snippets_with_labels(user),
            'save_btn': True,  # only privileged user will have access to post
            'delete_btn': bool(slug),
            'active_page': active_page,
            'page_title': page_title,
        })

    def delete(self, request, slug, username=None):
        """ Delete code snippet. """
        self.get_user(request, username)
        code_snippet = get_object_or_404(Code, slug=slug)
        code_snippet.delete()

        return JsonResponse({'redirect': reverse('code'), 'success': True})


class LinkView(View, GetUserMixin):
    def get(self, request, username=None):
        """ Get list of links. """
        try:
            user = self.get_user(request, username)
        except PermissionDenied:
            return redirect(reverse('login') + '?next=' + request.path)

        links = Link.objects.select_related('category').filter(
            user=user).order_by('category__title', 'weight')
        palette = set((link.color for link in links))

        categorized_links = defaultdict(list)
        for link in links:
            categorized_links[link.category or ''].append(link)
        categorized_links = categorized_links.items()

        return render(request, "links.html", dict(
            categorized_links=categorized_links,
            palette=palette,
            form=LinkForm(user=user),
            profile_user=user,
        ))

    def post(self, request, username=None):
        """ Form submit. """
        user = self.get_user(request, username)

        post_object = request.POST.copy()
        link_id = post_object.pop('id', [None])[0]
        if link_id:
            link = get_object_or_404(Link, pk=link_id, user=user)
        else:
            link = Link(user=user)
            first_link = Link.objects.filter(
                user=user).order_by('weight').first()
            link.weight = first_link.weight - 1 if first_link else 0

        form = LinkForm(data=request.POST, instance=link, user=user)
        if form.is_valid():
            try:
                link = form.save(commit=False)
                link.link = link.link.strip()
                link.user = user
                with transaction.atomic():
                    link.save()
            except IntegrityError:
                form.add_error(
                    'link',
                    'Link "{}" already exists.'.format(
                        link.link
                    )
                )
            else:
                return redirect(request.path)

        links = Link.objects.filter(user=user).order_by('weight')
        palette = set((link.color for link in links))

        return render(request, "links.html", dict(
            links=links,
            palette=palette,
            form=form,
            profile_user=user,
        ))

    def delete(self, request, pk, username=None):
        """ Delete link. """
        self.get_user(request, username)
        link = get_object_or_404(Link, pk=pk)
        link.delete()

        return JsonResponse({'redirect': reverse('links'), 'success': True})


class FakeCheckView(View, GetUserMixin):
    """ Tool to check if the news are fake or real. """

    def get(self, request):
        return render(request, "fake_check.html", {'page_title': "Fake News Check"})

    def post(self, request):
        title = request.POST.get('title', '')
        text = request.POST.get('text', '')
        label = None
        probability = None

        if title and text:
            probability = check_news(title, text)

            if probability is not None:
                probability = round(probability * 100, 2)
                label = "fake"

                if probability <= 50:
                    label = "truth"
                    probability = 100 - probability

        return render(request, "fake_check.html", {
            'title': title,
            'text': text,
            'label': label,
            'probability': probability,
            'page_title': "Fake News Check"
        })


@login_required
def log_out(request):
    """ User logout callback. """
    logout(request)
    return redirect(reverse('login'))
