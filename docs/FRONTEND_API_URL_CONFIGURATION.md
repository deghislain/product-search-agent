# Frontend API URL Configuration

## Overview

This document explains how the frontend connects to the backend API and WebSocket server using environment-based configuration.

## Configuration Files

### 1. Environment Variables

#### `frontend/.env.development`
Used during local development (`npm run dev`):

```bash
# API URL for local development
VITE_API_URL=http://localhost:8000

# WebSocket URL for local development
VITE_WS_URL=ws://localhost:8000/ws/notifications
```

#### `frontend/.env.production`
Used for production builds (`npm run build`):

```bash
# API URL for production (HTTPS required)
VITE_API_URL=https://your-backend.onrender.com

# WebSocket URL for production (WSS required)
VITE_WS_URL=wss://your-backend.onrender.com/ws/notifications
```

### 2. API Client Configuration

#### `frontend/src/services/api.ts`

The API client uses environment variables to determine the backend URL:

```typescript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
    timeout: 30000, // 30 second timeout
});
```

**Key Features:**
- ✅ Environment-based URL configuration
- ✅ 30-second timeout for requests
- ✅ Request/response interceptors for logging
- ✅ Enhanced error handling
- ✅ Development mode logging
- ✅ Ready for authentication tokens

## How It Works

### Development Mode

When you run `npm run dev`:

1. Vite loads `.env.development`
2. `VITE_API_URL` is set to `http://localhost:8000`
3. All API calls go to local backend
4. Vite proxy forwards `/api/*` and `/ws/*` requests

**Example:**
```typescript
// Frontend makes request
fetch('/api/health')

// Vite proxy forwards to
http://localhost:8000/api/health
```

### Production Mode

When you run `npm run build`:

1. Vite loads `.env.production`
2. `VITE_API_URL` is set to your production backend URL
3. All API calls go to production backend
4. No proxy needed (direct connection)

**Example:**
```typescript
// Frontend makes request
fetch('/api/health')

// Goes directly to
https://your-backend.onrender.com/api/health
```

## Environment Variable Naming

### ✅ Correct: `VITE_` Prefix

```bash
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws/notifications
```

Vite only exposes environment variables that start with `VITE_` to the client-side code.

### ❌ Incorrect: No Prefix

```bash
API_URL=http://localhost:8000  # Won't work!
WS_URL=ws://localhost:8000     # Won't work!
```

These won't be accessible in the frontend code.

## Accessing Environment Variables

### In TypeScript/JavaScript

```typescript
// Correct way
const apiUrl = import.meta.env.VITE_API_URL;
const wsUrl = import.meta.env.VITE_WS_URL;
const mode = import.meta.env.MODE; // 'development' or 'production'
const isDev = import.meta.env.DEV; // boolean
const isProd = import.meta.env.PROD; // boolean

// Incorrect way (Node.js style - doesn't work in Vite)
const apiUrl = process.env.VITE_API_URL; // ❌ Won't work!
```

### Built-in Environment Variables

Vite provides these automatically:

- `import.meta.env.MODE` - Current mode ('development' or 'production')
- `import.meta.env.DEV` - Boolean, true in development
- `import.meta.env.PROD` - Boolean, true in production
- `import.meta.env.BASE_URL` - Base URL of the app

## API Client Features

### 1. Request Interceptor

Logs all requests in development mode:

```typescript
apiClient.interceptors.request.use((config) => {
    if (import.meta.env.DEV) {
        console.log('API Request:', {
            method: config.method?.toUpperCase(),
            url: config.url,
            fullURL: `${config.baseURL}${config.url}`,
        });
    }
    return config;
});
```

**Output:**
```
API Request: {
  method: 'GET',
  url: '/api/health',
  fullURL: 'http://localhost:8000/api/health'
}
```

### 2. Response Interceptor

Logs responses and handles errors:

```typescript
apiClient.interceptors.response.use(
    (response) => {
        if (import.meta.env.DEV) {
            console.log('API Response:', {
                status: response.status,
                url: response.config.url,
                data: response.data,
            });
        }
        return response;
    },
    (error) => {
        // Enhanced error logging
        console.error('API Error:', error);
        return Promise.reject(error);
    }
);
```

### 3. Timeout Configuration

```typescript
const apiClient = axios.create({
    timeout: 30000, // 30 seconds
});
```

Prevents requests from hanging indefinitely.

### 4. Future: Authentication Support

Ready to add authentication tokens:

```typescript
apiClient.interceptors.request.use((config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});
```

## Deployment Configuration

### Step 1: Deploy Backend

First, deploy your backend to Render.com (or other hosting):

```bash
# Backend will be available at:
https://product-search-backend.onrender.com
```

### Step 2: Update Frontend Environment Variables

Update `frontend/.env.production`:

```bash
# Replace with your actual backend URL
VITE_API_URL=https://product-search-backend.onrender.com
VITE_WS_URL=wss://product-search-backend.onrender.com/ws/notifications
```

### Step 3: Build Frontend

```bash
cd frontend
npm run build
```

This creates a production build in `frontend/dist/` with the correct API URLs baked in.

### Step 4: Deploy Frontend

Deploy the `dist/` folder to Render.com, Netlify, or Vercel.

## Testing API Configuration

### Test 1: Check Environment Variables

Add this to any component temporarily:

```typescript
console.log('API URL:', import.meta.env.VITE_API_URL);
console.log('WS URL:', import.meta.env.VITE_WS_URL);
console.log('Mode:', import.meta.env.MODE);
```

### Test 2: Test API Connection

```typescript
import apiClient from './services/api';

// Test health endpoint
apiClient.get('/api/health')
    .then(response => console.log('API Connected:', response.data))
    .catch(error => console.error('API Error:', error));
```

### Test 3: Check Network Tab

1. Open browser DevTools (F12)
2. Go to Network tab
3. Make an API request
4. Check the request URL

**Development:**
```
Request URL: http://localhost:8000/api/health
```

**Production:**
```
Request URL: https://your-backend.onrender.com/api/health
```

## Common Issues & Solutions

### Issue 1: API URL Not Updating

**Problem:** Changed `.env.production` but API still uses old URL

**Solution:**
1. Stop the dev server
2. Delete `node_modules/.vite` cache
3. Restart: `npm run dev`

Or for production:
```bash
rm -rf dist
npm run build
```

### Issue 2: CORS Errors in Production

**Problem:**
```
Access to fetch at 'https://backend.com/api/health' from origin 
'https://frontend.com' has been blocked by CORS policy
```

**Solution:**
Update backend CORS settings to include frontend URL:

```bash
# In backend .env
CORS_ORIGINS=https://your-frontend.onrender.com
```

### Issue 3: WebSocket Connection Failing

**Problem:** WebSocket shows "Connection failed" in console

**Solutions:**

1. **Check URL protocol:**
   - Development: `ws://` (not `wss://`)
   - Production: `wss://` (not `ws://`)

2. **Check backend WebSocket endpoint:**
   ```bash
   # Should be accessible at
   ws://localhost:8000/ws/notifications  # Dev
   wss://backend.com/ws/notifications    # Prod
   ```

3. **Check CORS for WebSocket:**
   Backend must allow WebSocket connections from frontend origin.

### Issue 4: Environment Variables Not Defined

**Problem:** `import.meta.env.VITE_API_URL` is `undefined`

**Solutions:**

1. **Check variable name:**
   - Must start with `VITE_`
   - Use exact name: `VITE_API_URL`

2. **Check file location:**
   - Must be in `frontend/` directory
   - Named exactly `.env.development` or `.env.production`

3. **Restart dev server:**
   ```bash
   # Stop server (Ctrl+C)
   npm run dev
   ```

### Issue 5: Mixed Content Error

**Problem:**
```
Mixed Content: The page at 'https://frontend.com' was loaded over HTTPS, 
but requested an insecure resource 'http://backend.com/api/health'
```

**Solution:**
Use HTTPS for API URL in production:

```bash
# ❌ Wrong
VITE_API_URL=http://backend.com

# ✅ Correct
VITE_API_URL=https://backend.com
```

## Best Practices

### ✅ DO:

1. **Use environment variables for all URLs:**
   ```typescript
   const apiUrl = import.meta.env.VITE_API_URL;
   ```

2. **Provide fallback values:**
   ```typescript
   const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
   ```

3. **Use HTTPS in production:**
   ```bash
   VITE_API_URL=https://backend.com
   ```

4. **Log configuration in development:**
   ```typescript
   if (import.meta.env.DEV) {
       console.log('API URL:', import.meta.env.VITE_API_URL);
   }
   ```

5. **Test both environments:**
   - Test locally with `npm run dev`
   - Test production build with `npm run build && npm run preview`

### ❌ DON'T:

1. **Don't hardcode URLs:**
   ```typescript
   // ❌ Bad
   const apiUrl = 'http://localhost:8000';
   ```

2. **Don't commit `.env` files:**
   ```bash
   # Add to .gitignore
   .env
   .env.local
   ```

3. **Don't use HTTP in production:**
   ```bash
   # ❌ Insecure
   VITE_API_URL=http://backend.com
   ```

4. **Don't forget the `VITE_` prefix:**
   ```bash
   # ❌ Won't work
   API_URL=http://localhost:8000
   ```

## Render.com Deployment

### Backend Environment Variables

Set in Render.com dashboard for backend service:

```bash
CORS_ORIGINS=https://your-frontend.onrender.com
```

### Frontend Environment Variables

Set in Render.com dashboard for frontend service:

```bash
VITE_API_URL=https://your-backend.onrender.com
VITE_WS_URL=wss://your-backend.onrender.com/ws/notifications
```

**Note:** Render.com will automatically use these during build.

## Multiple Environments

You can create additional environment files:

```bash
.env                    # Loaded in all cases
.env.local              # Loaded in all cases, ignored by git
.env.development        # Loaded in development
.env.development.local  # Loaded in development, ignored by git
.env.production         # Loaded in production
.env.production.local   # Loaded in production, ignored by git
```

**Priority:** `.local` files have higher priority than non-local files.

## Summary

✅ **Development:**
- Uses `.env.development`
- API: `http://localhost:8000`
- WebSocket: `ws://localhost:8000/ws/notifications`
- Vite proxy handles requests

✅ **Production:**
- Uses `.env.production`
- API: `https://your-backend.onrender.com`
- WebSocket: `wss://your-backend.onrender.com/ws/notifications`
- Direct connection to backend

✅ **Configuration:**
- All URLs use environment variables
- Enhanced logging in development
- 30-second timeout
- Ready for authentication

## Next Steps

After configuring API URLs:
1. ✅ API URLs configured
2. ⏭️ Create .gitignore files (Step 1.6)
3. ⏭️ Test production build locally
4. ⏭️ Deploy to Render.com

## Related Files

- `frontend/src/services/api.ts` - API client configuration
- `frontend/.env.development` - Development environment variables
- `frontend/.env.production` - Production environment variables
- `frontend/vite.config.ts` - Vite configuration with proxy
- `docs/CORS_PRODUCTION_SETUP.md` - Backend CORS configuration
- `docs/DAY_28-29_CLOUD_DEPLOYMENT_DETAILED_PLAN.md` - Full deployment guide

## References

- [Vite Environment Variables](https://vitejs.dev/guide/env-and-mode.html)
- [Axios Configuration](https://axios-http.com/docs/config_defaults)
- [Render.com Environment Variables](https://render.com/docs/environment-variables)