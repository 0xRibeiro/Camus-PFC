<template>
  <UCard>
    <template #header>
      <div>
        <h2 class="font-medium">
          Evolução no período
        </h2>

        <p class="text-sm text-muted">
          {{ descricao }}
        </p>
      </div>
    </template>

    <div
      v-if="dadosGrafico.length"
      class="space-y-3 pt-3"
    >
      <UChart
        :type="barras ? 'bar' : 'area'"
        :stacked="barras"
        curve="monotone"
        :data="dadosGrafico"
        index="data"
        :categories="linhas"
        :x-axis="comEixos"
        :y-axis="comEixos"
        :x-label="eixoX"
        :y-label="eixoY"
        :grid="true"
        :legend="true"
        :format="formatarEixo"
        :aspect-ratio="3"
        :initial-width="1152"
        :aria-label="descricao"
      />

      <div
        v-if="!comEixos"
        class="flex justify-between gap-3 text-xs text-muted"
      >
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
// cada dash manda suas linhas, a data vem sempre em data.
// barras empilha as linhas, a altura vira o total do dia
const props = defineProps<{
  evolucao: ({ data: string } & Record<string, unknown>)[]
  linhas: { key: string, label: string, color: string }[]
  descricao: string
  agrupamento: 'dia' | 'semana' | 'mes'
  barras?: boolean
  // titulo de cada eixo, com eles o grafico mostra as datas e as quantidades
  eixoX?: string
  eixoY?: string
}>()

const comEixos = computed(() => Boolean(props.eixoX || props.eixoY))

const formatarNumero = new Intl.NumberFormat('pt-BR').format

// conta de aluno n tem meio, entao a marcacao quebrada do eixo fica sem texto
function formatarEixo(valor: number) {
  if (!Number.isInteger(valor)) return ''
  return formatarNumero(valor)
}
const formatoMes = new Intl.DateTimeFormat('pt-BR', { month: 'short', year: 'numeric', timeZone: 'UTC' })

// data vem yyyy-mm-dd, so troca a apresentacao
function rotulo(data: string) {
  const [ano, mes, dia] = data.split('-')
  if (props.agrupamento === 'mes') return formatoMes.format(new Date(`${data}T00:00:00Z`))
  if (props.agrupamento === 'semana') return `Semana de ${dia}/${mes}`
  // no eixo cada coluna tem a data embaixo, o ano so ocupa espaço
  if (comEixos.value) return `${dia}/${mes}`
  return `${dia}/${mes}/${ano}`
}

const dadosGrafico = computed(() => props.evolucao.map(ponto => ({ ...ponto, data: rotulo(ponto.data) })))
</script>
