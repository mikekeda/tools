from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.db import models

from easy_select2 import select2_modelform
from schedule.models import Event, Calendar
from schedule.admin import EventAdmin
from import_export.admin import ImportExportModelAdmin

from .models import Profile, Card, Word, Task, Canvas, Code, Label

User = get_user_model()
ProfileForm = select2_modelform(Profile)


class ProfileInline(admin.StackedInline):
    model = Profile
    form = ProfileForm
    max_num = 1


class AuthUserAdmin(UserAdmin):
    inlines = [ProfileInline]


class CardAdmin(ImportExportModelAdmin):
    list_filter = ('user__username',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'user':
            kwargs['initial'] = request.user.id
        return db_field.formfield(**kwargs)


class WordAdmin(CardAdmin):
    search_fields = ['en']


class ToolEventAdmin(EventAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'creator':
            kwargs['initial'] = request.user.id
        if db_field.name == 'calendar':
            calendar = Calendar.objects.filter(
                slug=request.user.username
            ).first()
            if calendar:
                kwargs['initial'] = calendar.id
        return db_field.formfield(**kwargs)


class TaskAdmin(ImportExportModelAdmin):
    list_filter = ('user__username',)

    formfield_overrides = {
        models.TextField: {
            'widget': forms.Textarea(attrs={'class': 'ckeditor'})
        }
    }

    class Media:
        js = ('bower_components/ckeditor/ckeditor.js',)
        css = {'all': ('css/admin-fix.css',)}

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'user':
            kwargs['initial'] = request.user.id

        return db_field.formfield(**kwargs)


class CanvasAdmin(ImportExportModelAdmin):
    fields = ('user', 'preview', 'canvas')
    readonly_fields = ('preview',)


class CodeAdmin(ImportExportModelAdmin):
    fields = ('title', 'user', 'link_to_code_snippet', 'text')
    readonly_fields = ('link_to_code_snippet',)

    formfield_overrides = {
        models.TextField: {
            'widget': forms.Textarea(attrs={'class': 'ckeditor'})
        }
    }

    class Media:
        js = (
            'bower_components/ckeditor/ckeditor.js',
            'bower_components/jquery/dist/jquery.min.js',
            'js/code.js'
        )
        css = {'all': ('css/admin-fix.css',)}

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'user':
            kwargs['initial'] = request.user.id
        return db_field.formfield(**kwargs)


class LabelAdmin(ImportExportModelAdmin):
    search_fields = ('title',)
    list_filter = ('user__username',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'user':
            kwargs['initial'] = request.user.id
        return db_field.formfield(**kwargs)


admin.site.register(Card, CardAdmin)
admin.site.register(Word, WordAdmin)
admin.site.unregister(Event)
admin.site.register(Event, ToolEventAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(Canvas, CanvasAdmin)
admin.site.register(Code, CodeAdmin)
admin.site.unregister(User)
admin.site.register(User, AuthUserAdmin)
admin.site.register(Label, LabelAdmin)
