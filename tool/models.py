from django.db import models
from django.contrib.auth.models import User
from django.conf import settings


class Card(models.Model):
    """Flashcard model"""

    DIFFICULTIES = (
        ('easy', 'Easy'),
        ('middle', 'Middle'),
        ('difficult', 'Difficult'),
    )

    word = models.CharField(max_length=60, unique=True)
    description = models.TextField(blank=True, null=True)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTIES, default='difficult')
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
    Word.add_to_class(lang[0], models.CharField(max_length=60, null=True, blank=True))
