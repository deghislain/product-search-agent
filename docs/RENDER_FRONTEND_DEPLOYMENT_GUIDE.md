# Render.com Frontend Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying the Product Search Agent frontend (React/Vite) to Render.com as a static site.

---

## Prerequisites

Before starting:
- ✅ Backend deployed and running on Render
- ✅ Backend URL available (e.g., `https://product-search-agent-api.onrender.com`)
- ✅ Frontend code pushed to GitHub
- ✅ Frontend builds successfully locally (`npm run build`)

---

## Step 4.1: Create Static Site (20 minutes)

### 1. Go to Render Dashboard

Visit: [https://dashboard.render.com](https://dashboard.render.com)

### 2. Create New Static Site

- Click **"New +"** button (top right)
- Select **"Static Site"**

### 3. Connect Repository

**If you signed up with GitHub:**
- Your repositories should appear automatically
- Find `product-search-agent`
- Click **"Connect"**

**If you signed up with email:**
- Click "Connect account" → GitHub
- Authorize Render
- Select `product-search-agent`
- Click **"Connect"**

### 4. Configure Static Site Settings

Fill in these fields carefully:

| Field | Value | Notes |
|-------|-------|-------|
| **Name** | `product-search-agent-frontend` | Or any name you prefer |
| **Branch** | `main` | Or your default branch |
| **Root Directory** | `frontend` | ⚠️ Important! |
| **Build Command** | `npm install && npm run build` | Installs deps and builds |
| **Publish Directory** | `dist` | Vite's output directory |

**⚠️ Critical Settings:**
- Root Directory MUST be `frontend`
- Publish Directory MUST be `dist` (Vite's default)
- Build Command must include `npm install`

### 5. Advanced Settings (Optional but Recommended)

Click **"Advanced"** to expand:

**Node Version:**
- Add environment variable: `NODE_VERSION=18`
- This ensures consistent Node.js version

**Auto-Deploy:**
- ✅ Keep "Auto-Deploy" enabled
- Automatically deploys when you push to GitHub

### 6. Select Plan

- Scroll down to "Plan"
- Select **"Free"** plan
- Note: Free tier limitations:
  - 100 GB bandwidth/month
  - Global CDN included
  - Custom domains supported
  - No sleep time (unlike web services)

### 7. Create Static Site

- Review all settings
- Click **"Create Static Site"** button
- Render will start building your frontend

---

## Step 4.2: Configure Environment Variables (15 minutes)

### Get Your Backend URL

First, you need your backend URL:

1. Go to Render dashboard
2. Click on your **backend service**
3. Copy the URL at the top
4. Example: `https://product-search-agent-api.onrender.com`

### Add Environment Variables

1. Go to your **frontend service** dashboard
2. Click **"Environment"** tab (left sidebar)
3. Click **"Add Environment Variable"**

### Required Variables

Add these two environment variables:

#### 1. VITE_API_URL (Required)

```
Key:   VITE_API_URL
Value: https://your-backend-url.onrender.com
```

**⚠️ Important:**
- Replace `your-backend-url` with your actual backend URL
- Must start with `https://` (not `http://`)
- No trailing slash
- Example: `https://product-search-agent-api.onrender.com`

#### 2. VITE_WS_URL (Required)

```
Key:   VITE_WS_URL
Value: wss://your-backend-url.onrender.com/ws/notifications
```

**⚠️ Important:**
- Use `wss://` (not `ws://`) for secure WebSocket
- Same domain as VITE_API_URL
- Must include `/ws/notifications` path
- Example: `wss://product-search-agent-api.onrender.com/ws/notifications`

### Save and Redeploy

1. Click **"Save Changes"**
2. Render will automatically redeploy with new environment variables
3. Wait for deployment to complete (~2-3 minutes)

---

## Step 4.3: Monitor Deployment (10 minutes)

### Watch Build Logs

1. Go to **"Logs"** tab (left sidebar)
2. Watch the deployment process

### Expected Log Output

You should see:

```
==> Cloning from https://github.com/YOUR_USERNAME/product-search-agent...
==> Checking out commit abc123...
==> Using Node version 18.x
==> Running build command: npm install && npm run build
==> npm install
==> added 500 packages in 30s
==> npm run build
==> vite v5.0.0 building for production...
==> ✓ 150 modules transformed.
==> dist/index.html                   0.50 kB
==> dist/assets/index-abc123.js     150.00 kB
==> dist/assets/react-vendor-def.js 800.00 kB
==> ✓ built in 15s
==> Build successful!
==> Uploading build...
==> Deploy successful!
==> Your site is live at https://product-search-agent-frontend.onrender.com
```

### Build Time

- First build: 2-4 minutes
- Subsequent builds: 1-2 minutes

### Common Build Errors

#### Error: "npm ERR! code ENOENT"

**Cause:** Root Directory not set to `frontend`

**Solution:**
1. Go to "Settings" tab
2. Find "Root Directory"
3. Change to `frontend`
4. Click "Save Changes"

#### Error: "Module not found"

**Cause:** Missing dependency in package.json

**Solution:**
1. Check package.json has all dependencies
2. Commit and push changes
3. Render will automatically redeploy

#### Error: "Build failed: dist directory not found"

**Cause:** Wrong Publish Directory

**Solution:**
1. Go to "Settings" tab
2. Find "Publish Directory"
3. Change to `dist`
4. Click "Save Changes"

#### Error: "VITE_API_URL is not defined"

**Cause:** Environment variables not set

**Solution:**
1. Go to "Environment" tab
2. Add VITE_API_URL and VITE_WS_URL
3. Click "Save Changes"

---

## Step 4.4: Test Frontend (15 minutes)

### Get Your Frontend URL

After deployment succeeds:
1. Go to top of dashboard
2. Copy your site URL
3. Example: `https://product-search-agent-frontend.onrender.com`

### Test 1: Access Homepage

**Visit:**
```
https://your-frontend-url.onrender.com
```

**Expected:**
- Product Search Agent dashboard loads
- No console errors
- Styling looks correct

### Test 2: Check API Connection

**Open browser console (F12):**
1. Go to Console tab
2. Look for API connection logs
3. Should see: `API Base URL: https://your-backend-url.onrender.com`

**Expected:**
- No CORS errors
- API requests succeed
- Data loads correctly

### Test 3: Test Navigation

**Click through pages:**
- Dashboard (/)
- Matches (/matches)
- Settings (/settings)

**Expected:**
- All pages load
- No 404 errors
- Navigation works

### Test 4: Test API Functionality

**Try creating a search:**
1. Go to Dashboard
2. Fill in search form
3. Click "Create Search"

**Expected:**
- Form submits successfully
- Search appears in list
- No errors in console

### Test 5: Test WebSocket Connection

**Open browser console:**
```javascript
// Check WebSocket connection
// Should see in Network tab (WS filter)
```

**Expected:**
- WebSocket connects to backend
- Connection status shows "Connected"
- Real-time updates work

---

## Step 4.5: Update Backend CORS (10 minutes)

### Why This is Needed

Your backend needs to allow requests from your frontend URL.

### Update CORS_ORIGINS

1. **Go to backend service** on Render
2. **Click "Environment" tab**
3. **Find CORS_ORIGINS** (or add it if missing)
4. **Update value to:**
   ```
   https://your-frontend-url.onrender.com
   ```
5. **Click "Save Changes"**
6. **Backend will automatically redeploy** (~1 minute)

### Multiple Origins (Optional)

If you want to allow both localhost and production:

```
http://localhost:5173,https://your-frontend-url.onrender.com
```

**Format:** Comma-separated, no spaces

### Verify CORS is Working

1. **Refresh your frontend**
2. **Open browser console**
3. **Check for CORS errors**

**Expected:**
- ✅ No CORS errors
- ✅ API requests succeed
- ✅ Data loads correctly

---

## Step 4.6: Configure Custom Domain (Optional - 30 minutes)

### Why Use a Custom Domain?

- Professional URL (e.g., `app.yourdomain.com`)
- Better branding
- Easier to remember

### Prerequisites

- You own a domain (e.g., `yourdomain.com`)
- Access to domain DNS settings

### Steps

#### 1. Add Custom Domain in Render

1. Go to frontend service
2. Click **"Settings"** tab
3. Scroll to **"Custom Domain"**
4. Click **"Add Custom Domain"**
5. Enter your domain (e.g., `app.yourdomain.com`)
6. Click **"Save"**

#### 2. Configure DNS

Render will show you DNS records to add:

**CNAME Record:**
```
Type:  CNAME
Name:  app (or your subdomain)
Value: your-frontend.onrender.com
TTL:   3600
```

**Add this record in your domain provider:**
- GoDaddy
- Namecheap
- Cloudflare
- Google Domains
- etc.

#### 3. Wait for DNS Propagation

- Usually takes 5-30 minutes
- Can take up to 48 hours
- Check status in Render dashboard

#### 4. SSL Certificate

- Render automatically provisions SSL certificate
- Usually takes 5-10 minutes
- Your site will be accessible via HTTPS

#### 5. Update Backend CORS

Don't forget to update CORS_ORIGINS:

```
https://app.yourdomain.com
```

---

## Step 4.7: Setup Redirects for SPA (Important!)

### Why This is Needed

React Router uses client-side routing. Without redirects, direct URLs (like `/matches`) will return 404.

### Configure Redirects

#### Option 1: Using _redirects File (Recommended)

1. **Create file:** `frontend/public/_redirects`

2. **Add this content:**
   ```
   /*    /index.html   200
   ```

3. **Commit and push:**
   ```bash
   git add frontend/public/_redirects
   git commit -m "Add SPA redirects"
   git push origin main
   ```

4. **Render will automatically redeploy**

#### Option 2: Using Render Dashboard

1. Go to "Redirects/Rewrites" in Settings
2. Add rule:
   - **Source:** `/*`
   - **Destination:** `/index.html`
   - **Status:** `200` (Rewrite)
3. Click "Save"

### Test Redirects

1. Visit a direct URL: `https://your-frontend.onrender.com/matches`
2. Should load correctly (not 404)
3. Refresh page - should still work

---

## Troubleshooting

### Issue: Build Fails with "npm ERR!"

**Check:**
1. Root Directory is `frontend`
2. package.json exists in frontend directory
3. All dependencies are listed in package.json

**Solution:**
```bash
# Test locally first
cd frontend
npm install
npm run build
# If this works, push to GitHub
```

### Issue: Blank Page After Deployment

**Causes:**
1. Wrong Publish Directory
2. Build failed silently
3. JavaScript errors

**Solutions:**
1. Check Publish Directory is `dist`
2. Check build logs for errors
3. Open browser console for errors

### Issue: API Requests Failing

**Check:**
1. VITE_API_URL is set correctly
2. Backend is running
3. CORS is configured on backend

**Solution:**
1. Verify environment variables
2. Check backend health: `curl https://backend-url/api/health`
3. Update CORS_ORIGINS on backend

### Issue: WebSocket Not Connecting

**Check:**
1. VITE_WS_URL uses `wss://` (not `ws://`)
2. Backend WebSocket endpoint is accessible
3. No firewall blocking WebSocket

**Solution:**
1. Test WebSocket manually:
   ```javascript
   const ws = new WebSocket('wss://backend-url/ws/notifications');
   ws.onopen = () => console.log('Connected!');
   ```

### Issue: 404 on Direct URLs

**Cause:** Missing SPA redirects

**Solution:**
1. Add `_redirects` file (see Step 4.7)
2. Or configure redirects in Render dashboard

### Issue: Styles Not Loading

**Check:**
1. Tailwind CSS is configured
2. CSS files are in correct location
3. Build includes CSS

**Solution:**
1. Check `frontend/src/index.css` exists
2. Verify `import './index.css'` in main.tsx
3. Rebuild locally to test

---

## Deployment Checklist

Before marking Step 4 complete:

- [ ] Static site created on Render
- [ ] Root Directory set to `frontend`
- [ ] Publish Directory set to `dist`
- [ ] Build Command correct
- [ ] VITE_API_URL environment variable set
- [ ] VITE_WS_URL environment variable set
- [ ] Deployment successful (green status)
- [ ] Frontend loads in browser
- [ ] No console errors
- [ ] API connection works
- [ ] Navigation works
- [ ] Backend CORS updated with frontend URL
- [ ] SPA redirects configured
- [ ] WebSocket connects successfully

---

## Post-Deployment Tasks

### 1. Update Documentation

Update your README with:
- Frontend URL
- Backend URL
- How to access the application

### 2. Test Full Workflow

1. Create a search request
2. Wait for search to execute
3. Check for matches
4. Verify notifications work
5. Test email notifications (if enabled)

### 3. Monitor Performance

- Check Render dashboard for:
  - Bandwidth usage
  - Build times
  - Error rates

### 4. Setup Monitoring (Optional)

Consider adding:
- Google Analytics
- Sentry for error tracking
- Uptime monitoring

---

## Updating Frontend

### When You Make Changes

1. **Make changes locally**
2. **Test locally:**
   ```bash
   cd frontend
   npm run dev
   ```
3. **Build locally to verify:**
   ```bash
   npm run build
   npm run preview
   ```
4. **Commit and push:**
   ```bash
   git add .
   git commit -m "Update frontend"
   git push origin main
   ```
5. **Render automatically redeploys**
6. **Monitor deployment in Render dashboard**

### Rollback if Needed

If deployment breaks:

1. Go to Render dashboard
2. Click "Deploys" tab
3. Find previous successful deploy
4. Click "Redeploy"

---

## Cost Considerations

### Free Tier Limits

**Static Sites (Free):**
- ✅ 100 GB bandwidth/month
- ✅ Unlimited builds
- ✅ Global CDN
- ✅ Custom domains
- ✅ Automatic SSL
- ✅ No sleep time

**Typical Usage:**
- Small app: 1-5 GB/month
- Medium app: 5-20 GB/month
- Large app: 20-100 GB/month

### Upgrade Considerations

Upgrade to paid plan if:
- Exceed 100 GB bandwidth
- Need priority support
- Need advanced features

**Paid Plans:**
- Starter: $7/month (400 GB bandwidth)
- Standard: $25/month (1 TB bandwidth)

---

## Quick Reference

### Frontend URLs

```
Production:  https://your-frontend.onrender.com
Custom:      https://app.yourdomain.com (if configured)
```

### Environment Variables

```
VITE_API_URL=https://your-backend.onrender.com
VITE_WS_URL=wss://your-backend.onrender.com/ws/notifications
```

### Build Configuration

```
Root Directory:    frontend
Build Command:     npm install && npm run build
Publish Directory: dist
```

### Important Files

```
frontend/public/_redirects    - SPA routing
frontend/.env.production      - Production env vars (template)
frontend/vite.config.ts       - Build configuration
frontend/package.json         - Dependencies
```

---

## Support

**Render Documentation:**
- [Static Sites](https://render.com/docs/static-sites)
- [Environment Variables](https://render.com/docs/environment-variables)
- [Custom Domains](https://render.com/docs/custom-domains)

**Project Documentation:**
- `docs/RENDER_BACKEND_DEPLOYMENT_GUIDE.md`
- `docs/FRONTEND_BUILD_CONFIGURATION.md`
- `docs/FRONTEND_API_URL_CONFIGURATION.md`

**Common Issues:**
- Check build logs first
- Verify environment variables
- Test locally before deploying
- Check browser console for errors

---

## Success Criteria

Your frontend is successfully deployed when:

✅ Site loads at production URL
✅ No console errors
✅ API requests work
✅ WebSocket connects
✅ Navigation works
✅ Direct URLs work (SPA redirects)
✅ Styling looks correct
✅ Forms submit successfully
✅ Real-time updates work
✅ Backend CORS configured

**Congratulations! Your Product Search Agent is now fully deployed! 🎉**