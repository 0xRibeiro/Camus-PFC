<template>
  <UCard>
    <template #header>
      <h2 class="font-medium">
        Distribuição das notas
      </h2>

      <p class="text-sm text-muted">
        Quantas tentativas da versão atual tiraram cada nota.
      </p>
    </template>

    <UChart
      v-if="total"
      type="bar"
      :data="dadosGrafico"
      index="nota"
      :categories="[{ key: 'quantidade', label: 'Tentativas', color: 'secondary' }]"
      :y-axis="false"
      :grid="true"
      :format="formatarNumero"
      :aspect-ratio="1.6"
      aria-label="Quantidade de tentativas por nota"
    />

    <p
      v-else
      class="text-sm text-muted"
    >
      Ninguém fez a versão atual do quiz ainda.
    </p>
  </UCard>
</template>

<script setup lang="ts">
import type { NotaQuizRead } from '~/types/generated'

const props = defineProps<{
  notas: NotaQuizRead[]
}>()

const formatarNumero = new Intl.NumberFormat('pt-BR').format

// ultima nota e o total de questoes
const dadosGrafico = computed(() => {
  const totalQuestoes = props.notas.length - 1
  return props.notas.map(nota => ({ nota: `${nota.acertos}/${totalQuestoes}`, quantidade: nota.quantidade }))
})

const total = computed(() => props.notas.reduce((soma, nota) => soma + nota.quantidade, 0))
</script>
