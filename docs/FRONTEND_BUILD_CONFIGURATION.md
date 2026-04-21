# Frontend Build Configuration

## Overview

This document explains the Vite build configuration for production deployment of the Product Search Agent frontend.

## Configuration File: `frontend/vite.config.ts`

### Complete Configuration

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  
  // Build configuration for production
  build: {
    outDir: 'dist',
    sourcemap: false,
    minify: 'esbuild',
    target: 'esnext',
    chunkSizeWarningLimit: 1000,
    
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules')) {
            if (id.includes('react') || id.includes('react-dom') || id.includes('react-router-dom')) {
              return 'react-vendor';
            }
            if (id.includes('@tanstack/react-query')) {
              return 'query-vendor';
            }
            return 'vendor';
          }
        },
      },
    },
  },
  
  server: {
    port: 5173,
    host: true,
    strictPort: false,
    
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true,
      },
    },
  },
  
  preview: {
    port: 4173,
    host: true,
    strictPort: false,
  },
})
```

## Configuration Sections Explained

### 1. Build Configuration

#### `outDir: 'dist'`
- **Purpose:** Specifies the output directory for production build
- **Default:** `dist`
- **Usage:** All compiled files will be in `frontend/dist/`

#### `sourcemap: false`
- **Purpose:** Disables source map generation in production
- **Security:** Prevents exposing source code in production
- **Development:** Set to `true` if you need to debug production builds
- **File Size:** Reduces bundle size significantly

#### `minify: 'esbuild'`
- **Purpose:** Minifies JavaScript and CSS
- **Options:** `'esbuild'` (fast), `'terser'` (smaller), `false` (no minification)
- **Performance:** esbuild is much faster than terser
- **Result:** Reduces bundle size by ~70%

#### `target: 'esnext'`
- **Purpose:** Target modern browsers with latest JavaScript features
- **Alternative:** `'es2015'` for older browser support
- **Trade-off:** Smaller bundles vs. broader compatibility

#### `chunkSizeWarningLimit: 1000`
- **Purpose:** Warn if chunk size exceeds 1000 KB
- **Default:** 500 KB
- **Reason:** React apps tend to be larger, adjusted threshold

### 2. Manual Chunks (Code Splitting)

```typescript
manualChunks(id) {
  if (id.includes('node_modules')) {
    if (id.includes('react') || id.includes('react-dom') || id.includes('react-router-dom')) {
      return 'react-vendor';
    }
    if (id.includes('@tanstack/react-query')) {
      return 'query-vendor';
    }
    return 'vendor';
  }
}
```

**Benefits:**
- **Better Caching:** Vendor code changes less frequently
- **Parallel Loading:** Browser can load chunks simultaneously
- **Faster Updates:** Only changed chunks need to be re-downloaded

**Output Files:**
```
dist/
├── index.html
├── assets/
│   ├── index-[hash].js          # Your app code
│   ├── react-vendor-[hash].js   # React libraries
│   ├── query-vendor-[hash].js   # React Query
│   └── vendor-[hash].js         # Other dependencies
```

### 3. Development Server Configuration

#### `port: 5173`
- **Purpose:** Development server port
- **Default:** 5173 (Vite default)
- **Access:** http://localhost:5173

#### `host: true`
- **Purpose:** Listen on all network interfaces (0.0.0.0)
- **Benefit:** Access from other devices on network
- **Usage:** http://192.168.1.x:5173 from phone/tablet

#### `strictPort: false`
- **Purpose:** Try next available port if 5173 is busy
- **Alternative:** Set to `true` to fail if port is taken

#### Proxy Configuration

```typescript
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true,
  },
  '/ws': {
    target: 'ws://localhost:8000',
    ws: true,
  },
}
```

**Purpose:** Forward API and WebSocket requests to backend during development

**How it works:**
- Frontend: `http://localhost:5173/api/health`
- Proxied to: `http://localhost:8000/api/health`
- No CORS issues in development!

**WebSocket Support:**
- Frontend: `ws://localhost:5173/ws/notifications`
- Proxied to: `ws://localhost:8000/ws/notifications`

### 4. Preview Server Configuration

```typescript
preview: {
  port: 4173,
  host: true,
  strictPort: false,
}
```

**Purpose:** Test production build locally before deploying

**Usage:**
```bash
npm run build
npm run preview
# Opens http://localhost:4173
```

## Build Commands

### Development

```bash
# Start development server with hot reload
npm run dev

# Access at http://localhost:5173
```

### Production Build

```bash
# Build for production
npm run build

# Output: frontend/dist/
```

### Preview Production Build

```bash
# Build and preview
npm run build
npm run preview

# Access at http://localhost:4173
```

### Lint Code

```bash
# Run ESLint
npm run lint
```

## Build Output Analysis

### Before Optimization
```
dist/assets/index-abc123.js    2.5 MB
```

### After Optimization (with code splitting)
```
dist/assets/index-abc123.js           150 KB  (your app code)
dist/assets/react-vendor-def456.js    800 KB  (React libraries)
dist/assets/query-vendor-ghi789.js    100 KB  (React Query)
dist/assets/vendor-jkl012.js          200 KB  (other deps)
```

**Benefits:**
- Initial load: Only loads what's needed
- Caching: Vendor chunks cached separately
- Updates: Only app code changes, vendors stay cached

## Environment-Specific Builds

### Development Build
```bash
# Uses .env.development
npm run dev
```

**Characteristics:**
- Source maps enabled
- Hot module replacement
- Detailed error messages
- Larger bundle size
- Faster build time

### Production Build
```bash
# Uses .env.production
npm run build
```

**Characteristics:**
- Source maps disabled
- Code minified
- Tree shaking applied
- Smaller bundle size
- Slower build time (more optimization)

## Performance Optimizations

### 1. Code Splitting
✅ Implemented via `manualChunks`
- Separates vendor code from app code
- Better caching strategy

### 2. Minification
✅ Enabled via `minify: 'esbuild'`
- Reduces bundle size by ~70%
- Removes whitespace, comments, shortens variable names

### 3. Tree Shaking
✅ Automatic with ES modules
- Removes unused code
- Only includes what you import

### 4. Asset Optimization
✅ Automatic by Vite
- Images optimized
- CSS minified
- Fonts optimized

### 5. Lazy Loading (Future Enhancement)
```typescript
// Example: Lazy load pages
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Matches = lazy(() => import('./pages/Matches'));
const Settings = lazy(() => import('./pages/Settings'));
```

## Deployment Considerations

### Static Site Hosting (Render.com, Netlify, Vercel)

**Build Command:**
```bash
npm run build
```

**Publish Directory:**
```
dist
```

**Environment Variables:**
- Set in hosting platform dashboard
- `VITE_API_URL` - Backend API URL
- `VITE_WS_URL` - WebSocket URL

### SPA Routing Configuration

For React Router to work with direct URLs, configure redirects:

**Render.com:** Create `render.yaml`
```yaml
services:
  - type: web
    name: product-search-frontend
    env: static
    buildCommand: npm install && npm run build
    staticPublishPath: ./dist
    routes:
      - type: rewrite
        source: /*
        destination: /index.html
```

**Netlify:** Create `_redirects` in `public/`
```
/*    /index.html   200
```

**Vercel:** Create `vercel.json`
```json
{
  "rewrites": [
    { "source": "/(.*)", "destination": "/index.html" }
  ]
}
```

## Testing the Build

### 1. Build Locally
```bash
cd frontend
npm run build
```

### 2. Check Output
```bash
ls -lh dist/assets/
# Should see minified JS and CSS files with hashes
```

### 3. Preview Locally
```bash
npm run preview
# Open http://localhost:4173
```

### 4. Test All Features
- [ ] Navigation works
- [ ] API calls work (update API_URL in .env.production)
- [ ] WebSocket connects
- [ ] Forms submit correctly
- [ ] Images load
- [ ] Styling looks correct

## Troubleshooting

### Issue: Build Fails with TypeScript Errors

**Solution:**
```bash
# Check TypeScript configuration
npx tsc --noEmit

# Fix errors before building
```

### Issue: Large Bundle Size

**Check bundle size:**
```bash
npm run build
# Look at the output sizes
```

**Solutions:**
1. Enable code splitting (already done)
2. Lazy load routes
3. Remove unused dependencies
4. Use lighter alternatives

### Issue: Assets Not Loading in Production

**Cause:** Incorrect base path

**Solution:** Add `base` to vite.config.ts
```typescript
export default defineConfig({
  base: '/', // or '/your-subdirectory/'
  // ... rest of config
})
```

### Issue: Environment Variables Not Working

**Check:**
1. Variables must start with `VITE_`
2. Restart dev server after changing .env
3. Use `import.meta.env.VITE_API_URL` not `process.env`

## Build Performance

### Current Build Time
- Development: ~2-3 seconds (with HMR)
- Production: ~15-20 seconds

### Optimization Tips
1. Use `npm ci` instead of `npm install` in CI/CD
2. Cache `node_modules` in CI/CD
3. Use `--mode production` explicitly
4. Consider using `vite-plugin-compression` for gzip

## Next Steps

After configuring the build:
1. ✅ Build configuration complete
2. ⏭️ Update Frontend API URLs (Step 1.5)
3. ⏭️ Test production build locally
4. ⏭️ Deploy to Render.com (Sub-Task 4)

## Related Files

- `frontend/vite.config.ts` - Build configuration
- `frontend/package.json` - Build scripts
- `frontend/.env.development` - Development environment variables
- `frontend/.env.production` - Production environment variables
- `docs/DAY_28-29_CLOUD_DEPLOYMENT_DETAILED_PLAN.md` - Full deployment guide

## References

- [Vite Build Configuration](https://vitejs.dev/config/build-options.html)
- [Vite Server Options](https://vitejs.dev/config/server-options.html)
- [Rollup Manual Chunks](https://rollupjs.org/configuration-options/#output-manualchunks)
- [Code Splitting Best Practices](https://web.dev/code-splitting-suspense/)