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
        leading: ['p-2.5 rounded-full ring ring-inset', indicador.fundo],
        leadingIcon: indicador.iconeCor,
        title: 'font-normal text-muted text-xs uppercase',
      }"
    >
      <div class="flex items-center gap-2">
        <span class="text-3xl font-semibold text-highlighted">
          {{ indicador.valor.toLocaleString('pt-BR') }}
        </span>

        <UBadge
          v-if="indicador.variacao !== null"
          :color="indicador.variacao >= 0 ? 'success' : 'error'"
          variant="subtle"
          class="text-xs"
        >
          {{ indicador.variacao >= 0 ? '+' : '' }}{{ indicador.variacao }}%
        </UBadge>
      </div>
    </UPageCard>
  </UPageGrid>
</template>

<script setup lang="ts">
import type { TotaisPeriodoRead } from '~/types/generated'

const props = defineProps<{
  totais: TotaisPeriodoRead
  anteriores: TotaisPeriodoRead
}>()

// periodo anterior zerado n tem %
function variacao(atual: number, anterior: number) {
  if (!anterior) return null
  return Math.round(((atual - anterior) / anterior) * 100)
}

// classes inteiras pro tailwind achar, msm cor das linhas do grafico
const indicadores = computed(() => [
  { titulo: 'Alunos novos', icone: 'i-lucide-users', chave: 'alunos', fundo: 'bg-primary/10 ring-primary/25', iconeCor: 'text-primary' },
  { titulo: 'Dispositivos IoT novos', icone: 'i-lucide-cpu', chave: 'dispositivos', fundo: 'bg-secondary/10 ring-secondary/25', iconeCor: 'text-secondary' },
  { titulo: 'Trilhas novas', icone: 'i-lucide-route', chave: 'trilhas', fundo: 'bg-tertiary/10 ring-tertiary/25', iconeCor: 'text-tertiary' },
  { titulo: 'Grupos novos', icone: 'i-lucide-users-round', chave: 'grupos', fundo: 'bg-quaternary/10 ring-quaternary/25', iconeCor: 'text-quaternary' },
].map((item) => {
  const chave = item.chave as keyof TotaisPeriodoRead
  return { ...item, valor: props.totais[chave], variacao: variacao(props.totais[chave], props.anteriores[chave]) }
}))
</script>
