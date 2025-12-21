from django import template

register = library = template.Library()

@register.simple_tag
def calculate_completion(milestones):
    if not milestones:
        return 0
    total = milestones.count()
    completed = milestones.filter(is_completed=True).count()
    return int((completed / total) * 100)
