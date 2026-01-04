# 🚀 Complete Beginner's Guide to Testing ConnectFlow Pro APIs with Postman

**Welcome!** This guide will walk you through testing your ConnectFlow Pro APIs locally, step by step. No prior Postman experience needed!

---

## 📋 Table of Contents
1. [What You'll Need](#what-youll-need)
2. [Step 1: Install Postman](#step-1-install-postman)
3. [Step 2: Start Your Local Server](#step-2-start-your-local-server)
4. [Step 3: Understanding API Testing](#step-3-understanding-api-testing)
5. [Step 4: Test Your First API (Login)](#step-4-test-your-first-api-login)
6. [Step 5: Save Your Token](#step-5-save-your-token)
7. [Step 6: Test Authenticated Endpoints](#step-6-test-authenticated-endpoints)
8. [Common API Tests](#common-api-tests)
9. [Troubleshooting](#troubleshooting)

---

## What You'll Need

- ✅ Postman installed (free)
- ✅ ConnectFlow Pro running locally
- ✅ A test user account (email and password)
- ✅ 15-30 minutes of your time

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
4. Enter this (replace with your actual test credentials):

```json
{
  "email": "apitest@test.com",
  "password": "testpassword123"
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

## Step 6: Test Authenticated Endpoints

Now let's test an endpoint that requires authentication!

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
  "username": "apitest@test.com",
  "email": "apitest@test.com",
  "first_name": "API",
  "last_name": "Test",
  "role": "TEAM_MEMBER",
  "organization": {
    "id": "uuid-here",
    "name": "Test Organization"
  },
  "status": "ONLINE",
  "theme": "LIGHT"
}
```

---

## Common API Tests

### 1. List All Users in Organization

**Method:** GET  
**URL:** `http://127.0.0.1:8000/api/v1/users/`  
**Headers:** `Authorization: Token {{auth_token}}`

**What it does:** Shows all users in your organization

---

### 2. List All Channels

**Method:** GET  
**URL:** `http://127.0.0.1:8000/api/v1/channels/`  
**Headers:** `Authorization: Token {{auth_token}}`

**What it does:** Shows all channels you have access to

---

### 3. Get Messages from a Channel

**Method:** GET  
**URL:** `http://127.0.0.1:8000/api/v1/channels/{channel_id}/messages/`  
**Headers:** `Authorization: Token {{auth_token}}`

Replace `{channel_id}` with an actual channel UUID from the previous response!

---

### 4. Send a Message

**Method:** POST  
**URL:** `http://127.0.0.1:8000/api/v1/messages/`  
**Headers:**
- `Authorization: Token {{auth_token}}`
- `Content-Type: application/json`

**Body:**
```json
{
  "channel": "channel-uuid-here",
  "content": "Hello from Postman! 🚀"
}
```

---

### 5. Create a Notification

**Method:** POST  
**URL:** `http://127.0.0.1:8000/api/v1/notifications/`  
**Headers:**
- `Authorization: Token {{auth_token}}`
- `Content-Type: application/json`

**Body:**
```json
{
  "title": "Test Notification",
  "content": "This is a test from Postman",
  "notification_type": "SYSTEM"
}
```

---

### 6. List Organizations

**Method:** GET  
**URL:** `http://127.0.0.1:8000/api/v1/organizations/`  
**Headers:** `Authorization: Token {{auth_token}}`

---

### 7. Toggle Theme

**Method:** POST  
**URL:** `http://127.0.0.1:8000/api/v1/users/toggle_theme/`  
**Headers:** `Authorization: Token {{auth_token}}`

**What it does:** Switches between LIGHT and DARK mode

---

### 8. Logout

**Method:** POST  
**URL:** `http://127.0.0.1:8000/api/v1/logout/`  
**Headers:** `Authorization: Token {{auth_token}}`

**What it does:** Invalidates your token and logs you out

---

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
📁 ConnectFlow Pro API
├── 🔐 Authentication
│   ├── Login
│   └── Logout
├── 👤 Users
│   ├── Get My Profile
│   ├── List All Users
│   └── Toggle Theme
├── 💬 Messaging
│   ├── List Channels
│   ├── Get Channel Messages
│   ├── Send Message
│   └── Delete Message
├── 📢 Notifications
│   ├── Get Notifications
│   └── Mark as Read
└── 🏢 Organizations
    ├── Get Organization
    ├── List Departments
    └── List Teams
```

---

## Quick Reference Card

### Most Common Headers

```
Content-Type: application/json
Authorization: Token YOUR_TOKEN_HERE
```

### Base URL
```
http://127.0.0.1:8000/api/v1/
```

### Login Endpoint
```
POST /api/v1/login/
Body: { "email": "...", "password": "..." }
```

### Get Profile
```
GET /api/v1/users/me/
Header: Authorization: Token YOUR_TOKEN
```

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

Create test user:
```bash
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> user = User.objects.create_user('test@test.com', password='testpass123')
```

---

## Success Checklist ✅

Before you finish, make sure you can:

- [ ] Start the Django server
- [ ] Open Postman
- [ ] Send a login request
- [ ] Get a token back
- [ ] Use the token to get your profile
- [ ] Test at least 3 different endpoints
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
