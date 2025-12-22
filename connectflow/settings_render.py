"""
Production settings for Render.com deployment
"""

from .settings import *
import os
import dj_database_url

# Media files - Use Cloudinary for persistent storage on Render
CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME')
CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY')
CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET')

# Debug: Print to logs (will show in Render logs)
print(f"[CLOUDINARY DEBUG] Cloud Name: {CLOUDINARY_CLOUD_NAME}")
print(f"[CLOUDINARY DEBUG] API Key: {CLOUDINARY_API_KEY[:5] if CLOUDINARY_API_KEY else 'NOT SET'}")
print(f"[CLOUDINARY DEBUG] API Secret: {'SET' if CLOUDINARY_API_SECRET else 'NOT SET'}")

if CLOUDINARY_CLOUD_NAME and CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET:
    print("[CLOUDINARY DEBUG] ✅ Configuring Cloudinary storage...")
    
    import cloudinary
    import cloudinary.uploader
    import cloudinary.api
    
    # Configure Cloudinary (get from environment variables)
    cloudinary.config(
        cloud_name=CLOUDINARY_CLOUD_NAME,
        api_key=CLOUDINARY_API_KEY,
        api_secret=CLOUDINARY_API_SECRET,
        secure=True
    )
    
    # Add Cloudinary apps FIRST
    INSTALLED_APPS = list(INSTALLED_APPS)
    # cloudinary_storage must be before django.contrib.staticfiles
    try:
        staticfiles_index = INSTALLED_APPS.index('django.contrib.staticfiles')
        INSTALLED_APPS.insert(staticfiles_index, 'cloudinary_storage')
        INSTALLED_APPS.insert(staticfiles_index, 'cloudinary')
    except ValueError:
        INSTALLED_APPS = ['cloudinary_storage', 'cloudinary'] + INSTALLED_APPS
    
    # Use Cloudinary for media files
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
    
    print(f"[CLOUDINARY DEBUG] ✅ DEFAULT_FILE_STORAGE set to: {DEFAULT_FILE_STORAGE}")
    print(f"[CLOUDINARY DEBUG] ✅ INSTALLED_APPS updated with cloudinary")
    
    # Don't override MEDIA_URL when using Cloudinary
    # Let Cloudinary handle it
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
else:
    print("[CLOUDINARY DEBUG] ❌ Cloudinary NOT configured - using local storage")
    print(f"[CLOUDINARY DEBUG]    Cloud Name: {CLOUDINARY_CLOUD_NAME}")
    print(f"[CLOUDINARY DEBUG]    API Key: {CLOUDINARY_API_KEY}")
    print(f"[CLOUDINARY DEBUG]    API Secret: {'SET' if CLOUDINARY_API_SECRET else 'NOT SET'}")
    
    # Fallback to local storage (development/testing)
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Allowed hosts
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '.onrender.com',  # Render.com domains
    # Add your custom domain here when ready
]

# Database - PostgreSQL (Render provides this automatically)
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Redis for Channels (Render provides this)
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [os.environ.get('REDIS_URL', 'redis://localhost:6379')],
            "capacity": 1500,
            "expiry": 10,
        },
    },
}

# Static files (CSS, JavaScript, Images)
# WhiteNoise for serving static files
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Security settings
SECRET_KEY = os.environ.get('SECRET_KEY', SECRET_KEY)

# HTTPS/SSL settings - Render handles SSL at proxy level
SECURE_SSL_REDIRECT = False  # Render already redirects to HTTPS
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')  # Trust Render's proxy
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
# Disabled HSTS for now to prevent issues during setup
# SECURE_HSTS_SECONDS = 31536000
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True

# CSRF trusted origins
CSRF_TRUSTED_ORIGINS = [
    'https://*.onrender.com',
    # Add your custom domain here
]

# CORS settings (if using separate frontend)
CORS_ALLOWED_ORIGINS = [
    'https://*.onrender.com',
]

# Logging configuration for Render
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'channels': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Cache configuration (use Redis)
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://localhost:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Session configuration (use Redis for sessions)
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
