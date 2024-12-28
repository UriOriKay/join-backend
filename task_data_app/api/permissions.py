from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsOwnerOAdmin(BasePermission):
    """
    Custom permission class to allow access to object owners or superusers.

    Methods
    -------
    has_object_permission(request, view, obj)
        Determines if the user has permission to access or modify the object.
    """
    def has_object_permission(self, request, view, obj):
        """
        Determines if the user has permission to access or modify the object.

        Parameters
        ----------
        request : rest_framework.request.Request
            The HTTP request being processed.
        view : rest_framework.views.APIView
            The view handling the request.
        obj : model instance
            The object being accessed or modified.

        Returns
        -------
        bool
            `True` if the request is safe (read-only) or if the user is a superuser
            or the owner of the object; otherwise, `False`.
        """
        if request.method in SAFE_METHODS:
            return True
        else:
            return bool(request.user and request.user.is_superuser or request.user.email == obj.email)
