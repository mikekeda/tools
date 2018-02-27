import datetime

from django import forms
from schedule.models import Event
from easy_select2 import apply_select2, select2_modelform

from .models import Profile, Word, Card, Task, Code

task_form = select2_modelform(Task)


class AvatarForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('avatar',)


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ('title', 'description', 'start', 'end', 'color_event',
                  'rule', 'end_recurring_period')


class WordForm(forms.ModelForm):
    class Meta:
        model = Word
        exclude = ('user',)


class CardForm(forms.ModelForm):
    class Meta:
        model = Card
        exclude = ('user', 'order',)


class FlightsForm(forms.Form):
    origin = forms.CharField(max_length=3, initial='AUS')
    destination = forms.CharField(max_length=3, initial='LWO')
    round_trip = forms.BooleanField(required=False, initial=True)
    date_start = forms.DateField(
        initial=datetime.datetime.today() + datetime.timedelta(days=7))
    date_back = forms.DateField(
        initial=datetime.datetime.today() + datetime.timedelta(days=14))


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        form = task_form
        exclude = ('user', 'weight', 'status', 'resolution', 'progress',
                   'labels')
        widgets = {
            'color': apply_select2(forms.Select),
            'description': forms.Textarea(attrs={'class': 'ckeditor'}),
        }


class CodeForm(forms.ModelForm):
    class Meta:
        model = Code
        exclude = ('user', 'slug')
