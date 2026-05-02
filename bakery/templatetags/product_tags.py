from django import template

register = template.Library()

@register.filter
def split(value, key):
    """Разделяет строку по указанному разделителю."""
    if not value:
        return []
    return [tag.strip() for tag in str(value).split(key)]
