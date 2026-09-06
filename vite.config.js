import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// `base` controls the public path assets are served from:
//   - Vercel / local dev  -> "/" (default)
//   - GitHub Pages        -> set VITE_BASE=/study-scheduler/ at build time
export default defineConfig({
  plugins: [react()],
  base: process.env.VITE_BASE || "/",
  server: {
    // Dev-only proxy: /api/* -> local FastAPI backend (same-origin, no CORS).
    // In production the app uses VITE_API_URL instead.
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
    },
  },
});
