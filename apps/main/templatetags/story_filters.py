from django import template
from django.utils.html import strip_tags

register = template.Library()

@register.filter
def div(value, divisor):
    """Divides value by divisor and returns the integer result."""
    try:
        return int(value) // int(divisor)
    except (ValueError, ZeroDivisionError):
        return 0

@register.filter
def wordcount(value):
    """Counts words in the given text, stripping HTML tags."""
    return len(strip_tags(value).split())