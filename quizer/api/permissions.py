from rest_framework import permissions


class IsLecturer(permissions.BasePermission):
    message = "Allow access only for users belong to 'lecturer' group"
    allowed_group = 'lecturer'

    def has_permission(self, request, view):
        return request.user.groups.filter(name=self.allowed_group)


class TestAPIPermission(permissions.BasePermission):
    message = "Allow full access to TestAPI only for users belong to 'lecturer' group. " \
              "For students allowed only get method"
    allowed_group = 'lecturer'

    def has_permission(self, request, view):
        if request.method == 'GET':
            return True
        return request.user.groups.filter(name=self.allowed_group)
