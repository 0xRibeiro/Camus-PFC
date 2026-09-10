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

const items: NavigationMenuItem[] = [
  { label: 'Trilhas', icon: 'i-lucide-route', to: '/trilhas' },
]
</script>