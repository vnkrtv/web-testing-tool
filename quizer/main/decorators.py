# pylint: disable=import-error, no-else-return
"""
Decorators for differentiate user rights
"""
from django.shortcuts import redirect, reverse


def unauthenticated_user(view_func):
    """
    Checked if user is authorized
    """

    def wrapper_func(request, *args, **kwargs):
        if request.path == "/ws_running_tests/":
            return view_func(request, *args, **kwargs)
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        else:
            return redirect(reverse("main:login_page"))

    return wrapper_func


def allowed_users(allowed_roles: list):
    """
    Checked if user belong to allowed group

    :param allowed_roles: 'student', 'lecturer' or 'superuser')
    """

    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            if request.path == "/ws_running_tests/":
                return view_func(request, *args, **kwargs)

            is_allowed = False
            for group in allowed_roles:
                if request.user.groups.filter(name=group):
                    is_allowed = True

            if "admin" in allowed_roles:
                if request.user.is_authenticated:
                    is_allowed = True

            if is_allowed:
                return view_func(request, *args, **kwargs)
            else:
                return redirect(reverse("main:available_tests"))

        return wrapper_func

    return decorator


def post_method(view_func):
    """
    Redirect to '/available_tests' page if method is not 'post'
    """

    def wrapper_func(request, *args, **kwargs):
        if request.method != "POST":
            return redirect(reverse("main:available_tests"))
        else:
            return view_func(request, *args, **kwargs)

    return wrapper_func
