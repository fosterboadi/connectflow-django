# Azure Deployment - Quick Start Checklist
## ConnectFlow Pro on Azure for Students

**Time Required:** 30 minutes  
**Cost:** $0 (Student credits)

---

## ✅ Files Ready

All deployment files have been created:

- [x] **`connectflow/settings_azure.py`** - Azure production settings
- [x] **`manage.py`** - Updated with auto-detection
- [x] **`connectflow/asgi.py`** - Updated with auto-detection
- [x] **`startup.sh`** - Azure startup script
- [x] **`requirements.txt`** - Updated with Azure packages
- [x] **`AZURE_DEPLOYMENT.md`** - Complete deployment guide

---

## 🚀 Deployment Steps

### **Before You Start:**

1. **Check your Azure account:**
   - [ ] Azure for Students activated
   - [ ] $100 credit available
   - [ ] Can access https://portal.azure.com

2. **Push to GitHub:**
```bash
git add .
git commit -m "Ready for Azure deployment"
git push origin main
```

---

### **Step-by-Step (30 mins):**

| Step | Task | Time | Status |
|------|------|------|--------|
| 1 | Create PostgreSQL Database | 5 min | ⬜ |
| 2 | Create Redis Cache | 5 min | ⬜ |
| 3 | Create Web App | 5 min | ⬜ |
| 4 | Set Environment Variables | 5 min | ⬜ |
| 5 | Configure Startup Command | 2 min | ⬜ |
| 6 | Run Migrations via SSH | 5 min | ⬜ |
| 7 | Test Deployment | 3 min | ⬜ |

**Total:** ~30 minutes

---

## 📋 Quick Configuration

### **Environment Variables to Set:**

Copy these to Azure App Service → Configuration:

```env
SECRET_KEY=[Generate: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"]
DATABASE_URL=postgresql://connectflow_admin:[PASSWORD]@connectflow-db.postgres.database.azure.com/postgres?sslmode=require
REDIS_URL=[Copy from Redis resource → Access keys]
ALLOWED_HOSTS=.azurewebsites.net
DJANGO_SETTINGS_MODULE=connectflow.settings_azure
WEBSITE_SITE_NAME=connectflow-pro
```

---

## 🎯 After Deployment

### **Create Superuser:**

In Azure SSH terminal:
```bash
python manage.py createsuperuser
```

### **Access Your App:**

- **URL:** https://connectflow-pro.azurewebsites.net
- **Admin:** https://connectflow-pro.azurewebsites.net/admin

### **Test Features:**

- [ ] Home page loads
- [ ] Can login to admin
- [ ] Can create organization
- [ ] Can create channels
- [ ] WebSockets connect (F12 → Console)
- [ ] Can send messages
- [ ] File upload works
- [ ] Voice messages work

---

## 💡 Quick Tips

### **Enable WebSockets:**

Web App → Configuration → General settings → **Web sockets: ON**

### **View Logs:**

Web App → Log stream

### **SSH Access:**

Web App → SSH → Go

### **Monitor Usage:**

Cost Management → Check student credit

---

## 🔧 Common Issues & Fixes

### **App won't start?**
```bash
# Check environment variables are set
# Check startup.sh is configured
# View logs: Web App → Log stream
```

### **Database connection fails?**
```bash
# Check DATABASE_URL format
# Check PostgreSQL firewall allows Azure services
# Verify password is correct
```

### **WebSockets not working?**
```bash
# Enable Web sockets in Configuration
# Check Redis is running
# Verify REDIS_URL is correct
```

---

## 📚 Full Documentation

**Read:** `AZURE_DEPLOYMENT.md` for detailed instructions

**Sections:**
1. Prerequisites
2. Step-by-step deployment
3. Environment configuration
4. Troubleshooting
5. Post-deployment setup
6. Monitoring

---

## ⚡ Quick Commands

### **SSH into Azure:**
```bash
# Via Azure CLI (if installed)
az webapp ssh --resource-group connectflow-rg --name connectflow-pro
```

### **Run migrations:**
```bash
python manage.py migrate
```

### **Create superuser:**
```bash
python manage.py createsuperuser
```

### **Collect static:**
```bash
python manage.py collectstatic --noinput
```

### **Check database:**
```bash
python manage.py check --database default
```

---

## 🎓 Resources

- **Azure Portal:** https://portal.azure.com
- **Azure for Students:** https://azure.microsoft.com/free/students
- **Django on Azure:** https://learn.microsoft.com/azure/app-service/quickstart-python
- **Azure Python SDK:** https://learn.microsoft.com/python/api/overview/azure/

---

## ✅ Success Criteria

Your deployment is successful when:

- [x] App loads at https://connectflow-pro.azurewebsites.net
- [x] Admin panel accessible
- [x] Can create/manage organizations
- [x] Chat channels work
- [x] WebSockets connect
- [x] Messages send in real-time
- [x] File uploads work
- [x] Voice messages work
- [x] No errors in logs

---

## 🎉 You're Ready!

**Everything is prepared for Azure deployment.**

**Next steps:**
1. Follow `AZURE_DEPLOYMENT.md` guide
2. Complete the 7 steps
3. Test your live app
4. Share with your team!

**Estimated time to live:** 30 minutes

**Good luck!** 🚀

---

**Need help?** Check the troubleshooting section in AZURE_DEPLOYMENT.md
