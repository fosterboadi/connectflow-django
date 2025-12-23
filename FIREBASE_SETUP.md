# Quick Firebase Setup Guide

## Get Your Firebase Service Account Credentials

### Step 1: Access Firebase Console
1. Go to https://console.firebase.google.com/
2. Select your project: **connectflowpro-f1202**

### Step 2: Generate Service Account Key
1. Click the gear icon (⚙️) → **Project Settings**
2. Go to the **Service Accounts** tab
3. Click **Generate New Private Key**
4. Click **Generate Key** (a JSON file will download)

### Step 3: Convert to Single-Line JSON (for Render)

**On Windows (PowerShell):**
```powershell
$json = Get-Content "path\to\your-firebase-key.json" -Raw | ConvertFrom-Json | ConvertTo-Json -Compress
Write-Output $json
```

**On Mac/Linux:**
```bash
python3 -c "import json; print(json.dumps(json.load(open('path/to/your-firebase-key.json'))))"
```

### Step 4: Add to Render
1. Go to Render Dashboard
2. Select your service
3. Go to **Environment** tab
4. Add variable:
   - Key: `FIREBASE_CREDENTIALS_JSON`
   - Value: `<paste the single-line JSON here>`

---

## Cloudinary Setup

### Step 1: Get Credentials
1. Sign up/login at https://cloudinary.com/
2. Go to **Dashboard**
3. Copy these values:
   - Cloud Name
   - API Key  
   - API Secret

### Step 2: Add to Render
Add these environment variables:
- `CLOUDINARY_CLOUD_NAME=<your-cloud-name>`
- `CLOUDINARY_API_KEY=<your-api-key>`
- `CLOUDINARY_API_SECRET=<your-api-secret>`

---

## Local Development Setup

Add to your `.env` file:
```
FIREBASE_CREDENTIALS_PATH=C:\path\to\your-firebase-key.json
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```

**Note:** For local development, you can use `FIREBASE_CREDENTIALS_PATH` to point to the JSON file directly.
