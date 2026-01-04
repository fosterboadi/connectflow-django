# 📌 Postman Quick Reference - ConnectFlow Pro

## 🔗 Base URL
```
http://127.0.0.1:8000
```

---

## 🔐 Authentication

### Login (Get Token)
```
POST /api/v1/login/

Headers:
  Content-Type: application/json

Body:
{
  "email": "your@email.com",
  "password": "yourpassword"
}

Response:
{
  "token": "abc123...",
  "user": { ... }
}
```

### Logout
```
POST /api/v1/logout/

Headers:
  Authorization: Token YOUR_TOKEN_HERE
```

---

## 👤 User Endpoints

### Get My Profile
```
GET /api/v1/users/me/

Headers:
  Authorization: Token YOUR_TOKEN_HERE
```

### List All Users (Same Org)
```
GET /api/v1/users/

Headers:
  Authorization: Token YOUR_TOKEN_HERE
```

### Toggle Theme (Light/Dark)
```
POST /api/v1/users/toggle_theme/

Headers:
  Authorization: Token YOUR_TOKEN_HERE
```

---

## 💬 Channel Endpoints

### List All Channels
```
GET /api/v1/channels/

Headers:
  Authorization: Token YOUR_TOKEN_HERE
```

### Get Channel Details
```
GET /api/v1/channels/{channel_id}/

Headers:
  Authorization: Token YOUR_TOKEN_HERE
```

### Get Channel Messages
```
GET /api/v1/channels/{channel_id}/messages/

Headers:
  Authorization: Token YOUR_TOKEN_HERE
```

---

## ✉️ Message Endpoints

### Send Message
```
POST /api/v1/messages/

Headers:
  Authorization: Token YOUR_TOKEN_HERE
  Content-Type: application/json

Body:
{
  "channel": "channel-uuid-here",
  "content": "Hello World!"
}
```

### Delete Message
```
DELETE /api/v1/messages/{message_id}/

Headers:
  Authorization: Token YOUR_TOKEN_HERE
```

---

## 🔔 Notification Endpoints

### Get My Notifications
```
GET /api/v1/notifications/

Headers:
  Authorization: Token YOUR_TOKEN_HERE
```

### Mark Notification as Read
```
POST /api/v1/notifications/{notification_id}/mark-read/

Headers:
  Authorization: Token YOUR_TOKEN_HERE
```

### Mark All as Read
```
POST /api/v1/notifications/mark-read/

Headers:
  Authorization: Token YOUR_TOKEN_HERE
```

---

## 🏢 Organization Endpoints

### Get Organization Info
```
GET /api/v1/organizations/

Headers:
  Authorization: Token YOUR_TOKEN_HERE
```

### List Departments
```
GET /api/v1/departments/

Headers:
  Authorization: Token YOUR_TOKEN_HERE
```

### List Teams
```
GET /api/v1/teams/

Headers:
  Authorization: Token YOUR_TOKEN_HERE
```

---

## 📊 Project Endpoints

### List Projects
```
GET /api/v1/projects/

Headers:
  Authorization: Token YOUR_TOKEN_HERE
```

### Create Project
```
POST /api/v1/projects/

Headers:
  Authorization: Token YOUR_TOKEN_HERE
  Content-Type: application/json

Body:
{
  "name": "New Project",
  "description": "Project description"
}
```

### Get Project Details
```
GET /api/v1/projects/{project_id}/

Headers:
  Authorization: Token YOUR_TOKEN_HERE
```

---

## ⚙️ Common Headers

### For All Requests (Except Login)
```
Authorization: Token YOUR_TOKEN_HERE
```

### For POST/PUT/PATCH Requests
```
Content-Type: application/json
```

---

## 🔧 Common Response Codes

| Code | Meaning | What to Do |
|------|---------|------------|
| **200** | OK | Success! ✅ |
| **201** | Created | Resource created ✅ |
| **400** | Bad Request | Check your JSON/data ❌ |
| **401** | Unauthorized | Check your token ❌ |
| **403** | Forbidden | No permission ❌ |
| **404** | Not Found | Check URL ❌ |
| **500** | Server Error | Check Django console ❌ |

---

## 🎯 Sample Workflow

### 1. Login
```
POST /api/v1/login/
→ Get token
→ Save token
```

### 2. Get Profile
```
GET /api/v1/users/me/
→ Verify authentication works
```

### 3. List Channels
```
GET /api/v1/channels/
→ Get channel IDs
```

### 4. Send Message
```
POST /api/v1/messages/
→ Use channel ID from step 3
```

### 5. Logout
```
POST /api/v1/logout/
→ Invalidate token
```

---

## 💡 Pro Tips

### Save Time with Variables
```
{{base_url}} = http://127.0.0.1:8000
{{auth_token}} = Your token here
{{channel_id}} = Channel UUID

Then use:
{{base_url}}/api/v1/channels/{{channel_id}}/
```

### Test with Real Data
- Use UUIDs from actual database
- Copy IDs from GET responses
- Test edge cases (empty strings, long text)

### Organize Your Requests
```
📁 ConnectFlow API
  ├── 🔐 Auth (Login, Logout)
  ├── 👤 Users (Profile, List)
  ├── 💬 Channels (List, Messages)
  └── 🔔 Notifications
```

---

## 🐛 Quick Troubleshooting

### "Connection refused"
→ Start Django server: `python manage.py runserver`

### "401 Unauthorized"
→ Login again to get fresh token

### "400 Bad Request"
→ Check JSON syntax (commas, quotes)

### "404 Not Found"
→ Verify URL (check for typos)

### "500 Internal Server Error"
→ Check Django terminal for errors

---

## 📚 Example Collection JSON

Save this as a file and import into Postman:

```json
{
  "info": {
    "name": "ConnectFlow Pro API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Login",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"email\": \"test@test.com\",\n  \"password\": \"password123\"\n}"
        },
        "url": {
          "raw": "http://127.0.0.1:8000/api/v1/login/",
          "protocol": "http",
          "host": ["127", "0", "0", "1"],
          "port": "8000",
          "path": ["api", "v1", "login", ""]
        }
      }
    }
  ]
}
```

---

**Keep this file handy while testing! 📌**

*Last Updated: January 4, 2026*
