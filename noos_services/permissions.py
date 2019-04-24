"""
Sets permission for the API (ONLY)
"""
from rest_framework import permissions
# TODO: Add restriction to users (get token, refresh token, verify token, post request)


class IsReadOnly(permissions.DjangoModelPermissions):
    """
    Custom permission to only allow reading.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True


class IsOwnerOrReadOnly(permissions.DjangoModelPermissions):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the snippet.
        return obj.user == request.user


class IsOwner(permissions.DjangoModelPermissions):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):

        # Permissions are only allowed to the owner of the snippet.
        return obj.user == request.user
