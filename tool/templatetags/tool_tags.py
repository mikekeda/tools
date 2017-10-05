from django.core import serializers
from django.template.defaulttags import register


@register.filter
def get_item(obj: object, k: str):
    return obj.get(str(k)) if isinstance(obj, dict) else getattr(obj, str(k))


@register.filter
def serialize(obj: object):
    return serializers.serialize('json', [obj])[1:-1]
