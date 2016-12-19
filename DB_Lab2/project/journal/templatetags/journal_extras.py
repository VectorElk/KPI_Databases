from django import template

register = template.Library()


@register.filter()
def object_id(dict):
    return dict['_id']