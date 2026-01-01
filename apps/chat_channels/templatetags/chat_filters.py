import os
import re
from django import template
from datetime import datetime, timedelta
from django.utils import timezone

register = template.Library()

@register.filter
def basename(value):
    """Return the basename of a file path."""
    if not value:
        return ''
    return os.path.basename(str(value))

@register.filter
def file_extension(value):
    """Return the file extension."""
    if not value:
        return ''
    name = str(value)
    _, ext = os.path.splitext(name)
    return ext.lower()

@register.filter
def is_image(value):
    """Check if file is an image based on extension."""
    ext = file_extension(value)
    return ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg']

@register.filter
def is_emoji_only(value):
    """Check if message contains only emojis (like WhatsApp)."""
    if not value or not isinstance(value, str):
        return False
    
    # Remove whitespace
    text = value.strip()
    if not text:
        return False
    
    # Emoji regex pattern - matches most Unicode emoji ranges
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002702-\U000027B0"  # dingbats
        "\U000024C2-\U0001F251"
        "\U0001F900-\U0001F9FF"  # supplemental symbols
        "\U0001FA00-\U0001FA6F"  # extended symbols
        "\U00002600-\U000026FF"  # miscellaneous symbols
        "\U00002700-\U000027BF"  # dingbats
        "\U0001F191-\U0001F19A"  # enclosed characters
        "]+", 
        flags=re.UNICODE
    )
    
    # Remove all emojis and whitespace
    text_without_emoji = emoji_pattern.sub('', text).strip()
    
    # If nothing remains and we had emojis, it's emoji-only
    has_emojis = bool(emoji_pattern.search(text))
    return has_emojis and not text_without_emoji

@register.filter
def emoji_count(value):
    """Count number of emojis in text."""
    if not value or not isinstance(value, str):
        return 0
    
    # Use the same logic as is_emoji_only but count matches
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002702-\U000027B0"  # dingbats
        "\U000024C2-\U0001F251"
        "\U0001F900-\U0001F9FF"  # supplemental symbols
        "\U0001FA00-\U0001FA6F"  # extended symbols
        "\U00002600-\U000026FF"  # miscellaneous symbols
        "\U00002700-\U000027BF"  # dingbats
        "\U0001F191-\U0001F19A"  # enclosed characters
        "]", 
        flags=re.UNICODE
    )
    
    return len(emoji_pattern.findall(value))

@register.filter
def format_date_separator(value):
    """
    Format date for message separators (like WhatsApp/Slack).
    Returns 'Today', 'Yesterday', or formatted date.
    """
    if not value:
        return ''
    
    # Ensure we're working with a date object
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace('Z', '+00:00'))
        except:
            return value
    
    # Make timezone-aware if needed
    if timezone.is_naive(value):
        value = timezone.make_aware(value)
    
    now = timezone.now()
    today = now.date()
    yesterday = today - timedelta(days=1)
    message_date = value.date()
    
    if message_date == today:
        return 'Today'
    elif message_date == yesterday:
        return 'Yesterday'
    else:
        # Format as "Monday, Jan 1" or "Jan 1, 2026" if different year
        if message_date.year == today.year:
            return value.strftime('%A, %b %d')
        else:
            return value.strftime('%b %d, %Y')

@register.filter
def get_item(dictionary, key):
    """
    Get item from dictionary using key.
    Usage: {{ mydict|get_item:mykey }}
    """
    if not dictionary:
        return None
    return dictionary.get(key)
