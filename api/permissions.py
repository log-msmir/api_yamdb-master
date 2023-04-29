from rest_framework import permissions

from .mixins import UserStatusMixin


class ReviewPermission(permissions.BasePermission, UserStatusMixin):

    def has_permission(self, request, view):
        if view.action in ['list', 'retrieve']:
            return True
        elif view.action == 'create':
            return self.is_authenticated(request)
        else:
            return True

    def has_object_permission(self, request, view, obj):
        if view.action in ['update', 'destroy']:
            if self.is_staff(request):
                return True
            elif request.user == obj.author:
                return True
            else:
                return False


class CommentPermission(permissions.BasePermission, UserStatusMixin):

    def has_permission(self, request, view):
        if view.action in ['list', 'retrieve']:
            return True
        elif view.action == 'create':
            return self.is_authenticated(request)
        else:
            return True

    def has_object_permission(self, request, view, obj):
        if view.action in ['update', 'destroy']:
            if self.is_staff(request):
                return True
            elif request.user == obj.author:
                return True
            else:
                return False


class UserPermission(permissions.BasePermission, UserStatusMixin):

    def has_permission(self, request, view):
        #Всегда возвращает 403 Оо
        if view.action in ['list', 'create']:
            return self.is_admin(request)
        if view.action == 'user_retrieve':
            return self.is_authenticated(request)
        else:
            return True

    def has_object_permission(self, request, view, obj):
        if view.action in ['admin_update', 'destroy', 'admin_retrieve']:
            return self.is_admin(request)
        if view.action == 'user_update':
            return self.is_authenticated(request)


class CategoryPermission(permissions.BasePermission, UserStatusMixin):

    def has_permission(self, request, view):
        if view.action == 'list':
            return True
        elif view.action in ['create', 'destroy']:
            return self.is_admin(request)
        else:
            return True


class GenrePermission(permissions.BasePermission, UserStatusMixin):

    def has_permission(self, request, view):
        if view.action == 'list':
            return True
        elif view.action in ['create', 'destroy']:
            return self.is_admin(request)
        else:
            return True


class TitlePermission(permissions.BasePermission, UserStatusMixin):

    def has_permission(self, request, view):
        if view.action == 'list':
            return True
        if view.action == 'create':
            return self.is_admin(request)
        else:
            return True

    def has_object_permission(self, request, view, obj):
        if view.action in ['update', 'destroy']:
            return self.is_admin(request)
