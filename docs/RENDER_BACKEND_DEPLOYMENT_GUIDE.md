# Render.com Backend Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying the Product Search Agent backend to Render.com with **only the mandatory configurations**.

---

## Prerequisites

Before starting:
- ✅ GitHub account created
- ✅ Code pushed to GitHub repository
- ✅ `backend/requirements.txt` exists
- ✅ `backend/Procfile` exists
- ✅ Backend tested locally and working

---

## Step 3.1: Create Render Account (10 minutes)

### 1. Go to Render.com

Visit: [https://render.com](https://render.com)

### 2. Sign Up

**Recommended:** Sign up with GitHub
- Click "Get Started"
- Click "Sign up with GitHub"
- Authorize Render to access your repositories

**Alternative:** Sign up with email
- Enter email and password
- Verify email address

### 3. Verify Account

Check your email and verify your account.

---

## Step 3.2: Create New Web Service (20 minutes)

### 1. Create New Service

- Click **"New +"** button (top right)
- Select **"Web Service"**

### 2. Connect Repository

- **Option A:** If you signed up with GitHub:
  - Your repositories should appear automatically
  - Find `product-search-agent`
  - Click **"Connect"**

- **Option B:** If you signed up with email:
  - Click "Connect account" → GitHub
  - Authorize Render
  - Select `product-search-agent`
  - Click **"Connect"**

### 3. Configure Service Settings

Fill in these fields:

| Field | Value | Notes |
|-------|-------|-------|
| **Name** | `product-search-agent-api` | Or any name you prefer |
| **Region** | Choose closest to you | e.g., Oregon (US West) |
| **Branch** | `main` | Or your default branch |
| **Root Directory** | `backend` | ⚠️ Important! |
| **Runtime** | `Python 3` | Auto-detected |
| **Build Command** | `pip install -r requirements.txt` | Auto-filled |
| **Start Command** | See below | ⚠️ Important! |

**Start Command:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**⚠️ Important Notes:**
- Root Directory MUST be `backend`
- Start Command MUST use `$PORT` (Render provides this)
- Don't add quotes around the start command

### 4. Select Plan

- Scroll down to "Instance Type"
- Select **"Free"** plan
- Note: Free tier has limitations:
  - Sleeps after 15 minutes of inactivity
  - Takes ~30 seconds to wake up
  - 512 MB RAM
  - Shared CPU

### 5. Create Service

- Click **"Create Web Service"** button
- Render will start building your service

---

## Step 3.3: Configure Environment Variables (30 minutes)

### Mandatory Configuration

After service is created, configure environment variables:

1. Go to your service dashboard
2. Click **"Environment"** tab (left sidebar)
3. Click **"Add Environment Variable"**

### Required Variables

Add these environment variables one by one:

#### 1. CORS_ORIGINS (Required)

**Purpose:** Allows frontend to make API requests

```
Key:   CORS_ORIGINS
Value: http://localhost:5173
```

**⚠️ Important:**
- Start with `http://localhost:5173` for testing
- After deploying frontend (Step 4), update to your frontend URL
- Example final value: `https://product-search-frontend.onrender.com`

**How to update later:**
1. Go to Environment tab
2. Find CORS_ORIGINS
3. Click edit icon
4. Update value
5. Click "Save Changes"
6. Service will automatically redeploy

### Optional Variables (Recommended)

#### 2. ENVIRONMENT (Optional but Recommended)

```
Key:   ENVIRONMENT
Value: production
```

**Purpose:** Sets application to production mode

#### 3. LOG_LEVEL (Optional but Recommended)

```
Key:   LOG_LEVEL
Value: INFO
```

**Purpose:** Controls logging verbosity
- `DEBUG` - Very verbose (development)
- `INFO` - Normal (production)
- `WARNING` - Only warnings and errors
- `ERROR` - Only errors

#### 4. DATABASE_URL (Optional)

```
Key:   DATABASE_URL
Value: sqlite:///./product_search.db
```

**Purpose:** Database connection
- Default is SQLite (file-based)
- Good for testing and small deployments
- For production, consider PostgreSQL (see Advanced section)

### Email Notifications (Optional)

Only add these if you want email notifications:

```
Key:   ENABLE_EMAIL_NOTIFICATIONS
Value: true

Key:   SMTP_HOST
Value: smtp.gmail.com

Key:   SMTP_PORT
Value: 587

Key:   SMTP_USERNAME
Value: your-email@gmail.com

Key:   SMTP_PASSWORD
Value: your-gmail-app-password

Key:   EMAIL_FROM
Value: your-email@gmail.com

Key:   EMAIL_FROM_NAME
Value: Product Search Agent
```

**⚠️ Important for Gmail:**
- Don't use your regular Gmail password
- Use an App Password instead
- See: `docs/GMAIL_APP_PASSWORD_SETUP_GUIDE.md`

### Summary of Variables

**Minimum (Required):**
```
CORS_ORIGINS=http://localhost:5173
```

**Recommended:**
```
CORS_ORIGINS=http://localhost:5173
ENVIRONMENT=production
LOG_LEVEL=INFO
```

**With Email Notifications:**
```
CORS_ORIGINS=http://localhost:5173
ENVIRONMENT=production
LOG_LEVEL=INFO
ENABLE_EMAIL_NOTIFICATIONS=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=your-email@gmail.com
```

---

## Step 3.4: Monitor Deployment (15 minutes)

### Watch Build Logs

1. Go to **"Logs"** tab (left sidebar)
2. Watch the deployment process

### Expected Log Output

You should see:
```
==> Cloning from https://github.com/YOUR_USERNAME/product-search-agent...
==> Checking out commit abc123...
==> Installing dependencies...
==> Collecting fastapi...
==> Successfully installed fastapi-0.104.1 ...
==> Build successful!
==> Starting service...
==> INFO:     Started server process
==> INFO:     Waiting for application startup.
==> INFO:     Application startup complete.
==> INFO:     Uvicorn running on http://0.0.0.0:10000
==> Your service is live 🎉
```

### Build Time

- First build: 3-5 minutes
- Subsequent builds: 1-2 minutes

### Common Build Errors

#### Error: "ModuleNotFoundError: No module named 'fastapi'"

**Cause:** Missing package in requirements.txt

**Solution:**
1. Add missing package to `backend/requirements.txt`
2. Commit and push to GitHub
3. Render will automatically redeploy

#### Error: "No such file or directory: 'app/main.py'"

**Cause:** Root Directory not set to `backend`

**Solution:**
1. Go to "Settings" tab
2. Find "Root Directory"
3. Change to `backend`
4. Click "Save Changes"

#### Error: "Port 8000 is already in use"

**Cause:** Not using `$PORT` variable

**Solution:**
1. Go to "Settings" tab
2. Find "Start Command"
3. Change to: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Click "Save Changes"

#### Error: "Application startup failed"

**Cause:** Various reasons

**Solution:**
1. Check logs for specific error
2. Common issues:
   - Database connection failed
   - Missing environment variable
   - Import error in code

---

## Step 3.5: Test Backend API (15 minutes)

### Get Your API URL

After deployment succeeds:
1. Go to top of dashboard
2. Copy your service URL
3. Example: `https://product-search-agent-api.onrender.com`

### Test 1: Health Check

**Using Browser:**
```
https://your-service-name.onrender.com/api/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Using curl:**
```bash
curl https://your-service-name.onrender.com/api/health
```

### Test 2: API Documentation

**Visit Swagger UI:**
```
https://your-service-name.onrender.com/docs
```

You should see:
- Interactive API documentation
- List of all endpoints
- Ability to test endpoints

### Test 3: Root Endpoint

**Visit:**
```
https://your-service-name.onrender.com/
```

**Expected Response:**
```json
{
  "name": "Product Search Agent API",
  "version": "1.0.0",
  "status": "running",
  "documentation": {
    "swagger": "/docs",
    "redoc": "/redoc"
  }
}
```

### Test 4: WebSocket Connection

**Using Browser Console:**
```javascript
const ws = new WebSocket('wss://your-service-name.onrender.com/ws/notifications');

ws.onopen = () => console.log('Connected!');
ws.onmessage = (event) => console.log('Message:', event.data);
ws.onerror = (error) => console.error('Error:', error);
```

**Expected:**
```
Connected!
```

---

## Step 3.6: Update CORS After Frontend Deployment

### When to Do This

After you deploy your frontend (Step 4), you'll have a frontend URL like:
```
https://product-search-frontend.onrender.com
```

### How to Update

1. Go to your backend service on Render
2. Click **"Environment"** tab
3. Find **CORS_ORIGINS**
4. Click edit icon
5. Update value to your frontend URL:
   ```
   https://product-search-frontend.onrender.com
   ```
6. Click **"Save Changes"**
7. Service will automatically redeploy (~1 minute)

### Multiple Origins

If you want to allow multiple origins (e.g., localhost + production):

```
http://localhost:5173,https://product-search-frontend.onrender.com
```

**Format:** Comma-separated, no spaces

---

## Troubleshooting

### Issue: Service Won't Start

**Check:**
1. Logs tab for error messages
2. Environment variables are set correctly
3. Root Directory is `backend`
4. Start Command uses `$PORT`

### Issue: 502 Bad Gateway

**Causes:**
- Service is still starting (wait 30 seconds)
- Service crashed (check logs)
- Build failed (check logs)

**Solution:**
1. Check Logs tab
2. Look for error messages
3. Fix issue in code
4. Push to GitHub
5. Render auto-redeploys

### Issue: CORS Errors in Frontend

**Error in browser console:**
```
Access to fetch at 'https://api.com/api/health' from origin 
'https://frontend.com' has been blocked by CORS policy
```

**Solution:**
1. Check CORS_ORIGINS includes your frontend URL
2. Make sure there are no typos
3. Include protocol (https://)
4. No trailing slash

### Issue: Database Not Persisting

**Cause:** SQLite on free tier doesn't persist between deploys

**Solutions:**
1. **Upgrade to paid plan** - Persistent disk included
2. **Use PostgreSQL** - See Advanced Configuration
3. **Accept data loss** - OK for testing

### Issue: Service Sleeping

**Behavior:** First request takes 30+ seconds

**Cause:** Free tier sleeps after 15 minutes of inactivity

**Solutions:**
1. **Upgrade to paid plan** - No sleeping
2. **Use a ping service** - Keep service awake
3. **Accept delay** - OK for testing

---

## Advanced Configuration

### Using PostgreSQL Instead of SQLite

**Why?**
- Better performance
- Data persists between deploys
- Supports concurrent connections

**How:**

1. **Create PostgreSQL Database on Render:**
   - Click "New +" → "PostgreSQL"
   - Name: `product-search-db`
   - Select Free plan
   - Click "Create Database"

2. **Get Connection String:**
   - Go to database dashboard
   - Copy "Internal Database URL"
   - Example: `postgresql://user:pass@host:5432/db`

3. **Update Backend Environment Variable:**
   ```
   Key:   DATABASE_URL
   Value: postgresql://user:pass@host:5432/db
   ```

4. **Service will auto-redeploy**

### Custom Domain

**Steps:**
1. Go to "Settings" tab
2. Scroll to "Custom Domain"
3. Click "Add Custom Domain"
4. Enter your domain (e.g., `api.yourdomain.com`)
5. Follow DNS configuration instructions
6. Wait for SSL certificate (automatic)

---

## Deployment Checklist

Before marking Step 3 complete:

- [ ] Render account created
- [ ] Web service created and deployed
- [ ] CORS_ORIGINS environment variable set
- [ ] Service is running (green status)
- [ ] Health check endpoint works
- [ ] API documentation accessible at /docs
- [ ] WebSocket connection works
- [ ] Service URL copied for frontend configuration

---

## Next Steps

After backend is deployed:

1. ✅ Backend deployed and tested
2. ⏭️ **Step 4:** Deploy Frontend to Render
3. ⏭️ Update CORS_ORIGINS with frontend URL
4. ⏭️ Test full application (frontend + backend)

---

## Quick Reference

### Service URLs

```
API Base:        https://your-service-name.onrender.com
Health Check:    https://your-service-name.onrender.com/api/health
Documentation:   https://your-service-name.onrender.com/docs
WebSocket:       wss://your-service-name.onrender.com/ws/notifications
```

### Required Environment Variables

```
CORS_ORIGINS=http://localhost:5173
```

### Recommended Environment Variables

```
CORS_ORIGINS=http://localhost:5173
ENVIRONMENT=production
LOG_LEVEL=INFO
```

### Build Configuration

```
Root Directory:  backend
Runtime:         Python 3
Build Command:   pip install -r requirements.txt
Start Command:   uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

---

## Support

**Render Documentation:**
- [Render Docs](https://render.com/docs)
- [Python on Render](https://render.com/docs/deploy-fastapi)

**Project Documentation:**
- `docs/DAY_28-29_CLOUD_DEPLOYMENT_DETAILED_PLAN.md`
- `docs/CORS_PRODUCTION_SETUP.md`
- `docs/GMAIL_APP_PASSWORD_SETUP_GUIDE.md`

**Common Issues:**
- Check Logs tab first
- Verify environment variables
- Ensure Root Directory is `backend`
- Confirm Start Command uses `$PORT`