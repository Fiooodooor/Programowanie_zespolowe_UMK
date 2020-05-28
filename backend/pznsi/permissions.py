from rest_framework import permissions


class DeletePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action == 'destroy':
            return request.user.is_superuser
        else:
            return True

