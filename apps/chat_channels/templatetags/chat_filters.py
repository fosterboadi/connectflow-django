import os
import re
from django import template

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
    return has_emojis and not text_without_emoji and len(text) <= 20  # Max 20 chars for emoji-only

@register.filter
def emoji_count(value):
    """Count number of emojis in text."""
    if not value:
        return 0
    
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"
        "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF"
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "\U0001F900-\U0001F9FF"
        "\U0001FA00-\U0001FA6F"
        "\U00002600-\U000026FF"
        "\U00002700-\U000027BF"
        "\U0001F191-\U0001F19A"
        "]+", 
        flags=re.UNICODE
    )
    
    matches = emoji_pattern.findall(str(value))
    return len(matches)
