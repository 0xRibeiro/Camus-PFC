<template>
  <UCard>
    <template #header>
      <h2 class="font-medium">
        Sensores
      </h2>
    </template>

    <USkeleton
      v-if="carregando"
      class="h-20 w-full"
    />

    <p
      v-else-if="modulos.length === 0"
      class="text-sm text-muted"
    >
      Nenhum módulo conectado no IoT.
    </p>

    <div
      v-else
      class="space-y-6"
    >
      <div
        v-for="modulo in modulos"
        :key="modulo.serial"
        class="space-y-3"
      >
        <div class="flex items-center gap-2">
          <span class="font-medium">{{ NOMES_TIPO[modulo.tipo] ?? 'Módulo' }}</span>
          <span class="text-xs text-muted">{{ modulo.serial }}</span>
        </div>

        <p
          v-if="modulo.series.length === 0"
          class="text-sm text-muted"
        >
          Sem leituras na última hora.
        </p>

        <div
          v-for="serie in modulo.series"
          :key="serie.nome"
          class="space-y-1"
        >
          <div class="flex items-baseline justify-between gap-2">
            <span class="text-3xl font-semibold">
              {{ ultimo(serie)?.valor.toFixed(1) }} {{ serie.unidade }}
            </span>
            <span class="text-xs text-muted">
              {{ haQuanto(ultimo(serie)?.tempo) }}
            </span>
          </div>

          <svg
            viewBox="0 0 300 60"
            preserveAspectRatio="none"
            class="h-16 w-full text-primary"
          >
            <polyline
              :points="linha(serie)"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              vector-effect="non-scaling-stroke"
            />
          </svg>
        </div>
      </div>
    </div>
  </UCard>
</template>

<script setup lang="ts">
import type { ModuloIotRead, PontoLeitura, SerieLeitura } from '~/types/generated'

const props = defineProps<{ aquarioId: number }>()

const NOMES_TIPO: Record<number, string> = { 1: 'Distância', 2: 'Temperatura' }

const api = useApi()
const modulos = ref<ModuloIotRead[]>([])
const carregando = ref(true)
const agora = useNow({ interval: 1000 })

function ultimo(serie: SerieLeitura): PontoLeitura | undefined {
  return serie.pontos[serie.pontos.length - 1]
}

function haQuanto(tempo: string | undefined): string {
  if (!tempo) return ''

  const segundos = Math.max(0, Math.round((agora.value.getTime() - new Date(tempo).getTime()) / 1000))
  if (segundos < 60) return `há ${segundos}s`
  return `há ${Math.floor(segundos / 60)} min`
}

// grafico simples, x pela ordem e y entre o menor e o maior valor
function linha(serie: SerieLeitura): string {
  let menor = Infinity
  let maior = -Infinity
  for (const ponto of serie.pontos) {
    menor = Math.min(menor, ponto.valor)
    maior = Math.max(maior, ponto.valor)
  }

  const faixa = maior - menor || 1
  const passo = 300 / Math.max(1, serie.pontos.length - 1)

  const coordenadas: string[] = []
  serie.pontos.forEach((ponto, indice) => {
    const y = 58 - ((ponto.valor - menor) / faixa) * 56
    coordenadas.push(`${indice * passo},${y}`)
  })
  return coordenadas.join(' ')
}

async function carregar() {
  try {
    modulos.value = await api(`/aquarios/${props.aquarioId}/modulos`)
  }
  catch {
    modulos.value = []
  }
  finally {
    carregando.value = false
  }
}

useIntervalFn(carregar, 5000)
onMounted(carregar)
</script>
