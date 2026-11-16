<template>
  <UCard>
    <template #header>
      <div>
        <h2 class="font-medium">
          Evolução no período
        </h2>

        <p class="text-sm text-muted">
          Novos cadastros de alunos, dispositivos IoT, trilhas e grupos.
        </p>
      </div>
    </template>

    <div
      v-if="dadosGrafico.length"
      class="space-y-3 pt-3"
    >
      <UChart
        type="area"
        curve="monotone"
        :data="dadosGrafico"
        index="data"
        :categories="linhas"
        :x-axis="false"
        :y-axis="false"
        :grid="true"
        :legend="true"
        :format="formatarNumero"
        :aspect-ratio="3"
        :initial-width="1152"
        aria-label="Novos cadastros no período"
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
import type { PontoEvolucaoRead } from '~/types/generated'

const props = defineProps<{
  evolucao: PontoEvolucaoRead[]
  agrupamento: 'dia' | 'semana' | 'mes'
}>()

// msm cor dos cards
const linhas = [
  { key: 'alunos', label: 'Alunos', color: 'primary' },
  { key: 'dispositivos', label: 'Dispositivos IoT', color: 'secondary' },
  { key: 'trilhas', label: 'Trilhas', color: 'tertiary' },
  { key: 'grupos', label: 'Grupos', color: 'quaternary' },
]

const formatarNumero = new Intl.NumberFormat('pt-BR').format
const formatoMes = new Intl.DateTimeFormat('pt-BR', { month: 'short', year: 'numeric', timeZone: 'UTC' })

// data vem yyyy-mm-dd, so troca a apresentacao
function rotulo(data: string) {
  const [ano, mes, dia] = data.split('-')
  if (props.agrupamento === 'mes') return formatoMes.format(new Date(`${data}T00:00:00Z`))
  if (props.agrupamento === 'semana') return `Semana de ${dia}/${mes}`
  return `${dia}/${mes}/${ano}`
}

const dadosGrafico = computed(() => props.evolucao.map(ponto => ({ ...ponto, data: rotulo(ponto.data) })))
</script>
