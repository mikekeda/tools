from django import forms
from schedule.models import Event
import datetime

from .models import Profile, Word, Card


class AvatarForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('avatar',)


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


class FlightsForm(forms.Form):
    origin = forms.CharField(
        max_length=3,
        initial='AUS')
    destination = forms.CharField(
        max_length=3,
        initial='LWO')
    round_trip = forms.BooleanField(
        required=False,
        initial=True)
    date_start = forms.DateField(
        initial=datetime.datetime.today() + datetime.timedelta(days=7))
    date_back = forms.DateField(
        initial=datetime.datetime.today() + datetime.timedelta(days=14))
