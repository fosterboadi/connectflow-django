# 🎓 ConnectFlow Pro: The Master Console Script (Browser Edition)

This guide allows you to test and present every part of the API directly inside your **Browser Console**. Since you are already logged in, the API will recognize your session automatically.

---

## 🛠 PHASE 0: The Setup
1.  **Open App:** Log into `https://connectflow-pro.onrender.com`.
2.  **Open Console:** Press **F12** (or Right-click > Inspect > Console).
3.  **Clear Screen:** Type `clear()` and hit Enter to start with a clean slate.

---

## 🚀 PHASE 1: The Identity Test
**What you are doing:** Asking the API to verify who you are based on your current session.
**Talk Track:** *"Even though I'm using a browser, I can talk directly to our API. I'll ask the server to identify my role and organization context."*

**Copy/Paste this:**
```javascript
fetch('/api/v1/users/me/')
  .then(response => response.json())
  .then(data => {
    console.log("%c IDENTITY VERIFIED: ", "background: #4F46E5; color: white; font-weight: bold;");
    console.table(data);
  });
```

---

## 🔒 PHASE 2: Data Isolation Test
**What you are doing:** Listing the projects. Notice how you only see your own company's data.
**Talk Track:** *"Security is built-in. This request returns only the projects my organization is authorized to see, proving our secure multi-tenant architecture."*

**Copy/Paste this:**
```javascript
fetch('/api/v1/projects/')
  .then(response => response.json())
  .then(data => {
    console.log("%c AUTHORIZED PROJECTS: ", "background: #10B981; color: white; font-weight: bold;");
    console.log(data);
    // Copy an ID from the results below for the next step!
  });
```

---

## 🛡️ PHASE 3: The SaaS Gatekeeper (The Upgrade Demo)
**What you are doing:** Trying to access a Premium feature (Analytics).
**Talk Track:** *"Now we show the business logic. I'll attempt to access Project Analytics. If the organization is on a 'Basic' plan, our Gatekeeper will block the request."*

**Copy/Paste this (Replace [ID] with a Project ID from Phase 2):**
```javascript
// Copy an ID from Phase 2 and paste it here:
const projectID = "PASTE_YOUR_ID_HERE";
fetch(`/api/v1/projects/${projectID}/analytics/`)
  .then(response => {
    if (response.status === 403) {
      console.log("%c GATEKEEPER TRIGGERED: Premium Plan Required ", "background: #EF4444; color: white; font-weight: bold;");
    }
    return response.json();
  })
  .then(console.log);
```

---

## 🏗️ PHASE 4: Headless Creation (POST Action)
**What you are doing:** Creating a new Department via code.
**Talk Track:** *"Finally, I'll prove our platform is 'Headless'. I'm sending a command to create a new Department. Watch how it uses the secure CSRF token to authorize the change."*

**Copy/Paste this:**
```javascript
const csrfToken = document.cookie.split('; ').find(row => row.startsWith('csrftoken=')).split('=')[1];

fetch('/api/v1/departments/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
    },
    body: JSON.stringify({ 
        name: "AI Research Lab", 
        description: "Built via Browser Console Demo" 
    })
})
.then(res => res.json())
.then(data => {
    console.log("%c DEPARTMENT CREATED SUCCESSFULLY! ", "background: #8B5CF6; color: white; font-weight: bold;");
    console.log(data);
    console.log("Refresh your Organization page to see it live!");
});
```

---

## 🏁 Final Conclusion
*"We've just demonstrated a secure, context-aware API that enforces business rules and allows for headless data creation. ConnectFlow Pro is ready to power any modern integration."*