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

@register.filter
def format_mb(value):
    """Converts MB to bytes and uses filesizeformat."""
    try:
        from django.template.defaultfilters import filesizeformat
        # 1 MB = 1048576 bytes
        return filesizeformat(int(value) * 1048576)
    except (ValueError, TypeError):
        return value

@register.filter
def replace_string(value, arg):
    """Replaces a string with another. Usage: {{ val|replace_string:"old,new" }}"""
    if ',' not in arg:
        return value
    old, new = arg.split(',', 1)
    return value.replace(old, new)

@register.filter
def float_sub(value, arg):
    """Subtracts the arg from the value."""
    try:
        return round(float(value) - float(arg), 2)
    except (ValueError, TypeError):
        return value

@register.simple_tag(takes_context=True)
def define_var(context, name, value):
    context[name] = value
    return ''
