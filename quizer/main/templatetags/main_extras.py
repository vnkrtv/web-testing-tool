# pylint: disable=invalid-name
"""Custom template tags"""
from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag
def sort_icon():
    """Sort icon source"""
    return '/static/main/images/sort.svg'


@register.simple_tag
def team_icon():
    """Team icon source"""
    return '/static/main/images/team.svg'


@register.simple_tag
def clock_icon():
    """Clock icon source"""
    return '/static/main/images/clock.svg'


@register.simple_tag
def task_icon():
    """Task icon source"""
    return '/static/main/images/task.svg'
