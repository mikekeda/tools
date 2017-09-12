from django.template.defaulttags import register


@register.filter
def get_item(obj, key: str):
    return obj.get(str(key)) if isinstance(obj, dict) else getattr(obj, str(key))
