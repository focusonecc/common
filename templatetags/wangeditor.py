from django import template
from django.utils.safestring import mark_safe


register = template.Library()


@register.filter(name='py2js')
def py2js(value):
    if isinstance(value, bool):
        return str(value).lower()
    elif isinstance(value, str):
        return mark_safe('"{}"'.format(value))
    else:
        return mark_safe(value)
