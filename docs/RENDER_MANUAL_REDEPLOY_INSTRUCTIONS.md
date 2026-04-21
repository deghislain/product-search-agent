# Manual Redeploy Instructions for Render

## Problem
After setting environment variables in Render, the backend service may not automatically restart, which means the new CORS_ORIGINS value isn't being used.

## Solution: Manual Redeploy

### Step 1: Go to Render Dashboard
1. Open https://dashboard.render.com
2. Click on your backend service: **product-search-agent-api**

### Step 2: Trigger Manual Deploy
1. Click the **"Manual Deploy"** button (top right)
2. Select **"Deploy latest commit"**
3. Click **"Deploy"**

### Step 3: Wait for Deployment
- Watch the logs as the service redeploys
- This takes about 2-3 minutes
- Look for: "Application startup complete"

### Step 4: Verify CORS is Working
After deployment completes:

1. **Test with curl**:
   ```bash
   curl -I -X OPTIONS https://product-search-agent-api.onrender.com/api/search-requests \
     -H "Origin: https://product-search-agent-ff7s.onrender.com" \
     -H "Access-Control-Request-Method: POST"
   ```

   **Expected response should include**:
   ```
   Access-Control-Allow-Origin: https://product-search-agent-ff7s.onrender.com
   Access-Control-Allow-Methods: DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT
   ```

2. **Test in browser**:
   - Open https://product-search-agent-ff7s.onrender.com
   - Open DevTools (F12) → Console
   - Refresh the page
   - The CORS error should be GONE

### Step 5: Test Create Search
1. Click "Create New Search"
2. Fill in the form
3. Submit
4. Should work without errors!

## Alternative: Use Render CLI

If you prefer command line:

```bash
# Install Render CLI
npm install -g @render/cli

# Login
render login

# List services
render services list

# Deploy specific service
render deploy --service product-search-agent-api
```

## Verify Environment Variables Are Set

Before redeploying, double-check your environment variables:

1. Go to backend service → **Environment** tab
2. Verify these are set:

```
CORS_ORIGINS=https://product-search-agent-ff7s.onrender.com
```

**Important Notes**:
- No quotes around the value
- No trailing slashes
- Exact URL match (https, not http)
- Can add multiple origins separated by commas:
  ```
  CORS_ORIGINS=https://product-search-agent-ff7s.onrender.com,http://localhost:5173
  ```

## Troubleshooting

### If CORS error persists after redeploy:

1. **Check the logs** for any errors during startup
2. **Verify the environment variable** is actually set (no typos)
3. **Try adding a debug endpoint** to see what CORS origins the backend is using
4. **Clear browser cache** and try again

### Check Backend Logs

1. Go to backend service in Render
2. Click "Logs" tab
3. Look for startup messages
4. Should see: "🚀 Product Search Agent API Starting Up"

### If service won't start:

1. Check for Python errors in logs
2. Verify all dependencies are in requirements.txt
3. Check that Procfile is correct
4. Try deploying from a clean state

## Quick Checklist

- [ ] CORS_ORIGINS environment variable is set correctly
- [ ] No typos in the frontend URL
- [ ] Clicked "Save Changes" in Render
- [ ] Manually triggered redeploy
- [ ] Waited for deployment to complete
- [ ] Checked logs for errors
- [ ] Tested with curl or browser
- [ ] CORS error is gone
- [ ] Create search works!

---

**After following these steps, your create search functionality should work!**