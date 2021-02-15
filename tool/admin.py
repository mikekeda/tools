from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.core.cache import cache
from django.db import models
from easy_select2 import select2_modelform
from import_export.admin import ImportExportModelAdmin
from schedule.admin import EventAdmin
from schedule.models import Calendar, Event

from tool.models import (
    Canvas,
    Card,
    Code,
    Label,
    Link,
    Profile,
    Task,
    Word,
    ShoppingList,
    ShoppingListItem,
    ShoppingItem,
)

User = get_user_model()
ProfileForm = select2_modelform(Profile)


class BaseModelAdmin(ImportExportModelAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """ Prepopulate current user. """
        if db_field.name == "user":
            kwargs["initial"] = request.user.id
        return db_field.formfield(**kwargs)

    def get_changelist_instance(self, request):
        """
        Get all related user usernames and send to the cache,
        we will use it later in __str__ method to improve performance.
        :param request: request object
        :return: `ChangeList` instance based on `request`
        """
        changelist = super().get_changelist_instance(request)
        uids = {instance.user_id for instance in changelist.result_list}
        elements = User.objects.filter(pk__in=uids).values_list("pk", "username")
        cache.set_many(
            {
                "username_by_id_{}".format(element[0]): element[1]
                for element in elements
            },
            settings.USER_ONLINE_TIMEOUT,
        )

        return changelist


class ProfileInline(admin.StackedInline):
    model = Profile
    form = ProfileForm
    max_num = 1


class AuthUserAdmin(UserAdmin):
    inlines = [ProfileInline]


class CardAdmin(BaseModelAdmin):
    list_filter = ("user__username",)


class WordAdmin(CardAdmin):
    search_fields = ["en"]


class ToolEventAdmin(EventAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "creator":
            kwargs["initial"] = request.user.id
        if db_field.name == "calendar":
            calendar = Calendar.objects.filter(slug=request.user.username).first()
            if calendar:
                kwargs["initial"] = calendar.id
        return db_field.formfield(**kwargs)


class TaskAdmin(BaseModelAdmin):
    list_filter = ("user__username",)

    formfield_overrides = {
        models.TextField: {"widget": forms.Textarea(attrs={"class": "ckeditor"})}
    }

    class Media:
        js = ("bower_components/ckeditor/ckeditor.js",)
        css = {"all": ("css/admin-fix.css",)}


class CanvasAdmin(BaseModelAdmin):
    fields = ("user", "preview", "canvas")
    readonly_fields = ("preview",)


class CodeAdmin(BaseModelAdmin):
    fields = ("title", "user", "link_to_code_snippet", "text", "labels")
    readonly_fields = ("link_to_code_snippet",)

    formfield_overrides = {
        models.TextField: {"widget": forms.Textarea(attrs={"class": "ckeditor"})}
    }

    class Media:
        js = (
            "bower_components/ckeditor/ckeditor.js",
            "bower_components/jquery/dist/jquery.min.js",
            "js/code.js",
        )
        css = {"all": ("css/admin-fix.css",)}


class LabelAdmin(BaseModelAdmin):
    search_fields = ("title",)
    list_filter = ("user__username",)


class LinkAdmin(BaseModelAdmin):
    search_fields = ("link",)
    list_filter = ("user__username",)


class ShoppingListItemInline(admin.StackedInline):
    model = ShoppingListItem
    form = select2_modelform(ShoppingListItem)
    extra = 1


class ShoppingListAdmin(BaseModelAdmin):
    inlines = (ShoppingListItemInline,)


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
admin.site.register(Link, LinkAdmin)
admin.site.register(ShoppingList, ShoppingListAdmin)
admin.site.register(ShoppingItem)
