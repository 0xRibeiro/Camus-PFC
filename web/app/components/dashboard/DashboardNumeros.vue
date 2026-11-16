<template>
  <UPageGrid class="gap-4 sm:grid-cols-2 lg:grid-cols-4">
    <UPageCard
      v-for="indicador in lista"
      :key="indicador.titulo"
      :icon="indicador.icone"
      :title="indicador.titulo"
      variant="subtle"
      :ui="{
        container: 'gap-y-1.5',
        wrapper: 'items-start',
        leading: ['p-2.5 rounded-full ring ring-inset', cores[indicador.cor].fundo],
        leadingIcon: cores[indicador.cor].icone,
        title: 'font-normal text-muted text-xs uppercase',
      }"
    >
      <div class="flex items-center gap-2">
        <span class="text-3xl font-semibold text-highlighted">
          {{ indicador.texto }}
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
type Cor = 'primary' | 'secondary' | 'tertiary' | 'quaternary'

export interface Indicador {
  titulo: string
  icone: string
  cor: Cor
  valor: number
  // null n mostra o %
  anterior: number | null
  formatar?: (valor: number) => string
}

const props = defineProps<{
  indicadores: Indicador[]
}>()

// classes inteiras pro tailwind achar
const cores: Record<Cor, { fundo: string, icone: string }> = {
  primary: { fundo: 'bg-primary/10 ring-primary/25', icone: 'text-primary' },
  secondary: { fundo: 'bg-secondary/10 ring-secondary/25', icone: 'text-secondary' },
  tertiary: { fundo: 'bg-tertiary/10 ring-tertiary/25', icone: 'text-tertiary' },
  quaternary: { fundo: 'bg-quaternary/10 ring-quaternary/25', icone: 'text-quaternary' },
}

// anterior zerado n tem %
function variacao(atual: number, anterior: number | null) {
  if (!anterior) return null
  return Math.round(((atual - anterior) / anterior) * 100)
}

const lista = computed(() => props.indicadores.map(indicador => ({
  ...indicador,
  texto: indicador.formatar ? indicador.formatar(indicador.valor) : indicador.valor.toLocaleString('pt-BR'),
  variacao: variacao(indicador.valor, indicador.anterior),
})))
</script>
