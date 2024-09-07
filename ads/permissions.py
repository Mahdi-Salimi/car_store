from rest_framework import permissions

class IsSellerPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='seller').exists()

    def has_object_permission(self, request, view, obj):
        # Only the seller who created the ad can update or delete it
        return obj.seller == request.user
