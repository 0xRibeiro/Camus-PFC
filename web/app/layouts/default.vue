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
          <!-- UColorModeButton = ja vem pronto do nuxt ui, alterna claro/escuro sozinho -->
          <UColorModeButton />

          <div
            v-if="auth.user"
            class="flex items-center gap-1 w-full"
          >
            <UUser
              :name="auth.user.username"
              :description="auth.user.role"
              :avatar="{ text: auth.user.username.charAt(0).toUpperCase() }"
              class="min-w-0 flex-1"
            />
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

      <div class="flex-1 p-4">
        <slot />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { NavigationMenuItem } from '@nuxt/ui'

const open = ref(true)
const auth = useAuthStore()

// computed pq precisa recalcular se o auth.role mudar (login/logout, por ex)
const items = computed<NavigationMenuItem[]>(() => {
  const lista: NavigationMenuItem[] = [
    { label: 'Trilhas', icon: 'i-lucide-route', to: '/author/trilhas' },
  ]

  if (auth.role === 'admin') {
    lista.push({ label: 'Usuários', icon: 'i-lucide-users', to: '/admin/usuarios' })
  }

  return lista
})

async function onLogout() {
  await auth.logout()
  await navigateTo('/login')
}
</script>
