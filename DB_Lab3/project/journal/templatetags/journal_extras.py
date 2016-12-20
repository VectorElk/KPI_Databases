from django import template

register = template.Library()


@register.filter()
def object_id(dict):
    return dict['_id']


@register.filter()
def score(dict):
    return dict['number']


@register.filter()
def value(dict):
    return dict['value']


@register.filter()
def count(dict):
    return dict['count']