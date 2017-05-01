from django.contrib import admin

from .models import Card, Word


class CardAdmin(admin.ModelAdmin):
    list_filter = ('user__username',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'user':
            kwargs['initial'] = request.user.id
        return db_field.formfield(**kwargs)


class WordAdmin(CardAdmin):
    search_fields = ['en']

admin.site.register(Card, CardAdmin)
admin.site.register(Word, WordAdmin)
