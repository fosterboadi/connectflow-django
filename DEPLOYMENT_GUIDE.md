# ConnectFlow Pro - Deployment Guide
## Free Platform Deployment with CI/CD

**Created:** December 21, 2025 @ 04:09 AM  
**Project:** ConnectFlow Pro (Django + Channels + WebSockets)

---

## 🎯 Recommended Platform: **Railway.app** (Best for Django + WebSockets)

**Why Railway?**
- ✅ **Free Tier:** $5/month credit (enough for development)
- ✅ **WebSocket Support:** Native support for Django Channels
- ✅ **PostgreSQL Included:** Free database
- ✅ **Redis Included:** For Channels layer
- ✅ **Automatic Deployments:** GitHub integration
- ✅ **Easy Setup:** One-click deploy
- ✅ **SSL/HTTPS:** Automatic certificates
- ✅ **Custom Domain:** Free subdomain + custom domain support

**Alternative Platforms:**
1. **Render.com** - Good for Django, supports WebSockets
2. **Fly.io** - Good performance, supports WebSockets
3. **PythonAnywhere** - Easy but limited WebSocket support
4. **Heroku** - Used to be free, now paid only

---

## 📋 Pre-Deployment Checklist

### **1. Update Project Files**

#### **Create `Procfile`** (for Railway/Render)
```procfile
web: daphne -b 0.0.0.0 -p $PORT connectflow.asgi:application
worker: python manage.py runworker channels
```

#### **Create `runtime.txt`**
```
python-3.11.9
```

#### **Update `requirements.txt`**
```bash
# Generate updated requirements
pip freeze > requirements.txt
```

Make sure it includes:
```
Django==5.2.9
channels==4.2.1
daphne==4.2.1
channels-redis==4.2.1
psycopg2-binary==2.9.9
gunicorn==21.2.0
whitenoise==6.6.0
redis==5.0.1
Pillow==10.1.0
```

#### **Create `railway.json`** (Railway specific)
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "daphne -b 0.0.0.0 -p $PORT connectflow.asgi:application",
    "healthcheckPath": "/",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

---

## 🚀 Deployment Steps (Railway.app)

### **Step 1: Prepare Django Settings**

Create `connectflow/settings_prod.py`:

```python
from .settings import *

# Production settings
DEBUG = False
ALLOWED_HOSTS = [
    '.railway.app',
    'connectflow-pro.up.railway.app',
    # Add your custom domain later
]

# Database - PostgreSQL (Railway provides this)
import dj_database_url
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600
    )
}

# Redis for Channels (Railway provides this)
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [os.environ.get('REDIS_URL', 'redis://localhost:6379')],
        },
    },
}

# Static files with WhiteNoise
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files (use Railway Volumes or AWS S3)
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# CSRF trusted origins
CSRF_TRUSTED_ORIGINS = [
    'https://*.railway.app',
    # Add your custom domain later
]

# Secret key from environment
SECRET_KEY = os.environ.get('SECRET_KEY', SECRET_KEY)
```

### **Step 2: Update `manage.py`**

```python
#!/usr/bin/env python
import os
import sys

def main():
    # Use production settings if RAILWAY_ENVIRONMENT is set
    if os.environ.get('RAILWAY_ENVIRONMENT'):
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'connectflow.settings_prod')
    else:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'connectflow.settings')
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
```

### **Step 3: Update `asgi.py`**

```python
import os
from django.core.asgi import get_asgi_application

# Use production settings if RAILWAY_ENVIRONMENT is set
if os.environ.get('RAILWAY_ENVIRONMENT'):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'connectflow.settings_prod')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'connectflow.settings')

django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import apps.chat_channels.routing

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            apps.chat_channels.routing.websocket_urlpatterns
        )
    ),
})
```

### **Step 4: Create `.gitignore`**

```gitignore
# Python
*.pyc
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# Django
*.log
db.sqlite3
db.sqlite3-journal
/media
/staticfiles
.env

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
```

### **Step 5: Push to GitHub**

```bash
# Initialize git (if not already)
git init

# Add all files
git add .

# Commit
git commit -m "Prepare for Railway deployment"

# Create GitHub repo and push
git remote add origin https://github.com/yourusername/connectflow-django.git
git branch -M main
git push -u origin main
```

---

## 🎯 Deploy on Railway

### **Option A: Quick Deploy (Recommended)**

1. **Go to Railway.app**
   - Visit: https://railway.app
   - Sign up with GitHub

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your `connectflow-django` repository

3. **Add Services**
   - Railway will auto-detect Django
   - Click "Add PostgreSQL" (free)
   - Click "Add Redis" (free)

4. **Set Environment Variables**
   ```
   DJANGO_SETTINGS_MODULE=connectflow.settings_prod
   SECRET_KEY=your-super-secret-key-here-generate-new-one
   ALLOWED_HOSTS=.railway.app
   DEBUG=False
   ```

5. **Deploy**
   - Railway will automatically deploy
   - Wait for build to complete (~5 minutes)

6. **Run Migrations**
   - In Railway dashboard, click your service
   - Go to "Settings" → "Custom Start Command"
   - Or use Railway CLI:
   ```bash
   railway run python manage.py migrate
   railway run python manage.py createsuperuser
   railway run python manage.py collectstatic --noinput
   ```

7. **Access Your App**
   - Click "Deployments" → Latest deployment
   - Copy the Railway URL (e.g., `https://connectflow-pro.up.railway.app`)
   - Visit the URL!

---

## 🔧 Post-Deployment Configuration

### **1. Create Superuser**

```bash
# Using Railway CLI
railway run python manage.py createsuperuser

# Or in Railway dashboard
# Settings → Variables → Add custom start command
```

### **2. Collect Static Files**

```bash
railway run python manage.py collectstatic --noinput
```

### **3. Set Up Media Files**

**Option A: Railway Volume (Simple)**
```bash
# In Railway dashboard
# Add Volume → Mount at /app/media
```

**Option B: AWS S3 (Better for production)**
- Use `django-storages` package
- Configure S3 bucket
- Update settings to use S3

### **4. Custom Domain (Optional)**

1. In Railway dashboard: Settings → Domains
2. Add custom domain: `connectflow.yourdomain.com`
3. Update DNS records (Railway provides instructions)
4. Update `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS`

---

## 📊 Monitoring & Maintenance

### **Railway Dashboard Features:**

- **Metrics:** CPU, Memory, Network usage
- **Logs:** Real-time application logs
- **Deployments:** History and rollback
- **Environment Variables:** Secure config
- **Billing:** Monitor free tier usage

### **Logging Configuration**

Add to `settings_prod.py`:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
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
    },
}
```

---

## 🔄 Continuous Deployment (Auto-Deploy)

### **Automatic Deployments:**

Railway automatically deploys when you push to GitHub!

```bash
# Make changes
git add .
git commit -m "Feature: Add new chat feature"
git push origin main

# Railway automatically:
# 1. Detects the push
# 2. Builds the app
# 3. Runs migrations (if configured)
# 4. Deploys new version
# 5. Updates live site
```

### **Set Up Auto-Migrations:**

Create `railway.toml`:

```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "python manage.py migrate && daphne -b 0.0.0.0 -p $PORT connectflow.asgi:application"
healthcheckPath = "/"
restartPolicyType = "ON_FAILURE"
```

---

## 💰 Cost Breakdown (Free Tier)

**Railway Free Tier:**
- $5 credit per month
- Enough for:
  - 1 Web service (Django)
  - 1 PostgreSQL database
  - 1 Redis instance
- Usage-based billing after $5

**Staying Within Free Tier:**
- Keep app small
- Optimize database queries
- Use caching effectively
- Monitor usage regularly

---

## 🎯 Alternative: Deploy on Render.com

**Render Advantages:**
- Completely free tier (no credit limit)
- Supports WebSockets
- Auto-SSL
- Persistent storage

**Render Quick Setup:**

1. Create `render.yaml`:
```yaml
services:
  - type: web
    name: connectflow-pro
    env: python
    buildCommand: pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
    startCommand: daphne -b 0.0.0.0 -p $PORT connectflow.asgi:application
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: connectflow-db
          property: connectionString
      - key: REDIS_URL
        fromService:
          name: connectflow-redis
          type: redis
          property: connectionString
      - key: SECRET_KEY
        generateValue: true
      - key: DJANGO_SETTINGS_MODULE
        value: connectflow.settings_prod

databases:
  - name: connectflow-db
    databaseName: connectflow
    user: connectflow

services:
  - type: redis
    name: connectflow-redis
    ipAllowList: []
```

2. Push to GitHub

3. Go to Render.com → New → Blueprint

4. Connect repo and deploy!

---

## 📝 Deployment Checklist

### Before Deployment:
- [ ] Create `Procfile`
- [ ] Create `runtime.txt`
- [ ] Update `requirements.txt`
- [ ] Create `settings_prod.py`
- [ ] Update `.gitignore`
- [ ] Push to GitHub
- [ ] Generate new SECRET_KEY for production

### After Deployment:
- [ ] Run migrations
- [ ] Create superuser
- [ ] Collect static files
- [ ] Test WebSocket connections
- [ ] Test file uploads
- [ ] Test voice messages
- [ ] Configure custom domain (optional)
- [ ] Set up monitoring
- [ ] Configure backups

---

## 🚀 Next Steps After Deployment

### **Integrations to Add:**

1. **Email Service (Mailgun/SendGrid)**
   - Password reset
   - Email notifications
   - Welcome emails

2. **Object Storage (AWS S3/Cloudinary)**
   - Media file hosting
   - File uploads
   - Avatar storage

3. **Monitoring (Sentry)**
   - Error tracking
   - Performance monitoring
   - User analytics

4. **CDN (CloudFlare)**
   - Static file delivery
   - DDoS protection
   - SSL/TLS

5. **Analytics (Google Analytics)**
   - User behavior
   - Usage metrics
   - Feature tracking

---

## 📚 Resources

**Documentation:**
- Railway: https://docs.railway.app
- Render: https://render.com/docs
- Django Deployment: https://docs.djangoproject.com/en/5.0/howto/deployment/
- Channels Deployment: https://channels.readthedocs.io/en/stable/deploying.html

**Helpful Commands:**
```bash
# Railway CLI
npm i -g @railway/cli
railway login
railway link
railway up
railway run python manage.py migrate
railway logs

# Check deployment
railway status
railway variables
```

---

**Status:** ✅ Ready to Deploy  
**Platform:** Railway.app (Recommended) or Render.com  
**Cost:** Free tier available  
**Time:** ~30 minutes initial setup

**Let me know which platform you prefer and I'll help you deploy!** 🚀
