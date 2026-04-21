# WebSocket Connection Fix - Deployment Instructions

## Problems Identified

The create search functionality was failing due to multiple issues:

### 1. WebSocket Connection Issues
- Rapid WebSocket connections and disconnections
- "Client disconnected" errors flooding the logs
- Frontend unable to maintain stable WebSocket connection

### 2. Configuration Parsing Error
- `cors_origins` environment variable causing JSON parsing error
- Pydantic trying to parse empty string as JSON
- Backend deployment failing on Render

## Root Causes

1. **Backend Timeout Too Short**: 30-second timeout was too aggressive, causing premature disconnections
2. **Missing Exception Handling**: WebSocket endpoint didn't properly handle all exception types
3. **Poor Logging**: Difficult to debug which client was having issues
4. **Frontend Ping Interval**: 30-second ping interval was at the edge of the 30-second backend timeout
5. **CORS Configuration Type**: `cors_origins` defined as `List[str]` causing Pydantic to attempt JSON parsing

## Changes Made

### Backend Changes

#### 1. WebSocket Endpoint (`backend/app/api/routes/websocket.py`)
1. **Increased Timeout**: Changed from 30 to 60 seconds
2. **Added Client ID Tracking**: Each connection now has a unique ID for better logging
3. **Improved Exception Handling**: Added proper try/finally blocks and exception logging
4. **Better Logging**: Added INFO level logs for connection lifecycle
5. **Connection Confirmation**: Send initial message when client connects
6. **Graceful Cleanup**: Always clean up connections in finally block

#### 2. Configuration (`backend/app/config.py`)
1. **Fixed CORS Type**: Changed `cors_origins` from `List[str]` to `str | List[str]`
2. **Updated Default**: Changed default from list to comma-separated string
3. **Enhanced Validator**: Added two-stage validation (before/after) to handle both string and list inputs
4. **Better Error Handling**: Prevents JSON parsing errors when environment variable is empty

### Frontend Changes (`frontend/src/hooks/useWebSocket.ts`)

1. **Adjusted Ping Interval**: Changed from 30 to 45 seconds (safely under 60-second backend timeout)

## Deployment Steps

### Step 1: Deploy Backend Changes

```bash
# Navigate to project root
cd /path/to/product-search-agent

# Commit all backend changes
git add backend/app/api/routes/websocket.py
git add backend/app/config.py
git commit -m "Fix WebSocket stability and CORS configuration parsing"

# Push to your repository
git push origin main
```

**On Render.com:**
- The backend will automatically redeploy when you push to GitHub
- Monitor the logs during deployment
- Look for: "Client {id} connected successfully" messages

### Step 2: Deploy Frontend Changes

```bash
# Navigate to frontend directory
cd frontend

# Commit changes
git add src/hooks/useWebSocket.ts
git commit -m "Adjust WebSocket ping interval for better stability"

# Push to your repository
git push origin main
```

**On Render.com:**
- The frontend will automatically rebuild and redeploy
- Wait for build to complete (usually 2-3 minutes)

### Step 3: Verify the Fix

1. **Open your deployed application** in a browser
2. **Open browser DevTools** (F12) → Console tab
3. **Look for WebSocket messages**:
   - Should see: "✅ WebSocket connected"
   - Should NOT see rapid reconnection attempts
4. **Test Create Search**:
   - Click "Create New Search"
   - Fill in the form
   - Submit
   - Verify search appears in the list

### Step 4: Monitor Backend Logs

**On Render.com Backend Service:**

1. Go to your backend service
2. Click "Logs" tab
3. Look for these patterns:

**Good Signs:**
```
Client {id} attempting to connect
Client {id} connected successfully
Client {id} ping/pong
Sent heartbeat to client {id}
```

**Bad Signs (should NOT see):**
```
Client disconnected (repeated rapidly)
WebSocket error for client {id}
```

## Testing Checklist

- [ ] Backend deployed successfully
- [ ] Frontend deployed successfully
- [ ] WebSocket connects without errors
- [ ] No rapid reconnection loops in logs
- [ ] Can create new search request
- [ ] Search appears in dashboard list
- [ ] Real-time notifications work (if applicable)
- [ ] Connection stays stable for 5+ minutes

## Rollback Plan

If issues persist:

1. **Check Environment Variables**:
   - Verify `VITE_WS_URL` in frontend
   - Verify `ALLOWED_ORIGINS` in backend

2. **Check CORS Settings**:
   - Ensure frontend URL is in backend CORS origins

3. **Revert Changes** (if needed):
```bash
# Backend
cd backend
git revert HEAD
git push origin main

# Frontend
cd frontend
git revert HEAD
git push origin main
```
## Common Configuration Issues

### Issue: "error parsing value for field 'cors_origins'"

**Cause**: Environment variable is empty or Pydantic trying to parse as JSON

**Solution**: Set `CORS_ORIGINS` in Render environment variables as comma-separated string:
```
CORS_ORIGINS=https://your-frontend.onrender.com,http://localhost:5173
```

**Note**: Do NOT use JSON format. Use simple comma-separated values.


## Additional Debugging

If create search still doesn't work after WebSocket fix:

### Check Backend API Directly

```bash
# Test health endpoint
curl https://your-backend.onrender.com/api/health

# Test create search (replace with your backend URL)
curl -X POST https://your-backend.onrender.com/api/search-requests \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "Test Product",
    "product_description": "Testing the API directly",
    "budget": 100,
    "search_craigslist": true,
    "search_ebay": true,
    "search_facebook": true
  }'
```

### Check Frontend API Configuration

1. Open browser DevTools → Console
2. Look for API request logs
3. Verify API URL is correct
4. Check for CORS errors

### Common Issues

**Issue**: "Failed to fetch" error
- **Solution**: Check backend is running and URL is correct

**Issue**: CORS error
- **Solution**: Add frontend URL to backend ALLOWED_ORIGINS

**Issue**: 422 Validation Error
- **Solution**: Check request payload matches backend schema

## Success Criteria

The fix is successful when:
1. ✅ WebSocket connection is stable (no rapid reconnects)
2. ✅ Create search form submits successfully
3. ✅ New search appears in dashboard
4. ✅ Backend logs show clean connection lifecycle
5. ✅ No error messages in browser console

## Support

If issues persist after following these steps:
1. Check Render.com service logs for both backend and frontend
2. Review browser console for JavaScript errors
3. Verify all environment variables are set correctly
4. Ensure database is accessible (if using PostgreSQL)

---

**Last Updated**: 2026-04-20
**Version**: 1.0