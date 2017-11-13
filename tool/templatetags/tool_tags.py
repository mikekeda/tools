from django.core import serializers
from django.template.defaulttags import register


@register.filter
def get_item(obj: object, k: str):
    """Template tag to get object field value or dict value."""
    if isinstance(obj, dict):
        return obj.get(str(k))
    return getattr(obj, str(k), None)


@register.filter
def serialize(obj: object):
    return serializers.serialize('json', [obj])[1:-1]
