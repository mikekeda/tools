from django.template.defaulttags import register


@register.filter
def get_item(obj, k: str):
    return obj.get(str(k)) if isinstance(obj, dict) else getattr(obj, str(k))
