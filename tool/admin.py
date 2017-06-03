from django.contrib import admin

from .models import Card, Word
from schedule.models import Event, Calendar
from schedule.admin import EventAdmin


class CardAdmin(admin.ModelAdmin):
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
            calendar = Calendar.objects.filter(slug=request.user.username).first()
            if calendar:
                kwargs['initial'] = calendar.id
        return db_field.formfield(**kwargs)

admin.site.register(Card, CardAdmin)
admin.site.register(Word, WordAdmin)
admin.site.unregister(Event)
admin.site.register(Event, ToolEventAdmin)
