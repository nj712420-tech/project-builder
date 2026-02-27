import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    allowedHosts: true,
    // This part is the magic bridge
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000', // Forward to your local Python backend
        changeOrigin: true,
        secure: false,
      }
    }
  }
})
