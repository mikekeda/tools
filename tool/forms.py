from django import forms
from schedule.models import Event

from .models import Word, Card


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ('title', 'description', 'start', 'end', 'color_event', )


class WordForm(forms.ModelForm):
    class Meta:
        model = Word
        exclude = ('user',)


class CardForm(forms.ModelForm):
    class Meta:
        model = Card
        exclude = ('user', 'order',)
