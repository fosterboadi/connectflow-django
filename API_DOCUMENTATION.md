# ConnectFlow Pro - API v1 Documentation & Multi-Platform Guide

## 📋 Table of Contents
- [Project Evolution](#project-evolution)
- [API Architecture (v1)](#api-architecture-v1)
- [Authentication & Security](#authentication--security)
- [Core API Endpoints](#core-api-endpoints)
- [Real-time WebSocket API](#real-time-websocket-api)
- [Postman Testing Guide](#postman-testing-guide)
- [Demonstration Script](#demonstration-script)

---

## 🚀 Project Evolution

ConnectFlow Pro has evolved from a traditional Django website into a **Multi-Platform Communication Hub**. While the web dashboard continues to serve HTML, our new **REST API v1** allows native mobile apps (React Native/Flutter) and external integrations to interact with the exact same data source.

### **The December 2025 Leap**
*   **API v1 Foundation:** Modularized backend with dedicated serializers and viewsets.
*   **SaaS Gatekeeper:** Integrated subscription limit enforcement (Users, Projects, Features) at the Serializer level.
*   **System Hardening:** Standardized media handling via Cloudinary `resource_type='auto'`.
*   **Data Integrity:** Implemented "Soft Delete" with real-time delete receipts.
*   **Mobile Readiness:** Built-in CORS and Firebase-ready authentication logic.

---

## 🏗️ API Architecture (v1)

### **Base URL**
`https://connectflow-pro.onrender.com/api/v1/`

### **Technology Stack**
- **Framework:** Django 5.2.9 + Django REST Framework 3.16
- **Real-time:** WebSockets via Django Channels + Redis
- **Billing:** Multi-provider support (Paystack) with automated Webhooks
- **Media:** Cloudinary (Secure HTTPS + Universal file support)

---

## 📡 Complete REST API Reference (v1)

### **1. Identity & Profile**
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/users/me/` | Identify current user, role, and org context. |
| `GET` | `/users/` | List all members within your organization. |
| `GET` | `/users/{id}/` | Retrieve a specific member's professional profile. |
| `POST` | `/users/toggle_theme/` | Toggle between LIGHT and DARK UI modes. |

### **2. Organization Structure**
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/organizations/` | View organization metadata (branding, industry, status). |
| `GET` | `/departments/` | List all departmental units in the organization. |
| `POST` | `/departments/` | Create a new department (Managers only). |
| `GET` | `/teams/` | List all internal teams. |
| `POST` | `/teams/` | Form a new internal team. |

### **3. Shared Projects & Analytics**
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/projects/` | List workspaces shared between organizations. |
| `POST` | `/projects/` | Launch workspace (**Gatekeeper**: Validates plan project limits). |
| `GET` | `/projects/{id}/` | Retrieve roster, milestones, and status of a project. |
| `GET` | `/projects/{id}/analytics/`| **Premium**: Returns collaboration maps and KPI data. |

### **4. Real-time Communication**
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/channels/` | List all accessible private and project channels. |
| `GET` | `/channels/{id}/messages/` | Retrieve message history for a specific channel. |
| `POST` | `/messages/` | Send message (**Universal Support**: text, image, file, voice). |
| `PATCH` | `/messages/{id}/` | Edit a previously sent message. |
| `DELETE` | `/messages/{id}/` | **Soft Delete**: Archives message and broadcasts delete receipt. |

### **5. SaaS Management & Billing**
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/billing/plans/` | List available subscription tiers and their benefits. |
| `POST` | `/billing/paystack/{plan_id}/` | Initialize a Paystack transaction for tier upgrade. |
| `POST` | `/webhooks/paystack/` | System listener for automated plan activation. |

---

## 🛡️ SaaS Gatekeeper Logic

The API is architected to protect your business model automatically.

### **1. Plan Limit Enforcement**
When a `POST` request is sent to `/projects/`, the **SharedProjectSerializer** validates the organization's subscription plan. If the limit is exceeded, the API returns:
*   **Status:** `400 Bad Request`
*   **Message:** `"Organization has reached the limit of X project(s)..."`

### **2. Feature Locking**
Endpoints like `/projects/{id}/analytics/` use the **HasSubscriptionFeature** permission class. If the organization's plan has `has_analytics=False`, the API returns:
*   **Status:** `403 Forbidden`
*   **Message:** `"Project Analytics is a premium feature."`

---

## 🧪 Postman Presentation Guide (Pure API Flow)

This guide walks you through a professional, **headless authentication flow**—exactly how a mobile app (Flutter/React Native) would interact with ConnectFlow Pro.

### **Step 1: The Firebase Handshake (Get ID Token)**
Instead of a browser, we request a secure identity token directly from Google's Identity Toolkit.

1.  **Method:** `POST`
2.  **URL:** `https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=AIzaSyAfkKZt1a7oKZDKrPpKIGGtc6inABx5-rw`
3.  **Body (Raw JSON):**
    ```json
    {
        "email": "your-staff-email@example.com",
        "password": "your-password",
        "returnSecureToken": true
    }
    ```
4.  **Action:** Click **Send**.
5.  **Result:** Copy the `"idToken"` from the response. 
    *   *Talk Track:* "We are starting with a pure API-to-API handshake. We request a secure JWT from Firebase, proving our identity without ever touching a browser."

### **Step 2: Backend Authorization (Session Exchange)**
Tell the ConnectFlow Django server to trust this Postman session.

1.  **Method:** `POST`
2.  **URL:** `https://connectflow-pro.onrender.com/accounts/login/`
3.  **Body (Raw JSON):**
    ```json
    { "id_token": "PASTE_THE_TOKEN_FROM_STEP_1" }
    ```
4.  **Headers:** Add `Referer` = `https://connectflow-pro.onrender.com` (for CSRF safety).
5.  **Action:** Click **Send**.
6.  **Result:** You should receive `{"status": "ok"}`. Postman has now saved your session cookies.
    *   *Talk Track:* "Now, we pass that token to our Django backend. The server verifies the signature with Google's public keys and establishes a secure, isolated session for this device."

### **Step 3: The Live Data Demo**

| Action | URL | Talk Track |
|--------|-----|------------|
| **Identify** | `GET /api/v1/users/me/` | "The API now identifies my role and organization context based on that handshake." |
| **Isolate** | `GET /api/v1/projects/` | "Demonstrating secure multi-tenancy. I only see projects I am authorized to access." |
| **Gatekeep**| `GET /projects/{id}/analytics/`| "Showcasing business logic. Lower tiers get a **403 Forbidden**; premium tiers see full data." |

---

## 🎓 Demonstration Script

**1. Subscription Gatekeeper (3 mins)**
Attempt to create a project via the API while on a "Starter" plan. Show the `400 Bad Request`. Upgrade the plan in the Platform Admin, try again, and show the `201 Created` success.

**2. Premium Feature Lock (2 mins)**
Request `/projects/{id}/analytics/` from a basic account. Show the `403 Forbidden`. This proves the API is aware of the business tiers.

**3. Universal Media Access (2 mins)**
Upload a non-image file (PDF/ZIP) and show the generated URL. Explain that the API forces **HTTPS** and uses **Raw Storage** to ensure the files are accessible and secure.

**4. Real-time Presence (2 mins)**
Open two browser windows. Show how changing status in one is reflected via the WebSocket API in the other instantly.

---

**This API v1 serves as the production-ready gateway for the ConnectFlow Pro ecosystem.** 🎓