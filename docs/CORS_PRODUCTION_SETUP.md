# CORS Configuration for Production Deployment

## Overview

This document explains the CORS (Cross-Origin Resource Sharing) configuration updates made to support production deployment of the Product Search Agent.

## Changes Made

### 1. Updated `backend/app/main.py`

**Before:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React development server
        "http://localhost:5173",  # Vite development server
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        # In production, replace with your actual frontend URL
        # "https://yourdomain.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**After:**
```python
from app.config import settings

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)
```

### 2. Updated `backend/.env.example`

Added production examples and better documentation:

```bash
# ============================================================================
# CORS Settings
# ============================================================================
# Comma-separated list of allowed origins
# Development: Use localhost URLs
# Production: Add your deployed frontend URL
# Example: CORS_ORIGINS=http://localhost:5173,https://your-frontend.onrender.com
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=*
CORS_ALLOW_HEADERS=*
```

## Configuration Details

### CORS Settings in `config.py`

The CORS configuration is already defined in `backend/app/config.py` (lines 228-245):

```python
cors_origins: List[str] = Field(
    default=["http://localhost:3000", "http://localhost:5173"],
    description="Allowed CORS origins"
)
cors_allow_credentials: bool = Field(
    default=True,
    description="Allow credentials in CORS requests"
)
cors_allow_methods: List[str] = Field(
    default=["*"],
    description="Allowed HTTP methods"
)
cors_allow_headers: List[str] = Field(
    default=["*"],
    description="Allowed HTTP headers"
)
```

### Environment Variable Support

The `cors_origins` field includes a validator that parses comma-separated strings:

```python
@field_validator('cors_origins', mode='before')
@classmethod
def parse_cors_origins(cls, v):
    """Parse CORS origins from string or list."""
    if isinstance(v, str):
        return [origin.strip() for origin in v.split(',')]
    return v
```

This allows you to set CORS origins via environment variable:

```bash
CORS_ORIGINS="http://localhost:5173,https://your-frontend.onrender.com,https://www.yourdomain.com"
```

## Usage

### Development

For local development, the default settings work out of the box:

```bash
# No need to set CORS_ORIGINS in .env for development
# Defaults to localhost:3000 and localhost:5173
```

### Production

When deploying to production, update your `.env` file or set environment variables:

**Option 1: Using .env file**
```bash
# backend/.env
CORS_ORIGINS=https://your-frontend.onrender.com,https://www.yourdomain.com
```

**Option 2: Using Render.com Environment Variables**
1. Go to your backend service on Render.com
2. Navigate to "Environment" tab
3. Add environment variable:
   - Key: `CORS_ORIGINS`
   - Value: `https://your-frontend.onrender.com,https://www.yourdomain.com`

### Multiple Environments

You can support multiple environments simultaneously:

```bash
CORS_ORIGINS=http://localhost:5173,https://staging.yourdomain.com,https://www.yourdomain.com
```

This allows:
- Local development (localhost:5173)
- Staging environment (staging.yourdomain.com)
- Production environment (www.yourdomain.com)

## Security Best Practices

### ✅ DO:

1. **Specify exact origins in production:**
   ```bash
   CORS_ORIGINS=https://www.yourdomain.com
   ```

2. **Use HTTPS in production:**
   ```bash
   CORS_ORIGINS=https://your-frontend.onrender.com
   ```

3. **Include all necessary subdomains:**
   ```bash
   CORS_ORIGINS=https://app.yourdomain.com,https://www.yourdomain.com
   ```

### ❌ DON'T:

1. **Don't use wildcards in production:**
   ```bash
   # BAD - allows any origin
   CORS_ORIGINS=*
   ```

2. **Don't include HTTP in production:**
   ```bash
   # BAD - insecure
   CORS_ORIGINS=http://yourdomain.com
   ```

3. **Don't leave development URLs in production:**
   ```bash
   # BAD - security risk
   CORS_ORIGINS=http://localhost:5173,https://yourdomain.com
   ```

## Testing CORS Configuration

### Test 1: Check Current Settings

```bash
# Start the backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

# In another terminal, check the CORS headers
curl -H "Origin: http://localhost:5173" \
     -H "Access-Control-Request-Method: GET" \
     -X OPTIONS \
     http://localhost:8000/api/health -v
```

Look for these headers in the response:
```
Access-Control-Allow-Origin: http://localhost:5173
Access-Control-Allow-Credentials: true
Access-Control-Allow-Methods: *
Access-Control-Allow-Headers: *
```

### Test 2: Test from Frontend

```javascript
// In your frontend code
fetch('http://localhost:8000/api/health')
  .then(response => response.json())
  .then(data => console.log('CORS working:', data))
  .catch(error => console.error('CORS error:', error));
```

If CORS is configured correctly, you should see the response. If not, you'll see a CORS error in the browser console.

### Test 3: Test Production URLs

Before deploying, test with your production URLs:

```bash
# Update .env temporarily
CORS_ORIGINS=https://your-frontend.onrender.com

# Restart the server
# Test from your deployed frontend
```

## Troubleshooting

### Issue: CORS Error in Browser Console

**Error:**
```
Access to fetch at 'https://api.yourdomain.com/api/health' from origin 
'https://www.yourdomain.com' has been blocked by CORS policy
```

**Solution:**
1. Check that your frontend URL is in `CORS_ORIGINS`
2. Ensure you're using the exact URL (including https://)
3. Restart the backend after changing CORS settings

### Issue: Credentials Not Working

**Error:**
```
The value of the 'Access-Control-Allow-Credentials' header in the response 
is '' which must be 'true' when the request's credentials mode is 'include'
```

**Solution:**
Ensure `CORS_ALLOW_CREDENTIALS=true` in your environment variables.

### Issue: Preflight Request Failing

**Error:**
```
Response to preflight request doesn't pass access control check
```

**Solution:**
1. Check that `CORS_ALLOW_METHODS` includes the method you're using
2. Check that `CORS_ALLOW_HEADERS` includes the headers you're sending
3. Default `*` should work for most cases

## Deployment Checklist

- [ ] Update `CORS_ORIGINS` in production environment variables
- [ ] Use HTTPS URLs only
- [ ] Remove localhost URLs from production
- [ ] Test CORS from deployed frontend
- [ ] Verify credentials are working (if needed)
- [ ] Check browser console for CORS errors
- [ ] Test all API endpoints from frontend

## Related Files

- `backend/app/main.py` - CORS middleware configuration
- `backend/app/config.py` - CORS settings definition
- `backend/.env.example` - Example environment variables
- `docs/DAY_28-29_CLOUD_DEPLOYMENT_DETAILED_PLAN.md` - Full deployment guide

## Next Steps

After configuring CORS:
1. Proceed to Step 1.4: Create Frontend Build Configuration
2. Update Frontend API URLs (Step 1.5)
3. Deploy to Render.com (Sub-Tasks 3-4)

## References

- [MDN CORS Documentation](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
- [FastAPI CORS Middleware](https://fastapi.tiangolo.com/tutorial/cors/)
- [Render.com Environment Variables](https://render.com/docs/environment-variables)