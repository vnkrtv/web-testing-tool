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


@register.simple_tag
def person_icon():
    """Person icon source"""
    return '/static/main/images/person.svg'


@register.simple_tag
def logout_icon():
    """Logout icon source"""
    return '/static/main/images/logout.svg'


@register.simple_tag
def wait_icon():
    """Wait icon source"""
    return '/static/main/images/wait.svg'


@register.simple_tag
def research_icon():
    """Research icon source"""
    return '/static/main/images/research.svg'


@register.simple_tag
def add_test_icon():
    """Add test icon source"""
    return '/static/main/images/add-test.svg'


@register.simple_tag
def edit_icon():
    """Edit test icon source"""
    return '/static/main/images/edit.svg'


@register.simple_tag
def user_icon():
    """User icon source"""
    return '/static/main/images/user.svg'


@register.simple_tag
def subject_icon():
    """Subject icon source"""
    return '/static/main/images/subject.svg'
