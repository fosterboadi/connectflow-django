# ConnectFlow Pro - Enterprise Collaboration Platform

ConnectFlow Pro is a high-performance, multi-tenant collaboration platform designed for modern organizations and joint ventures. It combines real-time messaging, hierarchical organizational management, and cross-company project synchronization into a secure, scalable ecosystem.

## 🚀 Key Enterprise Milestones (December 2025)

The platform has evolved into a production-ready SaaS with several critical hardening upgrades:

*   **SaaS Gatekeeper Logic:** Implemented a robust server-side enforcement layer that manages subscription plan limits (users, projects, and storage) and premium feature locks across both Web and REST API layers.
*   **Monetization Engine:** Fully integrated **Paystack** for automated recurring billing, featuring dynamic tier management and secure webhook handling.
*   **Platform Admin Suite:** A dedicated, icon-driven dashboard for internal team members (Super Admins) to manage global organizations, users, and subscription tiers.
*   **Multi-Platform REST API v1:** A comprehensive, JWT-secured API foundation ready for React Native/Flutter mobile integrations.
*   **Universal Media Delivery:** Standardized on Cloudinary with **Raw Storage** and forced **HTTPS** to ensure any file type (PDF, ZIP, Slides) is served securely and reliably.
*   **Real-time Collaboration:** Smart meeting detection for **Google Meet, Zoom, Teams, and Jitsi**, integrated directly into project timelines.

---

## ✨ Core Features

### 1. **Multi-Tenant Architecture**
- **Strict Isolation:** Data is siloed at the database level by Organization UUID.
- **Joint Ventures:** Secure "Shared Project" workspaces where multiple independent organizations can collaborate on common goals.
- **Granular Permissions:** Super Admins can explicitly toggle module access (Analytics, Chat, Projects) for individual staff members.

### 2. **Professional Communication Hub**
- **Intelligent Channels:** Automatic assignment to Department and Team channels.
- **Real-Time Messaging:** Powered by WebSockets (Django Channels) with typing indicators, presence tracking, and emoji reactions.
- **Soft Delete System:** Full audit trails with real-time delete receipts broadcasted to all participants.

### 3. **Project & Task Management**
- **Backlog & Milestones:** Track project progress with visual completion metrics.
- **Advanced Analytics:** Collaboration maps and KPI tracking (locked to premium tiers).
- **Meeting Portal:** One-click access to external video platforms with automated branding detection.

---

## 🛠️ Technology Stack

- **Backend:** Django 5.2.9 + Django REST Framework 3.16
- **Real-time:** WebSockets via Django Channels 4.3 + Redis
- **Auth:** Firebase Identity Platform (JWT-based session handshake)
- **Media:** Cloudinary (Automatic Resource Detection + Secure delivery)
- **Billing:** Paystack API (Localized for African markets)
- **Frontend:** Tailwind CSS + Vanilla JS (PWA Ready with custom Splash Screen)
- **Deployment:** Render (Production Environment) + PostgreSQL

---

## 📡 API & Documentation

ConnectFlow Pro is a "Headless-First" platform. All core business logic is accessible via our REST API.

*   **[API Guide](docs/api.md):** Authentication and key endpoint reference.
*   **[Deployment Guide](docs/deployment.md):** Production deployment checklist.
*   **[Performance Module Guide](docs/performance.md):** KPI and review workflows.
*   **[Docs Index](docs/README.md):** Full public documentation map.

---

## 🔧 Installation & Setup

```bash
# Clone and Enter
git clone https://github.com/fosterboadi/connectflow-django.git
cd connectflow-django

# Setup Environment
python -m venv venv
source venv/bin/activate # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Initial Setup
python manage.py migrate
python manage.py runserver
```

## 📝 Required Environment Variables (Production)
| Variable | Purpose |
| :--- | :--- |
| `STRIPE_SECRET_KEY` | (Legacy Support) |
| `PAYSTACK_SECRET_KEY` | Primary Billing |
| `PLATFORM_SECRET_KEY` | Super Admin Initialization |
| `CLOUDINARY_CLOUD_NAME` | Media Hosting |
| `FIREBASE_CREDENTIALS_PATH` | Secure Identity |

---

## 👨‍💻 Vision & Leadership
**Author:** Foster Boadi  
**Status:** Launch Ready (v1.0.0)  
**Last Updated:** December 26, 2025
