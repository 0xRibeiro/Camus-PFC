import { fileURLToPath } from 'node:url'

// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  modules: ['@nuxt/ui', '@nuxt/eslint', '@vueuse/nuxt', '@pinia/nuxt', 'pinia-plugin-persistedstate/nuxt'],
  ssr: false,
  devtools: { enabled: true },
  app: {
    head: {
      title: 'Camus',
      link: [{ rel: 'icon', type: 'image/png', href: '/favicon.png' }],
    },
  },
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
  hooks: {
    'pages:extend'(pages) {
      // As rotas de grupo abrem as mesmas paginas das trilhas globaiss mas com o id do grupo antes.
      const trilhasGrupo = '/grupos/:grupoId([1-9]\\d*)/trilhas'
      const trilhaGrupo = `${trilhasGrupo}/:id(\\d+)`
      for (const [name, path, file] of [
        ['grupo-trilhas', trilhasGrupo, 'trilhas/index'],
        ['grupo-trilhas-gerenciar', `${trilhasGrupo}/gerenciar`, 'author/trilhas/index'],
        ['grupo-trilha', trilhaGrupo, 'trilhas/[id]/index'],
        ['grupo-trilha-conteudo', `${trilhaGrupo}/conteudos/:conteudoId`, 'trilhas/[id]/conteudos/[conteudoId]'],
        ['grupo-trilha-editar', `${trilhaGrupo}/editar`, 'author/trilhas/[id]/index'],
        ['grupo-trilha-editar-conteudo', `${trilhaGrupo}/editar/conteudos/:conteudoId`, 'author/trilhas/[id]/conteudos/[conteudoId]'],
      ] as const) {
        pages.push({
          name,
          path,
          file: fileURLToPath(new URL(`./app/pages/${file}.vue`, import.meta.url)),
        })
      }
    },
  },
  eslint: {
    config: {
      stylistic: true,
    },
  },
})
