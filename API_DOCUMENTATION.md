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

## 📡 Core API Endpoints

### **1. User & Profile Management**
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/users/me/` | Get current authenticated user details |
| `GET` | `/users/` | List all users in your organization |
| `POST` | `/users/toggle_theme/` | Switch between LIGHT/DARK theme |

### **2. Organization & Billing**
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/organizations/` | Get current organization details & subscription status |
| `GET` | `/departments/` | List all departmental units |
| `GET` | `/teams/` | List team spaces you belong to |

### **3. Collaborative Projects & Analytics**
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/projects/` | List all active shared projects |
| `POST` | `/projects/` | Create workspace (**Gatekeeper protected**: Checks plan project limit) |
| `GET` | `/projects/{id}/` | Get project milestones and roster |
| `GET` | `/projects/{id}/analytics/` | **Premium Feature**: Returns statistics (Forbidden on lower tiers) |

### **4. Channels & Messaging**
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/channels/` | List all accessible chat channels |
| `GET` | `/channels/{id}/messages/` | Retrieve full message history |
| `POST` | `/messages/` | Send text or media (**Universal file support**) |
| `DELETE` | `/messages/{id}/` | **Soft Delete** a message (tracks who deleted) |

---

## 🛡️ SaaS Gatekeeper & Business Logic

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

## 🧪 Postman Presentation Guide

This guide walks you through the exact steps to demonstrate the **ConnectFlow Pro API** during a live presentation using Postman.

### **Phase 1: The Firebase Handshake (Getting your Token)**
ConnectFlow Pro uses Firebase for secure identity. You first need a valid **ID Token**.

1.  Open your browser and log into **ConnectFlow Pro**.
2.  Open the **Browser Console** (F12) and run:
    ```javascript
    firebase.auth().currentUser.getIdToken().then(token => console.log(token))
    ```
3.  **Copy the long string of text** that appears.

### **Phase 2: Postman Authorization Login**
Tell the backend that Postman should be treated as an authorized device.

1.  Open **Postman** and create a new **POST** request.
2.  **URL:** `https://connectflow-pro.onrender.com/accounts/login/`
3.  **Headers:** `Content-Type: application/json`
4.  **Body (Raw JSON):**
    ```json
    { "id_token": "PASTE_YOUR_COPIED_TOKEN_HERE" }
    ```
5.  **Click Send.** You should receive a `{"status": "ok"}` response. Postman has now saved your **Session Cookie**.

### **Phase 3: CSRF Security (Required for POST/DELETE)**
1.  In the browser Console, run:
    ```javascript
    document.cookie.split('; ').find(row => row.startsWith('csrftoken=')).split('=')[1]
    ```
2.  In Postman, for any `POST/DELETE` request, add this header:
    *   **Key:** `X-CSRFToken`
    *   **Value:** `(The code you just copied)`

### **Phase 4: Presentation Endpoints**

| Action | URL | Talking Point |
|--------|-----|---------------|
| **GET Identity** | `/api/v1/users/me/` | "Server identifies the user, role, and organization context independently of the UI." |
| **GET Projects** | `/api/v1/projects/` | "Demonstrating organization isolation and secure data multi-tenancy." |
| **GET Analytics**| `/projects/{id}/analytics/` | "Showcasing the **Gatekeeper**. Returns 403 on basic plans, data on premium tiers." |

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