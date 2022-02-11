from django.template import Library
from tracer import models
from django.shortcuts import reverse

register = Library()


@register.simple_tag
def string_just(num):
    """check if the id of issue is less than 100, if so, add a 0 in front of it"""
    if num < 100:
        num = str(num).rjust(3, '0')

    return f'#{num}'


@register.simple_tag
def get_issue_type_color(issue_type):
    """get the color of the issue typ ['Task', 'Bug', 'Feature']"""
    color_dict = {'Task': '#DB4437', 'Feature': '#F4B400', 'Bug': '#0F9D58'}
    return color_dict[issue_type]
