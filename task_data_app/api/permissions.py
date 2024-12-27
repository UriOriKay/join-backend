from rest_framework.permissions import BasePermission, SAFE_METHODS
class IsStafforReadOnly(BasePermission):
    def has_permission(self, request, view):
        is_staff = request.user and request.user.is_staff
        return request.method in SAFE_METHODS
    
class IsAdminForDeleteOrPatchAndReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        elif request.method == 'DELETE':
            return bool(request.user and request.user.is_superuser)
        else:
            return bool(request.user and request.user.is_staff)

class IsOwnerOAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        else:
            return bool(request.user and request.user.is_superuser or request.user.email == obj.email)
