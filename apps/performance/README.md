# Performance Management App

## Overview

Complete KPI and Performance Evaluation system for ConnectFlow. Supports role-based metrics, automated scoring, manual overrides, and comprehensive audit trails.

## Structure

```
apps/performance/
├── models.py                    # Database models
├── views.py                     # Manager & Member views
├── urls.py                      # URL routing
├── admin.py                     # Django admin configuration
├── permissions.py               # Role-based access control
├── utils.py                     # Helper utilities
├── tests.py                     # Test suite
├── services/
│   ├── __init__.py
│   └── performance_scoring.py  # Scoring service layer
└── management/
    └── commands/
        └── generate_reviews.py # Bulk review generation
```

## Models

- **KPIMetric**: Define performance metrics
- **KPIThreshold**: Set performance targets
- **KPIAssignment**: Assign metrics to users
- **PerformanceReview**: Review records
- **PerformanceScore**: Individual metric scores
- **PerformanceAuditLog**: Complete audit trail

## Key Features

✅ **Flexible KPI Metrics**: 5 metric types (numeric, percentage, rating, boolean, threshold)  
✅ **Automated Scoring**: Calculate scores from task performance  
✅ **Manual Overrides**: Justified manual adjustments  
✅ **Weighted Scores**: Configurable metric weights  
✅ **Review Locking**: Finalized reviews are immutable  
✅ **Role-Based Permissions**: Strict access control  
✅ **Audit Logging**: Track all actions  
✅ **Historical Preservation**: Never delete, use versioning  

## Usage

### Create KPI Metric

```python
from apps.performance.models import KPIMetric
from decimal import Decimal

metric = KPIMetric.objects.create(
    organization=org,
    name="Task Completion Rate",
    metric_type=KPIMetric.MetricType.PERCENTAGE,
    weight=Decimal('2.00'),
    role='TEAM_MEMBER',
    created_by=manager
)
```

### Conduct Review

```python
from apps.performance.models import PerformanceReview
from apps.performance.services import PerformanceScoringService
from datetime import date

# Create review
review = PerformanceReview.objects.create(
    user=member,
    reviewer=manager,
    organization=org,
    review_period_start=date(2026, 1, 1),
    review_period_end=date(2026, 1, 31)
)

# Auto-generate scores
PerformanceScoringService.generate_review_scores(review, manager)

# Finalize
PerformanceScoringService.finalize_review(review, manager)
```

### Bulk Generate Reviews

```bash
python manage.py generate_reviews --period 2026-01 --org <org_id>
python manage.py generate_reviews --period 2026-Q1 --org <org_id> --auto-finalize
```

## API Endpoints

- `GET /performance/api/metrics/` - List KPI metrics
- `GET /performance/api/my-performance/` - Personal performance data
- `GET /performance/api/team-performance/` - Team performance (managers only)
- `POST /performance/review/create/` - Create review
- `POST /performance/score/<id>/override/` - Override score
- `POST /performance/review/<id>/finalize/` - Finalize review

## Permissions

| Role | Create KPI | Assign KPI | Create Review | View Team | Finalize |
|------|------------|------------|---------------|-----------|----------|
| Admin | ✅ | ✅ | ✅ | ✅ | ✅ |
| Manager | ✅ | ✅ (own team) | ✅ (own team) | ✅ | ✅ |
| Member | ❌ | ❌ | ❌ | ❌ | ❌ |

## Testing

```bash
python manage.py test apps.performance
```

All 11 tests passing ✅

## Documentation

See `docs/performance.md` for the public performance guide.

## Admin Panel

Access at: `/admin/performance/`

---

**Version**: 1.0  
**Status**: Production Ready  
**Last Updated**: January 2026
