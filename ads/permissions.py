from rest_framework import permissions

import logging
logger = logging.getLogger(__name__)

class IsSellerPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        if not request.user.is_authenticated:
            logger.warning('Unauthenticated user tried to access seller endpoint')
            return False

        if request.user.user_type != 's':
            logger.warning(f'User {request.user} is not a seller')
            return False

        return True

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if obj.seller != request.user:
            logger.warning(f'User {request.user} tried to access another seller\'s ad')
            return False

        return True


