<template>
  <UPageGrid class="gap-4 sm:grid-cols-2 lg:grid-cols-4">
    <UPageCard
      v-for="indicador in indicadores"
      :key="indicador.titulo"
      :icon="indicador.icone"
      :title="indicador.titulo"
      variant="subtle"
      :ui="{
        container: 'gap-y-1.5',
        wrapper: 'items-start',
        leading: 'p-2.5 rounded-full bg-primary/10 ring ring-inset ring-primary/25',
        title: 'font-normal text-muted text-xs uppercase',
      }"
    >
      <span class="text-3xl font-semibold text-highlighted">
        {{ indicador.valor.toLocaleString('pt-BR') }}
      </span>
    </UPageCard>
  </UPageGrid>
</template>

<script setup lang="ts">
import type { DashboardRead } from '~/types/generated'

const props = defineProps<{
  dados: DashboardRead
}>()

// recalcula os números quando a página tiver novos dados
const indicadores = computed(() => [
  { titulo: 'Usuários cadastrados', icone: 'i-lucide-users', valor: props.dados.total_usuarios },
  { titulo: 'Grupos de estudo', icone: 'i-lucide-users-round', valor: props.dados.total_grupos },
  { titulo: 'Conquistas concedidas', icone: 'i-lucide-trophy', valor: props.dados.total_conquistas_concedidas },
  { titulo: 'Trilhas cadastradas', icone: 'i-lucide-route', valor: props.dados.total_trilhas },
])
</script>
