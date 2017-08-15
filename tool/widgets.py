from django import forms
from django.conf import settings


class ColorWidget(forms.TextInput):
    class Media:
        js = (
            settings.STATIC_URL + 'bower_components/jscolor-picker/jscolor.min.js',
        )

    def __init__(self, language=None, attrs=None):
        self.language = language or settings.LANGUAGE_CODE[:2]
        super(ColorWidget, self).__init__(attrs=attrs)

    def render(self, name, value, attrs=None):
        self.attrs = {'class': 'jscolor'}
        return super(ColorWidget, self).render(name, value, attrs)
