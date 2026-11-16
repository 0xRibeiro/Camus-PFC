<script setup lang="ts">
const route = useRoute()

const temaPagina = computed(() => {
  const [, secao, pagina] = route.path.split('/')

  if (secao === 'trilhas' || (secao === 'author' && pagina === 'trilhas')) return 'camus-trilhas'
  if (secao === 'grupos') return 'camus-grupos'
  if (secao === 'aquarios') return 'camus-aquarios'
  if (secao === 'minigames') return 'camus-minigames'
  if (secao === 'ranking') return 'camus-ranking'
  if (secao === 'conquistas' && !pagina) return 'camus-conquistas'
  if (secao === 'colecao') return 'camus-colecao'
  if (secao === 'perfil') return 'camus-perfil'
  if (secao === 'login' || secao === 'register') return 'camus-acesso'
  if (secao === 'recuperar-senha') return 'camus-recuperar-senha'
  if (secao === 'aceite-termos') return 'camus-aceite'
  if (secao === 'termos-de-uso') return 'camus-termos'
  if (secao === 'politica-de-privacidade') return 'camus-privacidade'
  if (secao === 'admin') {
    if (pagina === 'usuarios') return 'camus-usuarios'
    if (pagina === 'auditoria') return 'camus-auditoria'
    if (pagina === 'denuncias') return 'camus-denuncias'
    if (pagina === 'dashboard') return 'camus-dashboard'
  }

  return undefined
})
</script>

<template>
  <UApp :portal="temaPagina ? '#camus-portal' : 'body'">
    <div
      id="camus-portal"
      class="relative z-20"
      :class="temaPagina"
    />

    <div class="isolate flex min-h-dvh flex-col">
      <NuxtLayout>
        <div class="flex min-w-0 flex-1 flex-col">
          <main
            class="camus-pagina flex flex-1 flex-col p-4"
            :class="temaPagina"
          >
            <NuxtPage />
          </main>

          <CamusFooter class="shrink-0" />
        </div>
      </NuxtLayout>
    </div>

    <CamusAtualizacao />
  </UApp>
</template>
