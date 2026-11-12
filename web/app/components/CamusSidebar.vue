<template>
  <USidebar
    v-model:open="open"
    title="Camus"
    collapsible="icon"
    rail
    :ui="{
      container: 'h-full',
      body: 'px-1.5',
      footer: 'p-3',
    }"
  >
    <template #default="{ state }">
      <UNavigationMenu
        :items="items"
        orientation="vertical"
        :collapsed="state === 'collapsed'"
        :ui="{
          linkLeadingIcon: 'size-9',
          link: state === 'collapsed' ? 'justify-center' : undefined,
        }"
      />
    </template>

    <template #footer="{ state }">
      <div class="flex w-full flex-col items-start gap-1">
        <UColorModeButton />

        <div
          v-if="auth.user"
          class="flex w-full items-center gap-1"
          :class="{ 'flex-col': state === 'collapsed' }"
        >
          <NuxtLink
            to="/perfil"
            class="min-w-0 rounded-md p-0.5 hover:bg-elevated"
            :class="{ 'flex-1': state === 'expanded' }"
            aria-label="Meu perfil"
          >
            <UUser
              :name="auth.user.username"
              :description="auth.user.role"
              :ui="{ wrapper: state === 'collapsed' ? 'hidden' : undefined }"
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
</template>

<script setup lang="ts">
import type { NavigationMenuItem } from '@nuxt/ui'

const open = defineModel<boolean>('open', { required: true })
const auth = useAuthStore()

const items = computed<NavigationMenuItem[]>(() => {
  const lista: NavigationMenuItem[] = [
    { label: 'Trilhas', icon: 'i-lucide-route', to: '/trilhas' },
    { label: 'Coleção', icon: 'i-lucide-fish', to: '/colecao' },
  ]

  if (auth.role === 'aluno') {
    lista.push(
      { label: 'Aquários', icon: 'i-lucide-waves', to: '/aquarios' },
      { label: 'Conquistas', icon: 'i-lucide-trophy', to: '/conquistas' },
      { label: 'Grupos', icon: 'i-lucide-users', to: '/grupos' },
    )
  }

  if (auth.role === 'admin') {
    lista.push(
      { label: 'Usuários', icon: 'i-lucide-users', to: '/admin/usuarios' },
      { label: 'Auditoria', icon: 'i-lucide-history', to: '/admin/auditoria' },
      { label: 'Dashboard', icon: 'i-lucide-layout-dashboard', to: '/admin/dashboard' },
    )
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
