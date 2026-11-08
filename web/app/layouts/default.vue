<template>
  <div class="flex flex-1">
    <USidebar
      v-model:open="open"
      collapsible="icon"
      rail
      :ui="{
        container: 'h-full',
        inner: 'bg-elevated/25 divide-transparent',
        body: 'py-0',
      }"
    >
      <template #header>
        <span class="px-2 text-lg font-bold">Camus</span>
      </template>

      <template #default="{ state }">
        <UNavigationMenu
          :key="state"
          :items="items"
          orientation="vertical"
          :ui="{ link: 'p-1.5 overflow-hidden' }"
        />
      </template>

      <template #footer>
        <div class="flex flex-col gap-1 w-full">
          <!-- alterna entre os temas do site -->
          <UColorModeButton />

          <div
            v-if="auth.user"
            class="flex items-center gap-1 w-full"
          >
          <!-- clicar no usuario leva pro perfil -->
            <NuxtLink
              to="/perfil"
              class="min-w-0 flex-1 rounded-md p-1 hover:bg-elevated"
              aria-label="Meu perfil"
            >
              <UUser
                :name="auth.user.username"
                :description="auth.user.role"
              >
                <template #avatar>
                  <UsuarioAvatar
                    :avatar="auth.user.avatar"
                    :cor-fundo="auth.user.cor_fundo"
                    :tamanho="32"
                  />
                </template>
              </UUser>
            </NuxtLink>

            <UButton
              icon="i-lucide-log-out"
              color="neutral"
              variant="ghost"
              aria-label="Sair"
              @click="onLogout"
            />
          </div>
        </div>
      </template>
    </USidebar>

    <div class="flex flex-1 flex-col">
      <div class="h-(--ui-header-height) shrink-0 flex items-center px-4 border-b border-default">
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
import type { NavigationMenuItem } from '@nuxt/ui'
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

// recalcula os itens do menu quando o papel do usuário mudar
const items = computed<NavigationMenuItem[]>(() => {
  const lista: NavigationMenuItem[] = [
    { label: 'Trilhas', icon: 'i-lucide-route', to: '/trilhas' },
    { label: 'Coleção', icon: 'i-lucide-fish', to: '/colecao' },
    { label: 'Aquários', icon: 'i-lucide-waves', to: '/aquarios' },
    { label: 'Conquistas', icon: 'i-lucide-trophy', to: '/conquistas' },
    { label: 'Grupos', icon: 'i-lucide-users', to: '/grupos' },
  ]

  if (auth.role === 'admin') {
    lista.push({ label: 'Usuários', icon: 'i-lucide-users', to: '/admin/usuarios' })
    lista.push({ label: 'Auditoria', icon: 'i-lucide-history', to: '/admin/auditoria' })
    lista.push({ label: 'Dashboard', icon: 'i-lucide-layout-dashboard', to: '/admin/dashboard' })
  }

  if (auth.role === 'admin' || auth.role === 'author') {
    lista.push({ label: 'Gerenciar Trilhas', icon: 'i-lucide-square-text', to: '/author/trilhas' })
  }

  return lista
})

async function onLogout() {
  await auth.logout()
  await navigateTo('/login')
}
</script>
