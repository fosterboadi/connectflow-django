# Performance Module Guide

The performance app provides KPI setup, assignment, review workflows, and history tracking.

## Main Capabilities

- KPI metric definition and weighting
- Assignment by role/team/member
- Review creation and finalization
- Score generation and manual override
- Historical performance tracking

## Key Data Models

- `KPIMetric`
- `KPIThreshold`
- `KPIAssignment`
- `PerformanceReview`
- `PerformanceScore`

## Main Routes

- Manager:
  - `/performance/team/overview/`
  - `/performance/review/create/`
- Member:
  - `/performance/my/dashboard/`
  - `/performance/my/history/`

## API Endpoints

- `GET /performance/api/metrics/`
- `GET /performance/api/my-performance/`
- `GET /performance/api/team-performance/`

## Development

For implementation details in code structure, see:

- `apps/performance/README.md`
