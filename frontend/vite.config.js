import { defineConfig } from 'vite';

const proxy = { '/api': 'http://127.0.0.1:5000' };

export default defineConfig({
  server: { host: '127.0.0.1', port: 5173, strictPort: true, proxy },
  preview: { host: '127.0.0.1', port: 5173, strictPort: true, proxy },
});
