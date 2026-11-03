<template>
  <UCard>
    <template #header>
      <div class="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 class="font-medium">
            Cadastros por dia
          </h2>

          <p class="text-sm text-muted">
            Histórico registrado pela auditoria.
          </p>
        </div>

        <div class="text-right">
          <p class="text-2xl font-semibold text-highlighted">
            {{ formatarNumero(total) }}
          </p>

          <p class="text-xs text-muted">
            cadastros no período
          </p>
        </div>
      </div>
    </template>

    <div
      v-if="dadosGrafico.length"
      class="space-y-3"
    >
      <UChart
        type="area"
        curve="monotone"
        :data="dadosGrafico"
        index="data"
        :categories="[{ key: 'quantidade', label: 'Cadastros' }]"
        :x-axis="false"
        :y-axis="false"
        :grid="true"
        :format="formatarNumero"
        :aspect-ratio="3"
        :initial-width="1152"
        aria-label="Quantidade de cadastros por dia"
      />

      <div class="flex justify-between gap-3 text-xs text-muted">
        <span>{{ dadosGrafico[0]?.data }}</span>
        <span>{{ dadosGrafico.at(-1)?.data }}</span>
      </div>
    </div>

    <p
      v-else
      class="text-sm text-muted"
    >
      Nenhum dado disponível para o período.
    </p>
  </UCard>
</template>

<script setup lang="ts">
import type { CadastroDiaRead } from '~/types/generated'

const props = defineProps<{
  cadastros: CadastroDiaRead[]
}>()

const formatarNumero = new Intl.NumberFormat('pt-BR').format

// altera somente a apresentação da data, preservando o dia recebido da API
const dadosGrafico = computed(() => props.cadastros.map(item => ({
  data: item.data.split('-').reverse().join('/'),
  quantidade: item.quantidade,
})))

const total = computed(() => props.cadastros.reduce((soma, item) => soma + item.quantidade, 0))
</script>
