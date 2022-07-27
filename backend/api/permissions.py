from rest_framework.permissions import BasePermission


class RecipesPermissions(BasePermission):
    def has_permission(self, request, view):
        if view.action in ['list', 'retrieve']:
            return True
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if view.action == 'retrieve':
            return True
        if view.action in ['partial_update', 'destroy']:
            return request.user == obj.author or request.user.is_superuser
        return False
