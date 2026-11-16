<template>
  <div class="space-y-3">
    <div
      v-if="pontos.length > 1"
      class="space-y-1"
    >
      <UChart
        type="area"
        curve="monotone"
        :data="dadosGrafico"
        index="hora"
        :categories="[{ key: 'valor', label: rotulo, color: cor }]"
        :x-axis="false"
        :y-axis="true"
        :grid="true"
        :format="formatarEixo"
        :aspect-ratio="2.4"
        :aria-label="rotulo"
      />

      <div class="flex justify-between gap-3 text-xs text-muted">
        <span>{{ dadosGrafico[0]?.hora }}</span>
        <span>{{ dadosGrafico.at(-1)?.hora }}</span>
      </div>
    </div>

    <p
      v-else
      class="flex h-32 items-center justify-center rounded-lg bg-elevated/50 text-sm text-muted"
    >
      Poucas leituras nesse período pra montar o gráfico.
    </p>

    <dl
      v-if="pontos.length"
      class="grid grid-cols-3 divide-x divide-default rounded-lg bg-elevated/50 py-2 text-center"
    >
      <div
        v-for="estatistica in estatisticas"
        :key="estatistica.titulo"
      >
        <dt class="text-xs text-muted">
          {{ estatistica.titulo }}
        </dt>
        <dd class="font-semibold tabular-nums">
          {{ formatar(estatistica.valor) }}
        </dd>
      </div>
    </dl>
  </div>
</template>

<script setup lang="ts">
import type { PontoLeitura } from '~/types/generated'

const props = defineProps<{
  pontos: PontoLeitura[]
  rotulo: string
  cor: string
  minutos: number
  formatar: (valor: number) => string
  // maior valor fica embaixo, pro nivel subir qnd a distancia cai
  invertido?: boolean
  titulosEstatisticas?: [string, string, string]
}>()

// area do uchart sempre parte do 0, entao plota a diferenca pra uma base e soma de volta no texto
const base = computed(() => {
  let menor = Infinity
  let maior = -Infinity
  for (const ponto of props.pontos) {
    menor = Math.min(menor, ponto.valor)
    maior = Math.max(maior, ponto.valor)
  }

  const folga = Math.max((maior - menor) * 0.25, 0.5)
  if (props.invertido) return maior + folga
  return menor - folga
})

function paraGrafico(valor: number) {
  if (props.invertido) return base.value - valor
  return valor - base.value
}

function doGrafico(valor: number) {
  if (props.invertido) return base.value - valor
  return valor + base.value
}

function formatarEixo(valor: number) {
  return props.formatar(doGrafico(valor))
}

// segundo so faz falta na ultima hora, dia so no de 24h
function formatarHora(tempo: string) {
  const data = new Date(tempo)
  if (props.minutos <= 60) return data.toLocaleTimeString('pt-BR')
  if (props.minutos <= 360) return data.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
  return data.toLocaleString('pt-BR', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' })
}

const dadosGrafico = computed(() => props.pontos.map(ponto => ({
  hora: formatarHora(ponto.tempo),
  valor: paraGrafico(ponto.valor),
})))

const estatisticas = computed(() => {
  let menor = Infinity
  let maior = -Infinity
  let soma = 0
  for (const ponto of props.pontos) {
    menor = Math.min(menor, ponto.valor)
    maior = Math.max(maior, ponto.valor)
    soma += ponto.valor
  }

  const [tituloMenor, tituloMedia, tituloMaior] = props.titulosEstatisticas ?? ['Mínima', 'Média', 'Máxima']
  return [
    { titulo: tituloMenor, valor: menor },
    { titulo: tituloMedia, valor: soma / props.pontos.length },
    { titulo: tituloMaior, valor: maior },
  ]
})
</script>
