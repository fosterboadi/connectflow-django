from django import template

register = template.Library()

@register.filter
def lookup(dictionary, key):
    '''
    Template filter to get dictionary value by key.
    Usage: {{ mydict|lookup:mykey }}
    '''
    if dictionary is None:
        return None
    # Convert UUID to string if needed
    key = str(key)
    return dictionary.get(key, '')
