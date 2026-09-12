// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  modules: ['@nuxt/ui', '@nuxt/eslint', '@vueuse/nuxt', '@pinia/nuxt', 'pinia-plugin-persistedstate/nuxt'],
  ssr: false,
  devtools: { enabled: true },
  css: ['~/assets/css/main.css'],
  ui: {
    // array de nome das cores semanticas q as adicionais sao definidas no web/app/app.config.ts
    theme: {
      colors: ['primary', 'secondary', 'tertiary', 'quaternary', 'info', 'success', 'warning', 'error'],
    },
  },
  runtimeConfig: {
    public: {
      apiBase: 'http://localhost:8000',
      inatBase: 'https://api.inaturalist.org/v1',
    },
  },
  compatibilityDate: '2025-07-15',
  eslint: {
    config: {
      stylistic: true,
    },
  },
})
