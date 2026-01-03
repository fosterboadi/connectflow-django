# ConnectFlow Pro - API TESTING & PRESENTATION GUIDE

## 🚀 Two Ways to Test Your API

### Option 1: Browser DevTools (Quick & Easy)
Perfect for quick testing and live demonstrations. No installation required!

### Option 2: Interactive API Documentation
Professional API presentation for clients, stakeholders, and developers.

---

## 🎯 METHOD 1: BROWSER DEVTOOLS TESTING

### What You Need
- Modern browser (Chrome, Firefox, Edge, Safari)
- ConnectFlow account (register at `https://connectflow.onrender.com/accounts/register/`)
- Production URL: `https://connectflow.onrender.com`

⚠️ **Important:** Render free tier spins down after 15 minutes. First request may take 50-60 seconds.

---

### STEP 1: Open Browser DevTools

1. **Open your browser** and go to `https://connectflow.onrender.com`
2. **Login** to your account (or register if you don't have one)
3. **Press F12** or **Right-click → Inspect** to open DevTools
4. **Click "Console" tab**

You're ready to test! 🎉

---

### STEP 2: Get Your Authentication Token

**If you're already logged into ConnectFlow, this is super easy!**

Your token is already stored in your browser. Just run this:

```javascript
// Get your existing token (you're already logged in!)
const API_TOKEN = localStorage.getItem('auth_token');
console.log('✅ Token found:', API_TOKEN);
```

**That's it!** You can now skip to STEP 3 and start testing.

---

**Alternative: Login via API** (if you need a fresh token or testing login flow):

```javascript
// Login and get token
fetch('https://connectflow.onrender.com/api/v1/login/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'your-email@example.com',
    password: 'your-password'
  })
})
.then(res => res.json())
.then(data => {
  console.log('Login successful!');
  console.table(data.user);
  console.log('Token:', data.token);
  window.API_TOKEN = data.token; // Save for later use
})
.catch(err => console.error('Login failed:', err));
```

**💡 Pro Tip:** Save your token in a variable for easy reuse:
```javascript
const API_TOKEN = 'your-token-here';
```

---

### STEP 3: Test API Endpoints (Copy & Paste)

**Quick Start - Test Your Profile (No setup needed!)**

If you just got your token from localStorage, test it immediately:

```javascript
// Quick test - Get your profile
fetch('https://connectflow.onrender.com/api/v1/users/me/', {
  headers: { 'Authorization': `Token ${localStorage.getItem('auth_token')}` }
})
.then(res => res.json())
.then(data => {
  console.log('✅ API is working!');
  console.table(data);
})
.catch(err => console.error(err));
```

---

**Ready-to-Use Examples:**

Below are complete examples you can copy and paste. Since you're logged in, they'll use your existing token!

#### 🔹 Get Your Profile
```javascript
// Using your existing login session
fetch('https://connectflow.onrender.com/api/v1/users/me/', {
  headers: { 'Authorization': `Token ${localStorage.getItem('auth_token')}` }
})
.then(res => res.json())
.then(data => console.table(data))
.catch(err => console.error(err));
```

**OR** (if you saved API_TOKEN variable earlier):
```javascript
fetch('https://connectflow.onrender.com/api/v1/users/me/', {
  headers: { 'Authorization': `Token ${API_TOKEN}` }
})
.then(res => res.json())
.then(data => console.table(data))
.catch(err => console.error(err));
```

💡 **Pro Tip:** Use `localStorage.getItem('auth_token')` directly if you haven't saved it to a variable!

#### 🔹 List All Users in Your Organization
```javascript
fetch('https://connectflow.onrender.com/api/v1/users/', {
  headers: { 'Authorization': `Token ${API_TOKEN}` }
})
.then(res => res.json())
.then(users => {
  console.log(`Found ${users.length} users`);
  console.table(users);
})
.catch(err => console.error(err));
```

#### 🔹 List Your Projects
```javascript
fetch('https://connectflow.onrender.com/api/v1/projects/', {
  headers: { 'Authorization': `Token ${API_TOKEN}` }
})
.then(res => res.json())
.then(projects => {
  console.log(`You have ${projects.length} projects`);
  console.table(projects);
})
.catch(err => console.error(err));
```

#### 🔹 List Your Channels
```javascript
fetch('https://connectflow.onrender.com/api/v1/channels/', {
  headers: { 'Authorization': `Token ${API_TOKEN}` }
})
.then(res => res.json())
.then(channels => {
  console.log(`Found ${channels.length} channels`);
  console.table(channels);
})
.catch(err => console.error(err));
```

#### 🔹 Send a Message
```javascript
fetch('https://connectflow.onrender.com/api/v1/messages/', {
  method: 'POST',
  headers: {
    'Authorization': `Token ${API_TOKEN}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    channel: 1, // Replace with your channel ID
    content: 'Hello from DevTools! 🚀'
  })
})
.then(res => res.json())
.then(msg => {
  console.log('Message sent!');
  console.log(msg);
})
.catch(err => console.error(err));
```

#### 🔹 Create a New Project
```javascript
fetch('https://connectflow.onrender.com/api/v1/projects/', {
  method: 'POST',
  headers: {
    'Authorization': `Token ${API_TOKEN}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    name: 'DevTools Test Project',
    description: 'Created from browser console',
    members: []
  })
})
.then(res => res.json())
.then(project => {
  console.log('Project created!');
  console.table(project);
})
.catch(err => console.error(err));
```

#### 🔹 Toggle Your Theme (Light/Dark)
```javascript
fetch('https://connectflow.onrender.com/api/v1/users/toggle_theme/', {
  method: 'POST',
  headers: { 'Authorization': `Token ${API_TOKEN}` }
})
.then(res => res.json())
.then(data => console.log('Theme changed to:', data.theme))
.catch(err => console.error(err));
```

#### 🔹 Create Support Ticket
```javascript
fetch('https://connectflow.onrender.com/api/v1/tickets/', {
  method: 'POST',
  headers: {
    'Authorization': `Token ${API_TOKEN}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    subject: 'Test ticket from DevTools',
    description: 'Testing API from browser console',
    priority: 'MEDIUM',
    category: 'TECHNICAL'
  })
})
.then(res => res.json())
.then(ticket => {
  console.log('Ticket created!');
  console.table(ticket);
})
.catch(err => console.error(err));
```

---

### STEP 4: Helper Function for Easy Testing

**Save this reusable function for easier testing:**

```javascript
// Universal API tester - uses your logged-in token automatically!
async function api(endpoint, options = {}) {
  const baseURL = 'https://connectflow.onrender.com/api/v1';
  const url = `${baseURL}${endpoint}`;
  
  const config = {
    headers: {
      'Authorization': `Token ${localStorage.getItem('auth_token')}`, // Auto-uses your token!
      'Content-Type': 'application/json',
      ...options.headers
    },
    ...options
  };
  
  if (options.body && typeof options.body === 'object') {
    config.body = JSON.stringify(options.body);
  }
  
  try {
    const res = await fetch(url, config);
    const data = await res.json();
    
    if (res.ok) {
      console.log('✅ Success:', res.status);
      console.table(data);
      return data;
    } else {
      console.error('❌ Error:', res.status, data);
      return data;
    }
  } catch (err) {
    console.error('❌ Request failed:', err);
  }
}

console.log('✅ Helper function loaded!');
console.log('Usage: api("/users/me/") or api("/projects/")');
```

**Now testing is super easy:**
```javascript
// GET requests
api('/users/me/');
api('/channels/');
api('/projects/');

// POST requests
api('/messages/', { 
  method: 'POST', 
  body: { channel: 1, content: 'Easy!' } 
});

// DELETE requests
api('/messages/123/', { method: 'DELETE' });
```

---

### STEP 5: Advanced Testing - Monitor Network Tab

1. **Click "Network" tab** in DevTools
2. **Filter by "Fetch/XHR"**
3. **Run any API call** from console
4. **Click the request** to see:
   - Request Headers
   - Response Headers
   - Request Payload
   - Response Body
   - Timing information

This is perfect for debugging authentication issues, checking response times, and understanding the API better!

---

### STEP 6: Test File Uploads

```javascript
// Upload a file
const fileInput = document.createElement('input');
fileInput.type = 'file';
fileInput.onchange = async (e) => {
  const file = e.target.files[0];
  const formData = new FormData();
  formData.append('file', file);
  formData.append('channel', 1); // Replace with your channel ID
  formData.append('content', 'Uploaded from DevTools!');
  
  const res = await fetch('https://connectflow.onrender.com/api/v1/messages/', {
    method: 'POST',
    headers: { 'Authorization': `Token ${API_TOKEN}` },
    body: formData
  });
  
  const data = await res.json();
  console.log('File uploaded!', data);
};
fileInput.click();
```

---

## 🎯 METHOD 2: PRESENTING YOUR API TO OTHERS

### Option A: Django REST Framework Browsable API (Built-in)

**ConnectFlow already has a beautiful interactive API browser!**

#### How to Access:
1. Go to `https://connectflow.onrender.com/api/v1/`
2. **Login** (you'll see a login button in top-right)
3. **Browse endpoints** - Click any link to explore
4. **Test endpoints** - Fill forms and submit requests directly
5. **View responses** - See formatted JSON, HTML, or raw data

**Perfect for:**
- Live demos to clients
- Developer onboarding
- Quick API exploration
- Documentation that never goes stale

**Presentation Flow:**
```
1. Open browser, navigate to /api/v1/
2. Login to show authentication
3. Click /users/me/ → Show your profile
4. Click /projects/ → Show all projects
5. Fill POST form → Create new project live
6. Show response → Instant feedback
```

**💡 Pro Tip:** Use **screen sharing** during meetings and walk stakeholders through the API in real-time!

---

### Option B: Create API Documentation (Professional)

**Example README.md structure:**
````markdown
# ConnectFlow API Documentation

## Base URL
```
https://connectflow.onrender.com/api/v1
```

## Authentication
All endpoints require Token authentication:
```http
Authorization: Token YOUR_TOKEN_HERE
```

Get your token via:
```bash
POST /api/v1/login/
{
  "email": "user@example.com",
  "password": "password"
}
```

## Quick Start

### 1. Get Your Profile
```javascript
GET /api/v1/users/me/
```

### 2. List Projects
```javascript
GET /api/v1/projects/
```

### 3. Send Message
```javascript
POST /api/v1/messages/
{
  "channel": 1,
  "content": "Hello world!"
}
```

[See full endpoint reference below...]
````

**Share this documentation via:**
- GitHub repository README
- Company wiki/knowledge base
- Google Docs/Notion
- Email to stakeholders

---

### Option C: Video Walkthrough (For Presentations)

**Record a quick video demo:**

1. **Use Loom, OBS, or built-in screen recorder**
2. **Script outline:**
   - "Hi, I'm going to show you ConnectFlow's API"
   - Open browser DevTools
   - Run 3-5 key examples (login, get profile, send message)
   - Explain authentication and response format
   - Show how to integrate in real applications
3. **Keep it under 5 minutes**
4. **Share link** with clients/stakeholders

---

### Option D: Live Demo Script (For Meetings)

**Use this script for presentations:**

```
"Let me show you how our API works in real-time.

[Open browser console]

First, we authenticate with our email and password.
[Run login example]

See? We immediately get back our token and user profile.

Now, let's fetch all our current projects.
[Run projects example]

We have 3 active projects. Let's send a message to one.
[Run send message example]

And there it is - the message appears instantly in our dashboard
because of our WebSocket integration.

The API supports everything from user management, to real-time
messaging, to project analytics. Let me show you the full 
interactive documentation...

[Navigate to /api/v1/ browsable API]

This is our live API browser. You can test any endpoint right here,
see the expected input format, and get instant responses.

Perfect for integration testing or exploring the API.

Any questions?"
```

---

## 🚀 LIVE DEMO WORKFLOW (5 Minutes)

Perfect for client presentations and stakeholder meetings!

### Demo Script

**1. Authentication (30 seconds)**
```javascript
// Show login in console
api('/login/', { 
  method: 'POST', 
  body: { email: 'demo@example.com', password: 'demo123' } 
});
```
*"Token-based authentication - secure and simple"*

**2. User Profile (20 seconds)**
```javascript
api('/users/me/');
```
*"Here's my authenticated user profile with role and permissions"*

**3. Organization Structure (30 seconds)**
```javascript
api('/organizations/');
api('/departments/');
api('/teams/');
```
*"We support full organizational hierarchy"*

**4. Projects & Collaboration (1 minute)**
```javascript
api('/projects/');
```
*"These are our collaborative workspaces"*

```javascript
api('/projects/', { 
  method: 'POST', 
  body: { name: 'Client Demo Project', description: 'Created live!' } 
});
```
*"Creating a project in real-time"*

**5. Real-time Messaging (1 minute)**
```javascript
api('/channels/');
```
*"Our communication channels"*

```javascript
api('/messages/', { 
  method: 'POST', 
  body: { channel: 1, content: 'Hello from live demo! 🚀' } 
});
```
*"Messages appear instantly via WebSockets"*

**6. Advanced Features (1 minute)**
```javascript
api('/messages/123/pin/');
```
*"Pin important messages"*

```javascript
api('/messages/123/create_task/');
```
*"Convert messages to tasks"*

```javascript
api('/tickets/', { 
  method: 'POST', 
  body: { subject: 'Demo', description: 'Support system', priority: 'HIGH' } 
});
```
*"Integrated support ticketing"*

**7. Interactive Documentation (1 minute)**
- Navigate to `https://connectflow.onrender.com/api/v1/`
- Click around to show browsable API
- Show forms for testing endpoints
- *"Developers can explore and test everything here"*

**8. Q&A (Remaining time)**

---

## 💡 PRESENTATION TIPS

### For Technical Audiences (Developers)
- Focus on DevTools examples
- Show request/response formats
- Demonstrate authentication flow
- Explain rate limiting, pagination, error codes
- Share browsable API URL

### For Non-Technical Audiences (Clients/Stakeholders)
- Use browsable API (/api/v1/) for visual appeal
- Focus on *what* the API does, not *how*
- Show real-world examples (send message, create project)
- Emphasize security and reliability
- Avoid technical jargon

### For Mixed Audiences
- Start with browsable API (visual)
- Then show DevTools (for devs)
- Prepare both simple and advanced examples
- Have documentation links ready

---

## 🎯 COMMON USE CASES

### Use Case 1: Mobile App Integration
```javascript
// Mobile apps can use this API for:
// - User authentication
// - Fetching messages and channels
// - Sending messages with file attachments
// - Real-time updates via WebSockets
```

### Use Case 2: Third-Party Integrations
```javascript
// Integrate with:
// - Slack (forward messages)
// - Zapier (automation)
// - Custom CRM systems
// - Analytics platforms
```

### Use Case 3: Internal Automation
```javascript
// Automate tasks like:
// - Nightly report generation
// - Ticket auto-assignment
// - Bulk user imports
// - Data synchronization
```

---

## 📊 COMPLETE API ENDPOINT REFERENCE

### Base URL
**Production:** `https://connectflow.onrender.com/api/v1`

### Authentication Endpoints
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/login/` | Login and get token | No |
| POST | `/logout/` | Logout (delete token) | Yes |

### User Endpoints
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/users/` | List all users in organization | Yes |
| GET | `/users/me/` | Get current user profile | Yes |
| GET | `/users/{id}/` | Get specific user | Yes |
| PUT/PATCH | `/users/{id}/` | Update user | Yes |
| POST | `/users/toggle_theme/` | Toggle light/dark theme | Yes |

### Organization Endpoints
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/organizations/` | Get your organization | Yes |
| GET | `/organizations/{id}/` | Get organization details | Yes |

### Department Endpoints
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/departments/` | List all departments | Yes |
| POST | `/departments/` | Create department | Yes |
| GET | `/departments/{id}/` | Get department details | Yes |
| PUT/PATCH | `/departments/{id}/` | Update department | Yes |
| DELETE | `/departments/{id}/` | Delete department | Yes |

### Team Endpoints
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/teams/` | List all teams | Yes |
| POST | `/teams/` | Create team | Yes |
| GET | `/teams/{id}/` | Get team details | Yes |
| PUT/PATCH | `/teams/{id}/` | Update team | Yes |
| DELETE | `/teams/{id}/` | Delete team | Yes |

### Project Endpoints
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/projects/` | List all projects | Yes |
| POST | `/projects/` | Create project | Yes |
| GET | `/projects/{id}/` | Get project details | Yes |
| PUT/PATCH | `/projects/{id}/` | Update project | Yes |
| DELETE | `/projects/{id}/` | Delete project | Yes |
| GET | `/projects/{id}/analytics/` | Get project analytics (Premium) | Yes |

### Channel Endpoints
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/channels/` | List all channels | Yes |
| POST | `/channels/` | Create channel | Yes |
| GET | `/channels/{id}/` | Get channel details | Yes |
| PUT/PATCH | `/channels/{id}/` | Update channel | Yes |
| DELETE | `/channels/{id}/` | Delete channel | Yes |
| GET | `/channels/{id}/messages/` | Get channel messages | Yes |

### Message Endpoints
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/messages/` | List all messages | Yes |
| POST | `/messages/` | Send message | Yes |
| GET | `/messages/{id}/` | Get message details | Yes |
| PUT/PATCH | `/messages/{id}/` | Update message | Yes |
| DELETE | `/messages/{id}/` | Delete message (soft delete) | Yes |
| POST | `/messages/{id}/pin/` | Pin/unpin message | Yes |
| POST | `/messages/{id}/star/` | Star/unstar message | Yes |
| POST | `/messages/{id}/reply/` | Reply to message | Yes |
| POST | `/messages/{id}/forward/` | Forward message to channel | Yes |
| POST | `/messages/{id}/create_task/` | Create task from message | Yes |
| POST | `/messages/{id}/create_meeting/` | Create meeting from message | Yes |
| POST | `/messages/{id}/add_to_files/` | Add attachments to project files | Yes |
| POST | `/messages/{id}/link_milestone/` | Link to project milestone | Yes |

### Support Ticket Endpoints
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/tickets/` | List all tickets | Yes |
| POST | `/tickets/` | Create ticket | Yes |
| GET | `/tickets/{id}/` | Get ticket details | Yes |
| PUT/PATCH | `/tickets/{id}/` | Update ticket | Yes |
| DELETE | `/tickets/{id}/` | Delete ticket | Yes |
| POST | `/tickets/{id}/add_message/` | Add message to ticket | Yes |
| GET | `/ticket-messages/` | List ticket messages | Yes |

---

## 🚀 QUICK DEMO FLOW (5 MINUTES)

### Demo Script for Presentations

1. **Authentication**
   - POST `/login/` → "Token-based authentication"
   - GET `/users/me/` → "Here's my authenticated user profile"

2. **Organization Structure**
   - GET `/organizations/` → "My organization details"
   - GET `/departments/` → "Department structure"
   - GET `/teams/` → "Teams within departments"

3. **Projects & Collaboration**
   - GET `/projects/` → "All collaborative projects"
   - POST `/projects/` → "Create a new project"
   - GET `/projects/{id}/analytics/` → "Premium analytics dashboard"

4. **Communication**
   - GET `/channels/` → "Communication channels"
   - POST `/messages/` → "Send a message"
   - POST `/messages/{id}/pin/` → "Pin important messages"

5. **Advanced Features**
   - POST `/messages/{id}/create_task/` → "Convert message to task"
   - POST `/messages/{id}/forward/` → "Forward to another channel"
   - POST `/tickets/` → "Create support ticket"

6. **Real-time**
   - "Messages sent via API appear instantly via WebSockets"

---

## 💡 TESTING TIPS

### DevTools Testing
- **Save snippets:** DevTools > Sources > Snippets (save your test scripts)
- **Use console.table():** Better visualization for arrays of objects
- **Network tab:** Monitor all API calls, timing, and payloads
- **Preserve log:** Enable to keep history across page reloads
- **Copy as fetch:** Right-click network request → Copy → Copy as fetch

### Error Debugging
```javascript
// Better error handling
async function testAPI(endpoint, options) {
  try {
    const res = await fetch(`https://connectflow.onrender.com/api/v1${endpoint}`, {
      headers: { 'Authorization': `Token ${API_TOKEN}`, 'Content-Type': 'application/json' },
      ...options
    });
    
    const data = await res.json();
    
    if (!res.ok) {
      console.error(`❌ ${res.status}: ${res.statusText}`);
      console.error('Error details:', data);
    } else {
      console.log(`✅ Success (${res.status})`);
      console.table(data);
    }
    
    return data;
  } catch (err) {
    console.error('❌ Network error:', err);
  }
}
```

### Bulk Testing
```javascript
// Test multiple endpoints at once
const endpoints = ['/users/me/', '/projects/', '/channels/'];
Promise.all(endpoints.map(ep => api(ep)))
  .then(results => results.forEach((r, i) => {
    console.log(`\n${endpoints[i]}:`);
    console.table(r);
  }));
```

---

## ❓ TROUBLESHOOTING

### Error: 503 Service Unavailable
- **Cause:** Render free tier spins down after 15 minutes of inactivity
- **Solution:** Wait 50-60 seconds for service to wake up, then retry
- **Tip:** First request after inactivity always takes longer

### Error: 401 Unauthorized (DevTools)
- Token is invalid or expired
- Get new token: `api('/login/', { method: 'POST', body: { email, password } })`
- Save it: `API_TOKEN = 'your-new-token'`
- Authorization header must be `Token ${API_TOKEN}` (with "Token" prefix)

### Error: 403 Forbidden
- You don't have permission for this resource
- Check if it's a premium feature (requires subscription)
- Verify you're a member of the project/channel

### Error: 404 Not Found
- Check the ID in URL exists
- Verify base URL is correct
- Resource may have been deleted

### Error: CORS Issues (from external apps)
- ConnectFlow API allows cross-origin requests
- If blocked, check your request headers
- Ensure you're using HTTPS, not HTTP

### Can't Access from DevTools
- Make sure you're logged into ConnectFlow dashboard
- Try hard refresh (Ctrl+F5)
- Clear browser cache and cookies

---

## 🎓 ADDITIONAL RESOURCES

### Interactive API Explorer
**Best for presentations:** `https://connectflow.onrender.com/api/v1/`
- Beautiful web interface
- Click-to-test functionality
- Auto-generated documentation
- No setup required

### API Response Formats
```javascript
// Success Response (200/201)
{
  "id": 1,
  "name": "Project Name",
  "created_at": "2026-01-03T10:00:00Z"
}

// Error Response (400/403/404)
{
  "error": "Validation failed",
  "details": { "email": ["This field is required"] }
}

// List Response
[
  { "id": 1, "name": "Item 1" },
  { "id": 2, "name": "Item 2" }
]
```

### Authentication Flow
```
1. User registers at /accounts/register/
2. User logs in: POST /api/v1/login/
3. Server returns token
4. Client stores token (localStorage, secure storage)
5. Client includes token in all subsequent requests
6. Token remains valid until logout
```

### Rate Limiting (Production)
- **Free tier:** 100 requests/minute
- **Premium:** 1000 requests/minute
- **Enterprise:** Unlimited
- Header: `X-RateLimit-Remaining` shows remaining requests

### Response Status Codes
- **200 OK** - Successful GET, PUT, PATCH
- **201 Created** - Successful POST
- **204 No Content** - Successful DELETE
- **400 Bad Request** - Validation error
- **401 Unauthorized** - Invalid/missing token
- **403 Forbidden** - No permission
- **404 Not Found** - Resource doesn't exist
- **429 Too Many Requests** - Rate limit exceeded
- **500 Server Error** - Server-side error
- **503 Service Unavailable** - Server is waking up (Render free tier)

---

## ✅ FINAL CHECKLIST

### For Testing in DevTools
- [ ] Browser DevTools opened (F12)
- [ ] Logged into ConnectFlow dashboard
- [ ] Token obtained and saved to variable
- [ ] Helper function loaded (optional)
- [ ] Tested at least 3 endpoints
- [ ] Checked Network tab for request details

### For Presenting to Others
- [ ] Demo script prepared
- [ ] Test data created (projects, channels, messages)
- [ ] Browsable API bookmark ready (`/api/v1/`)
- [ ] Screen sharing software tested
- [ ] Backup examples if live demo fails
- [ ] Q&A talking points prepared

### For API Documentation
- [ ] Endpoint list documented
- [ ] Authentication flow explained
- [ ] Request/response examples provided
- [ ] Error codes documented
- [ ] Contact info for support included

---

**THAT'S IT! You're ready to test and present the ConnectFlow API. 🎉**

### Quick Links
- **Live API Browser:** `https://connectflow.onrender.com/api/v1/`
- **Web Dashboard:** `https://connectflow.onrender.com`
- **Register Account:** `https://connectflow.onrender.com/accounts/register/`

### Need Help?
- Create support ticket via API: `POST /api/v1/tickets/`
- Or use web interface support form

---

## 📚 APPENDIX: Full Endpoint List

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/login/` | Login and get token |
| POST | `/logout/` | Logout (delete token) |
