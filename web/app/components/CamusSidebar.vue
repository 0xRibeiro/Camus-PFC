<template>
  <USidebar
    v-model:open="open"
    title="Camus"
    collapsible="icon"
    rail
    :menu="{ ui: { overlay: 'z-40', content: 'z-50' } }"
    :ui="{
      header: 'group-data-[state=collapsed]/sidebar:px-3',
      title: 'flex group-data-[state=collapsed]/sidebar:justify-center',
      container: 'h-full',
      body: 'px-1.5',
      footer: 'p-3',
    }"
  >
  <template #title="{ state }">
  <NuxtLink
    to="/"
    aria-label="Camus — página inicial"
    class="inline-flex shrink-0 rounded-md bg-black focus-visible:outline-2 focus-visible:-outline-offset-2 focus-visible:outline-primary"
    @click="fecharMenuNoCelular"
  >
    <img
      src="/logo.png"
      alt=""
      width="384"
      height="384"
      class="rounded-md"
      :class="state === 'collapsed' ? 'size-8' : 'size-11'"
    >
  </NuxtLink>
  </template>
    <template #default="{ state }">
      <UNavigationMenu
        :items="items"
        orientation="vertical"
        :collapsed="state === 'collapsed'"
        :ui="{
          root: 'min-h-0 flex-1',
          list: 'flex min-h-0 flex-1 flex-col overflow-y-auto',
          item: 'flex min-h-12 flex-1',
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
            class="min-w-0 rounded-md p-0.5"
            :class="[
              { 'flex-1': state === 'expanded' },
              rotaAtual('/perfil')
                ? 'bg-indigo-100 hover:bg-indigo-200 dark:bg-indigo-500/25 dark:hover:bg-indigo-500/35'
                : 'hover:bg-elevated',
            ]"
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
const route = useRoute()
const menuDesktop = useMediaQuery('(min-width: 64rem)')

function fecharMenuNoCelular() {
  if (!menuDesktop.value) open.value = false
}

function rotaAtual(caminho: string) {
  return route.path === caminho || route.path.startsWith(`${caminho}/`)
}

// mesma cor que a pagina usa, as classes ficam escritas inteiras pro tailwind achar
const destaques = {
  primary: 'before:bg-primary/15',
  secondary: '[--ui-primary:var(--ui-secondary)] before:bg-secondary/15',
  tertiary: '[--ui-primary:var(--ui-tertiary)] before:bg-tertiary/15',
  error: '[--ui-primary:var(--ui-error)] before:bg-error/15',
  laranja: '[--ui-primary:var(--color-orange-700)] dark:[--ui-primary:var(--color-orange-400)] before:bg-orange-500/15',
  violeta: '[--ui-primary:var(--color-violet-600)] dark:[--ui-primary:var(--color-violet-400)] before:bg-violet-500/15',
  verdeAgua: '[--ui-primary:var(--color-teal-700)] dark:[--ui-primary:var(--color-teal-400)] before:bg-teal-500/15',
  azul: '[--ui-primary:var(--color-sky-700)] dark:[--ui-primary:var(--color-sky-400)] before:bg-sky-500/15',
}

// active na mao pq o menu so marca a rota exata, ai /minigames/jogo ficava sem cor
function item(label: string, icon: string, to: string, cor: keyof typeof destaques = 'primary'): NavigationMenuItem {
  const ativo = rotaAtual(to)
  return { label, icon, to, active: ativo, class: ativo ? destaques[cor] : undefined, onSelect: fecharMenuNoCelular}
}

const items = computed<NavigationMenuItem[]>(() => {
  const lista: NavigationMenuItem[] = [
    item('Trilhas', 'i-lucide-route', '/trilhas', 'error'),
    item('Coleção', 'i-lucide-fish', '/colecao'),
  ]

  if (auth.role === 'aluno') {
    lista.push(
      item('Aquários', 'i-lucide-waves', '/aquarios', 'violeta'),
      item('Conquistas', 'i-lucide-trophy', '/conquistas', 'secondary'),
      item('Grupos', 'i-lucide-users', '/grupos', 'laranja'),
      item('Minigames', 'i-lucide-gamepad-2', '/minigames', 'tertiary'),
      item('Ranking', 'i-lucide-medal', '/ranking', 'secondary'),
    )
  }

  if (auth.role === 'admin') {
    lista.push(
      item('Usuários', 'i-lucide-users', '/admin/usuarios', 'verdeAgua'),
      item('Auditoria', 'i-lucide-history', '/admin/auditoria', 'laranja'),
      item('Denúncias', 'i-lucide-flag', '/admin/denuncias', 'violeta'),
      item('Dashboard', 'i-lucide-layout-dashboard', '/admin/dashboard', 'azul'),
    )
  }

  if (auth.role === 'admin' || auth.role === 'author') {
    lista.push(item('Gerenciar Trilhas', 'i-lucide-square-text', '/author/trilhas', 'error'))
  }

  return lista
})

async function onLogout() {
  await auth.logout()
  await navigateTo('/login')
}
</script>
