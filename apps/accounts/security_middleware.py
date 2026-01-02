"""
Security middleware for ConnectFlow Pro
Adds additional security headers and validations
"""
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware:
    """
    Add additional security headers to all responses.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Only add headers if not in DEBUG mode
        if not settings.DEBUG:
            # Prevent clickjacking
            if 'X-Frame-Options' not in response:
                response['X-Frame-Options'] = 'DENY'
            
            # Prevent MIME type sniffing
            response['X-Content-Type-Options'] = 'nosniff'
            
            # Enable XSS protection
            response['X-XSS-Protection'] = '1; mode=block'
            
            # Referrer policy
            response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
            
            # Permissions policy (formerly Feature Policy)
            response['Permissions-Policy'] = 'geolocation=(), microphone=(self), camera=(self)'
        
        return response


class SQLiteProductionCheckMiddleware:
    """
    Prevent accidental use of SQLite in production.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Check on startup
        if not settings.DEBUG:
            db_engine = settings.DATABASES['default']['ENGINE']
            if 'sqlite' in db_engine.lower():
                logger.critical("CRITICAL: SQLite detected in production! Use PostgreSQL.")
                raise RuntimeError(
                    "SQLite is not allowed in production. "
                    "Please configure PostgreSQL via DATABASE_URL environment variable."
                )

    def __call__(self, request):
        return self.get_response(request)
