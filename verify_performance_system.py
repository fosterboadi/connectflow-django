"""
Verification script for KPI & Performance Management System.

Run with: python verify_performance_system.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'connectflow.settings')
django.setup()

from django.conf import settings
from apps.performance.models import (
    KPIMetric, KPIThreshold, KPIAssignment,
    PerformanceReview, PerformanceScore, PerformanceAuditLog
)

def verify_system():
    """Verify the performance system is properly configured."""
    
    print("🔍 Verifying KPI & Performance Management System...")
    print("=" * 60)
    
    checks = []
    
    # 1. Check app is installed
    app_installed = 'apps.performance' in settings.INSTALLED_APPS
    checks.append(("App in INSTALLED_APPS", app_installed))
    
    # 2. Check models are accessible
    try:
        KPIMetric.objects.all().count()
        models_ok = True
    except Exception as e:
        models_ok = False
    checks.append(("Models accessible", models_ok))
    
    # 3. Check database tables exist
    try:
        from django.db import connection
        tables = connection.introspection.table_names()
        required_tables = [
            'kpi_metrics',
            'kpi_thresholds',
            'kpi_assignments',
            'performance_reviews',
            'performance_scores',
            'performance_audit_logs'
        ]
        tables_exist = all(table in tables for table in required_tables)
    except Exception:
        tables_exist = False
    checks.append(("Database tables exist", tables_exist))
    
    # 4. Check services import
    try:
        from apps.performance.services import PerformanceScoringService
        services_ok = True
    except ImportError:
        services_ok = False
    checks.append(("Services importable", services_ok))
    
    # 5. Check permissions import
    try:
        from apps.performance.permissions import PerformancePermissions
        permissions_ok = True
    except ImportError:
        permissions_ok = False
    checks.append(("Permissions importable", permissions_ok))
    
    # 6. Check utils import
    try:
        from apps.performance.utils import ReviewPeriodHelper
        utils_ok = True
    except ImportError:
        utils_ok = False
    checks.append(("Utils importable", utils_ok))
    
    # 7. Check views import
    try:
        from apps.performance import views
        views_ok = True
    except ImportError:
        views_ok = False
    checks.append(("Views importable", views_ok))
    
    # 8. Check URLs configured
    try:
        from django.urls import reverse
        # This will raise NoReverseMatch if URL not configured
        reverse('performance:my_dashboard')
        urls_ok = True
    except Exception:
        urls_ok = False
    checks.append(("URLs configured", urls_ok))
    
    # 9. Check admin registered
    try:
        from django.contrib import admin
        admin_ok = KPIMetric in [m.model for m in admin.site._registry.values()]
    except Exception:
        admin_ok = False
    checks.append(("Admin registered", admin_ok))
    
    # 10. Check migrations applied
    try:
        from django.db.migrations.recorder import MigrationRecorder
        recorder = MigrationRecorder(connection)
        applied = recorder.applied_migrations()
        migration_ok = ('performance', '0001_initial') in applied
    except Exception:
        migration_ok = False
    checks.append(("Migrations applied", migration_ok))
    
    # Print results
    print("\n✓ System Checks:")
    print("-" * 60)
    
    all_passed = True
    for check_name, status in checks:
        icon = "✅" if status else "❌"
        print(f"{icon} {check_name}")
        if not status:
            all_passed = False
    
    print("\n" + "=" * 60)
    
    if all_passed:
        print("✅ ALL CHECKS PASSED - System is ready for use!")
        print("\n📚 Documentation:")
        print("   - Public Guide: docs/performance.md")
        print("   - Dev Guide: apps/performance/README.md")
        print("\n🔗 Admin Panel:")
        print("   - http://localhost:8000/admin/performance/")
        print("\n🧪 Run Tests:")
        print("   - python manage.py test apps.performance")
        return 0
    else:
        print("❌ SOME CHECKS FAILED - Please review the errors above")
        return 1

if __name__ == '__main__':
    exit_code = verify_system()
    exit(exit_code)
