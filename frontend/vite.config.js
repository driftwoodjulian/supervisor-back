import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  return {
    plugins: [react()],
    server: {
      host: env.HOST || '0.0.0.0',
      port: parseInt(env.PORT) || 8081,
      proxy: {
        '/api': {
          target: process.env.VITE_API_URL || 'http://127.0.0.1:6001',
          changeOrigin: true,
          secure: false,
        }
      }
    }
  }
})
