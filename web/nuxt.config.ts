// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  modules: ['@nuxt/ui', '@nuxt/eslint', '@vueuse/nuxt', '@pinia/nuxt', 'pinia-plugin-persistedstate/nuxt'],
  ssr: false,
  devtools: { enabled: true },
  css: ['~/assets/css/main.css'],
  app: {
    head: {
      title: 'Camus',
      link: [{ rel: 'icon', type: 'image/x-icon', href: '/favicon.ico'}],
    },
  },
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
  vite: {
    // o bun instalou versoes diferentes do prosemirror aninhadas, isso força todos a usar a da raiz
    resolve: {
      dedupe: ['prosemirror-model', 'prosemirror-state', 'prosemirror-transform', 'prosemirror-view'],
    },
    optimizeDeps: {
      // o UEditor importa essas extensoes direto do node_modules, sem isso o prosemirror carrega 2x e o editor quebra
      include: [
        '@tiptap/starter-kit',
        '@tiptap/extension-code',
        '@tiptap/extension-horizontal-rule',
        '@tiptap/extension-image',
        '@tiptap/extension-mention',
        '@tiptap/extension-placeholder',
        '@tiptap/markdown',
      ],
    },
  },
  eslint: {
    config: {
      stylistic: true,
    },
  },
})
