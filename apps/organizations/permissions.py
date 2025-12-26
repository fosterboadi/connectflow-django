from rest_framework import permissions

class HasSubscriptionFeature(permissions.BasePermission):
    """
    Scale-Ready Permission:
    Checks if the Organization has a specific feature enabled in their plan.
    Usage: permission_classes = [HasSubscriptionFeature('has_analytics')]
    """
    
    def __init__(self, feature_name):
        self.feature_name = feature_name

    def __call__(self):
        # This allows us to pass arguments to the permission class
        return self

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
            
        # Super Admins bypass all checks
        if request.user.role == 'SUPER_ADMIN':
            return True
            
        if not request.user.organization:
            return False
            
        return request.user.organization.has_feature(self.feature_name)

class CanAddMoreUsers(permissions.BasePermission):
    """
    Permission to check if the organization can still add more users.
    """
    def has_permission(self, request, view):
        if request.method != 'POST':
            return True
            
        if not request.user.organization:
            return False
            
        return request.user.organization.can_add_user()
