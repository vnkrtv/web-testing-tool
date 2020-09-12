from rest_framework import permissions


class IsLecturer(permissions.BasePermission):
    message = "Allow access only for users belong to 'lecturer' group"
    allowed_group = 'lecturer'

    def has_permission(self, request, view):
        return request.user.groups.filter(name=self.allowed_group)
