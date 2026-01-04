# 🎤 ConnectFlow Pro - Presentation API Testing Guide

**Perfect for Demos & Presentations!** Test your live deployed API in minutes.

**🌐 Live API:** `https://connectflow.onrender.com/api/v1/`

---

## 🚀 Quick Start (2 Minutes)

### Step 1: Open Your Browser

**Go to the API Root:**
```
https://connectflow.onrender.com/api/v1/
```

You'll see a beautiful browsable API interface showing all available endpoints!

### Step 2: Login First

**Option A: Login via Web Interface (Easiest)**
```
https://connectflow.onrender.com/accounts/login/
```
Use your credentials or register a new account.

**Option B: Login via API (Returns Token)**
```
POST https://connectflow.onrender.com/api/v1/login/
```

### Step 3: Explore APIs in Browser

Once logged in, visit these URLs directly in your browser:

✅ **API Root** - See all endpoints
```
https://connectflow.onrender.com/api/v1/
```

✅ **Your Organizations**
```
https://connectflow.onrender.com/api/v1/organizations/
```

✅ **All Channels**
```
https://connectflow.onrender.com/api/v1/channels/
```

✅ **All Messages**
```
https://connectflow.onrender.com/api/v1/messages/
```

✅ **All Users**
```
https://connectflow.onrender.com/api/v1/users/
```

✅ **Departments**
```
https://connectflow.onrender.com/api/v1/departments/
```

✅ **Teams**
```
https://connectflow.onrender.com/api/v1/teams/
```

✅ **Projects**
```
https://connectflow.onrender.com/api/v1/projects/
```

---

## 🎯 Presentation Demo Workflow (5 Minutes)

### **Demo 1: Browse Live API (No Tools Needed!)**

**1. Show API Root**
- Open: `https://connectflow.onrender.com/api/v1/`
- Point out: Clean, professional API interface
- Highlight: All available endpoints listed

**2. Show Live Data**
- Click on `/organizations/`
- Show: Real organization data in JSON
- Explain: RESTful API structure

**3. Show Interactive Forms**
- Scroll to bottom of any endpoint page
- Show: Built-in forms to test POST/PUT/DELETE
- Demonstrate: Creating data without writing code

**4. Show Different Endpoints**
- Click through:
  - `/channels/` - Chat channels
  - `/messages/` - Messages
  - `/users/` - User management
  - `/tickets/` - Support system

---

### **Demo 2: Create Data in Browser (No Postman!)**

**Create a New Channel:**

1. **Go to:** `https://connectflow.onrender.com/api/v1/channels/`

2. **Scroll to bottom** - You'll see a form

3. **Select:** "application/json" from content type dropdown

4. **Paste this JSON:**
   ```json
   {
     "name": "demo-presentation-2026",
     "description": "Created during live demo!",
     "channel_type": "TEAM",
     "organization": "your-org-uuid-from-step-1"
   }
   ```

5. **Click "POST"** button

6. **Show response:** Instant JSON response with new channel details!

**Send a Message:**

1. **Go to:** `https://connectflow.onrender.com/api/v1/messages/`

2. **Use the form to POST:**
   ```json
   {
     "channel": "channel-uuid-from-previous-step",
     "content": "Hello from our live presentation! 🎉"
   }
   ```

3. **Show result:** Message created instantly!

---

### **Demo 3: Postman for Advanced Testing**

**Setup (30 seconds):**

1. Open Postman
2. Create new request
3. Set URL: `https://connectflow.onrender.com/api/v1/login/`
4. Method: POST
5. Body (JSON):
   ```json
   {
     "email": "your-email@example.com",
     "password": "your-password"
   }
   ```
6. Send → Copy token from response

**Show Token Authentication:**

```
GET https://connectflow.onrender.com/api/v1/organizations/

Headers:
Authorization: Token YOUR_TOKEN_HERE
Content-Type: application/json
```

**Demo Complete CRUD:**

**CREATE** - New channel:
```
POST https://connectflow.onrender.com/api/v1/channels/

Headers:
Authorization: Token YOUR_TOKEN_HERE
Content-Type: application/json

Body:
{
  "name": "postman-demo-channel",
  "description": "Created via Postman",
  "channel_type": "TEAM",
  "organization": "org-uuid"
}
```

**READ** - List channels:
```
GET https://connectflow.onrender.com/api/v1/channels/

Headers:
Authorization: Token YOUR_TOKEN_HERE
```

**UPDATE** - Edit channel:
```
PUT https://connectflow.onrender.com/api/v1/channels/{channel-id}/

Headers:
Authorization: Token YOUR_TOKEN_HERE
Content-Type: application/json

Body:
{
  "name": "updated-demo-channel",
  "description": "Updated during demo"
}
```

**DELETE** - Remove channel:
```
DELETE https://connectflow.onrender.com/api/v1/channels/{channel-id}/

Headers:
Authorization: Token YOUR_TOKEN_HERE
```

---

## 📋 All Available Endpoints

### 🔐 Authentication
```
POST   /api/v1/login/           - Login & get token
POST   /api/v1/logout/          - Logout
```

### 👥 Users
```
GET    /api/v1/users/           - List all users
GET    /api/v1/users/me/        - Current user profile
GET    /api/v1/users/{id}/      - User details
PATCH  /api/v1/users/{id}/      - Update user
```

### 🏢 Organizations
```
GET    /api/v1/organizations/   - Your organization
GET    /api/v1/departments/     - List departments
POST   /api/v1/departments/     - Create department
GET    /api/v1/teams/           - List teams
POST   /api/v1/teams/           - Create team
GET    /api/v1/projects/        - List projects
POST   /api/v1/projects/        - Create project
```

### 💬 Channels & Messages
```
GET    /api/v1/channels/                      - List channels
POST   /api/v1/channels/                      - Create channel
GET    /api/v1/channels/{id}/                 - Channel details
PUT    /api/v1/channels/{id}/                 - Update channel
DELETE /api/v1/channels/{id}/                 - Delete channel
POST   /api/v1/channels/{id}/members/         - Add members
POST   /api/v1/channels/{id}/leave/           - Leave channel

GET    /api/v1/messages/                      - List messages
POST   /api/v1/messages/                      - Send message
GET    /api/v1/messages/{id}/                 - Message details
PUT    /api/v1/messages/{id}/                 - Edit message
DELETE /api/v1/messages/{id}/                 - Delete message
```

### 🎫 Support Tickets
```
GET    /api/v1/tickets/         - List tickets
POST   /api/v1/tickets/         - Create ticket
GET    /api/v1/tickets/{id}/    - Ticket details
PUT    /api/v1/tickets/{id}/    - Update ticket
```

---

## 🌐 Browser Testing Tips for Presentations

### ✅ What Works Great in Browser

**1. Viewing Data (GET Requests)**
- Just paste URL in browser
- Beautiful formatted JSON
- No tools needed
- Perfect for quick demos

**2. Creating Data (POST/PUT/DELETE)**
- Scroll to bottom of any endpoint
- Use built-in HTML forms
- Select JSON content type
- Fill in data and submit
- See instant results

**3. Exploring API Structure**
- Click through endpoints
- See relationships
- View sample data
- Understand data models

### ⚠️ When to Switch to Postman

**Use Postman when you need:**
- Token-based authentication (not session)
- Custom headers
- Multiple test accounts
- Saved request collections
- Automated testing
- File uploads
- Team collaboration

---

## 🎨 Presentation Best Practices

### Before Your Demo

**1. Prepare Test Data:**
```bash
# Create test organization, channels, users beforehand
# Don't create from scratch during demo (takes time)
```

**2. Bookmark These URLs:**
```
https://connectflow.onrender.com/api/v1/
https://connectflow.onrender.com/api/v1/organizations/
https://connectflow.onrender.com/api/v1/channels/
https://connectflow.onrender.com/api/v1/messages/
```

**3. Have Credentials Ready:**
```
Email: your-demo-account@example.com
Password: (saved in password manager)
```

**4. Pre-login:**
- Login 5 minutes before presentation
- Test all URLs work
- Verify data is visible
- Prepare sample JSON snippets

### During Your Demo

**Start Simple → Progress to Complex:**

1. **Show API Root** (30 seconds)
   - "Here's our live API endpoint"
   - Show browsable interface
   - Point out professional documentation

2. **Show Data** (1 minute)
   - Click on organizations
   - Show real data in JSON
   - Explain REST principles

3. **Create Something** (2 minutes)
   - Use browser form to create channel
   - Show instant response
   - Navigate to verify it appears in list

4. **Switch to Postman** (2 minutes)
   - "For advanced features, we use Postman"
   - Show token authentication
   - Demonstrate CRUD operations
   - Show response times

### Speaking Points

**When showing browser API:**
- "This is Django REST Framework's browsable API"
- "Notice the clean, self-documenting interface"
- "Anyone can explore our API without tools"
- "Forms at bottom let you test POST requests"

**When showing Postman:**
- "Postman is industry standard for API testing"
- "Allows token authentication for security"
- "We can save and organize test requests"
- "Perfect for automated testing"

**When showing responses:**
- "Notice the 200 OK status - successful request"
- "Response time under 500ms - very fast"
- "Clean JSON structure makes integration easy"
- "All CRUD operations work as expected"

---

## 📊 Demo Scenarios

### Scenario 1: "Complete User Journey" (3 minutes)

```
1. Register new user (browser)
   → https://connectflow.onrender.com/accounts/register/

2. Login and get token (Postman)
   → POST /api/v1/login/

3. View my profile (browser)
   → GET /api/v1/users/me/

4. See my organization (browser)
   → GET /api/v1/organizations/

5. Create a channel (Postman)
   → POST /api/v1/channels/

6. Send a message (browser form)
   → POST /api/v1/messages/

7. View the message (browser)
   → GET /api/v1/messages/
```

### Scenario 2: "Team Collaboration Features" (4 minutes)

```
1. Show existing channels
   → GET /api/v1/channels/

2. Create team channel
   → POST /api/v1/channels/ (channel_type: TEAM)

3. Add members to channel
   → POST /api/v1/channels/{id}/members/

4. Send team message
   → POST /api/v1/messages/

5. Show real-time capabilities
   → Explain WebSocket integration

6. Demonstrate message editing
   → PUT /api/v1/messages/{id}/
```

### Scenario 3: "Cross-Organization Project" (5 minutes)

```
1. Show organizations
   → GET /api/v1/organizations/

2. Create shared project
   → POST /api/v1/projects/

3. Add external participants
   → POST /api/v1/projects/{id}/participants/

4. Create project channel
   → POST /api/v1/channels/ (channel_type: PROJECT)

5. Share documents
   → POST /api/v1/messages/ (with file upload)

6. Track project activity
   → GET /api/v1/projects/{id}/activity/
```

---

## 🔧 Troubleshooting During Presentations

### Issue: "401 Unauthorized"

**Quick Fix:**
```
1. Open new tab
2. Login at: https://connectflow.onrender.com/accounts/login/
3. Return to API tab
4. Refresh page
```

**Explanation to Audience:**
- "Session expired - security feature"
- "Just need to re-authenticate"
- "Happens after 24 hours of inactivity"

### Issue: "403 Forbidden"

**Quick Fix:**
```
Check you're using correct organization UUID
Verify you have permission for this action
```

**Explanation to Audience:**
- "This demonstrates our permission system"
- "Users only access authorized resources"
- "Important for data security"

### Issue: "404 Not Found"

**Quick Fix:**
```
Verify UUID is correct
Check endpoint spelling
Ensure resource exists
```

**Explanation to Audience:**
- "Resource doesn't exist - expected behavior"
- "API returns proper HTTP status codes"
- "Makes debugging easy for developers"

### Issue: Slow Response

**Quick Fix:**
```
1. Explain: "Free tier, wakes from sleep"
2. Wait 10-15 seconds
3. Retry request
4. Will be fast after wake-up
```

**Explanation to Audience:**
- "Using free hosting tier for demo"
- "Production would use paid tier - instant response"
- "Still functional, just initial delay"

---

## 📱 Testing from Different Devices

### Desktop Browser
```
✅ Full browsable API
✅ Forms work perfectly
✅ Best presentation view
```

### Mobile Browser
```
⚠️ API works, but forms harder to use
⚠️ Better to use Postman mobile app
```

### Postman Desktop
```
✅ Best for complex demos
✅ Save request collections
✅ Environment variables
✅ Automated tests
```

### Postman Web
```
✅ No installation needed
✅ Access from any browser
✅ Good for quick demos
```

### cURL (Terminal)
```bash
# Login
curl -X POST https://connectflow.onrender.com/api/v1/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"yourpass"}'

# Get organizations (with token)
curl https://connectflow.onrender.com/api/v1/organizations/ \
  -H "Authorization: Token YOUR_TOKEN_HERE"

# Create channel
curl -X POST https://connectflow.onrender.com/api/v1/channels/ \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"name":"curl-demo","description":"Created via cURL","channel_type":"TEAM","organization":"org-uuid"}'
```

---

## 🎯 Quick Reference Card (Print This!)

### Base URL
```
https://connectflow.onrender.com/api/v1/
```

### Browser Quick Links
```
API Root:        https://connectflow.onrender.com/api/v1/
Login:           https://connectflow.onrender.com/accounts/login/
Organizations:   https://connectflow.onrender.com/api/v1/organizations/
Channels:        https://connectflow.onrender.com/api/v1/channels/
Messages:        https://connectflow.onrender.com/api/v1/messages/
Users:           https://connectflow.onrender.com/api/v1/users/
```

### Postman Headers
```
Authorization: Token YOUR_TOKEN_HERE
Content-Type: application/json
```

### Sample POST Bodies

**Login:**
```json
{
  "email": "user@example.com",
  "password": "yourpassword"
}
```

**Create Channel:**
```json
{
  "name": "demo-channel",
  "description": "Demo channel for presentation",
  "channel_type": "TEAM",
  "organization": "org-uuid-from-get-request"
}
```

**Send Message:**
```json
{
  "channel": "channel-uuid",
  "content": "Hello from the presentation! 👋"
}
```

**Create Project:**
```json
{
  "name": "Demo Project",
  "description": "Cross-org collaboration demo"
}
```

---

## 🏆 Pro Tips for Impressive Demos

### 1. Use Browser Console for Real-Time Testing

**Open browser console** (F12) and run:

```javascript
// Login and get token
fetch('https://connectflow.onrender.com/api/v1/login/', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    email: 'demo@example.com',
    password: 'yourpass'
  })
})
.then(r => r.json())
.then(data => {
  console.log('Token:', data.token);
  localStorage.setItem('token', data.token);
});

// Use token for authenticated request
const token = localStorage.getItem('token');
fetch('https://connectflow.onrender.com/api/v1/organizations/', {
  headers: {
    'Authorization': `Token ${token}`,
    'Content-Type': 'application/json'
  }
})
.then(r => r.json())
.then(data => console.log('Organizations:', data));
```

### 2. Prepare Postman Collection

**Export and import this collection for instant setup:**
- Save all common requests
- Use environment variables
- Share with team before presentation

### 3. Have Backup Accounts

```
Account 1: admin@demo.com (admin features)
Account 2: user@demo.com (regular user)
Account 3: external@demo.com (external collaborator)
```

### 4. Use Real-Looking Demo Data

**Don't use:**
- "test123"
- "asdf"
- "demo"

**Use instead:**
- "marketing-strategy-2026"
- "Q1 Product Launch"
- "Engineering Team Sync"

---

## ✅ Pre-Presentation Checklist

**1 Day Before:**
- [ ] Verify deployed app is running
- [ ] Test all demo URLs in browser
- [ ] Create demo accounts with good data
- [ ] Setup Postman collection
- [ ] Export backup of requests

**1 Hour Before:**
- [ ] Login to web interface
- [ ] Test API root URL
- [ ] Verify Postman token works
- [ ] Check internet connection
- [ ] Open all needed URLs in tabs

**5 Minutes Before:**
- [ ] Close unnecessary tabs
- [ ] Increase browser zoom (125% for visibility)
- [ ] Clear console/network tabs
- [ ] Have Postman ready
- [ ] Test microphone/screen share

**During Demo:**
- [ ] Start with browser (easiest to follow)
- [ ] Progress to Postman (advanced)
- [ ] Explain what you're doing
- [ ] Show responses clearly
- [ ] Have fun! 🎉

---

## 🚀 Next Steps

After your presentation:
1. Share API documentation with attendees
2. Provide Postman collection
3. Give access to demo environment
4. Schedule follow-up Q&A

---

## 📚 Additional Resources

- **Full API Documentation:** See `API_DOCUMENTATION.md`
- **Postman Detailed Guide:** See `POSTMAN_BEGINNER_GUIDE.md`
- **Security Guide:** See `DEPLOYMENT_SECURITY_GUIDE.md`
- **Project Overview:** See `PROJECT_DOCUMENTATION.md`

---

**Good luck with your presentation! 🎤**

*You've got this! Your API is live, tested, and ready to impress!*

---

**Last Updated:** January 4, 2026  
**Live API:** https://connectflow.onrender.com/api/v1/  
**Web Dashboard:** https://connectflow.onrender.com
