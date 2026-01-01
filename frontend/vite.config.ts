import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
import path from 'path';


export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
  resolve: {
    extensions: ['.js', '.jsx', '.ts', '.tsx', '.json'],
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  build: {
    target: 'esnext',
    outDir: 'build',
  },
  server: {
    port: 3000,
    open: true,
    host: true,// [추가] 외부 접속 허용 (0.0.0.0)
    proxy: {// [추가] 백엔드 연결 설정
      '/api': {
        target: 'http://backend:8000', // Docker 내부의 백엔드 주소
        changeOrigin: true,
        secure: false,
      },
    },
  },
});