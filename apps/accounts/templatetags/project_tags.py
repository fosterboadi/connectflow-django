from django import template

register = template.Library()

@register.simple_tag
def calculate_completion(milestones):
    if not milestones:
        return 0
    total = milestones.count()
    completed = milestones.filter(is_completed=True).count()
    return int((completed / total) * 100)

@register.filter
def get_item(dictionary, key):
    if not dictionary:
        return None
    return dictionary.get(key)

@register.filter
def has_module_access(user, module_name):
    """Check if user has access to a module."""
    if not user or not user.is_authenticated:
        return True # Or False depending on your default
    
    # If it's a SUPER_ADMIN, always True
    if hasattr(user, 'role') and user.role == 'SUPER_ADMIN':
        return True
        
    if hasattr(user, 'has_module_access'):
        return user.has_module_access(module_name)
        
    return True
