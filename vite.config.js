import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'
import path from 'path'

export default defineConfig({
  plugins: [svelte()],
  root: 'src/renderer',
  base: './',  // ✅ FIXED: Changed from '../' to './'
  build: {
    outDir: '../dist/renderer',
    emptyOutDir: true
  },
  resolve: {
    alias: {
      $lib: path.resolve(__dirname, 'src/renderer')
    }
  },
  server: {
    port: 5173,
    host: true
  }
})
