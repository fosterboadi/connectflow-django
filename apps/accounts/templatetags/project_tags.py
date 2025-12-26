from django import template

register = library = template.Library()

@register.simple_tag
def calculate_completion(milestones):
    if not milestones:
        return 0
    total = milestones.count()
    completed = milestones.filter(is_completed=True).count()
    return int((completed / total) * 100)

@register.filter(name='get_item')
def get_item(dictionary, key):
    if not dictionary:
        return None
    return dictionary.get(key)

@register.filter(name='has_module_access')
def has_module_access(user, module_name):
    if not hasattr(user, 'has_module_access'):
        return True
    return user.has_module_access(module_name)
