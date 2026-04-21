# Troubleshooting: Create Search Not Working

## Problem
The "Create Search" functionality is not working in the deployed application. No errors appear in the logs, but the frontend cannot communicate with the backend.

## Root Cause
The issue has **two parts**:

1. **Frontend Configuration**: The `frontend/.env.production` file had placeholder URLs instead of the actual deployed backend URL
2. **Backend CORS Configuration**: The backend needs to allow requests from the deployed frontend URL

## Solution

### Part 1: Update Frontend Environment Variables ✅ COMPLETED

The `frontend/.env.production` file has been updated with the correct URLs:

```env
VITE_API_URL=https://product-search-agent-api.onrender.com
VITE_WS_URL=wss://product-search-agent-api.onrender.com/ws/notifications
```

### Part 2: Update Backend CORS Configuration (REQUIRED)

You need to configure the backend to allow requests from your frontend URL.

#### Option A: Update via Render Dashboard (RECOMMENDED)

1. **Go to Render Dashboard**: https://dashboard.render.com
2. **Select your backend service**: `product-search-agent-api`
3. **Go to "Environment" tab**
4. **Add or update the `CORS_ORIGINS` environment variable**:
   ```
   CORS_ORIGINS=https://product-search-agent-ff7s.onrender.com,http://localhost:5173,http://localhost:3000
   ```
5. **Click "Save Changes"**
6. **Wait for automatic redeployment** (takes 2-3 minutes)

#### Option B: Create Backend .env File (For Local Testing)

If you want to test locally first, create a `backend/.env` file:

```bash
cd backend
cp .env.example .env
```

Then edit `backend/.env` and update:

```env
# CORS Settings - Add your deployed frontend URL
CORS_ORIGINS=https://product-search-agent-ff7s.onrender.com,http://localhost:5173,http://localhost:3000

# Other important production settings
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
DATABASE_URL=sqlite:///./product_search.db
```

**Note**: The `.env` file is for local development only. For production on Render, use the Environment Variables in the dashboard.

### Part 3: Redeploy Frontend

After updating the backend CORS settings, you need to rebuild and redeploy the frontend:

#### Method 1: Automatic Deployment (If connected to GitHub)

1. **Commit the changes**:
   ```bash
   git add frontend/.env.production
   git commit -m "fix: Update production API URLs for deployed backend"
   git push origin main
   ```

2. **Render will automatically detect the changes and redeploy**

#### Method 2: Manual Deployment via Render Dashboard

1. Go to Render Dashboard
2. Select your frontend service: `product-search-agent-ff7s`
3. Click "Manual Deploy" → "Deploy latest commit"
4. Wait for build to complete (3-5 minutes)

### Part 4: Verify the Fix

After both services are redeployed, test the following:

#### 1. Check Backend Health
Visit: https://product-search-agent-api.onrender.com/api/health

Expected response:
```json
{
  "status": "healthy",
  "message": "Product Search Agent API is running",
  "timestamp": "2026-04-21T21:00:00.000Z",
  "version": "1.0.0"
}
```

#### 2. Check Backend API Documentation
Visit: https://product-search-agent-api.onrender.com/docs

You should see the Swagger UI with all API endpoints.

#### 3. Test Frontend
1. Open: https://product-search-agent-ff7s.onrender.com
2. Open browser DevTools (F12)
3. Go to Console tab
4. Click "Create New Search"
5. Fill in the form and submit

**Expected behavior**:
- No CORS errors in console
- API request shows in Network tab
- Search is created successfully
- You see the new search in the list

#### 4. Check for Errors

**In Browser Console (F12 → Console tab)**, you should see:
```
API Base URL: https://product-search-agent-api.onrender.com
Environment: production
API Request: POST /api/search-requests
API Response: 200 OK
```

**If you see errors like**:
- `"Access to fetch at '...' from origin '...' has been blocked by CORS policy"` → Backend CORS not configured correctly
- `"Network Error"` → Backend might be sleeping (free tier) or not accessible
- `"Failed to fetch"` → Check if backend URL is correct

## Common Issues and Solutions

### Issue 1: "CORS Policy" Error

**Error in Console**:
```
Access to fetch at 'https://product-search-agent-api.onrender.com/api/search-requests' 
from origin 'https://product-search-agent-ff7s.onrender.com' has been blocked by CORS policy
```

**Solution**:
- Verify `CORS_ORIGINS` environment variable in backend includes your frontend URL
- Make sure there are no typos in the URL
- Restart backend service after updating CORS settings

### Issue 2: Backend Returns 503 or Takes Long to Respond

**Cause**: Free tier services on Render sleep after 15 minutes of inactivity

**Solution**:
- Wait 30-60 seconds for the service to wake up
- Consider upgrading to paid tier ($7/month) for always-on service
- Use a service like UptimeRobot to ping your backend every 14 minutes

### Issue 3: "Network Error" or "Failed to Fetch"

**Possible Causes**:
1. Backend is not running
2. Wrong backend URL in frontend
3. Backend crashed

**Solution**:
1. Check backend logs in Render dashboard
2. Verify backend health endpoint is accessible
3. Check for any deployment errors in Render logs

### Issue 4: Changes Not Reflecting

**Solution**:
1. Clear browser cache (Ctrl+Shift+Delete)
2. Hard refresh (Ctrl+Shift+R or Cmd+Shift+R)
3. Try in incognito/private window
4. Verify the build completed successfully in Render logs

## Deployment Checklist

Use this checklist to ensure everything is configured correctly:

### Backend Configuration
- [ ] Backend deployed to Render
- [ ] Health endpoint accessible: `/api/health`
- [ ] API docs accessible: `/docs`
- [ ] `CORS_ORIGINS` includes frontend URL
- [ ] Environment variables set correctly
- [ ] No errors in deployment logs

### Frontend Configuration
- [ ] `frontend/.env.production` has correct `VITE_API_URL`
- [ ] `frontend/.env.production` has correct `VITE_WS_URL`
- [ ] Frontend deployed to Render
- [ ] Build completed successfully
- [ ] No errors in browser console

### Testing
- [ ] Can access frontend URL
- [ ] Can access backend health endpoint
- [ ] Can create a new search
- [ ] Search appears in the list
- [ ] No CORS errors in console
- [ ] WebSocket connection works (status shows "🟢 Live")

## Quick Reference

### Your Deployment URLs
- **Backend API**: https://product-search-agent-api.onrender.com
- **Frontend App**: https://product-search-agent-ff7s.onrender.com
- **API Docs**: https://product-search-agent-api.onrender.com/docs
- **Health Check**: https://product-search-agent-api.onrender.com/api/health

### Environment Variables to Set on Render

**Backend Service** (`product-search-agent-api`):
```
CORS_ORIGINS=https://product-search-agent-ff7s.onrender.com,http://localhost:5173
ENVIRONMENT=production
DEBUG=false
DATABASE_URL=sqlite:///./product_search.db
```

**Frontend Service** (`product-search-agent-ff7s`):
```
VITE_API_URL=https://product-search-agent-api.onrender.com
VITE_WS_URL=wss://product-search-agent-api.onrender.com/ws/notifications
```

## Next Steps

1. **Update Backend CORS** via Render Dashboard (see Part 2 above)
2. **Commit and push** the frontend changes
3. **Wait for redeployment** (both services)
4. **Test the application** using the verification steps
5. **Monitor logs** for any errors

## Need More Help?

If you're still experiencing issues:

1. **Check Render Logs**:
   - Go to your service in Render Dashboard
   - Click "Logs" tab
   - Look for errors or warnings

2. **Check Browser Console**:
   - Open DevTools (F12)
   - Go to Console tab
   - Look for red error messages
   - Go to Network tab to see API requests

3. **Test Backend Directly**:
   - Use Postman or curl to test API endpoints
   - Example:
     ```bash
     curl https://product-search-agent-api.onrender.com/api/health
     ```

4. **Verify Environment Variables**:
   - In Render Dashboard, check all environment variables are set correctly
   - No typos in URLs
   - No extra spaces

---

**Last Updated**: 2026-04-21  
**Status**: Frontend .env.production updated ✅ | Backend CORS needs update ⏳