import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { cpSync } from 'fs'
import { resolve, dirname } from 'path'
import { fileURLToPath } from 'url'

const __dirname = dirname(fileURLToPath(import.meta.url))

export default defineConfig({
  plugins: [
    vue(),
    {
      name: 'copy-data-dir',
      closeBundle() {
        cpSync(resolve(__dirname, 'data'), resolve(__dirname, 'dist/data'), { recursive: true })
      }
    }
  ],
  server: {
    host: '0.0.0.0',
    port: 5173,
    strictPort: false,
  },
  build: {
    outDir: 'dist',
  }
})
