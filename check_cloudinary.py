#!/usr/bin/env python
"""
Diagnostic script to check Cloudinary configuration on Render.
Run this in Render shell to see if Cloudinary is configured.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'connectflow.settings_render')
django.setup()

from django.conf import settings

print("=" * 60)
print("CLOUDINARY CONFIGURATION CHECK")
print("=" * 60)

# Check environment variables
print("\n1. ENVIRONMENT VARIABLES:")
cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME')
api_key = os.environ.get('CLOUDINARY_API_KEY')
api_secret = os.environ.get('CLOUDINARY_API_SECRET')

print(f"   CLOUDINARY_CLOUD_NAME: {'✅ SET' if cloud_name else '❌ NOT SET'}")
if cloud_name:
    print(f"      Value: {cloud_name}")

print(f"   CLOUDINARY_API_KEY: {'✅ SET' if api_key else '❌ NOT SET'}")
if api_key:
    print(f"      Value: {api_key[:5]}...{api_key[-5:]}")

print(f"   CLOUDINARY_API_SECRET: {'✅ SET' if api_secret else '❌ NOT SET'}")
if api_secret:
    print(f"      Value: {api_secret[:3]}...{api_secret[-3:]}")

# Check Django settings
print("\n2. DJANGO SETTINGS:")
file_storage = getattr(settings, 'DEFAULT_FILE_STORAGE', 'Not set')
print(f"   DEFAULT_FILE_STORAGE: {file_storage}")

if 'cloudinary' in file_storage.lower():
    print("   ✅ Using Cloudinary storage")
else:
    print("   ❌ NOT using Cloudinary (still using local storage)")

# Check installed apps
print("\n3. INSTALLED APPS:")
installed = settings.INSTALLED_APPS
has_cloudinary = 'cloudinary' in installed
has_cloudinary_storage = 'cloudinary_storage' in installed

print(f"   cloudinary: {'✅ INSTALLED' if has_cloudinary else '❌ NOT INSTALLED'}")
print(f"   cloudinary_storage: {'✅ INSTALLED' if has_cloudinary_storage else '❌ NOT INSTALLED'}")

# Try to test Cloudinary connection
print("\n4. CLOUDINARY CONNECTION TEST:")
if cloud_name and api_key and api_secret:
    try:
        import cloudinary
        import cloudinary.api
        
        # Try to get account info
        result = cloudinary.api.ping()
        print("   ✅ Connection successful!")
        print(f"      Status: {result.get('status', 'Unknown')}")
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
else:
    print("   ⚠️  Skipped - credentials not set")

# Check actual user avatars
print("\n5. USER AVATARS IN DATABASE:")
from apps.accounts.models import User

users_with_avatars = User.objects.exclude(avatar='').exclude(avatar__isnull=True)[:3]
if users_with_avatars:
    for user in users_with_avatars:
        print(f"\n   User: {user.username}")
        print(f"      Avatar field: {user.avatar}")
        try:
            print(f"      Avatar URL: {user.avatar.url}")
        except Exception as e:
            print(f"      Avatar URL: Error - {e}")
else:
    print("   No users with avatars found")

print("\n" + "=" * 60)
print("DIAGNOSIS COMPLETE")
print("=" * 60)

# Summary
print("\n🎯 SUMMARY:")
if cloud_name and api_key and api_secret:
    if 'cloudinary' in file_storage.lower():
        print("✅ Cloudinary is CONFIGURED and ACTIVE!")
        print("\n📝 Next steps:")
        print("   1. Upload a NEW profile image")
        print("   2. Check if URL starts with: https://res.cloudinary.com/")
        print("   3. Old images won't move automatically - need to re-upload")
    else:
        print("⚠️  Credentials are set but Django is NOT using Cloudinary!")
        print("\n🔧 Possible issues:")
        print("   1. App needs to restart after adding env vars")
        print("   2. Check if settings_render.py is being used (DJANGO_SETTINGS_MODULE)")
        print("   3. Manual redeploy might be needed")
else:
    print("❌ Cloudinary credentials are NOT SET in environment!")
    print("\n🔧 Fix:")
    print("   1. Add environment variables in Render dashboard")
    print("   2. Save changes and wait for redeploy")
    print("   3. Run this script again")

print("\n" + "=" * 60)
