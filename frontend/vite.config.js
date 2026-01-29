import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "")
  const allowedHosts = env.VITE_ALLOWED_HOSTS
    ? env.VITE_ALLOWED_HOSTS.split(",").map(h => h.trim())
    : "all"

  return {
    plugins: [react()],
    resolve: {
      alias: {
        "@": path.resolve(__dirname, "src"),
      },
    },
    server: {
      // host: true,
      allowedHosts: allowedHosts // Добавил домен фронта
    }
  }
})
