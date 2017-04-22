from django.contrib import admin

from .models import Card, Word


class CardAdmin(admin.ModelAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'user':
            kwargs['initial'] = request.user.id
        return db_field.formfield(**kwargs)

admin.site.register(Card, CardAdmin)
admin.site.register(Word, CardAdmin)
