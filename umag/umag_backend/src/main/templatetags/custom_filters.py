# src/main/templatetags/custom_filters.py

from django import template

register = template.Library()

@register.filter(name='get_item')
def get_item(dictionary, key):
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None
@register.filter(name='get_verbose_name')
def get_verbose_name(field_name, data):
    model_name = data.get('type')
    if model_name:
        model = register.get_model('main', model_name)
        if model:
            field = model._meta.get_field(field_name)
            if field:
                return field.verbose_name
    return field_name