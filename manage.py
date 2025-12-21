#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    # Auto-detect environment
    if os.environ.get('RENDER'):  # Render.com
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'connectflow.settings_render')
    elif os.environ.get('WEBSITE_SITE_NAME'):  # Azure App Service
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'connectflow.settings_azure')
    elif os.environ.get('RAILWAY_ENVIRONMENT'):  # Railway
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'connectflow.settings_prod')
    else:  # Local development
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'connectflow.settings')
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
