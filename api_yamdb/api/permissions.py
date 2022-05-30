from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Разрешает доступ только администратору и суперадминистратору Django."""
    message = 'Это действие доступно только администратору.'

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class IsAdminOrReadOnly(permissions.BasePermission):
    """Разрешает доступ к безопасным методам (чтение) авторизованным
    пользователям, администратору и суперадминистратору Django -
    ко всем прочим."""
    message = 'Только администратор может изменять этот объект.'

    def has_permission(self, request, view):
        return ((request.method in permissions.SAFE_METHODS)
                or (request.user.is_authenticated
                    and request.user.is_admin))


class IsOwnerModeratorAdminOrReadOnly(permissions.BasePermission):
    """Разрешает доступ к безопасным методам (чтение) всем пользователям,
    автору, модератору, администратору и суперадминистратору Django -
    ко всем прочим."""
    message = ('Только автор, модератор или администратор '
               'может изменять этот объект.')

    def has_permission(self, request, view):
        return (request.user.is_authenticated
                or request.method in permissions.SAFE_METHODS)

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user
                or request.user.is_admin
                or request.user.is_moderator)
