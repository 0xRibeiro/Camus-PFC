<template>
  <UCard :class="card">
    <template #header>
      <div class="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 class="font-medium">
            XP ganho
          </h2>
          <p class="text-sm text-muted">
            <span class="font-semibold text-primary tabular-nums">{{ totalPeriodo }} XP</span>
            nos últimos {{ dias }} dias
          </p>
        </div>

        <UTabs
          v-model="dias"
          :items="periodos"
          :content="false"
          size="xs"
        />
      </div>
    </template>

    <!-- o chart n tem pattern, entao o xadrez fica aqui e a area usa pelo id -->
    <svg
      v-if="estilo === 'xadrez'"
      class="absolute size-0"
      aria-hidden="true"
    >
      <defs>
        <pattern
          id="xadrez-xp"
          width="10"
          height="10"
          patternUnits="userSpaceOnUse"
        >
          <rect
            width="10"
            height="10"
            style="fill: var(--ui-bg)"
          />
          <rect
            width="5"
            height="5"
            style="fill: var(--ui-border-accented)"
          />
          <rect
            x="5"
            y="5"
            width="5"
            height="5"
            style="fill: var(--ui-border-accented)"
          />
        </pattern>
      </defs>
    </svg>

    <USkeleton
      v-if="carregando"
      class="aspect-[3] w-full"
    />

    <UChart
      v-else
      :definition="definicao"
      :aspect-ratio="3"
      :aria-label="`XP ganho por dia nos últimos ${dias} dias`"
    >
      <template #tooltip="{ primaryPoint }">
        <p class="text-xs text-muted">
          {{ formatarDia(primaryPoint.datum.tempo) }}
        </p>
        <p class="font-semibold tabular-nums">
          {{ primaryPoint.datum.pontos }} XP
        </p>
      </template>
    </UChart>
  </UCard>
</template>

<script setup lang="ts">
import { areaY, defineChart, dot, lineY } from '@tanstack/charts'
import { crosshair } from '@tanstack/charts/crosshair'
import { decorative } from '@tanstack/charts/mark/decorative'
import { scaleLinear } from '@tanstack/charts/scales/linear'
import { chartCurves } from '#ui/utils/chart'
import type { XpDiaRead } from '~/types/generated'

const { estilo, card } = usePerfilVisual()

const DIA = 24 * 60 * 60 * 1000
const COR = 'var(--ui-primary)'

// valor do tab vai como string, por isso o Number la embaixo
const periodos = [
  { label: '7 dias', value: 7 },
  { label: '30 dias', value: 30 },
]

const dias = ref(7)
const lista = ref<XpDiaRead[]>([])
const carregando = ref(true)

async function buscar() {
  carregando.value = true
  try {
    lista.value = await useApi()('/pontuacao/xp/dias', { query: { dias: Number(dias.value) } })
  }
  catch {
    lista.value = []
  }
  carregando.value = false
}

watch(dias, buscar, { immediate: true })

// a data vem 2026-11-20, sem o T00:00 o js le em utc e volta 1 dia
const dados = computed(() => {
  const pontos = []
  for (const item of lista.value) {
    pontos.push({ tempo: new Date(`${item.data}T00:00:00`).getTime(), pontos: item.pontos })
  }
  return pontos
})

const totalPeriodo = computed(() => {
  let total = 0
  for (const item of lista.value) total += item.pontos
  return total
})

// teto redondo, sem xp nenhum fica 0 a 10 pra linha n ficar no meio
const teto = computed(() => {
  let maior = 0
  for (const item of lista.value) maior = Math.max(maior, item.pontos)
  if (maior === 0) return 10
  const passo = maior <= 50 ? 10 : maior <= 200 ? 50 : 100
  return Math.ceil(maior / passo) * passo
})

// 7 dias marca todo dia, 30 so de 5 em 5 se n embola
const rotulos = computed(() => {
  const passo = Number(dias.value) <= 7 ? 1 : 5
  const marcas = []
  for (let indice = dados.value.length - 1; indice >= 0; indice -= passo) {
    marcas.push(dados.value[indice]!.tempo)
  }
  return marcas
})

function formatarRotulo(tempo: number) {
  const data = new Date(tempo)
  if (Number(dias.value) <= 7) return data.toLocaleDateString('pt-BR', { weekday: 'short' }).replace('.', '')
  return data.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' })
}

function formatarDia(tempo: number) {
  return new Date(tempo).toLocaleDateString('pt-BR', { weekday: 'long', day: '2-digit', month: '2-digit' })
}

// xadrez: quadriculado embaixo da linha e um degrade do fundo por cima, pra ele sumir descendo
// vidro: area branca fosca
function areas(curva: typeof chartCurves.monotone) {
  if (estilo.value === 'vidro') {
    return [decorative(areaY(dados.value, { x: 'tempo', y1: () => 0, y2: 'pontos', curve: curva, fill: 'url(#area-xp-vidro)', fillOpacity: 1 }))]
  }
  if (estilo.value !== 'xadrez') {
    return [decorative(areaY(dados.value, { x: 'tempo', y1: () => 0, y2: 'pontos', curve: curva, fill: 'url(#area-xp)', fillOpacity: 1 }))]
  }
  return [
    decorative(areaY(dados.value, { x: 'tempo', y1: () => 0, y2: 'pontos', curve: curva, fill: 'url(#xadrez-xp)', fillOpacity: 1 })),
    decorative(areaY(dados.value, { x: 'tempo', y1: () => 0, y2: 'pontos', curve: curva, fill: 'url(#area-xp-some)', fillOpacity: 1 })),
  ]
}

const definicao = computed(() => {
  const curva = chartCurves.monotone
  const inicio = dados.value[0]?.tempo ?? Date.now() - DIA
  const fim = dados.value.at(-1)?.tempo ?? Date.now()

  return defineChart({
    marks: [
      ...areas(curva),
      // no vidro a linha fica tracejada, meio fantasma
      lineY(dados.value, { x: 'tempo', y: 'pontos', curve: curva, stroke: COR, strokeWidth: 2, strokeDasharray: estilo.value === 'vidro' ? '6 4' : undefined }),
      // bolinha de cada dia, menor no de 30 pra n virar uma linha grossa
      dot(dados.value, {
        x: 'tempo',
        y: 'pontos',
        r: Number(dias.value) <= 7 ? 5 : 3,
        fill: estilo.value === 'vidro' ? 'white' : 'var(--ui-bg)',
        fillOpacity: estilo.value === 'vidro' ? 0.5 : 1,
        stroke: COR,
        strokeWidth: 2,
      }),
      crosshair({ x: true, y: false }),
    ],
    scales: {
      x: {
        scale: scaleLinear().domain([inicio, fim]),
        axis: { ticks: { values: rotulos.value, format: formatarRotulo } },
      },
      y: {
        scale: scaleLinear().domain([0, teto.value]),
        grid: true,
      },
    },
    gradients: [{
      id: 'area-xp',
      x1: 0,
      y1: 0,
      x2: 0,
      y2: 1,
      stops: [
        { offset: 0, color: COR, opacity: 0.3 },
        { offset: 1, color: COR, opacity: 0.02 },
      ],
    }, {
      id: 'area-xp-vidro',
      x1: 0,
      y1: 0,
      x2: 0,
      y2: 1,
      stops: [
        { offset: 0, color: 'white', opacity: 0.55 },
        { offset: 1, color: 'white', opacity: 0.05 },
      ],
    }, {
      id: 'area-xp-some',
      x1: 0,
      y1: 0,
      x2: 0,
      y2: 1,
      stops: [
        { offset: 0, color: 'var(--ui-bg)', opacity: 0 },
        { offset: 1, color: 'var(--ui-bg)', opacity: 0.9 },
      ],
    }],
    focus: 'group-x',
    maxFocusDistance: Number.POSITIVE_INFINITY,
  })
})
</script>
