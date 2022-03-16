from rest_framework import permissions


class BoardPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action in ["create", "retrieve", "update", "destroy"]:
            return request.user.is_authenticated
        elif view.action in ["list"]:
            return True
        else:
            return False
