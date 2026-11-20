<template>
  <div class="space-y-3">
    <div
      v-if="serie.pontos.length > 1"
      class="space-y-2"
    >
      <UChart
        :definition="definicao"
        :aspect-ratio="2.4"
        :aria-label="rotulo"
      >
        <template #tooltip="{ primaryPoint }">
          <p class="text-xs text-muted">
            {{ formatarTooltip(primaryPoint.datum.tempo) }}
          </p>
          <p class="font-semibold tabular-nums">
            {{ formatar(primaryPoint.datum.valor) }}
          </p>
        </template>
      </UChart>

      <div
        v-if="semLeitura.length || erros.length"
        class="flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted"
      >
        <span
          v-if="semLeitura.length"
          class="flex items-center gap-1.5"
        >
          <span class="size-2.5 rounded-sm bg-neutral-500/30" />
          IoT desligado
        </span>
        <span
          v-if="erros.length"
          class="flex items-center gap-1.5"
        >
          <span class="size-2.5 rounded-sm bg-amber-500/40" />
          Erro do sensor
        </span>
      </div>
    </div>

    <p
      v-else
      class="flex h-32 items-center justify-center rounded-lg bg-elevated/50 text-sm text-muted"
    >
      Poucas leituras nesse período pra montar o gráfico.
    </p>

    <dl
      v-if="serie.minimo != null && serie.media != null && serie.maximo != null"
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
import { areaY, defineChart, lineY, rect, ruleX } from '@tanstack/charts'
import { crosshair } from '@tanstack/charts/crosshair'
import { decorative } from '@tanstack/charts/mark/decorative'
import { scaleLinear } from '@tanstack/charts/scales/linear'
import { chartCurves } from '#ui/utils/chart'
import type { SerieLeitura } from '~/types/generated'

const props = defineProps<{
  serie: SerieLeitura
  rotulo: string
  cor: string
  minutos: number
  formatar: (valor: number) => string
  // maior valor fica embaixo, pro nivel subir qnd a distancia cai
  invertido?: boolean
  titulosEstatisticas?: [string, string, string]
}>()

const MINUTO = 60 * 1000
const HORA = 60 * MINUTO
const DIA = 24 * HORA

// linha = coluna de referencia, rotulo = horario escrito embaixo. ~12 linhas em qualquer periodo
const MARCAS: Record<number, { linha: number, rotulo: number }> = {
  60: { linha: 5 * MINUTO, rotulo: 15 * MINUTO },
  360: { linha: 30 * MINUTO, rotulo: HORA },
  1440: { linha: 2 * HORA, rotulo: 6 * HORA },
  10080: { linha: 12 * HORA, rotulo: DIA },
  43200: { linha: 2 * DIA, rotulo: 7 * DIA },
}

// dia 0 do Date foi numa quinta, 4 dias depois e segunda. semana comeca na segunda
const SEGUNDA = 4 * DIA

///// eixo de tempo

const fim = computed(() => {
  // le a serie so pra recalcular a cada busca nova
  void props.serie
  return Date.now()
})
const inicio = computed(() => fim.value - props.minutos * MINUTO)

// horarios redondos no fuso de quem ta vendo, tipo 14:05 e n 14:07
function horariosRedondos(passo: number) {
  const fuso = new Date(inicio.value).getTimezoneOffset() * MINUTO
  const desvio = passo === 7 * DIA ? SEGUNDA : 0

  const horarios = []
  let horario = Math.ceil((inicio.value - fuso - desvio) / passo) * passo + fuso + desvio
  while (horario <= fim.value) {
    horarios.push(horario)
    horario += passo
  }
  return horarios
}

const marcas = computed(() => MARCAS[props.minutos] ?? { linha: props.minutos * MINUTO / 12, rotulo: props.minutos * MINUTO / 4 })
const linhas = computed(() => horariosRedondos(marcas.value.linha))
const rotulos = computed(() => horariosRedondos(marcas.value.rotulo))

function formatarRotulo(tempo: number) {
  const data = new Date(tempo)
  if (props.minutos <= 1440) return data.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
  if (props.minutos <= 10080) {
    const semana = data.toLocaleDateString('pt-BR', { weekday: 'short' }).replace('.', '')
    return `${semana} ${data.getDate()}`
  }
  return data.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' })
}

// segundo so faz falta na ultima hora, dia so a partir de 7 dias
function formatarTooltip(tempo: number) {
  const data = new Date(tempo)
  if (props.minutos <= 60) return data.toLocaleTimeString('pt-BR')
  if (props.minutos <= 1440) return data.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
  return data.toLocaleString('pt-BR', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' })
}

///// dados

const trechos = computed(() => {
  const lista = []
  for (const trecho of props.serie.trechos ?? []) {
    lista.push({ inicio: new Date(trecho.inicio).getTime(), fim: new Date(trecho.fim).getTime(), tipo: trecho.tipo })
  }
  return lista
})

const semLeitura = computed(() => trechos.value.filter(trecho => trecho.tipo === 'sem_leitura'))
const erros = computed(() => trechos.value.filter(trecho => trecho.tipo === 'erro'))

// valor null no meio de cada trecho corta a linha ali, se n ela ligava os dois lados com uma reta
const dados = computed(() => {
  const lista: { tempo: number, valor: number | null }[] = []
  for (const ponto of props.serie.pontos) {
    lista.push({ tempo: new Date(ponto.tempo).getTime(), valor: ponto.valor })
  }
  for (const trecho of trechos.value) {
    lista.push({ tempo: (trecho.inicio + trecho.fim) / 2, valor: null })
  }

  lista.sort((a, b) => a.tempo - b.tempo)
  return lista
})

///// eixo vertical

const eixo = computed(() => {
  let menor = Infinity
  let maior = -Infinity
  for (const ponto of props.serie.pontos) {
    menor = Math.min(menor, ponto.valor)
    maior = Math.max(maior, ponto.valor)
  }
  return calcularEixo(props.serie.nome, menor, maior)
})

///// grafico

// faixa do chao ate o teto do grafico, cada tipo de trecho com sua cor
function faixa(lista: typeof trechos.value, cor: string, opacidade: number) {
  const [menorEixo, maiorEixo] = eixo.value
  return decorative(rect(lista, {
    x1: 'inicio',
    x2: 'fim',
    y1: () => menorEixo,
    y2: () => maiorEixo,
    fill: cor,
    fillOpacity: opacidade,
    inset: 0,
  }))
}

const definicao = computed(() => {
  const [menorEixo, maiorEixo] = eixo.value
  // area pinta do chao do grafico ate a linha, no invertido o chao e o maior valor
  const chao = props.invertido ? maiorEixo : menorEixo
  const curva = chartCurves.monotone

  return defineChart({
    marks: [
      decorative(ruleX(linhas.value, { stroke: 'var(--ui-border)', strokeOpacity: 1 })),
      faixa(semLeitura.value, 'var(--color-neutral-500)', 0.2),
      faixa(erros.value, 'var(--color-amber-500)', 0.3),
      decorative(areaY(dados.value, { x: 'tempo', y1: () => chao, y2: 'valor', curve: curva, fill: 'url(#area)', fillOpacity: 1 })),
      lineY(dados.value, { x: 'tempo', y: 'valor', curve: curva, stroke: props.cor, strokeWidth: 2 }),
      crosshair({ x: true, y: false }),
    ],
    scales: {
      x: {
        scale: scaleLinear().domain([inicio.value, fim.value]),
        axis: { ticks: { values: rotulos.value, format: formatarRotulo } },
      },
      y: {
        scale: scaleLinear().domain([menorEixo, maiorEixo]),
        reverse: props.invertido,
        grid: true,
        axis: { ticks: { format: props.formatar } },
      },
    },
    gradients: [{
      id: 'area',
      x1: 0,
      y1: 0,
      x2: 0,
      y2: 1,
      stops: [
        { offset: 0, color: props.cor, opacity: 0.4 },
        { offset: 1, color: props.cor, opacity: 0.05 },
      ],
    }],
    focus: 'group-x',
    // sem isso o tooltip so aparece bem em cima do ponto
    maxFocusDistance: Number.POSITIVE_INFINITY,
  })
})

///// estatisticas

// minima e maxima de vdd, vindas do backend, n das medias do grafico
const estatisticas = computed(() => {
  const [tituloMenor, tituloMedia, tituloMaior] = props.titulosEstatisticas ?? ['Mínima', 'Média', 'Máxima']
  return [
    { titulo: tituloMenor, valor: props.serie.minimo ?? 0 },
    { titulo: tituloMedia, valor: props.serie.media ?? 0 },
    { titulo: tituloMaior, valor: props.serie.maximo ?? 0 },
  ]
})
</script>
