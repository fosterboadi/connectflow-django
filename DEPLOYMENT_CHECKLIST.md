# Deployment Checklist for Render

## ⚠️ CRITICAL: Must Complete Before Deploying

### 1. Firebase Service Account Setup
- [ ] Go to [Firebase Console](https://console.firebase.google.com/)
- [ ] Select your project: `connectflowpro-f1202`
- [ ] Navigate to: **Project Settings** → **Service Accounts**
- [ ] Click **Generate New Private Key**
- [ ] Download the JSON file (keep it safe - never commit to git!)

### 2. Prepare Firebase Credentials for Render
You need to convert the JSON file to a single-line string:

**Option A: Using Python (Recommended)**
```bash
python -c "import json; print(json.dumps(json.load(open('path/to/your-firebase-key.json'))))"
```

**Option B: Using Node.js**
```bash
node -e "console.log(JSON.stringify(require('./path/to/your-firebase-key.json')))"
```

**Option C: Manual**
- Open the JSON file
- Remove all newlines and extra spaces
- Copy the entire JSON as one line

### 3. Set Environment Variables on Render

Go to your Render dashboard → Your service → Environment

**Required Variables:**

```
FIREBASE_CREDENTIALS_JSON=<paste-the-single-line-json-here>
CLOUDINARY_CLOUD_NAME=<your-cloudinary-name>
CLOUDINARY_API_KEY=<your-cloudinary-key>
CLOUDINARY_API_SECRET=<your-cloudinary-secret>
```

**Existing Variables (verify they're still set):**
- `SECRET_KEY`
- `DATABASE_URL`
- `REDIS_URL`
- `DEBUG=False`
- `ALLOWED_HOSTS` (include your render domain)

### 4. Cloudinary Setup (if not done)
- [ ] Sign up at [Cloudinary](https://cloudinary.com/)
- [ ] Get your credentials from the dashboard
- [ ] Add them to Render environment variables

### 5. Pre-Deployment Checks
- [ ] Run tests locally: `python manage.py test`
- [ ] Check if migrations are needed: `python manage.py makemigrations --check --dry-run`
- [ ] Verify requirements.txt includes all dependencies

### 6. Deploy
```bash
git add .
git commit -m "Add Firebase authentication and Cloudinary storage"
git push origin main
```

### 7. Post-Deployment Verification
- [ ] Check Render logs for errors
- [ ] Test login at: `https://your-app.onrender.com/accounts/login/`
- [ ] Test Google Sign-In
- [ ] Test email/password login
- [ ] Test file uploads (avatar)

---

## 🔥 If Deployment Fails

**Common Issues:**

1. **"Firebase app not initialized"**
   - Check `FIREBASE_CREDENTIALS_JSON` is set correctly
   - Verify the JSON is valid (no syntax errors)

2. **"Cloudinary configuration error"**
   - Verify all 3 Cloudinary env vars are set
   - Check for typos in variable names

3. **Import errors**
   - Make sure `requirements.txt` is up to date
   - Render should auto-install from `requirements.txt`

4. **Static files not loading**
   - Run: `python manage.py collectstatic --noinput`
   - Check `STATIC_ROOT` and `STATIC_URL` in settings

---

## 📝 Notes

- Firebase credentials contain sensitive data - NEVER commit them to git
- The `.env` file is git-ignored for security
- Keep a backup of your Firebase service account JSON file
- Test everything locally before deploying to production
