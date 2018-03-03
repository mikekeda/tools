import base64
from collections import namedtuple
import datetime
import random
import string
import pytz

from cryptography.fernet import Fernet

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.core.cache import cache
from django.core.validators import MaxValueValidator, MinValueValidator
from django.urls import reverse
from django.utils.html import format_html

from .widgets import ColorWidget

TIMEZONES = sorted([
    (tz, tz + ' ' + datetime.datetime.now(pytz.timezone(tz)).strftime('%z'))
    for tz in pytz.common_timezones
])

default_palette_colors = (
    'f5f5f5',
    'dff0d8',
    'd9edf7',
    'fcf8e3',
    'f2dede',
)

_char_map = string.ascii_letters + string.digits


def number_to_chars(num: int):
    base = len(_char_map)
    if num == 0:
        return _char_map[0]
    digits = []
    while num:
        digits.append(_char_map[int(num % base)])
        num //= base
    return ''.join(map(str, digits[::-1]))


def save_and_add_slug(obj, force_insert=False, force_update=False, using=None,
                      update_fields=None):
    need_slug = not obj.pk
    super(type(obj), obj).save(force_insert, force_update,
                               using, update_fields)
    if need_slug:
        obj.slug = ''.join(random.sample(_char_map, 3)) +\
                    number_to_chars(obj.pk)
        obj.save()


def get_username_by_uid(obj):
    """ Helper function to get user username by user id. """
    # Try to get username from the cache to avoid unneeded queries,
    # pattern is 'username_by_id_<user_id>'
    username = cache.get('username_by_id_{}'.format(obj.user_id))
    if not username:
        # We don't have the username - get username and set it to the cache.
        username = obj.user.username
        cache.set(
            'username_by_id_{}'.format(obj.user_id),
            username,
            settings.USER_ONLINE_TIMEOUT
        )

    return username


class ColorField(models.CharField):
    """ Color field. """

    def formfield(self, **kwargs):
        kwargs['widget'] = ColorWidget
        return super(ColorField, self).formfield(**kwargs)


class Profile(models.Model):
    """ Profile model. """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name='profile',
        on_delete=models.CASCADE
    )
    timezone = models.CharField(
        max_length=64,
        choices=TIMEZONES,
        blank=True,
        null=True
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        default='avatars/no-avatar.png'
    )
    email = models.EmailField(
        max_length=64,
        blank=True,
        null=True
    )
    email_password = models.CharField(
        max_length=256,
        blank=True,
        null=True
    )

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        """ Encrypt password on save in case if it was changed. """
        if self.email_password:
            origin = None
            if self.pk:
                origin = type(self).objects.get(pk=self.pk)
            # Check if password was changed.
            if not origin or origin.email_password != self.email_password:
                # Encrypt password.
                key = base64.urlsafe_b64encode(
                    settings.SECRET_KEY[:32].encode('utf-8')
                )
                self.email_password = Fernet(key).encrypt(
                    self.email_password.encode('utf-8')
                ).decode('utf-8')

        super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return get_username_by_uid(self)


for i, default_color in enumerate(default_palette_colors, 1):
    Profile.add_to_class(
        'palette_color_' + str(i),
        ColorField(max_length=6, default=default_color)
    )


class Card(models.Model):
    """ Flashcard model. """
    DIFFICULTIES = (
        ('easy', 'Easy'),
        ('middle', 'Medium'),
        ('difficult', 'Difficult'),
    )

    word = models.CharField(max_length=60)
    description = models.TextField(blank=True, null=True)
    difficulty = models.CharField(
        max_length=10,
        choices=DIFFICULTIES,
        default='difficult'
    )
    user = models.ForeignKey(
        User,
        related_name='cards',
        on_delete=models.CASCADE
    )
    order = models.PositiveSmallIntegerField(default=0)
    created_date = models.DateTimeField(auto_now_add=True)
    changed_date = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (('word', 'user'),)

    def __str__(self):
        return self.word


class Word(models.Model):
    """ Word model. """
    user = models.ForeignKey(
        User,
        related_name='words',
        on_delete=models.CASCADE
    )
    created = models.DateTimeField(auto_now_add=True)
    changed = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.en


for lang in settings.LANGUAGES:
    Word.add_to_class(
        lang[0],
        models.CharField(max_length=60, null=True, blank=True)
    )


class Label(models.Model):
    """ Label model. """
    CATEGORIES = (
        ('programing', 'Programing'),
    )

    title = models.CharField(max_length=60)
    user = models.ForeignKey(
        User,
        related_name='labels',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    category = models.CharField(
        max_length=16,
        choices=CATEGORIES,
        default='programing'
    )
    created = models.DateTimeField(auto_now_add=True)
    changed = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Task(models.Model):
    """ Task model. """
    STATUSES = (
        ('todo', 'TODO'),
        ('doing', 'Doing'),
        ('done', 'Done'),
    )
    RESOLUTIONS = (
        ("fixed", "Fixed"),
        ("won't fix", "Won't Fix"),
        ("duplicate", "Duplicate"),
        ("incomplete", "Incomplete"),
        ("Cannot Reproduce", "Cannot Reproduce"),
        ("obsolete", "Obsolete"),
        ("works as designed", "Works as Designed"),
        ("done", "Done"),
        ("won't Do", "Won't Do"),
    )

    title = models.CharField(max_length=60)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUSES, default='todo')
    resolution = models.CharField(
        max_length=16,
        choices=RESOLUTIONS,
        blank=True,
        null=True
    )
    progress = models.PositiveSmallIntegerField(
        default=0,
        blank=True,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100)
        ]
    )
    labels = models.ManyToManyField(Label, blank=True)
    color = models.PositiveSmallIntegerField(
        default=1,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(len(default_palette_colors))
        ]
    )
    user = models.ForeignKey(
        User,
        related_name='tasks',
        on_delete=models.CASCADE
    )
    weight = models.SmallIntegerField(default=0)
    due_date = models.DateTimeField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    changed_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Canvas(models.Model):
    """ Canvas model. """
    user = models.ForeignKey(
        User,
        related_name='canvases',
        on_delete=models.CASCADE
    )
    canvas = models.TextField(blank=True, null=True)
    slug = models.CharField(max_length=10, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    changed = models.DateTimeField(auto_now=True)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        save_and_add_slug(self, force_insert, force_update, using,
                          update_fields)

    def preview(self):
        return format_html('<img src="{}" />', self.canvas)

    preview.short_description = 'Image'
    preview.allow_tags = True

    def __str__(self):
        return '{}: {}'.format(get_username_by_uid(self), self.pk)


class Code(models.Model):
    """ Code model. """
    title = models.CharField(max_length=60)
    text = models.TextField()
    user = models.ForeignKey(
        User,
        related_name='code_fragments',
        on_delete=models.CASCADE
    )
    slug = models.CharField(max_length=10, unique=True)
    labels = models.ManyToManyField(Label, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    changed = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (('title', 'user'),)

    def link_to_code_snippet(self):
        return format_html(
            '<a href="{}">{}</a>',
            reverse('code_slug', kwargs={'slug': self.slug}),
            self.title
        ) if self.slug else ''

    @classmethod
    def get_code_snippets_with_labels(cls, user):
        """ Get code snippets with labels. """
        code_snippets = cls.objects.filter(user=user).prefetch_related(
            'labels'
        ).order_by('-pk').values_list(
            'title', 'slug', 'labels__title', named=True
        )

        code_snippets_dict = {}
        for snippet in code_snippets:
            snippet = snippet._asdict()
            snippet['labels__title'] = [snippet['labels__title']]
            if snippet['labels__title'][0] is None:
                snippet['labels__title'] = []

            if snippet['slug'] in code_snippets_dict:
                code_snippets_dict[snippet['slug']]['labels__title'] += \
                    snippet['labels__title']
            else:
                code_snippets_dict[snippet['slug']] = snippet

        for slug, snippet in code_snippets_dict.items():
            code_snippets_dict[slug] = \
                namedtuple('Row', snippet.keys())(**snippet)

        return code_snippets_dict.values()

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        save_and_add_slug(self, force_insert, force_update, using,
                          update_fields)

    def __str__(self):
        return '{}: {}'.format(get_username_by_uid(self), self.title)
