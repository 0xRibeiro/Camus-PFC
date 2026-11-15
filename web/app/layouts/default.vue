<template>
  <div class="flex min-w-0 flex-1">
    <CamusSidebar v-model:open="open" />

    <div class="flex min-w-0 flex-1 flex-col">
      <div class="flex h-(--ui-header-height) shrink-0 items-center border-b border-default px-4">
        <UButton
          icon="i-lucide-panel-left"
          color="neutral"
          variant="ghost"
          aria-label="Abrir ou fechar menu"
          @click="open = !open"
        />
      </div>

      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
import { useConquistasStore } from '~/stores/conquistas'

const open = ref(true)
const auth = useAuthStore()
const conquistas = useConquistasStore()
const colorMode = useColorMode()
const route = useRoute()

// conquista 1: trocar o tema do site
watch(
  () => colorMode.preference,
  async (novoTema, temaAnterior) => {
    if (!temaAnterior || novoTema === temaAnterior || !auth.isAuthenticated) return

    await conquistas.desbloquearConquista(1).catch(() => {})
  },
)

// conquista 2: esconder o menu lateral
watch(
  () => [open.value, auth.isAuthenticated] as const,
  async ([menuAberto, autenticado]) => {
    if (menuAberto || !autenticado) return

    await conquistas.desbloquearConquista(2).catch(() => {})
  },
)

// conquistas obtidas ao visitar determinadas páginas
const conquistasPorPagina: Record<string, number> = {
  '/conquistas/segredo': 4,
  '/colecao': 5,
}

watch(
  () => [route.path, auth.isAuthenticated] as const,
  async ([caminho, autenticado]) => {
    if (!autenticado) return

    const conquistaId = conquistasPorPagina[caminho]
    if (conquistaId === undefined) return

    await conquistas.desbloquearConquista(conquistaId).catch(() => {})
  },
  { immediate: true },
)
</script>
