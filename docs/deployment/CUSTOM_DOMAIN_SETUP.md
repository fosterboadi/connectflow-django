# Custom Domain Setup on Render.com

## ✅ **YES! Custom Domains Work on FREE Tier**

Render.com supports custom domains on **ALL plans** including **FREE**!

---

## 🎯 **Quick Answer**

**Cost:** $8-15/year (just the domain name)
**Time:** 15-30 minutes for subdomain, 1-24 hours for root domain
**SSL:** FREE and automatic
**Setup:** Easy (follow guide below)

---

## 📋 **Step-by-Step Guide**

### **Step 1: Buy a Domain ($8-15/year)**

**Where to buy:**
- **Namecheap** - https://www.namecheap.com (~$10/year) ⭐ Recommended
- **Cloudflare** - https://www.cloudflare.com/products/registrar/ (~$9/year)
- **Google Domains** - https://domains.google (~$12/year)
- **GoDaddy** - https://www.godaddy.com (~$15/year)

---

### **Step 2: Add Domain in Render**

1. Go to: https://dashboard.render.com/
2. Click your **connectflow-pro** service
3. Click **"Settings"** tab
4. Scroll to **"Custom Domains"**
5. Click **"Add Custom Domain"**
6. Enter your domain:
   - Subdomain: `app.yourcompany.com` (recommended - faster)
   - Root: `yourcompany.com`
7. Click **"Save"**
8. **Copy the DNS records** Render shows you

---

### **Step 3: Add DNS Records**

#### **Option A: Subdomain (RECOMMENDED - 5-10 min)**

Add this to your domain's DNS:
```
Type: CNAME
Name: app
Value: connectflow-pro.onrender.com
TTL: 3600
```

#### **Option B: Root Domain (1-24 hours)**

Add these to your domain's DNS:
```
Type: A
Name: @ (or blank)
Value: 216.24.57.1

Type: AAAA  
Name: @ (or blank)
Value: 2600:1f1c:0:4000::1
```

---

### **Step 4: Wait for DNS**

- **Subdomain:** 5-30 minutes ⚡
- **Root domain:** 1-24 hours 🐢

Check status: https://dnschecker.org/

---

### **Step 5: Update Django Settings**

Edit `connectflow/settings_render.py`:

```python
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '.onrender.com',
    'yourcompany.com',        # ← Add your domain
    'app.yourcompany.com',    # ← Add subdomain
]

CSRF_TRUSTED_ORIGINS = [
    'https://*.onrender.com',
    'https://yourcompany.com',
    'https://app.yourcompany.com',
]
```

Commit and push - Render auto-deploys!

---

### **Step 6: SSL Automatic ✅**

Render automatically:
- Provisions FREE SSL certificate
- Enables HTTPS
- Redirects HTTP → HTTPS
- Renews certificate automatically

**You don't need to do anything!**

---

## 🚀 **Recommended Setup**

```
Buy: yourcompany.com
Use: app.yourcompany.com (subdomain)

Why?
✅ Faster (5-10 min vs 24 hours)
✅ Easier setup
✅ Professional (app.company.com is standard)
✅ Can use root for website later
```

---

## 💰 **Total Cost**

| Item | Cost |
|------|------|
| Domain name | $8-15/year |
| Custom domain on Render | FREE ✅ |
| SSL certificate | FREE ✅ |
| **Total** | **$8-15/year** |

---

## 🎯 **Examples**

**Professional:**
- `app.yourcompany.com` ⭐
- `connectflow.yourcompany.com`
- `team.yourcompany.com`

**Simple:**
- `yourcompany.com`

---

## 🛠️ **Troubleshooting**

### **"Domain not verified"**
- Check DNS records match exactly
- Wait longer (up to 24 hours)
- Use dnschecker.org to verify

### **"DisallowedHost error"**
- Add domain to `ALLOWED_HOSTS`
- Add to `CSRF_TRUSTED_ORIGINS`
- Commit and push

### **SSL/Certificate error**
- Wait 5-10 min for SSL provisioning
- Clear browser cache
- Try incognito mode

---

## ✅ **Quick Checklist**

- [ ] Buy domain name
- [ ] Add custom domain in Render
- [ ] Add DNS records (CNAME or A/AAAA)
- [ ] Wait for DNS propagation
- [ ] Update Django ALLOWED_HOSTS
- [ ] Push to GitHub
- [ ] Wait for Render deploy
- [ ] Visit your custom domain! 🎉

---

## 📞 **Need Help?**

**DNS Setup Guides by Registrar:**
- [Namecheap DNS Guide](https://www.namecheap.com/support/knowledgebase/article.aspx/319/2237/how-can-i-set-up-an-a-address-record-for-my-domain/)
- [Cloudflare DNS Guide](https://developers.cloudflare.com/dns/manage-dns-records/how-to/create-dns-records/)
- [Google Domains Guide](https://support.google.com/domains/answer/3290350)

**Render Documentation:**
- https://render.com/docs/custom-domains

---

**Bottom Line: YES, custom domains work perfectly on Render's FREE tier! Total cost is just the domain name ($8-15/year).** 🎊
