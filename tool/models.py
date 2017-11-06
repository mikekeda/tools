import datetime
import string
import random
import pytz

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator

from .widgets import ColorWidget

TIMEZONES = [
    (tz, tz + ' ' + datetime.datetime.now(pytz.timezone(tz)).strftime('%z'))
    for tz in pytz.common_timezones
]

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


class ColorField(models.CharField):
    """Color field"""

    def formfield(self, **kwargs):
        kwargs['widget'] = ColorWidget
        return super(ColorField, self).formfield(**kwargs)


class Profile(models.Model):
    """Profile model"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name='profile'
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

    def __str__(self):
        return u'%s' % (
            self.user.username,
        )


for i, default_color in enumerate(default_palette_colors, 1):
    Profile.add_to_class(
        'palette_color_' + str(i),
        ColorField(max_length=6, default=default_color)
    )


class Card(models.Model):
    """Flashcard model"""
    DIFFICULTIES = (
        ('easy', 'Easy'),
        ('middle', 'Medium'),
        ('difficult', 'Difficult'),
    )

    word = models.CharField(max_length=60, unique=True)
    description = models.TextField(blank=True, null=True)
    difficulty = models.CharField(
        max_length=10,
        choices=DIFFICULTIES,
        default='difficult'
    )
    user = models.ForeignKey(User, related_name='cards')
    order = models.PositiveSmallIntegerField(default=0)
    created_date = models.DateTimeField(auto_now_add=True)
    changed_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return u'%s' % (
            self.word,
        )


class Word(models.Model):
    """Word model"""
    user = models.ForeignKey(User, related_name='words')
    created = models.DateTimeField(auto_now_add=True)
    changed = models.DateTimeField(auto_now=True)

    def __str__(self):
        return u'%s' % (
            self.en,
        )


for lang in settings.LANGUAGES:
    Word.add_to_class(
        lang[0],
        models.CharField(max_length=60, null=True, blank=True)
    )


class Task(models.Model):
    """Task model"""
    STATUSES = (
        ('todo', 'TODO'),
        ('doing', 'Doing'),
        ('done', 'Done'),
    )

    title = models.CharField(max_length=60, unique=True)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUSES, default='todo')
    color = models.PositiveSmallIntegerField(
        default=1,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(len(default_palette_colors))
        ]
    )
    user = models.ForeignKey(User, related_name='tasks')
    weight = models.SmallIntegerField(default=0)
    created_date = models.DateTimeField(auto_now_add=True)
    changed_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return u'%s' % (
            self.title,
        )


class Canvas(models.Model):
    """Canvas model"""
    user = models.ForeignKey(User, related_name='canvases')
    canvas = models.TextField(blank=True, null=True)
    slug = models.CharField(max_length=10, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    changed = models.DateTimeField(auto_now=True)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        need_slug = not self.pk
        super(Canvas, self).save(force_insert, force_update,
                                 using, update_fields)
        if need_slug:
            self.slug = ''.join(random.sample(_char_map, 3)) +\
                        number_to_chars(self.pk)
            self.save()

    def preview(self):
        return u'<img src="{}" />'.format(self.canvas)

    preview.short_description = 'Image'
    preview.allow_tags = True

    def __str__(self):
        return u'%s' % (
            '{}: {}'.format(self.user.username, self.pk)
        )
