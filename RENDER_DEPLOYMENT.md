# ConnectFlow Pro - Render.com Deployment Guide
## Deploy in 10 Minutes! 🚀

**Date:** December 21, 2025 @ 05:02 AM  
**Platform:** Render.com  
**Cost:** $0 (100% Free)

---

## ✅ What You Get (FREE)

- ✅ **Web Service** - 750 hours/month (enough for 1 app 24/7)
- ✅ **PostgreSQL** - 1GB database (free forever)
- ✅ **Redis** - 25MB cache (free forever)
- ✅ **SSL/HTTPS** - Automatic certificates
- ✅ **Custom Domain** - Free subdomain + custom domain support
- ✅ **Auto Deploy** - GitHub integration
- ✅ **WebSocket Support** - Django Channels works perfectly

**No credit card required!**

---

## 🚀 Quick Deployment (10 Minutes)

### **Step 1: Push to GitHub (2 mins)**

```bash
# Make sure all files are committed
git add .
git commit -m "Ready for Render deployment"
git push origin main
```

**Files now ready:**
- ✅ `render.yaml` - Render configuration
- ✅ `connectflow/settings_render.py` - Production settings
- ✅ `build.sh` - Build script
- ✅ `requirements.txt` - Dependencies
- ✅ `manage.py` - Auto-detects Render
- ✅ `connectflow/asgi.py` - Auto-detects Render

---

### **Step 2: Create Render Account (1 min)**

1. Go to **https://render.com**
2. Click **"Get Started for Free"**
3. Sign up with **GitHub** (easiest)
4. Authorize Render to access your GitHub

**No credit card needed!**

---

### **Step 3: Deploy from GitHub (2 mins)**

#### **Option A: Using Blueprint (EASIEST - One Click!)**

1. In Render Dashboard, click **"New +"**
2. Select **"Blueprint"**
3. Connect your GitHub repository: **connectflow-django**
4. Render reads `render.yaml` automatically
5. Click **"Apply"**

**That's it!** Render will:
- Create PostgreSQL database
- Create Redis cache
- Create Web service
- Build and deploy automatically

**Skip to Step 4!**

---

#### **Option B: Manual Setup (If Blueprint doesn't work)**

**3a. Create PostgreSQL Database:**

1. Click **"New +"** → **"PostgreSQL"**
2. Configure:
   ```
   Name: connectflow-db
   Database: connectflow
   User: connectflow
   Region: Oregon (US West)
   Plan: Free
   ```
3. Click **"Create Database"**
4. Wait 1-2 minutes for provisioning

**3b. Create Redis:**

1. Click **"New +"** → **"Redis"**
2. Configure:
   ```
   Name: connectflow-redis
   Region: Oregon (same as database)
   Plan: Free
   Maxmemory Policy: noeviction
   ```
3. Click **"Create Redis"**

**3c. Create Web Service:**

1. Click **"New +"** → **"Web Service"**
2. **Connect GitHub repository:** connectflow-django
3. Configure:
   ```
   Name: connectflow-pro
   Region: Oregon (same as others)
   Branch: main
   Runtime: Python 3
   Build Command: bash build.sh
   Start Command: daphne -b 0.0.0.0 -p $PORT connectflow.asgi:application
   Plan: Free
   ```

**3d. Add Environment Variables:**

Click **"Advanced"** → **"Add Environment Variable"**

```
Key: PYTHON_VERSION
Value: 3.11.9

Key: SECRET_KEY
Value: [Generate with: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"]

Key: DJANGO_SETTINGS_MODULE
Value: connectflow.settings_render

Key: RENDER
Value: true

Key: DATABASE_URL
Value: [Copy from PostgreSQL database "Internal Database URL"]

Key: REDIS_URL
Value: [Copy from Redis "Internal Connection String"]
```

4. Click **"Create Web Service"**

---

### **Step 4: Wait for Build (5 mins)**

**Render will now:**
1. ✅ Pull code from GitHub
2. ✅ Install dependencies (pip install)
3. ✅ Collect static files
4. ✅ Run migrations
5. ✅ Start Daphne server

**Watch the build logs in real-time!**

**Build progress:**
```
==> Installing dependencies...
==> Collecting static files...
==> Running migrations...
==> Starting server...
==> Your service is live at https://connectflow-pro.onrender.com
```

**First build takes ~5 minutes**

---

### **Step 5: Create Superuser (2 mins)**

**After deployment completes:**

1. Go to your Web Service in Render
2. Click **"Shell"** (left sidebar)
3. Run:
   ```bash
   python manage.py createsuperuser
   ```
4. Follow prompts:
   ```
   Username: admin
   Email: your@email.com
   Password: [create password]
   Password (again): [confirm]
   ```

**Superuser created!**

---

### **Step 6: Access Your App! (1 min)**

**Your app is now live!**

1. Go to your Web Service
2. Click the **URL** at top (https://connectflow-pro.onrender.com)
3. Your app loads!

**Test:**
- [ ] Home page loads ✅
- [ ] Visit /admin ✅
- [ ] Login with superuser ✅
- [ ] Create organization ✅
- [ ] Create channels ✅
- [ ] Send messages ✅

---

## 🎉 **YOU'RE LIVE!**

**Your URLs:**
- **App:** https://connectflow-pro.onrender.com
- **Admin:** https://connectflow-pro.onrender.com/admin

**Total time:** ~10 minutes  
**Total cost:** $0

---

## 🔄 Continuous Deployment (Auto-Deploy)

**Render watches your GitHub repo!**

**Every time you push:**
```bash
git add .
git commit -m "Add new feature"
git push origin main
```

**Render automatically:**
1. Detects the push
2. Pulls latest code
3. Runs build.sh
4. Deploys new version
5. Your changes are live! (~3 mins)

**No manual deployment needed!**

---

## 🔧 Important Settings

### **Enable WebSockets**

**Already configured!** Daphne handles WebSockets automatically.

To verify:
1. Web Service → **Settings**
2. Scroll to **"Environment"**
3. Check that `RENDER=true` is set

---

### **Database Backups**

**Free tier includes:**
- ✅ Daily backups (last 7 days)
- ✅ Point-in-time recovery
- ✅ Automatic maintenance

**To access backups:**
1. Go to PostgreSQL service
2. Click **"Backups"** tab

---

### **View Logs**

**Real-time logs:**
1. Web Service → **"Logs"** tab
2. See all application output
3. Filter by log level

**Useful for debugging!**

---

## ⚠️ Important Notes

### **Free Tier Limitations**

**Web Service:**
- ✅ 750 hours/month (31 days = 744 hours, so you're good!)
- ⚠️ **Sleeps after 15 minutes of inactivity**
- ⚠️ First request after sleep takes ~30 seconds to wake up
- ✅ 512MB RAM
- ✅ Shared CPU

**What "sleep" means:**
- No visitors for 15 mins → server stops
- Next visitor → server starts (30 sec delay)
- Then works normally

**How to prevent sleep:**
- Upgrade to paid plan ($7/mo - always on)
- Or use a free uptime monitor (pings your site every 5 mins)

**Database & Redis:**
- ✅ **Never sleep!**
- ✅ Always available
- ✅ 99.9% uptime

---

### **Media Files (Important!)**

**Free tier doesn't persist uploaded files on deploy!**

**What this means:**
- User uploads avatar → Works
- You redeploy app → Avatar lost! ❌

**Solutions:**

**Option 1: Use Cloudinary (Free)**
1. Sign up at https://cloudinary.com (free tier)
2. Install: `pip install django-cloudinary-storage`
3. Configure in `settings_render.py`

**Option 2: Use AWS S3 Free Tier**
1. AWS S3 free tier (5GB, 12 months)
2. Install: `pip install django-storages boto3`
3. Configure in `settings_render.py`

**I can help set this up later if needed!**

---

## 🎯 Post-Deployment Setup

### **1. Custom Domain (Optional)**

**Add your own domain:**

1. Buy domain (Namecheap, GoDaddy, etc.)
2. Render Web Service → **"Settings"** → **"Custom Domains"**
3. Click **"Add Custom Domain"**
4. Enter: `connectflow.yourdomain.com`
5. Update DNS records (Render shows instructions)
6. SSL certificate auto-issued!

**Update settings:**
```python
# In settings_render.py
ALLOWED_HOSTS = ['.onrender.com', 'connectflow.yourdomain.com']
CSRF_TRUSTED_ORIGINS = ['https://connectflow.yourdomain.com']
```

---

### **2. Environment Variables**

**Add more env vars:**

1. Web Service → **"Environment"** tab
2. Click **"Add Environment Variable"**
3. Examples:
   ```
   EMAIL_HOST=smtp.sendgrid.net
   EMAIL_HOST_USER=apikey
   EMAIL_HOST_PASSWORD=[your-sendgrid-key]
   SENTRY_DSN=[your-sentry-dsn]
   ```

---

### **3. Monitoring**

**Free monitoring tools:**

**Render built-in:**
- Metrics tab (CPU, Memory, Network)
- Logs tab (Real-time)
- Events tab (Deploy history)

**External (optional):**
- **UptimeRobot** - Free uptime monitoring
- **Sentry** - Free error tracking
- **LogRocket** - Free session replay

---

## 🔍 Troubleshooting

### **Build Fails?**

**Check build logs:**
1. Web Service → **"Logs"** tab
2. Look for errors

**Common issues:**
```
❌ "No module named 'X'"
   Fix: Add package to requirements.txt

❌ "Migration failed"
   Fix: Check DATABASE_URL is set

❌ "Static files error"
   Fix: Ensure WhiteNoise in MIDDLEWARE
```

---

### **App Not Loading?**

**Checklist:**
- [ ] Build succeeded (green checkmark)
- [ ] Service is "Live" (not deploying)
- [ ] DATABASE_URL environment variable set
- [ ] REDIS_URL environment variable set
- [ ] SECRET_KEY environment variable set

**Check:**
1. Web Service → **"Logs"**
2. Look for startup errors

---

### **WebSockets Not Working?**

**Verify:**
1. Redis is running (check Redis service)
2. REDIS_URL is correct
3. Daphne is starting (check logs for "Daphne" message)

**Test WebSocket:**
- Open browser console (F12)
- Look for WebSocket connection messages
- Should see: `WebSocket connected`

---

### **Database Connection Issues?**

**Check DATABASE_URL:**
1. PostgreSQL service → **"Info"** tab
2. Copy **"Internal Database URL"**
3. Paste in Web Service environment variables
4. Format: `postgresql://user:password@host/database`

**Verify connection:**
```bash
# In Shell
python manage.py check --database default
```

---

## 📊 Monitor Usage

### **Check Free Tier Usage:**

1. Dashboard → **"Account Settings"**
2. **"Usage"** tab
3. See:
   - Hours used this month
   - Database size
   - Redis size

**Free tier limits:**
- Web Service: 750 hours/month
- PostgreSQL: 1GB storage
- Redis: 25MB storage

**You'll get email if close to limit!**

---

## ⚡ Quick Commands

### **Shell Access:**

```bash
# In Render Web Service → Shell tab

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Check database
python manage.py check --database default

# Django shell
python manage.py shell

# Collect static files
python manage.py collectstatic --noinput
```

---

### **Useful Management:**

**Restart Service:**
- Web Service → **"Manual Deploy"** → **"Deploy latest commit"**

**View Environment:**
- Web Service → **"Environment"** tab

**See Metrics:**
- Web Service → **"Metrics"** tab

**Download Logs:**
- Logs tab → Click download icon

---

## 🎓 Render Dashboard Overview

**Left Sidebar:**

- **Dashboard** - All services
- **Web Services** - Your apps
- **Databases** - PostgreSQL instances  
- **Redis** - Redis caches
- **Cron Jobs** - Scheduled tasks
- **Background Workers** - Async jobs

**Each Service Has:**

- **Logs** - Real-time output
- **Metrics** - Usage graphs
- **Environment** - Variables
- **Settings** - Configuration
- **Shell** - Terminal access
- **Events** - Deploy history

---

## 🚀 Going to Production

**When ready for real users:**

### **Upgrade Web Service ($7/mo):**

**Benefits:**
- ✅ Never sleeps (always on)
- ✅ 4GB RAM (vs 512MB)
- ✅ 2 vCPU (vs shared)
- ✅ Faster performance
- ✅ More concurrent users

**To upgrade:**
1. Web Service → **"Settings"**
2. **"Instance Type"** → **"Starter"** ($7/mo)
3. Click **"Save Changes"**

**Database & Redis stay free!**

---

### **Add Media Storage:**

**Cloudinary (Recommended):**
```bash
pip install django-cloudinary-storage
```

**Configure:**
```python
# settings_render.py
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.environ.get('CLOUDINARY_API_KEY'),
    'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET'),
}

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
```

---

## ✅ Deployment Checklist

**Before Deployment:**
- [x] Code pushed to GitHub
- [x] `render.yaml` exists
- [x] `settings_render.py` created
- [x] `build.sh` created
- [x] `requirements.txt` updated

**During Deployment:**
- [ ] Render account created
- [ ] Blueprint deployed OR services created manually
- [ ] Build completed successfully
- [ ] Environment variables set
- [ ] Superuser created

**After Deployment:**
- [ ] App loads at .onrender.com URL
- [ ] Admin panel accessible
- [ ] Can login with superuser
- [ ] WebSockets connect
- [ ] Messages send successfully
- [ ] File uploads work (temporarily)

---

## 🎉 Success!

**Your ConnectFlow Pro is now LIVE on Render!**

**What you have:**
- ✅ Free PostgreSQL database (1GB)
- ✅ Free Redis cache (25MB)
- ✅ Free web hosting (750 hrs/mo)
- ✅ Automatic SSL/HTTPS
- ✅ Auto-deploy from GitHub
- ✅ WebSockets working
- ✅ Professional URL

**Next steps:**
1. Create your organization
2. Set up departments
3. Create chat channels
4. Invite team members
5. Start chatting!

**Share your app:** https://connectflow-pro.onrender.com 🚀

---

## 📞 Need Help?

**Render Support:**
- Docs: https://render.com/docs
- Community: https://community.render.com
- Status: https://status.render.com

**Common Issues:**
- Check this guide's Troubleshooting section
- View Render logs
- Check browser console (F12)

---

**Congratulations! You're deployed on Render.com!** 🎉

**Total time:** 10 minutes  
**Total cost:** $0  
**Future deployments:** Automatic on git push
