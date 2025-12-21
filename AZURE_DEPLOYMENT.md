# ConnectFlow Pro - Azure Deployment Guide
## Deploy to Azure App Service with Student Account

**Date:** December 21, 2025  
**Platform:** Microsoft Azure for Students  
**Cost:** $0 (using student credits)

---

## ✅ Prerequisites

- [x] Azure for Students account activated
- [x] $100 credit available
- [x] GitHub repository ready
- [x] Project files prepared

---

## 🚀 Quick Deployment (30 Minutes)

### **Step 1: Prepare Azure Account (5 mins)**

1. **Activate Azure for Students:**
   - Visit: https://azure.microsoft.com/en-us/free/students/
   - Sign in with Microsoft account
   - Verify with .edu email
   - Get $100 credit instantly

2. **Access Azure Portal:**
   - Go to: https://portal.azure.com
   - Sign in with your account

---

### **Step 2: Create PostgreSQL Database (5 mins)**

1. In Azure Portal, click **"Create a resource"**
2. Search for **"Azure Database for PostgreSQL"**
3. Click **"Create"** → **"Flexible server"**

**Configuration:**
```
Basics:
- Subscription: Azure for Students
- Resource Group: Create new → "connectflow-rg"
- Server name: connectflow-db
- Region: Choose closest to you
- PostgreSQL version: 16
- Workload type: Development
- Compute + Storage: Burstable, B1ms (Free tier)

Authentication:
- Authentication method: PostgreSQL authentication only
- Admin username: connectflow_admin
- Password: [Create strong password - SAVE THIS!]

Networking:
- Allow public access from any Azure service: Yes
- Add current client IP address: Yes
```

4. Click **"Review + create"** → **"Create"**
5. Wait 3-5 minutes for deployment

**Save this info:**
```
Server name: connectflow-db.postgres.database.azure.com
Admin username: connectflow_admin
Password: [your password]
Database: postgres (default, we'll create our DB)
```

---

### **Step 3: Create Redis Cache (5 mins)**

1. Click **"Create a resource"**
2. Search for **"Azure Cache for Redis"**
3. Click **"Create"**

**Configuration:**
```
Basics:
- Resource Group: connectflow-rg
- DNS name: connectflow-redis
- Location: Same as database
- Cache type: Basic C0 (250 MB) - Free for 12 months
- Eviction policy: volatile-lru

Networking:
- Connectivity method: Public endpoint
- Allow public network access: Yes
```

4. Click **"Review + create"** → **"Create"**
5. Wait 5-10 minutes for deployment

**After deployment:**
- Go to Redis resource
- Click **"Access keys"** → Copy **Primary connection string**
- Save it (format: `redis://...`)

---

### **Step 4: Create Web App (5 mins)**

1. Click **"Create a resource"**
2. Search for **"Web App"**
3. Click **"Create"**

**Configuration:**
```
Basics:
- Resource Group: connectflow-rg
- Name: connectflow-pro (will be connectflow-pro.azurewebsites.net)
- Publish: Code
- Runtime stack: Python 3.11
- Operating System: Linux
- Region: Same as database

App Service Plan:
- Linux Plan: Create new → "connectflow-plan"
- Sku and size: F1 (Free) - Click "Change size" → Dev/Test → F1
```

**Deployment:**
```
- Continuous deployment: Enable
- GitHub account: Connect your account
- Organization: Your username
- Repository: connectflow-django
- Branch: main
```

4. Click **"Review + create"** → **"Create"**

---

### **Step 5: Configure Environment Variables (5 mins)**

1. Go to your Web App resource
2. Click **"Configuration"** (left sidebar)
3. Click **"+ New application setting"** for each:

```
Name: SECRET_KEY
Value: [Generate new secret key]
```
Generate with: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`

```
Name: DATABASE_URL
Value: postgresql://connectflow_admin:[password]@connectflow-db.postgres.database.azure.com/postgres?sslmode=require
```

```
Name: REDIS_URL
Value: [Your Redis connection string from Step 3]
```

```
Name: ALLOWED_HOSTS
Value: .azurewebsites.net
```

```
Name: DJANGO_SETTINGS_MODULE
Value: connectflow.settings_azure
```

```
Name: WEBSITE_SITE_NAME
Value: connectflow-pro
```

4. Click **"Save"** at the top
5. Click **"Continue"** when prompted

---

### **Step 6: Configure Startup Command (2 mins)**

1. Still in **Configuration** page
2. Go to **"General settings"** tab
3. Find **"Startup Command"**
4. Enter:
```bash
bash startup.sh
```

5. Click **"Save"**

---

### **Step 7: Create Database and Run Migrations (5 mins)**

1. In your Web App, go to **"SSH"** (left sidebar)
2. Click **"Go"**
3. Terminal will open

**Run these commands:**

```bash
# Create database
python manage.py migrate

# Create superuser
python manage.py createsuperuser
# Follow prompts to create admin account

# Collect static files (if needed)
python manage.py collectstatic --noinput
```

---

### **Step 8: Test Your Deployment (2 mins)**

1. Go back to Web App **"Overview"**
2. Click the **URL** (https://connectflow-pro.azurewebsites.net)
3. Your app should load!

**Test checklist:**
- [ ] Home page loads
- [ ] Can access /admin
- [ ] Can login with superuser
- [ ] Can create organization
- [ ] WebSockets connect (check browser console)
- [ ] Can send chat messages
- [ ] File uploads work

---

## 🔧 Troubleshooting

### **App doesn't start?**

**Check logs:**
1. Web App → **"Log stream"** (left sidebar)
2. Look for errors

**Common issues:**
- Missing environment variables
- Database connection failed
- Static files not collected

**Fix:**
```bash
# SSH into app
# Check environment
env | grep DJANGO

# Test database connection
python manage.py check --database default

# Re-run migrations
python manage.py migrate
```

---

### **WebSockets not working?**

**Check:**
1. Redis is running (go to Redis resource)
2. REDIS_URL is correct
3. Daphne is starting (check logs)

**Enable WebSocket:**
1. Web App → **"Configuration"**
2. **"General settings"** tab
3. **Web sockets:** ON
4. Click **"Save"**

---

### **Static files not loading?**

```bash
# SSH into app
python manage.py collectstatic --noinput
```

Check WhiteNoise is in settings_azure.py (it is!)

---

### **Database connection fails?**

**Check:**
1. PostgreSQL firewall rules (should allow Azure services)
2. DATABASE_URL format is correct
3. Password is correct

**Update firewall:**
1. Go to PostgreSQL resource
2. **"Networking"** → **"Firewall rules"**
3. Ensure "Allow public access from any Azure service" is ON

---

## 📊 Monitor Your App

### **Usage & Costs:**

1. Go to **"Cost Management + Billing"**
2. Check student credit remaining
3. Monitor resource usage

**Free tier limits:**
- App Service F1: 60 CPU minutes/day
- PostgreSQL B1ms: 750 hours/month (free for 12 months)
- Redis C0: 250MB (free for 12 months)

---

## 🎯 Post-Deployment Setup

### **1. Set Up Custom Domain (Optional)**

1. Buy domain (Namecheap, GoDaddy, etc.)
2. Web App → **"Custom domains"**
3. Add custom domain
4. Update DNS records
5. Update `ALLOWED_HOSTS` in environment variables

---

### **2. Enable Azure Blob Storage for Media Files**

**Why?** Azure App Service doesn't persist uploaded files on restart

**Setup:**

1. **Create Storage Account:**
   - Create resource → Storage account
   - Name: connectflowstorage
   - Performance: Standard
   - Replication: LRS (cheapest)

2. **Create Container:**
   - Go to Storage account
   - Containers → + Container
   - Name: media
   - Public access: Blob

3. **Install django-storages:**
```bash
pip install django-storages[azure]
# Add to requirements.txt
```

4. **Update settings_azure.py:**
```python
INSTALLED_APPS += ['storages']

DEFAULT_FILE_STORAGE = 'storages.backends.azure_storage.AzureStorage'
AZURE_ACCOUNT_NAME = os.environ.get('AZURE_STORAGE_ACCOUNT_NAME')
AZURE_ACCOUNT_KEY = os.environ.get('AZURE_STORAGE_ACCOUNT_KEY')
AZURE_CONTAINER = 'media'
```

5. **Add environment variables:**
   - AZURE_STORAGE_ACCOUNT_NAME
   - AZURE_STORAGE_ACCOUNT_KEY

---

### **3. Set Up Email (SendGrid)**

**Azure integrates with SendGrid:**

1. Create SendGrid account via Azure
2. Get API key
3. Update settings_azure.py (already configured)
4. Add environment variables:
   - EMAIL_HOST
   - EMAIL_HOST_USER
   - EMAIL_HOST_PASSWORD

---

## 🔄 Continuous Deployment

**Already set up!** Every push to GitHub main branch will:

1. Trigger Azure build
2. Install dependencies
3. Run migrations
4. Collect static files
5. Restart app

**To deploy changes:**
```bash
git add .
git commit -m "Update feature"
git push origin main
# Azure automatically deploys!
```

---

## 📝 Important URLs

**Your App:**
- Production: https://connectflow-pro.azurewebsites.net
- Admin: https://connectflow-pro.azurewebsites.net/admin

**Azure Resources:**
- Portal: https://portal.azure.com
- Resource Group: connectflow-rg

**Credentials (SAVE THESE):**
```
Database:
- Host: connectflow-db.postgres.database.azure.com
- Username: connectflow_admin
- Password: [your password]
- Database: postgres

Admin Account:
- Username: [created in Step 7]
- Password: [your password]

Secret Key: [in environment variables]
```

---

## ✅ Deployment Checklist

- [ ] Azure for Students activated
- [ ] PostgreSQL database created
- [ ] Redis cache created
- [ ] Web App created
- [ ] Environment variables configured
- [ ] Startup command set
- [ ] Database migrated
- [ ] Superuser created
- [ ] App accessible online
- [ ] WebSockets working
- [ ] File uploads working
- [ ] Custom domain configured (optional)
- [ ] Blob storage configured (optional)

---

## 🎉 You're Live!

**Your ConnectFlow Pro is now deployed on Azure!**

**Next steps:**
1. Create your organization
2. Invite team members
3. Start using chat channels
4. Share your live URL!

**App URL:** https://connectflow-pro.azurewebsites.net

**Total time:** ~30 minutes  
**Total cost:** $0 (using student credits) 🎓

---

## 📞 Need Help?

**Check:**
1. Log stream in Azure
2. Browser console (F12)
3. Django debug toolbar (if enabled)

**Common issues solved above in Troubleshooting section**

---

**Congratulations on deploying to Azure!** 🚀
