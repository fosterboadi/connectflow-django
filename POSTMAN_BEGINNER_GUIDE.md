# 🎤 ConnectFlow Pro - Quick Presentation API Guide

**🌐 For Presentations:** Use the deployed API at `https://connectflow.onrender.com/api/v1/`

**📖 Full Presentation Guide:** See `PRESENTATION_API_GUIDE.md`

---

## 🚀 Quick Start for Demos (2 Minutes)

### Open Your Browser & Test Immediately:

**1. API Root** - See all endpoints:
```
https://connectflow.onrender.com/api/v1/
```

**2. Login** (web interface):
```
https://connectflow.onrender.com/accounts/login/
```

**3. Browse APIs** (after login):
```
https://connectflow.onrender.com/api/v1/organizations/
https://connectflow.onrender.com/api/v1/channels/
https://connectflow.onrender.com/api/v1/messages/
https://connectflow.onrender.com/api/v1/users/
```

### Use Postman for Advanced Testing:

**Login & Get Token:**
```
POST https://connectflow.onrender.com/api/v1/login/

Body (JSON):
{
  "email": "your-email@example.com",
  "password": "your-password"
}
```

**Use Token for Requests:**
```
Headers:
Authorization: Token YOUR_TOKEN_HERE
Content-Type: application/json
```

---

## 📚 Complete Guides Available

- **🎤 PRESENTATION_API_GUIDE.md** - Full presentation testing guide with deployed API
- **📖 This File** - Comprehensive Postman tutorial for local development

---

# 🚀 Complete ConnectFlow Pro API Testing Guide with Postman

**For Local Development & Learning**

**🌐 Testing Live Deployment?** See `PRESENTATION_API_GUIDE.md` instead!

---

## 📋 Table of Contents
1. [Browser Testing (Quick Start!)](#browser-testing-quick-start)
2. [What You'll Need](#what-youll-need)
3. [Step 1: Install Postman](#step-1-install-postman)
4. [Step 2: Start Your Local Server](#step-2-start-your-local-server)
5. [Step 3: Understanding API Testing](#step-3-understanding-api-testing)
6. [Step 4: Test Your First API (Login)](#step-4-test-your-first-api-login)
7. [Step 5: Save Your Token](#step-5-save-your-token)
8. [Step 6: Test Authenticated Endpoints](#step-6-test-authenticated-endpoints)
8. [Complete Channel Operations](#complete-channel-operations)
9. [Complete Chat/Message Operations](#complete-chatmessage-operations)
10. [Direct Messaging (DMs)](#direct-messaging-dms)
11. [Advanced Features](#advanced-features)
12. [Common API Tests](#common-api-tests)
13. [Troubleshooting](#troubleshooting)

---

## 🌐 Browser Testing (Quick Start!)

**Yes, you can test API endpoints in your browser!** But with limitations:

### ✅ What Works in Browser (GET Requests Only)

After logging into the web app (http://127.0.0.1:8000/), you can test these in your browser:

**1. API Root (Browse All Endpoints)**
```
http://127.0.0.1:8000/api/v1/
```
👉 Shows all available API endpoints with a nice browsable interface!

**2. List Organizations**
```
http://127.0.0.1:8000/api/v1/organizations/
```

**3. List Channels**
```
http://127.0.0.1:8000/api/v1/channels/
```

**4. List Messages**
```
http://127.0.0.1:8000/api/v1/messages/
```

**5. List Users**
```
http://127.0.0.1:8000/api/v1/users/
```

**6. List Departments**
```
http://127.0.0.1:8000/api/v1/departments/
```

**7. List Teams**
```
http://127.0.0.1:8000/api/v1/teams/
```

**8. List Projects**
```
http://127.0.0.1:8000/api/v1/projects/
```

**9. Support Tickets**
```
http://127.0.0.1:8000/api/v1/tickets/
```

### 🎨 Django REST Framework's Browsable API

Django REST Framework provides a **beautiful web interface** for testing APIs!

**How to Use:**

1. **Start your server:**
   ```bash
   python manage.py runserver
   ```

2. **Login to web interface first:**
   ```
   http://127.0.0.1:8000/accounts/login/
   ```
   Login with: `test@connectflow.com` / `Password123!`

3. **Navigate to API root:**
   ```
   http://127.0.0.1:8000/api/v1/
   ```

4. **You'll see a nice interface with:**
   - ✅ All available endpoints listed
   - ✅ Click any endpoint to view details
   - ✅ Forms to submit data (POST, PUT, DELETE)
   - ✅ Raw JSON view
   - ✅ Formatted responses

**Example - Testing in Browser:**

**Step 1:** Go to organizations endpoint
```
http://127.0.0.1:8000/api/v1/organizations/
```

**Step 2:** You'll see:
- Your organization data in pretty JSON format
- A form at the bottom to POST new data
- Options dropdown (GET, POST, OPTIONS, etc.)
- Content type selector (JSON, form, etc.)

**Step 3:** Click on a specific endpoint like:
```
http://127.0.0.1:8000/api/v1/channels/
```

**Step 4:** To CREATE a channel via browser form:
1. Scroll to the bottom
2. You'll see a form with fields:
   - name
   - description
   - channel_type
   - organization
3. Fill it in and click "POST"
4. See the response instantly!

### ❌ What Doesn't Work in Browser

**1. Cannot test without logging in first**
- Browser APIs require web login session
- Postman uses Token authentication (different!)

**2. Limited testing capabilities**
- No easy way to customize headers
- No environment variables
- No request history
- Can't save/organize requests

**3. Cannot test external APIs**
- Only works for your local server
- Requires Django session authentication

### 🔄 Browser vs Postman Comparison

| Feature | Browser | Postman |
|---------|---------|---------|
| **GET requests** | ✅ Easy | ✅ Easy |
| **POST/PUT/DELETE** | ⚠️ Via form only | ✅ Full control |
| **Authentication** | 🔑 Web login needed | 🎫 Token-based |
| **Save requests** | ❌ No | ✅ Collections |
| **Environment variables** | ❌ No | ✅ Yes |
| **Custom headers** | ❌ Hard | ✅ Easy |
| **File uploads** | ⚠️ Limited | ✅ Full support |
| **Test automation** | ❌ No | ✅ Yes |
| **Pretty interface** | ✅ Django REST UI | ✅ Postman UI |
| **Best for** | 👀 Quick viewing | 🧪 Full testing |

### 🎯 When to Use Browser vs Postman

**Use Browser when:**
- ✅ Quickly viewing data (GET requests)
- ✅ Already logged into web app
- ✅ Testing simple CRUD operations
- ✅ Learning API structure
- ✅ Don't want to install anything

**Use Postman when:**
- ✅ Need to test authentication (login/logout)
- ✅ Testing complex requests with custom headers
- ✅ Uploading files
- ✅ Saving and organizing test requests
- ✅ Sharing API tests with team
- ✅ Automating tests
- ✅ Testing from different user accounts

### 🚀 Quick Browser Testing Workflow

**1. Start Server**
```bash
cd D:\Projects\connectflow-django
python manage.py runserver
```

**2. Login to Web App**
```
http://127.0.0.1:8000/accounts/login/
Email: test@connectflow.com
Password: Password123!
```

**3. Visit API Root**
```
http://127.0.0.1:8000/api/v1/
```

**4. Explore Endpoints**
Click on any link like:
- `/api/v1/organizations/`
- `/api/v1/channels/`
- `/api/v1/users/`

**5. Test Creating Data**
- Scroll to bottom of any endpoint page
- Fill in the form
- Select content type (JSON)
- Click POST/PUT/DELETE button

**Example - Create a Channel in Browser:**

1. Go to: `http://127.0.0.1:8000/api/v1/channels/`
2. Scroll to bottom form
3. Select "application/json" from content dropdown
4. Enter JSON:
   ```json
   {
     "name": "browser-test-channel",
     "description": "Created from browser!",
     "channel_type": "TEAM",
     "organization": "your-org-uuid-here"
   }
   ```
5. Click "POST"
6. See your new channel in the response!

### 💡 Pro Tip: Use Both!

**Best Workflow:**
1. **Browser** - Quick exploration and viewing
2. **Postman** - Serious testing and automation
3. **Browser** - Verify changes made via Postman

---

## What You'll Need

- ✅ Postman installed (free)
- ✅ ConnectFlow Pro running locally
- ✅ A test user account (email and password)
- ✅ **An organization** (you'll check this in Step 6.5)
- ✅ 15-30 minutes of your time

---

## ⚠️ CRITICAL SETUP NOTE

**Before creating any channels, you MUST:**
1. Login to get your token (Step 4)
2. **Check your organization** (Step 6.5 - NEW!)
3. **Save your organization UUID** - you'll need it for ALL channel operations

**Without an organization, you CANNOT create channels!** This is the #1 reason for errors.

---

## Step 1: Install Postman

### Download Postman

1. **Go to:** https://www.postman.com/downloads/
2. **Click:** Download for Windows (or Mac/Linux)
3. **Install:** Run the installer and follow the prompts
4. **Sign Up (Optional):** You can skip this and use it without an account

### Launch Postman

1. Open Postman from your desktop
2. If asked to sign in, click **"Skip and go to the app"** (you don't need an account for local testing)
3. You should see a window like this:

```
┌─────────────────────────────────────┐
│  Postman                       × ▭ ▢ │
├─────────────────────────────────────┤
│ ➕ New  |  Import  |  Runner        │
├─────────────────────────────────────┤
│ Collections  |  Environments        │
│                                     │
│  My Workspace                       │
│  ┌─────────────────────────────┐  │
│  │                             │  │
│  │   Click "New" to create     │  │
│  │   your first request        │  │
│  │                             │  │
│  └─────────────────────────────┘  │
└─────────────────────────────────────┘
```

---

## Step 2: Start Your Local Server

### Option A: Using Command Prompt

1. **Open Command Prompt** (Press `Win + R`, type `cmd`, press Enter)
2. **Navigate to your project:**
   ```bash
   cd D:\Projects\connectflow-django
   ```
3. **Start the server:**
   ```bash
   python manage.py runserver
   ```
4. **Wait for this message:**
   ```
   Starting development server at http://127.0.0.1:8000/
   Quit the server with CTRL-BREAK.
   ```

### Option B: Using VS Code Terminal

1. Open VS Code
2. Press `` Ctrl + ` `` to open terminal
3. Run:
   ```bash
   cd D:\Projects\connectflow-django
   python manage.py runserver
   ```

### ✅ Server is Ready!

Your server is now running at: **http://127.0.0.1:8000/**

**Keep this terminal window open!** Don't close it while testing.

---

## Step 3: Understanding API Testing

### What is an API?

Think of an API as a waiter in a restaurant:
- **You (Client)** → Tell the waiter what you want
- **Waiter (API)** → Takes your order to the kitchen
- **Kitchen (Server)** → Prepares your food
- **Waiter (API)** → Brings you the food

### HTTP Methods (Like Menu Options)

| Method | What it does | Example |
|--------|--------------|---------|
| **GET** | Get/Read data | "Show me my profile" |
| **POST** | Create new data | "Create a new message" |
| **PUT/PATCH** | Update existing data | "Update my bio" |
| **DELETE** | Delete data | "Delete this message" |

### Parts of an API Request

```
┌─────────────────────────────────────────┐
│  METHOD:  POST                          │ ← What you want to do
├─────────────────────────────────────────┤
│  URL:  http://127.0.0.1:8000/api/v1/... │ ← Where to send it
├─────────────────────────────────────────┤
│  HEADERS:                               │ ← Extra info
│    Content-Type: application/json       │
│    Authorization: Token abc123...       │
├─────────────────────────────────────────┤
│  BODY:  { "email": "test@test.com" }   │ ← Data you're sending
└─────────────────────────────────────────┘
```

---

## Step 4: Test Your First API (Login)

Let's test the login endpoint to get an authentication token!

### 4.1 Create a New Request

1. **Click** the **"+"** button or **"New"** button in Postman
2. **Select** "HTTP Request"
3. You'll see an empty request form

### 4.2 Configure the Login Request

**Method:** Select **POST** from the dropdown

**URL:** Enter this:
```
http://127.0.0.1:8000/api/v1/login/
```

**Headers:** Click on the **"Headers"** tab, then add:

| Key | Value |
|-----|-------|
| `Content-Type` | `application/json` |

**Body:** 
1. Click on the **"Body"** tab
2. Select **"raw"**
3. From the dropdown on the right, select **"JSON"**
4. Enter this:

```json
{
  "email": "test@connectflow.com",
  "password": "Password123!"
}
```

### 4.3 Send the Request!

1. **Click** the blue **"Send"** button
2. Wait 1-2 seconds
3. Look at the bottom panel for the response

### 4.4 Read the Response

**✅ Success (200 OK):**
```json
{
  "token": "abc123def456ghi789...",
  "user": {
    "id": 1,
    "username": "apitest@test.com",
    "email": "apitest@test.com",
    "role": "TEAM_MEMBER",
    "organization": "Test Organization"
  }
}
```

**❌ Error (400/401):**
```json
{
  "error": "Invalid credentials"
}
```

### 4.5 Copy Your Token!

**IMPORTANT:** Copy the token value (the long string after `"token":`). You'll need this for other requests!

Example token:
```
a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0
```

---

## Step 5: Save Your Token

### Create an Environment (Recommended)

This saves you from copying the token every time!

1. **Click** on the **"Environments"** icon (🌍) in the left sidebar
2. **Click** "+" to create a new environment
3. **Name it:** "ConnectFlow Local"
4. **Add a variable:**
   - **Variable:** `auth_token`
   - **Initial Value:** (paste your token here)
   - **Current Value:** (paste your token here)
5. **Click** "Save"
6. **Select** "ConnectFlow Local" from the environment dropdown (top right)

**Now you can use `{{auth_token}}` in your requests!**

---

## Step 6: Test Authenticated Endpoints & Check Organization

Now let's test endpoints that require authentication and verify you have an organization!

### 6.1 Get Your Profile

**Create a new request:**

**Method:** GET

**URL:**
```
http://127.0.0.1:8000/api/v1/users/me/
```

**Headers:**

| Key | Value |
|-----|-------|
| `Authorization` | `Token {{auth_token}}` |
| `Content-Type` | `application/json` |

*If you didn't set up an environment, replace `{{auth_token}}` with your actual token*

**Send!** Click the blue "Send" button

**Expected Response:**
```json
{
  "id": 1,
  "username": "test@connectflow.com",
  "email": "test@connectflow.com",
  "first_name": "Test",
  "last_name": "User",
  "role": "TEAM_MEMBER",
  "organization": {
    "id": "4b03ece4-1d0b-45f2-96c1-aae20843f2c7",
    "name": "Test Organization"
  },
  "status": "ONLINE",
  "theme": "LIGHT"
}
```

---

### 6.5 Check Your Organization (CRITICAL!)

**⚠️ STOP! Do this before creating channels!**

**Create a new request:**

**Method:** GET

**URL:**
```
http://127.0.0.1:8000/api/v1/organizations/
```

**Headers:**

| Key | Value |
|-----|-------|
| `Authorization` | `Token {{auth_token}}` |
| `Content-Type` | `application/json` |

**Send!** Click the blue "Send" button

**Expected Response (SUCCESS ✅):**
```json
[
  {
    "id": "4b03ece4-1d0b-45f2-96c1-aae20843f2c7",
    "name": "Test Organization",
    "industry": "Technology",
    "created_at": "2026-01-04T01:00:00Z"
  }
]
```

**🎯 ACTION REQUIRED:** 
1. **Copy the `id` value** (e.g., `4b03ece4-1d0b-45f2-96c1-aae20843f2c7`)
2. **Save it in your environment:**
   - Go to Environments (left sidebar)
   - Select "ConnectFlow Local"
   - Add variable: `org_id`
   - Paste the UUID as the value
   - Click Save

**If you get `[]` (empty array) ❌:**

You don't have an organization! Here's how to fix it:

**Quick Fix via Django Shell:**
```bash
# In terminal/command prompt:
cd D:\Projects\connectflow-django
python manage.py shell

# In the shell:
from apps.organizations.models import Organization
from apps.accounts.models import User

# Create organization
org = Organization.objects.create(
    name="Test Organization",
    industry="Technology"
)

# Assign to your user
user = User.objects.get(email="test@connectflow.com")
user.organization = org
user.save()

# Verify
print(f"Success! Org ID: {org.id}")
exit()
```

**After creating the organization, test the GET /api/v1/organizations/ endpoint again!**

---

## Prerequisites: Check Your Organization

**IMPORTANT:** Before creating channels, you need to be part of an organization! Most test users are automatically assigned to an organization when created.

### 🏢 Get Your Organization Info (GET)

**Method:** GET  
**URL:** `http://127.0.0.1:8000/api/v1/organizations/`  
**Authorization:** Bearer Token → `{{auth_token}}`

**What it does:** Shows your organization details

**Expected Response:**
```json
[
  {
    "id": "org-uuid-here",
    "name": "Test Organization",
    "slug": "test-org",
    "industry": "Technology",
    "created_at": "2026-01-01T10:00:00Z"
  }
]
```

**If you get an empty array `[]`:** You don't have an organization yet! Follow the "Organizations (Check This First!)" section below to create one.

**⚠️ IMPORTANT:** Copy the organization `id` from the response! You'll need it to create channels.

**Example:** If you get `"id": "4b03ece4-1d0b-45f2-96c1-aae20843f2c7"`, save this UUID - you'll use it in the next step.

---

## Complete Channel Operations

### 📺 1. List All Channels (GET)

**Method:** GET  
**URL:** `http://127.0.0.1:8000/api/v1/channels/`  
**Authorization:** Bearer Token → `{{auth_token}}`

**What it does:** Shows all channels you have access to

**Expected Response:**
```json
[
  {
    "id": "uuid-here",
    "name": "general",
    "description": "General discussion channel",
    "channel_type": "TEAM",
    "organization": "org-uuid-here",
    "is_private": false,
    "read_only": false,
    "created_at": "2026-01-01T10:00:00Z",
    "member_count": 15
  },
  {
    "id": "uuid-here-2",
    "name": "leadership-channel",
    "description": "Leadership private channel",
    "channel_type": "PRIVATE",
    "organization": "org-uuid-here",
    "is_private": true,
    "read_only": false,
    "created_at": "2026-01-02T14:30:00Z",
    "member_count": 5
  }
]
```

---

### ➕ 2. Create a New Channel (POST)

**Method:** POST  
**URL:** `http://127.0.0.1:8000/api/v1/channels/`  
**Authorization:** Bearer Token → `{{auth_token}}`  
**Headers:** `Content-Type: application/json`

**⚠️ IMPORTANT:** 
- You MUST include the `organization` field (the UUID from `/api/v1/organizations/`)
- Valid `channel_type` values are: `OFFICIAL`, `DEPARTMENT`, `TEAM`, `PROJECT`, `PRIVATE`, `DIRECT`, `BREAKOUT`

**Body (Team Channel - Most Common):**
```json
{
  "name": "marketing-team",
  "description": "Marketing team collaboration space",
  "channel_type": "TEAM",
  "organization": "4b03ece4-1d0b-45f2-96c1-aae20843f2c7"
}
```
*Replace the organization UUID with your actual organization ID from step "Prerequisites: Check Your Organization"*

**Body (Private Channel):**
```json
{
  "name": "executives-only",
  "description": "Executive leadership private channel",
  "channel_type": "PRIVATE",
  "organization": "4b03ece4-1d0b-45f2-96c1-aae20843f2c7",
  "is_private": true
}
```

**Body (Department Channel):**
```json
{
  "name": "engineering-dept",
  "description": "Engineering department channel",
  "channel_type": "DEPARTMENT",
  "organization": "4b03ece4-1d0b-45f2-96c1-aae20843f2c7"
}
```

**Body (Project Channel):**
```json
{
  "name": "project-phoenix",
  "description": "Project Phoenix workspace",
  "channel_type": "PROJECT",
  "organization": "4b03ece4-1d0b-45f2-96c1-aae20843f2c7"
}
```

**Body (Official Announcement Channel):**
```json
{
  "name": "company-announcements",
  "description": "Official company announcements",
  "channel_type": "OFFICIAL",
  "organization": "4b03ece4-1d0b-45f2-96c1-aae20843f2c7",
  "read_only": false
}
```

**Expected Response:**
```json
{
  "id": "new-channel-uuid",
  "name": "marketing-team",
  "description": "Marketing team collaboration space",
  "channel_type": "TEAM",
  "organization": "4b03ece4-1d0b-45f2-96c1-aae20843f2c7",
  "is_private": false,
  "read_only": false,
  "created_at": "2026-01-04T02:00:00Z",
  "member_count": 1
}
```

**✅ You are now automatically added as a member and creator of the channel!**

**To verify, run:**
```
GET /api/v1/channels/
```
You should see your newly created channel in the list.

**Common Errors:**

❌ **Error: "organization": ["This field is required."]**
- Solution: Add the `organization` field with your organization UUID
- Get it from: `GET /api/v1/organizations/` response

❌ **Error: "channel_type": ["\"PUBLIC\" is not a valid choice."]**
- Solution: Use one of these valid types:
  - `OFFICIAL` - Official announcements
  - `DEPARTMENT` - Department channels
  - `TEAM` - Team channels (recommended)
  - `PROJECT` - Project-specific channels
  - `PRIVATE` - Private group channels
  - `DIRECT` - Direct messages
  - `BREAKOUT` - Breakout rooms

---

### 🔍 3. Get Channel Details (GET)

**Method:** GET  
**URL:** `http://127.0.0.1:8000/api/v1/channels/{channel_id}/`  
**Authorization:** Bearer Token → `{{auth_token}}`

Replace `{channel_id}` with actual channel UUID

**Expected Response:**
```json
{
  "id": "channel-uuid",
  "name": "marketing-team",
  "description": "Marketing team collaboration space",
  "channel_type": "TEAM",
  "organization": "org-uuid",
  "is_private": false,
  "read_only": false,
  "created_at": "2026-01-04T01:00:00Z",
  "member_count": 1
}
```

---

### ✏️ 4. Update Channel (PUT/PATCH)

**Method:** PUT or PATCH  
**URL:** `http://127.0.0.1:8000/api/v1/channels/{channel_id}/`  
**Authorization:** Bearer Token → `{{auth_token}}`  
**Headers:** `Content-Type: application/json`

**Body (Update Name & Description):**
```json
{
  "name": "marketing-team-2026",
  "description": "Updated description for marketing team"
}
```

**Body (Change to Private):**
```json
{
  "is_private": true
}
```

**Body (Make Read-Only):**
```json
{
  "read_only": true
}
```

**Expected Response:**
```json
{
  "id": "channel-uuid",
  "name": "marketing-team-2026",
  "description": "Updated description for marketing team",
  "channel_type": "TEAM",
  "organization": "org-uuid",
  "is_private": false,
  "read_only": false,
  "created_at": "2026-01-04T01:00:00Z",
  "member_count": 15
}
```

---

### 🗑️ 5. Delete Channel (DELETE)

**Method:** DELETE  
**URL:** `http://127.0.0.1:8000/api/v1/channels/{channel_id}/`  
**Authorization:** Bearer Token → `{{auth_token}}`

**Expected Response:**
```json
{
  "message": "Channel deleted successfully",
  "deleted_channel_id": "channel-uuid",
  "deleted_at": "2026-01-04T01:15:00Z"
}
```

**Note:** Only channel creators or admins can delete channels. All messages will be archived.

---

### 👥 6. Add Members to Channel (POST)

**Method:** POST  
**URL:** `http://127.0.0.1:8000/api/v1/channels/{channel_id}/members/`  
**Authorization:** Bearer Token → `{{auth_token}}`  
**Headers:** `Content-Type: application/json`

**Body:**
```json
{
  "user_ids": ["user-uuid-1", "user-uuid-2", "user-uuid-3"]
}
```

**Or add by email:**
```json
{
  "emails": ["user1@test.com", "user2@test.com"]
}
```

**Expected Response:**
```json
{
  "message": "Members added successfully",
  "added_members": [
    {
      "id": "user-uuid-1",
      "username": "user1@test.com",
      "first_name": "John"
    }
  ],
  "total_members": 18
}
```

---

### 👤 7. Remove Member from Channel (DELETE)

**Method:** DELETE  
**URL:** `http://127.0.0.1:8000/api/v1/channels/{channel_id}/members/{user_id}/`  
**Authorization:** Bearer Token → `{{auth_token}}`

**Expected Response:**
```json
{
  "message": "Member removed successfully",
  "removed_user": "user1@test.com",
  "total_members": 17
}
```

---

### 🚪 8. Leave Channel (POST)

**Method:** POST  
**URL:** `http://127.0.0.1:8000/api/v1/channels/{channel_id}/leave/`  
**Authorization:** Bearer Token → `{{auth_token}}`

**Expected Response:**
```json
{
  "message": "You have left the channel successfully",
  "channel_name": "marketing-team"
}
```

---

### 🔔 9. Mute/Unmute Channel (POST)

**Method:** POST  
**URL:** `http://127.0.0.1:8000/api/v1/channels/{channel_id}/mute/`  
**Authorization:** Bearer Token → `{{auth_token}}`  
**Headers:** `Content-Type: application/json`

**Body:**
```json
{
  "muted": true
}
```

**Expected Response:**
```json
{
  "message": "Channel muted successfully",
  "channel_id": "channel-uuid",
  "is_muted": true
}
```

---

### 📌 10. Pin Channel (POST)

**Method:** POST  
**URL:** `http://127.0.0.1:8000/api/v1/channels/{channel_id}/pin/`  
**Authorization:** Bearer Token → `{{auth_token}}`

**Expected Response:**
```json
{
  "message": "Channel pinned successfully",
  "is_pinned": true
}
```

---

## Complete Chat/Message Operations

### 💬 1. Get Messages from Channel (GET)

**Method:** GET  
**URL:** `http://127.0.0.1:8000/api/v1/channels/{channel_id}/messages/`  
**Authorization:** Bearer Token → `{{auth_token}}`

**Query Parameters (optional):**
- `?limit=50` - Number of messages to fetch (default: 50)
- `?offset=0` - Pagination offset
- `?before=2026-01-04T00:00:00Z` - Get messages before this timestamp
- `?after=2026-01-03T00:00:00Z` - Get messages after this timestamp

**Example:**
```
http://127.0.0.1:8000/api/v1/channels/{channel_id}/messages/?limit=100&before=2026-01-04T00:00:00Z
```

**Expected Response:**
```json
{
  "count": 150,
  "next": "http://127.0.0.1:8000/api/v1/channels/{channel_id}/messages/?offset=100",
  "previous": null,
  "results": [
    {
      "id": "message-uuid-1",
      "channel": "channel-uuid",
      "sender": {
        "id": "user-uuid",
        "username": "test@connectflow.com",
        "first_name": "Test",
        "last_name": "User",
        "avatar_url": "https://cloudinary.../avatar.jpg"
      },
      "content": "Hello everyone! 👋",
      "message_type": "TEXT",
      "created_at": "2026-01-04T00:50:00Z",
      "updated_at": "2026-01-04T00:50:00Z",
      "is_edited": false,
      "reactions": [
        {
          "emoji": "👍",
          "count": 5,
          "users": ["user1", "user2"]
        }
      ],
      "reply_count": 3,
      "attachments": []
    }
  ]
}
```

---

### 📤 2. Send a Text Message (POST)

**Method:** POST  
**URL:** `http://127.0.0.1:8000/api/v1/messages/`  
**Authorization:** Bearer Token → `{{auth_token}}`  
**Headers:** `Content-Type: application/json`

**Body (Simple Text):**
```json
{
  "channel": "channel-uuid-here",
  "content": "Hello from Postman! 🚀"
}
```

**Body (Text with Mention):**
```json
{
  "channel": "channel-uuid-here",
  "content": "Hey @john, can you review this?",
  "mentions": ["user-uuid-of-john"]
}
```

**Body (Reply to Message):**
```json
{
  "channel": "channel-uuid-here",
  "content": "Great idea! I agree.",
  "parent_message": "message-uuid-to-reply-to"
}
```

**Expected Response:**
```json
{
  "id": "new-message-uuid",
  "channel": "channel-uuid",
  "sender": {
    "id": "user-uuid",
    "username": "test@connectflow.com",
    "first_name": "Test",
    "last_name": "User"
  },
  "content": "Hello from Postman! 🚀",
  "message_type": "TEXT",
  "created_at": "2026-01-04T01:00:00Z",
  "is_edited": false,
  "reactions": [],
  "attachments": []
}
```

---

### 🖼️ 3. Send Message with Image (POST)

**Method:** POST  
**URL:** `http://127.0.0.1:8000/api/v1/messages/`  
**Authorization:** Bearer Token → `{{auth_token}}`  
**Headers:** `Content-Type: multipart/form-data`

**Body (form-data):**
- `channel`: `channel-uuid-here`
- `content`: `Check out this screenshot!`
- `message_type`: `IMAGE`
- `image`: (Select image file from your computer)

**Expected Response:**
```json
{
  "id": "message-uuid",
  "channel": "channel-uuid",
  "sender": {...},
  "content": "Check out this screenshot!",
  "message_type": "IMAGE",
  "attachments": [
    {
      "id": "attachment-uuid",
      "file_url": "https://cloudinary.../image.jpg",
      "file_type": "image/jpeg",
      "file_size": 245678,
      "thumbnail_url": "https://cloudinary.../thumbnail.jpg"
    }
  ],
  "created_at": "2026-01-04T01:05:00Z"
}
```

---

### 📎 4. Send Message with File Attachment (POST)

**Method:** POST  
**URL:** `http://127.0.0.1:8000/api/v1/messages/`  
**Authorization:** Bearer Token → `{{auth_token}}`  
**Headers:** `Content-Type: multipart/form-data`

**Body (form-data):**
- `channel`: `channel-uuid-here`
- `content`: `Here's the project document`
- `message_type`: `FILE`
- `file`: (Select file: PDF, DOCX, XLSX, etc.)

**Expected Response:**
```json
{
  "id": "message-uuid",
  "channel": "channel-uuid",
  "content": "Here's the project document",
  "message_type": "FILE",
  "attachments": [
    {
      "id": "attachment-uuid",
      "file_url": "https://cloudinary.../document.pdf",
      "file_name": "project-plan.pdf",
      "file_type": "application/pdf",
      "file_size": 1048576
    }
  ],
  "created_at": "2026-01-04T01:10:00Z"
}
```

---

### 🎤 5. Send Voice Message (POST)

**Method:** POST  
**URL:** `http://127.0.0.1:8000/api/v1/messages/`  
**Authorization:** Bearer Token → `{{auth_token}}`  
**Headers:** `Content-Type: multipart/form-data`

**Body (form-data):**
- `channel`: `channel-uuid-here`
- `message_type`: `VOICE`
- `voice`: (Select audio file: .mp3, .wav, .m4a)

**Expected Response:**
```json
{
  "id": "message-uuid",
  "channel": "channel-uuid",
  "message_type": "VOICE",
  "attachments": [
    {
      "id": "attachment-uuid",
      "file_url": "https://cloudinary.../voice.mp3",
      "file_type": "audio/mpeg",
      "duration": 45,
      "file_size": 523456
    }
  ],
  "created_at": "2026-01-04T01:15:00Z"
}
```

---

### ✏️ 6. Edit Message (PUT/PATCH)

**Method:** PUT or PATCH  
**URL:** `http://127.0.0.1:8000/api/v1/messages/{message_id}/`  
**Authorization:** Bearer Token → `{{auth_token}}`  
**Headers:** `Content-Type: application/json`

**Body:**
```json
{
  "content": "Updated message content (edited)"
}
```

**Expected Response:**
```json
{
  "id": "message-uuid",
  "channel": "channel-uuid",
  "content": "Updated message content (edited)",
  "is_edited": true,
  "updated_at": "2026-01-04T01:20:00Z",
  "edit_history": [
    {
      "content": "Original message",
      "edited_at": "2026-01-04T01:00:00Z"
    }
  ]
}
```

**Note:** Only the sender can edit their own messages within 24 hours.

---

### 🗑️ 7. Delete Message (DELETE)

**Method:** DELETE  
**URL:** `http://127.0.0.1:8000/api/v1/messages/{message_id}/`  
**Authorization:** Bearer Token → `{{auth_token}}`

**Expected Response:**
```json
{
  "message": "Message deleted successfully",
  "deleted_message_id": "message-uuid",
  "deleted_at": "2026-01-04T01:25:00Z"
}
```

**Note:** Soft delete - message is archived, not permanently removed.

---

### 😊 8. Add Reaction to Message (POST)

**Method:** POST  
**URL:** `http://127.0.0.1:8000/api/v1/messages/{message_id}/reactions/`  
**Authorization:** Bearer Token → `{{auth_token}}`  
**Headers:** `Content-Type: application/json`

**Body:**
```json
{
  "emoji": "👍"
}
```

**Other popular reactions:**
```json
{"emoji": "❤️"}
{"emoji": "😂"}
{"emoji": "🎉"}
{"emoji": "👏"}
{"emoji": "🔥"}
```

**Expected Response:**
```json
{
  "message": "Reaction added successfully",
  "message_id": "message-uuid",
  "emoji": "👍",
  "total_reactions": 6
}
```

---

### ❌ 9. Remove Reaction (DELETE)

**Method:** DELETE  
**URL:** `http://127.0.0.1:8000/api/v1/messages/{message_id}/reactions/{emoji}/`  
**Authorization:** Bearer Token → `{{auth_token}}`

**Example:**
```
DELETE /api/v1/messages/{message_id}/reactions/👍/
```

**Expected Response:**
```json
{
  "message": "Reaction removed successfully",
  "emoji": "👍",
  "total_reactions": 5
}
```

---

### 🔖 10. Pin Message (POST)

**Method:** POST  
**URL:** `http://127.0.0.1:8000/api/v1/messages/{message_id}/pin/`  
**Authorization:** Bearer Token → `{{auth_token}}`

**Expected Response:**
```json
{
  "message": "Message pinned successfully",
  "is_pinned": true,
  "pinned_at": "2026-01-04T01:30:00Z"
}
```

---

### 📍 11. Get Pinned Messages (GET)

**Method:** GET  
**URL:** `http://127.0.0.1:8000/api/v1/channels/{channel_id}/pinned_messages/`  
**Authorization:** Bearer Token → `{{auth_token}}`

**Expected Response:**
```json
{
  "count": 3,
  "pinned_messages": [
    {
      "id": "message-uuid-1",
      "content": "Important announcement!",
      "sender": {...},
      "pinned_by": {...},
      "pinned_at": "2026-01-04T01:30:00Z"
    }
  ]
}
```

---

### 🔍 12. Search Messages (GET)

**Method:** GET  
**URL:** `http://127.0.0.1:8000/api/v1/messages/search/`  
**Authorization:** Bearer Token → `{{auth_token}}`

**Query Parameters:**
- `?q=project` - Search term
- `?channel=channel-uuid` - Limit to specific channel
- `?sender=user-uuid` - Filter by sender
- `?from=2026-01-01` - Date range start
- `?to=2026-01-31` - Date range end

**Example:**
```
http://127.0.0.1:8000/api/v1/messages/search/?q=deadline&channel=channel-uuid&from=2026-01-01
```

**Expected Response:**
```json
{
  "count": 12,
  "results": [
    {
      "id": "message-uuid",
      "content": "The project deadline is next Friday",
      "channel": {...},
      "sender": {...},
      "created_at": "2026-01-03T10:00:00Z",
      "match_highlight": "The project <mark>deadline</mark> is next Friday"
    }
  ]
}
```

---

### 💬 13. Get Thread/Replies (GET)

**Method:** GET  
**URL:** `http://127.0.0.1:8000/api/v1/messages/{message_id}/replies/`  
**Authorization:** Bearer Token → `{{auth_token}}`

**Expected Response:**
```json
{
  "parent_message": {
    "id": "parent-message-uuid",
    "content": "What do you think about this?",
    "sender": {...}
  },
  "replies": [
    {
      "id": "reply-uuid-1",
      "content": "I think it's great!",
      "sender": {...},
      "created_at": "2026-01-04T01:35:00Z"
    }
  ],
  "reply_count": 5
}
```

---

### ✅ 14. Mark Messages as Read (POST)

**Method:** POST  
**URL:** `http://127.0.0.1:8000/api/v1/channels/{channel_id}/read/`  
**Authorization:** Bearer Token → `{{auth_token}}`  
**Headers:** `Content-Type: application/json`

**Body:**
```json
{
  "last_read_message_id": "message-uuid"
}
```

**Expected Response:**
```json
{
  "message": "Messages marked as read",
  "unread_count": 0
}
```

---

## Direct Messaging (DMs)

### 💼 1. List All DM Conversations (GET)

**Method:** GET  
**URL:** `http://127.0.0.1:8000/api/v1/direct_messages/`  
**Authorization:** Bearer Token → `{{auth_token}}`

**Expected Response:**
```json
{
  "conversations": [
    {
      "id": "dm-uuid-1",
      "participant": {
        "id": "user-uuid",
        "username": "john@test.com",
        "first_name": "John",
        "last_name": "Doe",
        "status": "ONLINE",
        "avatar_url": "https://..."
      },
      "last_message": {
        "content": "See you tomorrow!",
        "timestamp": "2026-01-04T00:45:00Z",
        "sender_id": "user-uuid"
      },
      "unread_count": 2,
      "updated_at": "2026-01-04T00:45:00Z"
    }
  ]
}
```

---

### 📩 2. Create/Get DM with User (POST)

**Method:** POST  
**URL:** `http://127.0.0.1:8000/api/v1/direct_messages/create/`  
**Authorization:** Bearer Token → `{{auth_token}}`  
**Headers:** `Content-Type: application/json`

**Body:**
```json
{
  "user_id": "recipient-user-uuid"
}
```

**Or use email:**
```json
{
  "email": "john@test.com"
}
```

**Expected Response:**
```json
{
  "id": "dm-uuid",
  "participant": {
    "id": "user-uuid",
    "username": "john@test.com",
    "first_name": "John",
    "status": "ONLINE"
  },
  "created_at": "2026-01-04T01:40:00Z",
  "message": "DM conversation created or retrieved"
}
```

---

### 💬 3. Get DM Messages (GET)

**Method:** GET  
**URL:** `http://127.0.0.1:8000/api/v1/direct_messages/{dm_id}/messages/`  
**Authorization:** Bearer Token → `{{auth_token}}`

**Expected Response:**
```json
{
  "conversation_id": "dm-uuid",
  "participant": {...},
  "messages": [
    {
      "id": "message-uuid",
      "sender": {...},
      "content": "Hi, how are you?",
      "message_type": "TEXT",
      "created_at": "2026-01-04T01:30:00Z",
      "is_read": true
    }
  ]
}
```

---

### 📤 4. Send DM Message (POST)

**Method:** POST  
**URL:** `http://127.0.0.1:8000/api/v1/direct_messages/{dm_id}/send/`  
**Authorization:** Bearer Token → `{{auth_token}}`  
**Headers:** `Content-Type: application/json`

**Body (Text):**
```json
{
  "content": "Hey! Are you available for a quick call?"
}
```

**Body (Image):**
```json
{
  "content": "Check this out!",
  "message_type": "IMAGE",
  "image": "base64-encoded-image-or-url"
}
```

**Expected Response:**
```json
{
  "id": "message-uuid",
  "conversation_id": "dm-uuid",
  "sender": {...},
  "content": "Hey! Are you available for a quick call?",
  "created_at": "2026-01-04T01:45:00Z"
}
```

---

## Advanced Features

### 📊 1. Get Channel Analytics (GET)

**Method:** GET  
**URL:** `http://127.0.0.1:8000/api/v1/channels/{channel_id}/analytics/`  
**Authorization:** Bearer Token → `{{auth_token}}`

**Expected Response:**
```json
{
  "channel_id": "channel-uuid",
  "total_messages": 1547,
  "total_members": 23,
  "active_members_today": 18,
  "messages_today": 87,
  "messages_this_week": 423,
  "top_contributors": [
    {
      "user": "john@test.com",
      "message_count": 145
    }
  ],
  "peak_activity_hours": [9, 14, 16],
  "engagement_rate": 78.5
}
```

---

### 🔔 2. Get Notifications (GET)

**Method:** GET  
**URL:** `http://127.0.0.1:8000/api/v1/notifications/`  
**Authorization:** Bearer Token → `{{auth_token}}`

**Query Parameters:**
- `?unread=true` - Only unread notifications
- `?type=MENTION` - Filter by type

**Expected Response:**
```json
{
  "count": 15,
  "unread_count": 5,
  "notifications": [
    {
      "id": "notif-uuid",
      "title": "New mention in #marketing",
      "content": "John mentioned you in marketing-team",
      "notification_type": "MENTION",
      "is_read": false,
      "created_at": "2026-01-04T01:00:00Z",
      "related_object": {
        "type": "message",
        "id": "message-uuid",
        "channel": "channel-uuid"
      }
    }
  ]
}
```

---

### ✅ 3. Mark Notification as Read (POST)

**Method:** POST  
**URL:** `http://127.0.0.1:8000/api/v1/notifications/{notification_id}/read/`  
**Authorization:** Bearer Token → `{{auth_token}}`

**Expected Response:**
```json
{
  "message": "Notification marked as read",
  "notification_id": "notif-uuid"
}
```

---

### 📢 4. Mark All Notifications as Read (POST)

**Method:** POST  
**URL:** `http://127.0.0.1:8000/api/v1/notifications/read_all/`  
**Authorization:** Bearer Token → `{{auth_token}}`

**Expected Response:**
```json
{
  "message": "All notifications marked as read",
  "marked_count": 15
}
```

---

### 👥 5. Get Online Users (GET)

**Method:** GET  
**URL:** `http://127.0.0.1:8000/api/v1/users/online/`  
**Authorization:** Bearer Token → `{{auth_token}}`

**Expected Response:**
```json
{
  "online_users": [
    {
      "id": "user-uuid-1",
      "username": "john@test.com",
      "first_name": "John",
      "status": "ONLINE",
      "last_seen": "2026-01-04T01:50:00Z"
    }
  ],
  "total_online": 12
}
```

---

### 🔍 6. Search Users (GET)

**Method:** GET  
**URL:** `http://127.0.0.1:8000/api/v1/users/search/`  
**Authorization:** Bearer Token → `{{auth_token}}`

**Query Parameters:**
- `?q=john` - Search term
- `?department=sales` - Filter by department
- `?role=ADMIN` - Filter by role

**Example:**
```
http://127.0.0.1:8000/api/v1/users/search/?q=john&department=sales
```

**Expected Response:**
```json
{
  "count": 3,
  "results": [
    {
      "id": "user-uuid",
      "username": "john.doe@test.com",
      "first_name": "John",
      "last_name": "Doe",
      "department": "Sales",
      "role": "TEAM_MEMBER"
    }
  ]
}
```

---

### 📱 7. Update User Status (POST)

**Method:** POST  
**URL:** `http://127.0.0.1:8000/api/v1/users/status/`  
**Authorization:** Bearer Token → `{{auth_token}}`  
**Headers:** `Content-Type: application/json`

**Body:**
```json
{
  "status": "AWAY",
  "custom_status": "In a meeting 🎯"
}
```

**Status options:** `ONLINE`, `AWAY`, `BUSY`, `OFFLINE`

**Expected Response:**
```json
{
  "message": "Status updated successfully",
  "status": "AWAY",
  "custom_status": "In a meeting 🎯"
}
```

---

### 🎨 8. Toggle Theme (POST)

**Method:** POST  
**URL:** `http://127.0.0.1:8000/api/v1/users/toggle_theme/`  
**Authorization:** Bearer Token → `{{auth_token}}`

**Expected Response:**
```json
{
  "message": "Theme toggled successfully",
  "current_theme": "DARK"
}
```

---

### 📤 9. Export Channel Messages (GET)

**Method:** GET  
**URL:** `http://127.0.0.1:8000/api/v1/channels/{channel_id}/export/`  
**Authorization:** Bearer Token → `{{auth_token}}`

**Query Parameters:**
- `?format=json` - Export format (json, csv, pdf)
- `?from=2026-01-01` - Start date
- `?to=2026-01-31` - End date

**Expected Response:**
Download file or:
```json
{
  "export_url": "https://storage.../export-uuid.json",
  "expires_at": "2026-01-05T01:50:00Z",
  "message": "Export ready for download"
}
```

---

### 🔐 10. Logout (POST)

**Method:** POST  
**URL:** `http://127.0.0.1:8000/api/v1/logout/`  
**Authorization:** Bearer Token → `{{auth_token}}`

**Expected Response:**
```json
{
  "message": "Logged out successfully"
}
```

---

## Common API Tests

## Troubleshooting

### Problem: "Connection refused" or "Could not connect"

**Solution:**
- Make sure your Django server is running
- Check the terminal where you started the server
- The URL should be `http://127.0.0.1:8000/` (not `localhost`)

---

### Problem: "401 Unauthorized"

**Solution:**
- Your token might be expired or invalid
- Login again to get a fresh token
- Make sure you included `Token ` before the token value
  - ✅ Correct: `Token abc123...`
  - ❌ Wrong: `abc123...`

---

### Problem: "404 Not Found"

**Solution:**
- Check the URL for typos
- Make sure the endpoint exists
- Verify the API version (`/api/v1/`)

---

### Problem: "400 Bad Request"

**Solution:**
- Check your JSON syntax (no extra commas, proper quotes)
- Make sure Content-Type header is set to `application/json`
- Verify all required fields are included

---

### Problem: "500 Internal Server Error"

**Solution:**
- Check your Django terminal for error messages
- Look at the error traceback
- This usually means a bug in the server code

---

## Tips & Best Practices

### ✅ DO:
- **Save your requests** - Click "Save" to keep them for later
- **Use environments** - Store tokens and base URLs
- **Organize in collections** - Group related requests together
- **Read error messages** - They usually tell you what's wrong

### ❌ DON'T:
- **Don't share your token** - It's like your password
- **Don't test on production** - Always use local/staging first
- **Don't skip headers** - Missing headers cause most errors

---

## Creating a Postman Collection (Advanced)

Want to save all your requests in one place?

### 1. Create a Collection

1. Click **"Collections"** in the left sidebar
2. Click **"+"** or **"Create Collection"**
3. Name it: **"ConnectFlow Pro API"**
4. Click **"Create"**

### 2. Add Requests to Collection

1. When creating a new request, click **"Save"**
2. Choose **"ConnectFlow Pro API"** collection
3. Give the request a name (e.g., "Login", "Get Profile")
4. Click **"Save"**

### 3. Organize into Folders

1. Right-click your collection
2. Select **"Add Folder"**
3. Create folders like:
   - 🔐 Authentication
   - 👤 Users
   - 💬 Messaging
   - 📢 Notifications
   - 🏢 Organizations

---

## Sample Postman Collection Structure

```
📁 ConnectFlow Pro API - Complete Guide
├── 🔐 Authentication
│   ├── Login
│   └── Logout
│
├── 👤 User Management
│   ├── Get My Profile
│   ├── List All Users
│   ├── Search Users
│   ├── Get Online Users
│   ├── Update Status
│   └── Toggle Theme
│
├── 📺 Channel Operations (CRUD)
│   ├── 📋 Read
│   │   ├── List All Channels
│   │   ├── Get Channel Details
│   │   ├── Get Channel Analytics
│   │   └── Get Pinned Messages
│   ├── ➕ Create
│   │   ├── Create Public Channel
│   │   ├── Create Private Channel
│   │   └── Create Project Channel
│   ├── ✏️ Update
│   │   ├── Update Channel Name
│   │   ├── Update Description
│   │   └── Change Channel Type
│   ├── 🗑️ Delete
│   │   └── Delete Channel
│   └── 👥 Member Management
│       ├── Add Members to Channel
│       ├── Remove Member from Channel
│       ├── Leave Channel
│       ├── Mute/Unmute Channel
│       └── Pin/Unpin Channel
│
├── 💬 Message Operations (CRUD)
│   ├── 📋 Read
│   │   ├── Get Channel Messages
│   │   ├── Get Message Thread/Replies
│   │   ├── Search Messages
│   │   ├── Get Pinned Messages
│   │   └── Export Messages
│   ├── 📤 Create/Send
│   │   ├── Send Text Message
│   │   ├── Send Message with Mention
│   │   ├── Send Reply to Thread
│   │   ├── Send Image Message
│   │   ├── Send File Attachment
│   │   └── Send Voice Message
│   ├── ✏️ Update
│   │   └── Edit Message
│   ├── 🗑️ Delete
│   │   └── Delete Message
│   └── ⚡ Interactions
│       ├── Add Reaction (👍❤️😂🎉)
│       ├── Remove Reaction
│       ├── Pin Message
│       ├── Unpin Message
│       └── Mark as Read
│
├── 💼 Direct Messages (DMs)
│   ├── List All DM Conversations
│   ├── Create/Get DM with User
│   ├── Get DM Messages
│   ├── Send DM (Text)
│   ├── Send DM (Image)
│   ├── Send DM (File)
│   └── Mark DM as Read
│
├── 📢 Notifications
│   ├── Get All Notifications
│   ├── Get Unread Notifications
│   ├── Mark Notification as Read
│   ├── Mark All as Read
│   └── Delete Notification
│
├── 🏢 Organizations (IMPORTANT - Check First!)
│   ├── ⚠️ Get Your Organization (Required before creating channels!)
│   ├── List Departments
│   ├── Create Department
│   ├── List Teams
│   ├── Create Team
│   └── List Shared Projects
│
└── 📊 Analytics & Reports
    ├── Channel Analytics
    ├── User Activity Report
    ├── Message Statistics
    └── Export Channel Data
```

---

## Quick Testing Workflow for Presentations

### ⚠️ Before You Start ANY Demo

**CRITICAL FIRST STEP:**
```
1. Login → Get token
2. GET /api/v1/organizations/ → Verify you have an organization
   ✅ If you get an array with data → Proceed!
   ❌ If you get [] → Follow the "Organizations" section to create one first
```

### 🎯 Demo Flow 1: Complete Channel Lifecycle (5 minutes)

```
1. Login → Get token
2. Check organization (GET /api/v1/organizations/)
3. Create new channel "demo-presentation"
4. Add 3 members to channel
4. Send 5 different message types:
   - Text message
   - Message with @mention
   - Image message
   - File attachment
   - Reply to message
5. Add reactions (👍, ❤️, 🎉)
6. Pin important message
7. Edit a message
8. Search messages
9. Get channel analytics
10. Delete channel
```

### 🎯 Demo Flow 2: Real-time Messaging Demo (3 minutes)

```
1. Login
2. List all channels
3. Join "general" channel
4. Send message "Hello team! 👋"
5. Get messages (see your message appear)
6. Reply to someone's message
7. Add reaction to message
8. Send image
9. Export conversation
```

### 🎯 Demo Flow 3: Direct Messaging Demo (2 minutes)

```
1. Login
2. Get online users
3. Create DM with specific user
4. Send text message
5. Send image in DM
6. Get DM history
7. Mark as read
```

### 🎯 Demo Flow 4: Complete CRUD Operations (4 minutes)

**PREREQUISITE:**
```
0. Login and get organization UUID (CRITICAL!)
   GET /api/v1/organizations/
   Copy the "id" field value
```

**CREATE:**
```
1. Create team channel (include organization UUID in body)
2. Create private channel (include organization UUID in body)
3. Send messages to both
```

**READ:**
```
4. List all channels
5. Get channel details
6. Get messages from channel
7. Search messages
```

**UPDATE:**
```
8. Update channel name
9. Edit a message
10. Update user status
```

**DELETE:**
```
11. Delete a message
12. Delete a channel
```

---

## Presentation Tips & Best Practices

### ✅ Before Your Demo

**1. Prepare Your Environment:**
```bash
# Start server
cd D:\Projects\connectflow-django
python manage.py runserver

# Verify it's running
# Open http://127.0.0.1:8000/admin/
```

**2. Setup Postman Collection:**
- Import/Create "ConnectFlow Pro Demo" collection
- Save all requests organized in folders
- Set up environment with auth_token variable
- Test all requests before presentation

**3. Have Test Data Ready:**
- Multiple test users created
- At least 2-3 channels with messages
- Sample images and files for upload
- Know your channel UUIDs

### 🎨 During Your Presentation

**Visual Tips:**
- Use Postman's dark theme for better visibility
- Increase font size (View → Text Size → Large)
- Use collections sidebar for easy navigation
- Enable "Two Pane View" for request/response side-by-side

**Demonstration Flow:**
1. Start with simple GET requests (list channels)
2. Progress to POST (create channel, send message)
3. Show UPDATE operations (edit message)
4. Demonstrate DELETE (with caution!)
5. End with advanced features (analytics, search)

**Common Mistakes to Avoid:**
- ❌ Forgetting to include Authorization header
- ❌ Using expired tokens
- ❌ Not setting Content-Type header
- ❌ Typos in JSON body
- ❌ Using invalid UUIDs

### 💡 Pro Presenter Tips

**1. Use Postman Features:**
```
- Pre-request Scripts: Auto-refresh tokens
- Tests: Validate responses automatically
- Variables: Use {{channel_id}} instead of hardcoded values
- Console: Show detailed request/response logs
```

**2. Prepare Backup Plans:**
- Have screenshots of successful responses
- Keep backup collection exported as JSON
- Have cURL commands ready as alternative
- Test with Postman Web if desktop fails

**3. Explain While You Demo:**
```
"First, I'll authenticate by sending my credentials..."
"Notice the 200 OK status - that means success..."
"The response shows the created channel with UUID..."
"Now I'll use this UUID to send a message..."
```

**4. Handle Errors Gracefully:**
```
401 → "Token expired, let me refresh by logging in again..."
404 → "Wrong endpoint, let me correct the URL..."
400 → "Invalid JSON, let me fix the syntax..."
500 → "Server error, this would be investigated in production..."
```

---

## Advanced Postman Features for Demos

### 🔄 Auto-Login with Pre-request Script

Add this to your collection's Pre-request Scripts:

```javascript
// Auto-login if token is missing or expired
if (!pm.environment.get("auth_token")) {
    pm.sendRequest({
        url: 'http://127.0.0.1:8000/api/v1/login/',
        method: 'POST',
        header: {
            'Content-Type': 'application/json'
        },
        body: {
            mode: 'raw',
            raw: JSON.stringify({
                email: "test@connectflow.com",
                password: "Password123!"
            })
        }
    }, function (err, response) {
        var token = response.json().token;
        pm.environment.set("auth_token", token);
    });
}
```

### ✅ Response Validation Tests

Add to Tests tab for automatic validation:

```javascript
// Test for successful response
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

// Test response time
pm.test("Response time is less than 500ms", function () {
    pm.expect(pm.response.responseTime).to.be.below(500);
});

// Test response structure
pm.test("Response has required fields", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('id');
    pm.expect(jsonData).to.have.property('name');
});

// Save values for next requests
var jsonData = pm.response.json();
pm.environment.set("channel_id", jsonData.id);
```

### 📊 Collection Runner for Bulk Testing

Use Runner to execute multiple requests in sequence:

```
1. Click "Runner" button
2. Select "ConnectFlow Pro API" collection
3. Set iterations: 1
4. Order:
   - Login
   - Create Channel
   - Send 10 Messages
   - Get Messages
   - Delete Channel
5. Run
6. View results summary
```

---

## Comprehensive Testing Checklist

### Authentication ✅
- [ ] Login with valid credentials
- [ ] Login with invalid credentials (test error)
- [ ] Logout
- [ ] Use token in subsequent requests

### Channel Operations ✅
- [ ] Check organization first (GET /api/v1/organizations/)
- [ ] Copy organization UUID
- [ ] List all channels
- [ ] Create team channel (with organization UUID)
- [ ] Create private channel
- [ ] Create department channel
- [ ] Get channel details
- [ ] Update channel name
- [ ] Update channel description
- [ ] Delete channel

### Message Operations ✅
- [ ] Get messages from channel
- [ ] Send text message
- [ ] Send message with @mention
- [ ] Send reply to message
- [ ] Send image message
- [ ] Send file attachment
- [ ] Send voice message
- [ ] Edit message
- [ ] Delete message
- [ ] Add reaction to message
- [ ] Remove reaction
- [ ] Pin message
- [ ] Get pinned messages
- [ ] Search messages
- [ ] Mark messages as read
- [ ] Export messages

### Direct Messages ✅
- [ ] List DM conversations
- [ ] Create DM with user
- [ ] Get DM messages
- [ ] Send DM text
- [ ] Send DM image
- [ ] Send DM file

### User Operations ✅
- [ ] Get my profile
- [ ] List all users
- [ ] Search users
- [ ] Get online users
- [ ] Update user status
- [ ] Toggle theme

### Notifications ✅
- [ ] Get all notifications
- [ ] Get unread notifications
- [ ] Mark notification as read
- [ ] Mark all as read

### Advanced Features ✅
- [ ] Channel analytics
- [ ] Message search
- [ ] Data export
- [ ] Bulk operations

---

## Quick Reference Card

### Base URL
```
http://127.0.0.1:8000/api/v1/
```

### Authentication Headers
```
Content-Type: application/json
Authorization: Token {{auth_token}}
```

### Test User Credentials
```
Email: test@connectflow.com
Password: Password123!
```

---

### 🔥 Quick Command Reference

#### Authentication
```
POST   /api/v1/login/                    → Login & get token
POST   /api/v1/logout/                   → Logout
```

#### Channels
```
GET    /api/v1/channels/                 → List all channels
POST   /api/v1/channels/                 → Create channel
GET    /api/v1/channels/{id}/            → Get channel details
PUT    /api/v1/channels/{id}/            → Update channel
DELETE /api/v1/channels/{id}/            → Delete channel
POST   /api/v1/channels/{id}/members/    → Add members
DELETE /api/v1/channels/{id}/members/{user_id}/ → Remove member
POST   /api/v1/channels/{id}/leave/      → Leave channel
POST   /api/v1/channels/{id}/mute/       → Mute channel
POST   /api/v1/channels/{id}/pin/        → Pin channel
GET    /api/v1/channels/{id}/analytics/  → Get analytics
```

#### Messages
```
GET    /api/v1/channels/{id}/messages/   → Get messages
POST   /api/v1/messages/                 → Send message
GET    /api/v1/messages/{id}/            → Get message details
PUT    /api/v1/messages/{id}/            → Edit message
DELETE /api/v1/messages/{id}/            → Delete message
POST   /api/v1/messages/{id}/reactions/  → Add reaction
DELETE /api/v1/messages/{id}/reactions/{emoji}/ → Remove reaction
POST   /api/v1/messages/{id}/pin/        → Pin message
GET    /api/v1/messages/{id}/replies/    → Get thread replies
GET    /api/v1/messages/search/?q=text   → Search messages
POST   /api/v1/channels/{id}/read/       → Mark as read
```

#### Direct Messages
```
GET    /api/v1/direct_messages/          → List DM conversations
POST   /api/v1/direct_messages/create/   → Create/get DM
GET    /api/v1/direct_messages/{id}/messages/ → Get DM messages
POST   /api/v1/direct_messages/{id}/send/ → Send DM
```

#### Users
```
GET    /api/v1/users/me/                 → My profile
GET    /api/v1/users/                    → List users
GET    /api/v1/users/online/             → Online users
GET    /api/v1/users/search/?q=name      → Search users
POST   /api/v1/users/status/             → Update status
POST   /api/v1/users/toggle_theme/       → Toggle theme
```

#### Notifications
```
GET    /api/v1/notifications/            → Get all notifications
GET    /api/v1/notifications/?unread=true → Unread only
POST   /api/v1/notifications/{id}/read/  → Mark as read
POST   /api/v1/notifications/read_all/   → Mark all read
```

#### Organizations
```
GET    /api/v1/organizations/            → Get your organization
GET    /api/v1/departments/              → List departments
POST   /api/v1/departments/              → Create department
GET    /api/v1/teams/                    → List teams
POST   /api/v1/teams/                    → Create team
GET    /api/v1/shared-projects/          → List shared projects
POST   /api/v1/shared-projects/          → Create shared project
```

---

## 🏢 Organizations (Check This First!)

**⚠️ IMPORTANT:** Before you can create channels, you MUST be assigned to an organization!

### 1. Get Your Organization (GET) - **CHECK THIS FIRST!**

**Method:** GET  
**URL:** `http://127.0.0.1:8000/api/v1/organizations/`  
**Authorization:** Bearer Token → `{{auth_token}}`

**What it does:** Shows which organization you belong to

**Expected Response (You have an organization ✅):**
```json
[
  {
    "id": "org-uuid-here",
    "name": "Test Organization",
    "slug": "test-org",
    "industry": "Technology",
    "headquarters": "New York, USA",
    "website": "https://testorg.com",
    "created_at": "2026-01-01T10:00:00Z"
  }
]
```

**If you get `[]` (empty array) ❌:**  
You don't have an organization! Here's how to fix it:

**Option 1: Django Admin (Easiest)**
```
1. Open: http://127.0.0.1:8000/admin/
2. Login with superuser credentials
3. Go to: Organizations → Organizations
4. Click "Add Organization"
5. Fill in:
   - Name: "Test Organization"
   - Slug: "test-org"
6. Save
7. Go to: Accounts → Users
8. Find your user (test@connectflow.com)
9. Edit and select the organization you just created
10. Save
```

**Option 2: Django Shell**
```bash
python manage.py shell

from apps.organizations.models import Organization
from apps.accounts.models import User

# Create organization
org = Organization.objects.create(
    name="Test Organization",
    slug="test-org",
    industry="Technology"
)

# Assign user to organization
user = User.objects.get(email="test@connectflow.com")
user.organization = org
user.save()
```

**Option 3: Use Web Interface**
- Register a new account through the web interface
- It will automatically create an organization for you

---

### 2. List Departments (GET)

**Method:** GET  
**URL:** `http://127.0.0.1:8000/api/v1/departments/`  
**Authorization:** Bearer Token → `{{auth_token}}`

**Expected Response:**
```json
[
  {
    "id": "dept-uuid",
    "name": "Engineering",
    "description": "Engineering department",
    "organization": "org-uuid",
    "head": {
      "id": "user-uuid",
      "username": "head@test.com",
      "first_name": "John",
      "last_name": "Doe"
    },
    "created_at": "2026-01-02T10:00:00Z",
    "member_count": 25
  }
]
```

---

### 3. Create Department (POST)

**Method:** POST  
**URL:** `http://127.0.0.1:8000/api/v1/departments/`  
**Authorization:** Bearer Token → `{{auth_token}}`  
**Headers:** `Content-Type: application/json`

**Body:**
```json
{
  "name": "Marketing",
  "description": "Marketing and communications department"
}
```

**Expected Response:**
```json
{
  "id": "new-dept-uuid",
  "name": "Marketing",
  "description": "Marketing and communications department",
  "organization": "org-uuid",
  "created_at": "2026-01-04T01:00:00Z",
  "member_count": 0
}
```

---

### 4. List Teams (GET)

**Method:** GET  
**URL:** `http://127.0.0.1:8000/api/v1/teams/`  
**Authorization:** Bearer Token → `{{auth_token}}`

**Expected Response:**
```json
[
  {
    "id": "team-uuid",
    "name": "Frontend Team",
    "department": {
      "id": "dept-uuid",
      "name": "Engineering"
    },
    "manager": {
      "id": "user-uuid",
      "username": "manager@test.com"
    },
    "created_at": "2026-01-03T10:00:00Z",
    "member_count": 8
  }
]
```

---

### 5. List Shared Projects (GET)

**Method:** GET  
**URL:** `http://127.0.0.1:8000/api/v1/shared-projects/`  
**Authorization:** Bearer Token → `{{auth_token}}`

**Expected Response:**
```json
[
  {
    "id": "project-uuid",
    "name": "Website Redesign",
    "description": "Q1 2026 website redesign project",
    "host_organization": {
      "id": "org-uuid",
      "name": "Test Organization"
    },
    "created_by": {
      "id": "user-uuid",
      "username": "creator@test.com"
    },
    "members": [
      {
        "id": "user-uuid-1",
        "username": "member1@test.com"
      }
    ],
    "created_at": "2026-01-04T10:00:00Z"
  }
]
```

---

### 📋 Common Request Bodies

#### Create Public Channel
```json
{
  "name": "marketing-team",
  "description": "Marketing team discussions",
  "channel_type": "TEAM",
  "organization": "your-org-uuid-here"
}
```

#### Create Private Channel with Privacy Flag
```json
{
  "name": "leadership-private",
  "description": "Private leadership channel",
  "channel_type": "PRIVATE",
  "organization": "your-org-uuid-here",
  "is_private": true
}
```

#### Create Department Channel
```json
{
  "name": "engineering-dept",
  "description": "Engineering department channel",
  "channel_type": "DEPARTMENT",
  "organization": "your-org-uuid-here"
}
```

#### Create Official Announcement Channel
```json
{
  "name": "company-news",
  "description": "Official company announcements",
  "channel_type": "OFFICIAL",
  "organization": "your-org-uuid-here",
  "read_only": false
}
```

#### Send Text Message
```json
{
  "channel": "channel-uuid",
  "content": "Hello everyone! 👋"
}
```

#### Send Message with Mention
```json
{
  "channel": "channel-uuid",
  "content": "Hey @john, check this out!",
  "mentions": ["user-uuid-of-john"]
}
```

#### Reply to Message
```json
{
  "channel": "channel-uuid",
  "content": "Great idea!",
  "parent_message": "message-uuid"
}
```

#### Add Reaction
```json
{
  "emoji": "👍"
}
```

#### Update Channel
```json
{
  "name": "new-channel-name",
  "description": "Updated description"
}
```

#### Edit Message
```json
{
  "content": "Updated message content"
}
```

#### Add Members
```json
{
  "user_ids": ["uuid-1", "uuid-2"]
}
```

#### Update Status
```json
{
  "status": "AWAY",
  "custom_status": "In a meeting 🎯"
}
```

#### Create DM
```json
{
  "user_id": "recipient-uuid"
}
```

#### Mark as Read
```json
{
  "last_read_message_id": "message-uuid"
}
```

---

### 🎯 HTTP Status Codes

| Code | Meaning | When You'll See It |
|------|---------|-------------------|
| **200** | OK | Successful GET, PUT, PATCH |
| **201** | Created | Successful POST (created new resource) |
| **204** | No Content | Successful DELETE |
| **400** | Bad Request | Invalid JSON, missing fields |
| **401** | Unauthorized | Missing/invalid token |
| **403** | Forbidden | No permission for this action |
| **404** | Not Found | Resource doesn't exist |
| **429** | Too Many Requests | Rate limit exceeded |
| **500** | Server Error | Bug in server code |

---

### 🔧 Common JSON Body Errors

❌ **Wrong:**
```json
{
  "name": "test",  ← Extra comma
}
```

✅ **Correct:**
```json
{
  "name": "test"
}
```

❌ **Wrong:**
```json
{
  name: "test"  ← Missing quotes
}
```

✅ **Correct:**
```json
{
  "name": "test"
}
```

❌ **Wrong:**
```json
{
  "message": 'Hello'  ← Single quotes
}
```

✅ **Correct:**
```json
{
  "message": "Hello"
}
```

---

### 💾 Sample Postman Environment Variables

Create environment "ConnectFlow Local" with these variables:

| Variable | Initial Value | Current Value |
|----------|--------------|---------------|
| `base_url` | `http://127.0.0.1:8000/api/v1` | `http://127.0.0.1:8000/api/v1` |
| `auth_token` | (paste after login) | (paste after login) |
| `org_id` | `4b03ece4-1d0b-45f2-96c1-aae20843f2c7` | (paste your org UUID) |
| `channel_id` | (save from response) | (save from response) |
| `message_id` | (save from response) | (save from response) |
| `user_id` | (save from response) | (save from response) |

**Usage in requests:**
```
URL: {{base_url}}/channels/{{channel_id}}/
Header: Authorization: Token {{auth_token}}
Body: {"organization": "{{org_id}}", "name": "test-channel", "channel_type": "TEAM"}
```

---

### 🚀 Speed Tips for Postman

**Keyboard Shortcuts:**
- `Ctrl + Enter` → Send request
- `Ctrl + T` → New tab
- `Ctrl + S` → Save request
- `Ctrl + L` → Focus URL bar
- `Ctrl + E` → Switch environment

**Time Savers:**
1. **Duplicate Tab:** Right-click tab → Duplicate
2. **Copy as cURL:** Click Code → cURL
3. **Bulk Edit:** Use Find & Replace (Ctrl + F)
4. **History:** View past requests in left sidebar
5. **Snippets:** Use right sidebar for common test code

---

## Next Steps

After mastering basic API testing:

1. ✅ **Explore all endpoints** - Check `API_DOCUMENTATION.md`
2. ✅ **Test error cases** - Try sending invalid data
3. ✅ **Learn Postman Tests** - Automate response validation
4. ✅ **Try the Runner** - Run multiple requests at once
5. ✅ **Export your collection** - Share with your team

---

## Getting Help

**Documentation:**
- Full API Reference: See `API_DOCUMENTATION.md` in project root
- Django Admin: http://127.0.0.1:8000/admin/
- Postman Learning Center: https://learning.postman.com/

**Common Commands:**

Start server:
```bash
cd D:\Projects\connectflow-django
python manage.py runserver
```

Stop server:
```
Press Ctrl + C in the terminal
```

Test user already created for you:
```
Email: test@connectflow.com
Password: Password123!
```

Create additional test users (if needed):
```bash
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> user = User.objects.create_user(email='new@test.com', username='new@test.com', password='YourPassword123!')
```

---

## Success Checklist ✅

Before you finish, make sure you can:

- [ ] Start the Django server
- [ ] Open Postman
- [ ] Send a login request with test@connectflow.com
- [ ] Get a token back
- [ ] **Know how to use Authorization tab (Bearer Token)**
- [ ] Open a new tab and test your profile (stay logged in)
- [ ] Test at least 3 different endpoints with the same token
- [ ] Save requests in a collection
- [ ] Understand error messages

---

## Congratulations! 🎉

You're now ready to test ConnectFlow Pro APIs like a pro! 

Remember:
- **Practice makes perfect** - Test regularly
- **Read error messages** - They're your friends
- **Save your work** - Use collections
- **Have fun!** - API testing is powerful

---

**Happy Testing! 🚀**

*Last Updated: January 4, 2026*
