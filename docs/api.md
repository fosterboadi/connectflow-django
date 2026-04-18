# API Guide

ConnectFlow provides REST endpoints for authentication, collaboration, support, and performance workflows.

## Authentication

- The API uses JWT-based authentication.
- Include `Authorization: Bearer <token>` for protected endpoints.

## Core Areas

- Accounts and organization access
- Channels and messaging
- Shared project collaboration
- Support/ticketing flows
- Performance/KPI APIs:
  - `GET /performance/api/metrics/`
  - `GET /performance/api/my-performance/`
  - `GET /performance/api/team-performance/`

## Client Integration

- Mobile/web clients should treat the API as the source of truth for business operations.
- Use role-aware UI logic (manager/admin/member) aligned with server permissions.

## Notes

- Keep all credentials in environment variables.
- Prefer HTTPS-only requests in production.
