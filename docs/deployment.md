# Deployment Guide

This project is deployed as a Django app with PostgreSQL and Redis-backed real-time features.

## Prerequisites

- Python environment with dependencies installed
- PostgreSQL database
- Redis (for Channels)
- Cloudinary configuration (media)
- Billing/auth provider keys as required

## Environment Variables

At minimum, configure:

- `PAYSTACK_SECRET_KEY`
- `PLATFORM_SECRET_KEY`
- `CLOUDINARY_CLOUD_NAME`
- `FIREBASE_CREDENTIALS_PATH`

## Build & Release Checklist

1. Install dependencies from `requirements*.txt`.
2. Run migrations.
3. Run app checks/tests.
4. Confirm static and media settings.
5. Validate websocket/presence features.
6. Validate platform admin and billing paths.
7. Deploy and smoke test key routes.

## Post-Deploy Smoke Tests

- Login/register
- Channels/messages
- Project pages
- Support tickets
- Performance dashboard/history
