<template>
  <UCard>
    <template #header>
      <h2 class="font-medium">
        Engajamento
      </h2>

      <p class="text-sm text-muted">
        Desde a criação da trilha, sobre {{ engajamento.base.toLocaleString('pt-BR') }} {{ rotuloBase }}.
      </p>
    </template>

    <div class="space-y-5">
      <div
        v-for="etapa in etapas"
        :key="etapa.titulo"
        class="space-y-2"
      >
        <div class="flex items-baseline justify-between gap-3">
          <p class="flex items-center gap-2 font-medium text-highlighted">
            <UIcon
              :name="etapa.icone"
              class="size-4 text-muted"
            />
            {{ etapa.titulo }}
          </p>

          <p class="shrink-0 text-sm">
            <span class="font-semibold tabular-nums">{{ formatarPorcentagem(etapa.porcentagem) }}</span>
            <span class="text-muted"> · {{ etapa.valor.toLocaleString('pt-BR') }}</span>
          </p>
        </div>

        <UProgress
          :model-value="etapa.porcentagem"
          :max="1"
          :color="etapa.cor"
          size="sm"
        />
      </div>

      <USeparator />

      <div class="flex items-baseline justify-between gap-3">
        <p class="text-sm text-muted">
          Dos que começaram, terminaram
        </p>

        <p class="text-2xl font-semibold text-highlighted tabular-nums">
          {{ engajamento.iniciaram ? formatarPorcentagem(engajamento.concluiram / engajamento.iniciaram) : '—' }}
        </p>
      </div>
    </div>
  </UCard>
</template>

<script setup lang="ts">
import type { EngajamentoTrilhaRead } from '~/types/generated'

const props = defineProps<{
  engajamento: EngajamentoTrilhaRead
  rotuloBase: string
}>()

const formatarPorcentagem = new Intl.NumberFormat('pt-BR', { style: 'percent', maximumFractionDigits: 1 }).format

// base zerada fica 0
function porcentagem(valor: number) {
  if (!props.engajamento.base) return 0
  return valor / props.engajamento.base
}

const etapas = computed(() => [
  { titulo: 'Começaram', icone: 'i-lucide-play', cor: 'primary' as const, valor: props.engajamento.iniciaram, porcentagem: porcentagem(props.engajamento.iniciaram) },
  { titulo: 'Terminaram', icone: 'i-lucide-flag', cor: 'tertiary' as const, valor: props.engajamento.concluiram, porcentagem: porcentagem(props.engajamento.concluiram) },
])
</script>
