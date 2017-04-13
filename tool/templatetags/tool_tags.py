from django.template.defaulttags import register


@register.filter
def get_item(obj, key):
    return getattr(obj, key)
