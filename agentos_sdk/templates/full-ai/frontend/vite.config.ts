import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import fs from "fs";

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 3001,
    strictPort: true,
    allowedHosts: true,
    https: {
      key: fs.readFileSync("/certs/key.pem"),
      cert: fs.readFileSync("/certs/cert.pem"),
    },
    proxy: {
      '/api': { target: 'http://backend:8000', changeOrigin: false },
    },
  },
});
