import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
    // 代码分割优化
    rollupOptions: {
      output: {
        // 手动分割代码块
        manualChunks: {
          // React 核心库
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          // Redux 状态管理
          'redux-vendor': ['@reduxjs/toolkit', 'react-redux'],
          // Ant Design UI 库
          'antd-vendor': ['antd', '@ant-design/icons'],
          // 图表库
          'chart-vendor': ['recharts', 'cytoscape', 'cytoscape-dagre'],
          // 3D 可视化库
          '3d-vendor': ['three', '@react-three/fiber', '@react-three/drei'],
        },
        // 优化 chunk 文件名
        chunkFileNames: 'assets/js/[name]-[hash].js',
        entryFileNames: 'assets/js/[name]-[hash].js',
        assetFileNames: 'assets/[ext]/[name]-[hash].[ext]',
      },
    },
    // 使用 esbuild 压缩（更快，不需要额外依赖）
    minify: 'esbuild',
    // chunk 大小警告限制
    chunkSizeWarningLimit: 1000,
  },
  // 优化依赖预构建
  optimizeDeps: {
    include: [
      'react',
      'react-dom',
      'react-router-dom',
      '@reduxjs/toolkit',
      'react-redux',
      'antd',
      '@ant-design/icons',
      'axios',
      'recharts',
      'cytoscape',
    ],
  },
});

