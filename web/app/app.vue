<script setup lang="ts">
const route = useRoute()

const temaPagina = computed(() => {
  const [, secao, pagina] = route.path.split('/')

  if (secao === 'trilhas' || (secao === 'author' && pagina === 'trilhas')) return 'camus-trilhas'
  if (secao === 'grupos') return 'camus-grupos'
  if (secao === 'aquarios') return 'camus-aquarios'
  if (secao === 'minigames') return 'camus-minigames'
  if (route.path === '/ranking' || route.path === '/ranking/') return 'camus-ranking'
  if (secao === 'admin') {
    if (pagina === 'usuarios') return 'camus-usuarios'
    if (pagina === 'auditoria') return 'camus-auditoria'
    if (pagina === 'denuncias') return 'camus-denuncias'
    if (pagina === 'dashboard') return 'camus-dashboard'
  }
})
</script>

<template>
  <UApp :portal="temaPagina ? '#camus-portal' : 'body'">
    <div
      id="camus-portal"
      :class="temaPagina"
    />

    <div class="flex min-h-dvh flex-col">
      <NuxtLayout>
        <div class="flex min-w-0 flex-1 flex-col">
          <main
            class="flex flex-1 flex-col p-4"
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
