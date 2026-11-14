<script setup lang="ts">
import type { NavigationMenuItem } from '@nuxt/ui'
import { version } from '../../package.json'

const items: NavigationMenuItem[] = [
  {
    label: 'Termos de Uso',
    to: '/termos-de-uso',
  },
  {
    label: 'Politica de Privacidade',
    to: '/politica-de-privacidade',
  },
  {
    label: 'Fale Conosco',
    to: 'https://github.com/0xRibeiro/Camus-PFC/issues',
    target: '_blank',
  },
]
</script>

<template>
  <UFooter>
    <template #left>
      <p class="text-muted text-sm">
        Camus © {{ new Date().getFullYear() }}
        <span class="ms-2 font-mono text-xs">v{{ version }}</span>
      </p>
    </template>

    <UNavigationMenu
      :items="items"
      variant="link"
    />

    <template #right>
      <UButton
        icon="i-simple-icons-github"
        color="neutral"
        variant="ghost"
        to="https://github.com/0xRibeiro/Camus-PFC"
        target="_blank"
        aria-label="GitHub"
      />
    </template>
  </UFooter>
</template>
