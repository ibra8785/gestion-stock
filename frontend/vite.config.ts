
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [react()],

  server: {
    proxy: {
      // Transmet les requêtes de l'API à Django.
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },

      // Transmet les pages d'authentification Django.
      '/accounts': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
})
