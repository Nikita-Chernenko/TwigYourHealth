import json

from django import template
from django.core.serializers.json import DjangoJSONEncoder

register = template.Library()


@register.filter('json')
def as_json(value):
    return json.dumps(value, cls=DjangoJSONEncoder)
