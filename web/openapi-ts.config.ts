import { defineConfig } from '@hey-api/openapi-ts'

export default defineConfig({
  input: `${process.env.API_BASE || 'http://localhost:8000'}/openapi.json`,
  output: 'app/types/generated',
  plugins: ['@hey-api/typescript', 'zod'],
})
