from django.contrib import admin
from tool.models import Card


class CardAdmin(admin.ModelAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'user':
            kwargs['initial'] = request.user.id
        return db_field.formfield(**kwargs)

admin.site.register(Card, CardAdmin)
