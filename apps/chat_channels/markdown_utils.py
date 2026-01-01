"""
Markdown to HTML conversion utilities for messages.
Supports basic markdown with XSS protection.
"""

import re
import bleach
from django.utils.html import escape


# Allowed HTML tags after markdown conversion
ALLOWED_TAGS = [
    'p', 'br', 'strong', 'em', 'code', 'pre', 'a', 'ul', 'ol', 'li',
    'blockquote', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'del', 'span'
]

ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'target', 'rel'],
    'code': ['class'],
    'pre': ['class'],
    'span': ['class']
}


def convert_markdown_to_html(text):
    """
    Convert markdown text to safe HTML.
    Supports: *bold*, _italic_, `code`, ```code blocks```, links, lists, quotes.
    """
    if not text or not isinstance(text, str):
        return text
    
    # Start with escaped HTML to prevent XSS
    html = escape(text)
    
    # Code blocks (must be done first, before inline code)
    html = re.sub(
        r'```(\w+)?\n(.*?)```',
        lambda m: f'<pre><code class="language-{m.group(1) or "text"}">{m.group(2)}</code></pre>',
        html,
        flags=re.DOTALL
    )
    
    # Inline code
    html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)
    
    # Bold (**text** or __text__)
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'__(.+?)__', r'<strong>\1</strong>', html)
    
    # Italic (*text* or _text_)
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
    html = re.sub(r'(?<!_)_(.+?)_(?!_)', r'<em>\1</em>', html)
    
    # Strikethrough (~~text~~)
    html = re.sub(r'~~(.+?)~~', r'<del>\1</del>', html)
    
    # Links [text](url)
    html = re.sub(
        r'\[([^\]]+)\]\(([^\)]+)\)',
        r'<a href="\2" target="_blank" rel="noopener noreferrer">\1</a>',
        html
    )
    
    # Auto-link URLs (only if not already in <a> tag)
    html = re.sub(
        r'(?<!href=")(https?://[^\s<>"]+)',
        r'<a href="\1" target="_blank" rel="noopener noreferrer">\1</a>',
        html
    )
    
    # Headers (# H1, ## H2, etc.)
    html = re.sub(r'^##### (.+)$', r'<h5>\1</h5>', html, flags=re.MULTILINE)
    html = re.sub(r'^#### (.+)$', r'<h4>\1</h4>', html, flags=re.MULTILINE)
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    
    # Blockquotes (> text)
    html = re.sub(r'^&gt; (.+)$', r'<blockquote>\1</blockquote>', html, flags=re.MULTILINE)
    
    # Unordered lists (- item or * item)
    lines = html.split('\n')
    in_list = False
    result_lines = []
    
    for line in lines:
        if re.match(r'^[\*\-] ', line):
            if not in_list:
                result_lines.append('<ul>')
                in_list = True
            item = re.sub(r'^[\*\-] ', '', line)
            result_lines.append(f'<li>{item}</li>')
        else:
            if in_list:
                result_lines.append('</ul>')
                in_list = False
            result_lines.append(line)
    
    if in_list:
        result_lines.append('</ul>')
    
    html = '\n'.join(result_lines)
    
    # Line breaks
    html = html.replace('\n', '<br>')
    
    # Clean up HTML with bleach for security
    html = bleach.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True
    )
    
    return html


def has_markdown_formatting(text):
    """
    Check if text contains markdown formatting.
    """
    if not text or not isinstance(text, str):
        return False
    
    markdown_patterns = [
        r'\*\*(.+?)\*\*',  # Bold
        r'__(.+?)__',      # Bold
        r'\*(.+?)\*',      # Italic
        r'_(.+?)_',        # Italic
        r'`(.+?)`',        # Code
        r'```',            # Code block
        r'\[.+?\]\(.+?\)', # Link
        r'^#{1,6} ',       # Headers
        r'^&gt; ',         # Blockquote
        r'^[\*\-] ',       # List
        r'~~(.+?)~~',      # Strikethrough
    ]
    
    for pattern in markdown_patterns:
        if re.search(pattern, text, re.MULTILINE):
            return True
    
    return False


def extract_links(text):
    """
    Extract all URLs from text (for link previews).
    """
    if not text:
        return []
    
    # Match markdown links [text](url)
    markdown_links = re.findall(r'\[([^\]]+)\]\(([^\)]+)\)', text)
    urls = [url for _, url in markdown_links]
    
    # Match plain URLs
    plain_urls = re.findall(r'https?://[^\s<>"]+', text)
    urls.extend(plain_urls)
    
    return list(set(urls))  # Remove duplicates
