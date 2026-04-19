import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  
  // Build configuration for production
  build: {
    // Output directory for production build
    outDir: 'dist',
    
    // Generate sourcemaps for debugging (disable in production for security)
    sourcemap: false,
    
    // Minify the output
    minify: 'esbuild',
    
    // Target modern browsers
    target: 'esnext',
    
    // Chunk size warnings
    chunkSizeWarningLimit: 1000,
    
    // Rollup options
    rollupOptions: {
      output: {
        // Manual chunks for better caching
        manualChunks(id) {
          if (id.includes('node_modules')) {
            if (id.includes('react') || id.includes('react-dom') || id.includes('react-router-dom')) {
              return 'react-vendor';
            }
            if (id.includes('@tanstack/react-query')) {
              return 'query-vendor';
            }
            // All other node_modules go into vendor chunk
            return 'vendor';
          }
        },
      },
    },
  },
  
  // Server configuration for development
  server: {
    port: 5173,
    host: true, // Listen on all addresses
    strictPort: false, // Try next port if 5173 is busy
    
    // Proxy API requests to backend during development
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
  
  // Preview server configuration (for testing production build locally)
  preview: {
    port: 4173,
    host: true,
    strictPort: false,
  },
})
