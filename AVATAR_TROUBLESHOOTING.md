# Profile Image Troubleshooting Guide

## ✅ What I've Fixed

### 1. **Media Context Processor** (settings.py)
   - Added `django.template.context_processors.media` 
   - Required for `{{ MEDIA_URL }}` in templates

### 2. **Cloudinary Integration** (settings_render.py)
   - Configured Cloudinary for persistent storage on Render
   - Render's free tier deletes files on redeploy - Cloudinary solves this
   - Conditional setup: only uses Cloudinary if env vars are set

### 3. **Error Handling in Templates**
   - Added `onerror` handlers to show fallback avatars
   - Added cache-busting timestamps to avatar URLs
   - Graceful degradation if image fails to load

### 4. **Debug Logging** (views.py)
   - Added console logging when avatar is saved
   - Shows form validation errors to user
   - Helps identify upload issues

---

## 🔍 How to Diagnose the Issue

### On Render.com (Production):

1. **Check Render Logs**:
   - Go to https://dashboard.render.com/
   - Click your `connectflow-pro` service
   - Click "Logs" tab
   - Look for:
     ```
     [DEBUG] Avatar saved: avatars/filename.jpg
     [DEBUG] Avatar URL: https://res.cloudinary.com/...
     ```

2. **Check if Cloudinary is Configured**:
   - In Render dashboard, go to "Environment" tab
   - Verify these 3 variables exist:
     - `CLOUDINARY_CLOUD_NAME`
     - `CLOUDINARY_API_KEY`
     - `CLOUDINARY_API_SECRET`
   - If missing → Images save locally but disappear on redeploy
   - If present → Images should upload to Cloudinary

3. **Check Browser Console**:
   - Open DevTools (F12)
   - Go to "Console" tab
   - Look for errors like:
     - `404 Not Found` → Image URL is wrong
     - `403 Forbidden` → Cloudinary credentials issue
     - `Mixed Content` → HTTP/HTTPS issue

4. **Check Network Tab**:
   - Open DevTools → "Network" tab
   - Upload an image
   - Look for the avatar image request
   - Check the URL it's trying to load
   - If URL starts with `/media/` → Not using Cloudinary (will break on redeploy)
   - If URL starts with `https://res.cloudinary.com/` → Using Cloudinary ✅

---

## 🎯 Most Common Issues & Solutions

### Issue 1: "Upload successful but image doesn't show"

**Diagnosis:**
- Form says "Profile updated successfully"
- But avatar area still shows initials/placeholder

**Causes:**
1. **Browser cache** - Old page cached
2. **Cloudinary not configured** - Image saved locally (will disappear)
3. **Image URL broken** - File exists but URL is wrong

**Solutions:**
1. Hard refresh browser: `Ctrl + Shift + R` or `Ctrl + F5`
2. Check if Cloudinary env vars are set in Render
3. Check browser console for 404 errors
4. Look at Render logs for "[DEBUG] Avatar URL:"

---

### Issue 2: "Images disappear after redeployment"

**Diagnosis:**
- Images work after upload
- Stop working after Render redeploys

**Cause:**
- Cloudinary NOT configured
- Images saving to local filesystem
- Render deletes local files on redeploy

**Solution:**
1. Set up Cloudinary (see CLOUDINARY_SETUP.md)
2. Add environment variables to Render
3. Wait for redeploy
4. Upload a NEW image (old ones are lost)

---

### Issue 3: "403 Forbidden or broken image icon"

**Diagnosis:**
- Broken image icon shows
- Browser console shows 403 error
- Image URL is correct but won't load

**Causes:**
1. **Invalid Cloudinary credentials**
2. **Cloudinary URL expired/malformed**
3. **CORS issues**

**Solutions:**
1. Double-check Cloudinary credentials in Render
2. Make sure no spaces/typos in env vars
3. Check Cloudinary dashboard - is account active?
4. Try uploading a new image

---

### Issue 4: "Mixed Content Warning"

**Diagnosis:**
- Browser console: "Mixed Content: The page was loaded over HTTPS, but requested an insecure resource"
- Images won't load on HTTPS site

**Cause:**
- Image URL uses `http://` instead of `https://`

**Solution:**
- Already fixed in settings_render.py with `secure=True`
- If still happening, check Cloudinary dashboard settings

---

## 🧪 Test Locally

To test avatar upload locally without Cloudinary:

1. **Start dev server:**
   ```bash
   python manage.py runserver
   ```

2. **Upload an image** to http://localhost:8000/accounts/profile/settings/

3. **Check if it shows** - should work locally

4. **Check the file was saved:**
   ```bash
   dir media\avatars
   ```

5. **Check the URL** in browser DevTools:
   - Should be: `http://localhost:8000/media/avatars/filename.jpg`

---

## 📋 Checklist for Production

Before considering this "fixed" on Render:

- [ ] Cloudinary account created
- [ ] 3 environment variables added to Render
- [ ] Latest code deployed (check commit on GitHub)
- [ ] Render build completed successfully
- [ ] Service is "Live" not "Building"
- [ ] Hard refresh browser (Ctrl+Shift+R)
- [ ] Upload a NEW image (don't reuse old one)
- [ ] Check browser console for errors
- [ ] Check Render logs for "[DEBUG] Avatar URL"
- [ ] Avatar URL should start with `https://res.cloudinary.com/`

---

## 🔧 Quick Fixes

### If image still not showing after all above:

1. **Clear browser cache completely**
2. **Use incognito/private mode**
3. **Try different image** (small JPG, under 500KB)
4. **Check image format** - Use JPG, PNG, or GIF only
5. **Check file size** - Must be under 2MB (see forms.py)

---

## 📞 Still Not Working?

Check these advanced issues:

1. **Database issue?**
   ```python
   # In Render shell
   from apps.accounts.models import User
   u = User.objects.get(username='your_username')
   print(u.avatar)  # Should show: avatars/filename.jpg
   print(u.avatar.url)  # Should show full URL
   ```

2. **Permissions issue?**
   - Cloudinary account active?
   - API limits reached? (Check Cloudinary dashboard)
   - Firewall blocking uploads?

3. **Django issue?**
   - Check `INSTALLED_APPS` has `'cloudinary'` and `'cloudinary_storage'`
   - Check `DEFAULT_FILE_STORAGE` is set correctly
   - Restart Render service manually

---

## 📌 Expected Behavior After Fix

1. Upload image in profile settings
2. See success message: "Your profile has been updated successfully!"
3. Image appears immediately (no page reload needed for preview)
4. After page reload, image loads from Cloudinary
5. Image URL starts with: `https://res.cloudinary.com/your-cloud-name/...`
6. Image persists even after Render redeploys
7. Image shows in navbar and profile page

---

## 🎓 Understanding the Flow

```
User uploads image
    ↓
Django receives file in request.FILES
    ↓
ProfileSettingsForm validates it
    ↓
form.save() triggers model save
    ↓
Django's ImageField processes it
    ↓
DEFAULT_FILE_STORAGE (Cloudinary) uploads to cloud
    ↓
Cloudinary returns URL
    ↓
Django saves URL path in database
    ↓
Template renders: {{ user.avatar.url }}
    ↓
Cloudinary storage generates full URL
    ↓
Browser loads image from Cloudinary CDN
```

---

That's the complete troubleshooting guide! If you've done all the steps in CLOUDINARY_SETUP.md and this guide, your images WILL work. 🎉
