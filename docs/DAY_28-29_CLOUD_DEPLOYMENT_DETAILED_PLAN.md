# Day 28-29: Cloud Deployment - Detailed Implementation Plan

**Estimated Time:** 8 hours (spread over 2 days)  
**Difficulty:** Intermediate  
**Prerequisites:** Basic understanding of Git, environment variables, and web hosting concepts

---

## 📋 Overview

This task involves deploying your Product Search Agent application to the cloud so it's accessible from anywhere on the internet. We'll use **Render.com** (recommended) as it's free, easy to use, and perfect for full-stack applications.

**What You'll Deploy:**
- Backend API (FastAPI)
- Frontend Dashboard (React + Vite)
- Database (SQLite or PostgreSQL)
- WebSocket connections for real-time notifications

**End Result:** Your app will be live at a public URL like `https://your-app.onrender.com`

---

## 🎯 Learning Objectives

By completing this task, you will learn:
1. How to prepare an application for production deployment
2. How to use Git and GitHub for code hosting
3. How to configure environment variables for production
4. How to deploy backend and frontend separately
5. How to troubleshoot deployment issues
6. How to monitor application health

---

## 📚 Background Knowledge

### What is Cloud Deployment?

**Cloud deployment** means hosting your application on servers managed by a cloud provider (like Render, Heroku, AWS, etc.) instead of your local computer. This makes your app:
- ✅ Accessible 24/7 from anywhere
- ✅ Scalable (can handle more users)
- ✅ Reliable (automatic backups and monitoring)
- ✅ Professional (custom domain support)

### Why Render.com?

- **Free Tier:** Perfect for learning and small projects
- **Easy Setup:** No credit card required for free tier
- **Auto-Deploy:** Automatically deploys when you push to GitHub
- **Full-Stack Support:** Can host both backend and frontend
- **Built-in Database:** PostgreSQL included in free tier

### Deployment Architecture

```
GitHub Repository
       ↓
   Render.com
       ↓
   ┌─────────────────┐
   │   Backend API   │ ← https://your-api.onrender.com
   │   (FastAPI)     │
   └─────────────────┘
       ↓
   ┌─────────────────┐
   │   Frontend      │ ← https://your-app.onrender.com
   │   (React)       │
   └─────────────────┘
```

---

## 🔧 Sub-Tasks Breakdown

### **Sub-Task 1: Prepare Code for Deployment** (90 minutes)

#### Step 1.1: Create Production Requirements File (15 min)

**File to Create:** `backend/requirements.txt`

**Why?** Render needs to know which Python packages to install.

**How to Create:**

1. Activate your virtual environment:
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Generate requirements file:
```bash
pip freeze > requirements.txt
```

3. Review and clean up the file:
```bash
cat requirements.txt
```

**Expected Content:**
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
beautifulsoup4==4.12.2
selenium==4.15.2
apscheduler==3.10.4
rapidfuzz==3.5.2
spacy==3.7.2
httpx==0.25.1
aiosmtplib==3.0.1
jinja2==3.1.2
python-multipart==0.0.6
websockets==12.0
```

**Important:** Remove any local-only packages like:
- `pkg-resources==0.0.0` (Linux artifact)
- Any packages with file paths

#### Step 1.2: Create Procfile for Backend (10 min)

**File to Create:** `backend/Procfile`

**What is Procfile?** Tells Render how to start your application.

**Content:**
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**Explanation:**
- `web:` - Declares this is a web service
- `uvicorn app.main:app` - Starts FastAPI app
- `--host 0.0.0.0` - Listens on all network interfaces
- `--port $PORT` - Uses Render's assigned port

#### Step 1.3: Update CORS Settings for Production (20 min)

**File to Modify:** `backend/app/main.py`

**Why?** Your frontend will be on a different domain than your backend, so you need to allow cross-origin requests.

**Find this section:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Replace with:**
```python
import os

# Get allowed origins from environment variable
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:3000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Why?** This allows you to configure allowed origins via environment variable in production.

#### Step 1.4: Create Frontend Build Configuration (15 min)

**File to Check:** `frontend/vite.config.ts`

**Ensure it has:**
```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
  },
  build: {
    outDir: 'dist',
    sourcemap: false, // Disable for production
  }
})
```

#### Step 1.5: Update Frontend API URLs (20 min)

**File to Modify:** `frontend/src/services/api.ts`

**Current (Development):**
```typescript
const API_BASE_URL = 'http://localhost:8000';
```

**Update to (Production-Ready):**
```typescript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const WS_BASE_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';
```

**Why?** This allows different URLs for development and production.

#### Step 1.6: Create .gitignore Files (10 min)

**Ensure these files exist:**

**`backend/.gitignore`:**
```
venv/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg
*.egg-info/
dist/
build/
.env
.env.local
*.db
*.sqlite
*.sqlite3
.DS_Store
.vscode/
.idea/
```

**`frontend/.gitignore`:**
```
node_modules/
dist/
.env
.env.local
.env.production.local
.DS_Store
.vscode/
.idea/
```

---

### **Sub-Task 2: Setup GitHub Repository** (60 minutes)

#### Step 2.1: Create GitHub Account (10 min)

**If you don't have one:**

1. Go to [github.com](https://github.com)
2. Click "Sign up"
3. Follow the registration process
4. Verify your email

#### Step 2.2: Create New Repository (15 min)

1. **Click "New repository"** (green button)

2. **Repository Settings:**
   - Name: `product-search-agent`
   - Description: "AI-powered product search agent with real-time notifications"
   - Visibility: Public (required for free Render deployment)
   - ✅ Add README
   - ✅ Add .gitignore (Python)
   - License: MIT (optional)

3. **Click "Create repository"**

#### Step 2.3: Initialize Local Git Repository (15 min)

**In your project root directory:**

```bash
cd /path/to/product-search-agent

# Initialize git (if not already done)
git init

# Add all files
git add .

# Create first commit
git commit -m "Initial commit: Product Search Agent"

# Add remote repository https://github.com/deghislain/product-search-agent
git remote add origin https://github.com/deghislain/product-search-agent.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**Troubleshooting:**

**Error: "remote origin already exists"**
```bash
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/product-search-agent.git
```

**Error: "Authentication failed"**
- Use GitHub Personal Access Token instead of password
- Go to GitHub Settings → Developer settings → Personal access tokens
- Generate new token with `repo` scope
- Use token as password when pushing

#### Step 2.4: Verify Repository (5 min)

1. Go to your GitHub repository URL
2. Verify all files are uploaded
3. Check that `.env` files are NOT uploaded (should be in .gitignore)

#### Step 2.5: Create Production Branch (Optional - 15 min)

**Why?** Separate development from production code.

```bash
# Create production branch
git checkout -b production

# Push production branch
git push -u origin production
```

---

### **Sub-Task 3: Deploy Backend to Render** (90 minutes)

#### Step 3.1: Create Render Account (10 min)

1. Go to [render.com](https://render.com)
2. Click "Get Started"
3. Sign up with GitHub (recommended)
4. Authorize Render to access your repositories

#### Step 3.2: Create New Web Service (20 min)

1. **Click "New +"** → "Web Service"

2. **Connect Repository:**
   - Select your `product-search-agent` repository
   - Click "Connect"

3. **Configure Service:**
   - **Name:** `product-search-agent-api`
   - **Region:** Choose closest to you
   - **Branch:** `main` (or `production`)
   - **Root Directory:** `backend`
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

4. **Select Plan:**
   - Choose "Free" plan
   - Note: Free tier sleeps after 15 min of inactivity

5. **Click "Create Web Service"**

#### Step 3.3: Configure Environment Variables (30 min)

**In Render Dashboard:**

1. Go to your service → "Environment" tab
2. Add these variables:

```
# Required Variables
DATABASE_URL=sqlite:///./product_search.db
SECRET_KEY=your-secret-key-here-change-this-in-production
ALLOWED_ORIGINS=https://your-frontend-url.onrender.com

# Email Configuration (if using email notifications)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=your-email@gmail.com

# Optional: Upgrade to PostgreSQL
# DATABASE_URL=postgresql://user:password@host:port/database
```

**How to Generate SECRET_KEY:**
```python
import secrets
print(secrets.token_urlsafe(32))
```

**Important Notes:**
- Don't use quotes around values
- Update `ALLOWED_ORIGINS` after deploying frontend
- For Gmail, use App Password (not regular password)

#### Step 3.4: Monitor Deployment (15 min)

**Watch the Logs:**

1. Go to "Logs" tab
2. Watch for:
   - ✅ "Installing dependencies..."
   - ✅ "Starting service..."
   - ✅ "Application startup complete"

**Common Errors:**

**"ModuleNotFoundError"**
- Missing package in `requirements.txt`
- Add it and redeploy

**"Port already in use"**
- Make sure you're using `$PORT` variable
- Check Procfile is correct

**"Database connection failed"**
- Check `DATABASE_URL` environment variable
- Verify database is accessible

#### Step 3.5: Test Backend API (15 min)

**Your API URL:** `https://product-search-agent-api.onrender.com`

**Test Endpoints:**

1. **Health Check:**
```bash
curl https://product-search-agent-api.onrender.com/api/health
```

Expected: `{"status": "healthy"}`

2. **API Documentation:**
- Visit: `https://product-search-agent-api.onrender.com/docs`
- Should see Swagger UI

3. **Test WebSocket:**
```javascript
// In browser console
const ws = new WebSocket('wss://product-search-agent-api.onrender.com/ws/notifications');
ws.onopen = () => console.log('Connected!');
```

---

### **Sub-Task 4: Deploy Frontend to Render** (90 minutes)

#### Step 4.1: Create Static Site (20 min)

1. **In Render Dashboard:**
   - Click "New +" → "Static Site"

2. **Connect Repository:**
   - Select same repository
   - Click "Connect"

3. **Configure Site:**
   - **Name:** `product-search-agent`
   - **Branch:** `main`
   - **Root Directory:** `frontend`
   - **Build Command:** `npm install && npm run build`
   - **Publish Directory:** `dist`

4. **Click "Create Static Site"**

#### Step 4.2: Configure Frontend Environment Variables (20 min)

**In Render Dashboard (Static Site):**

1. Go to "Environment" tab
2. Add these variables:

```
VITE_API_URL=https://product-search-agent-api.onrender.com
VITE_WS_URL=wss://product-search-agent-api.onrender.com/ws/notifications
```

**Important:** 
- Use `https://` for API (not `http://`)
- Use `wss://` for WebSocket (not `ws://`)

#### Step 4.3: Update Backend CORS (15 min)

**Now that you have frontend URL:**

1. Go to backend service in Render
2. Update `ALLOWED_ORIGINS` environment variable:
```
ALLOWED_ORIGINS=https://product-search-agent.onrender.com,http://localhost:5173
```

3. Click "Save Changes"
4. Service will automatically redeploy

#### Step 4.4: Monitor Frontend Deployment (15 min)

**Watch Build Logs:**

1. Go to "Logs" tab
2. Watch for:
   - ✅ "Installing dependencies..."
   - ✅ "Building application..."
   - ✅ "Build completed"
   - ✅ "Site is live"

**Common Errors:**

**"Build failed: npm ERR!"**
- Check `package.json` for errors
- Verify all dependencies are listed
- Try building locally first

**"Module not found"**
- Missing import in code
- Check file paths are correct
- Verify case sensitivity (Linux is case-sensitive)

#### Step 4.5: Test Frontend Application (20 min)

**Your App URL:** `https://product-search-agent.onrender.com`

**Test Checklist:**

1. **Page Loads:**
   - [ ] Dashboard page loads
   - [ ] No console errors
   - [ ] Styling looks correct

2. **API Connection:**
   - [ ] Can create new search
   - [ ] Can view matches
   - [ ] Settings page works

3. **WebSocket Connection:**
   - [ ] Status shows "🟢 Live"
   - [ ] No connection errors in console

4. **Functionality:**
   - [ ] Create a test search
   - [ ] Verify it appears in list
   - [ ] Check matches page

---

### **Sub-Task 5: Configure Custom Domain (Optional)** (30 minutes)

#### Step 5.1: Purchase Domain (15 min)

**Domain Registrars:**
- Namecheap (recommended for beginners)
- Google Domains
- GoDaddy

**Cost:** ~$10-15/year

#### Step 5.2: Add Custom Domain to Render (15 min)

1. **In Render Dashboard:**
   - Go to your static site
   - Click "Settings" → "Custom Domains"
   - Click "Add Custom Domain"

2. **Enter Domain:**
   - Example: `myproductsearch.com`
   - Click "Save"

3. **Configure DNS:**
   - Render will show DNS records to add
   - Go to your domain registrar
   - Add the CNAME record
   - Wait 24-48 hours for propagation

---

### **Sub-Task 6: Setup Monitoring & Logging** (60 minutes)

#### Step 6.1: Enable Render Monitoring (15 min)

**Built-in Features:**

1. **Health Checks:**
   - Render automatically pings `/health` endpoint
   - Service restarts if unhealthy

2. **Logs:**
   - View real-time logs in dashboard
   - Search and filter logs
   - Download logs for analysis

3. **Metrics:**
   - CPU usage
   - Memory usage
   - Request count
   - Response times

#### Step 6.2: Setup Error Tracking (Optional - 20 min)

**Using Sentry (Free Tier):**

1. **Create Sentry Account:**
   - Go to [sentry.io](https://sentry.io)
   - Sign up for free

2. **Create Project:**
   - Choose "Python" for backend
   - Choose "React" for frontend

3. **Install Sentry:**

**Backend:**
```bash
pip install sentry-sdk[fastapi]
```

**Add to `main.py`:**
```python
import sentry_sdk

sentry_sdk.init(
    dsn="your-sentry-dsn",
    traces_sample_rate=1.0,
)
```

**Frontend:**
```bash
npm install @sentry/react
```

**Add to `main.tsx`:**
```typescript
import * as Sentry from "@sentry/react";

Sentry.init({
  dsn: "your-sentry-dsn",
  integrations: [new Sentry.BrowserTracing()],
  tracesSampleRate: 1.0,
});
```

#### Step 6.3: Setup Uptime Monitoring (Optional - 15 min)

**Using UptimeRobot (Free):**

1. Go to [uptimerobot.com](https://uptimerobot.com)
2. Create account
3. Add new monitor:
   - Type: HTTP(s)
   - URL: Your API health endpoint
   - Interval: 5 minutes
4. Get email alerts if site goes down

#### Step 6.4: Create Status Page (Optional - 10 min)

**Using Render:**

1. In dashboard, go to "Status Page"
2. Enable public status page
3. Share URL with users

---

### **Sub-Task 7: Testing & Verification** (60 minutes)

#### Step 7.1: End-to-End Testing (30 min)

**Test Scenario 1: Create Search**
1. Open your deployed app
2. Create a new search request
3. Verify it appears in the list
4. Check backend logs for execution

**Test Scenario 2: Real-Time Notifications**
1. Open app in browser
2. Trigger a search (or use test script)
3. Verify notification appears
4. Check WebSocket connection is stable

**Test Scenario 3: Multiple Users**
1. Open app in 2 different browsers
2. Create search in one
3. Verify both receive notifications

**Test Scenario 4: Mobile Responsiveness**
1. Open app on mobile device
2. Test all features
3. Verify layout is responsive

#### Step 7.2: Performance Testing (15 min)

**Use Lighthouse (Built into Chrome):**

1. Open DevTools (F12)
2. Go to "Lighthouse" tab
3. Run audit
4. Check scores:
   - Performance: >80
   - Accessibility: >90
   - Best Practices: >90
   - SEO: >80

#### Step 7.3: Security Check (15 min)

**Checklist:**
- [ ] HTTPS enabled (should be automatic on Render)
- [ ] Environment variables not exposed in code
- [ ] No API keys in frontend code
- [ ] CORS properly configured
- [ ] Rate limiting enabled (if implemented)

---

## ✅ Definition of Done

Deployment is complete when:

- [ ] Backend API is live and accessible
- [ ] Frontend is live and accessible
- [ ] WebSocket connections work
- [ ] Can create and view searches
- [ ] Real-time notifications work
- [ ] No console errors
- [ ] All environment variables configured
- [ ] CORS properly set up
- [ ] Monitoring enabled
- [ ] Documentation updated with URLs

---

## 📝 Post-Deployment Checklist

### **Update Documentation:**

1. **README.md:**
   - Add live demo URL
   - Update installation instructions
   - Add deployment section

2. **Environment Variables:**
   - Document all required variables
   - Provide example values

3. **API Documentation:**
   - Update base URL in examples
   - Add production endpoints

### **Share Your Project:**

1. **GitHub:**
   - Add live demo link to repository description
   - Create releases/tags for versions

2. **Portfolio:**
   - Add to your portfolio website
   - Include screenshots
   - Write case study

3. **Social Media:**
   - Share on LinkedIn
   - Post on Twitter
   - Share in developer communities

---

## 🚨 Common Issues & Solutions

### **Issue: "Application Error" on Render**

**Solutions:**
1. Check logs for specific error
2. Verify all environment variables are set
3. Ensure `requirements.txt` is complete
4. Check Procfile syntax

### **Issue: Frontend can't connect to backend**

**Solutions:**
1. Verify CORS settings include frontend URL
2. Check API URL in frontend env variables
3. Ensure using `https://` not `http://`
4. Check backend is actually running

### **Issue: WebSocket connection fails**

**Solutions:**
1. Use `wss://` not `ws://` in production
2. Check WebSocket endpoint is accessible
3. Verify no firewall blocking WebSocket
4. Check browser console for specific errors

### **Issue: "Service Unavailable" after 15 minutes**

**Explanation:** Free tier services sleep after inactivity

**Solutions:**
1. Upgrade to paid plan ($7/month)
2. Use a service like UptimeRobot to ping every 14 minutes
3. Accept the limitation for development

### **Issue: Database resets on redeploy**

**Explanation:** SQLite file is ephemeral on Render

**Solutions:**
1. Upgrade to PostgreSQL (free on Render)
2. Use external database service
3. Implement database backups

---

## 💰 Cost Breakdown

### **Free Tier (Recommended for Learning):**
- Render Backend: $0/month
- Render Frontend: $0/month
- GitHub: $0/month
- **Total: $0/month**

**Limitations:**
- Services sleep after 15 min inactivity
- 750 hours/month (enough for 1 service)
- Slower cold starts

### **Paid Tier (Production Ready):**
- Render Backend: $7/month
- Render Frontend: $0/month (static sites always free)
- Custom Domain: $10-15/year
- **Total: ~$7-8/month**

**Benefits:**
- No sleeping
- Faster performance
- More resources
- Better support

---

## 🎓 Learning Resources

**Render Documentation:**
- [Deploy FastAPI](https://render.com/docs/deploy-fastapi)
- [Deploy React](https://render.com/docs/deploy-create-react-app)
- [Environment Variables](https://render.com/docs/environment-variables)

**Git & GitHub:**
- [Git Basics](https://git-scm.com/book/en/v2/Getting-Started-Git-Basics)
- [GitHub Guides](https://guides.github.com/)

**Production Best Practices:**
- [12 Factor App](https://12factor.net/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)

---

## 🚀 Next Steps

After deployment:

1. **Monitor Performance:**
   - Check logs daily
   - Monitor error rates
   - Track user feedback

2. **Iterate:**
   - Fix bugs as they appear
   - Add new features
   - Improve performance

3. **Scale:**
   - Upgrade to paid tier if needed
   - Add caching (Redis)
   - Implement CDN for static assets

4. **Maintain:**
   - Keep dependencies updated
   - Regular security audits
   - Backup database regularly

---

## 💡 Tips for Junior Developers

1. **Start Simple:** Deploy basic version first, add features later
2. **Test Locally:** Always test thoroughly before deploying
3. **Read Logs:** Logs are your best friend for debugging
4. **Use Git:** Commit often, push regularly
5. **Document Everything:** Future you will thank present you
6. **Ask for Help:** Render has great community support
7. **Be Patient:** First deployment takes time, gets easier

**Good luck with your deployment! 🎉**