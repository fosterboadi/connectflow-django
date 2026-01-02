#!/usr/bin/env python
"""
Deployment Health Check Script
Run this on Render to diagnose 500 errors
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'connectflow.settings')
django.setup()

from django.core.management import call_command
from django.db import connection

print("=" * 60)
print("CONNECTFLOW DEPLOYMENT HEALTH CHECK")
print("=" * 60)

# 1. Check Database Connection
print("\n1. Database Connection...")
try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
    print("   ✅ Database connected successfully")
except Exception as e:
    print(f"   ❌ Database connection failed: {e}")
    sys.exit(1)

# 2. Check for Unapplied Migrations
print("\n2. Checking Migrations...")
try:
    from django.db.migrations.executor import MigrationExecutor
    executor = MigrationExecutor(connection)
    plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
    
    if plan:
        print(f"   ⚠️  {len(plan)} unapplied migrations found:")
        for migration, backwards in plan:
            print(f"      - {migration.app_label}.{migration.name}")
        print("\n   Run: python manage.py migrate")
    else:
        print("   ✅ All migrations applied")
except Exception as e:
    print(f"   ❌ Migration check failed: {e}")

# 3. Check Static Files
print("\n3. Static Files...")
static_root = os.environ.get('STATIC_ROOT', 'static')
if os.path.exists(static_root) and os.listdir(static_root):
    print(f"   ✅ Static files found in {static_root}")
else:
    print(f"   ⚠️  Static files not found. Run: python manage.py collectstatic --noinput")

# 4. Check Environment Variables
print("\n4. Environment Variables...")
required_vars = [
    'SECRET_KEY',
    'DATABASE_URL',
    'CLOUDINARY_CLOUD_NAME',
    'CLOUDINARY_API_KEY',
    'CLOUDINARY_API_SECRET'
]
missing_vars = []
for var in required_vars:
    if os.environ.get(var):
        print(f"   ✅ {var} is set")
    else:
        print(f"   ❌ {var} is missing")
        missing_vars.append(var)

if missing_vars:
    print(f"\n   ⚠️  Missing environment variables: {', '.join(missing_vars)}")

# 5. Test Template Rendering
print("\n5. Template Check...")
try:
    from django.template.loader import get_template
    template = get_template('chat_channels/channel_detail.html')
    print("   ✅ channel_detail.html template loads successfully")
except Exception as e:
    print(f"   ❌ Template error: {e}")

print("\n" + "=" * 60)
print("HEALTH CHECK COMPLETE")
print("=" * 60)
