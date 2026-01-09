import path from 'path';
import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');

  // Default to 0.0.0.0 for external access support
  const host = process.env.VITE_HOST || '0.0.0.0';
  const port = Number(process.env.VITE_PORT) || 5173;

  // Explicit backend URL or default to 127.0.0.1 to avoid localhost issues
  const backendUrl = process.env.VITE_BACKEND_URL || 'http://127.0.0.1:8000';

  console.log(`[Vite] Mode: ${mode}`);
  console.log(`[Vite] Frontend: http://${host}:${port}`);
  console.log(`[Vite] Backend: ${backendUrl}`);

  return {
    plugins: [react()],
    server: {
      host: host,
      port: port,
      proxy: {
        '/api': {
          target: backendUrl,
          changeOrigin: true,
          secure: false,
          // Optional: Add rewrite if needed, but per strict proxying:
          // rewrite: (path) => path.replace(/^\/api/, ''), 
        }
      }
    },
    resolve: {
      alias: {
        "@": path.resolve(__dirname, "./src"),
      },
    },
  };
});
