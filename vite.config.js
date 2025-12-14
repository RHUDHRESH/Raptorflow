import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// Force restart
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  // Optimize for OneDrive folders - reduce file watching overhead
  optimizeDeps: {
    include: ['react', 'react-dom', 'react-router-dom', '@supabase/supabase-js', 'framer-motion'],
    exclude: ['@dnd-kit/core', '@dnd-kit/sortable'],
  },
  server: {
    port: 3000,
    // Reduce file system polling for OneDrive
    watch: {
      usePolling: false,
      interval: 1000,
      ignored: ['**/node_modules/**', '**/.git/**', '**/dist/**'],
    },
    hmr: {
      overlay: true,
    },
    proxy: {
      '/api': {
        target: 'http://localhost:3001',
        changeOrigin: true,
        secure: false
      }
    },
    overlay: {
      warnings: false,
      errors: true
    }
  },
  build: {
    target: 'es2020',
    outDir: 'dist',
    emptyOutDir: true,
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true
      }
    },
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor-react': ['react', 'react-dom', 'react-router-dom'],
          'vendor-ui': ['lucide-react', 'framer-motion'],
          'vendor-supabase': ['@supabase/supabase-js'],
          'vendor-utils': ['uuid', 'clsx', 'tailwind-merge', 'dompurify']
        }
      },
      onwarn(warning, warn) {
        if (warning.code === 'UNUSED_EXTERNAL_IMPORT') return
        warn(warning)
      }
    },
    sourcemap: false,
    reportCompressedSize: false
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.js',
    css: true,
  },
  // Don't override NODE_ENV - let Vite handle it automatically
  // define: {
  //   'process.env.NODE_ENV': JSON.stringify(process.env.NODE_ENV)
  // }
})
