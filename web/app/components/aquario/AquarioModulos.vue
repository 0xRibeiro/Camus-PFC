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

          <!-- so atuador tem ligado, fica cinza ate o esp confirmar -->
          <USwitch
            v-if="modulo.ligado !== null && modulo.ligado !== undefined"
            class="ml-auto"
            :model-value="pendentes[modulo.serial] ?? modulo.ligado"
            :loading="pendentes[modulo.serial] !== undefined"
            :disabled="!podeEditar || pendentes[modulo.serial] !== undefined"
            :label="(pendentes[modulo.serial] ?? modulo.ligado) ? 'Relé ligado' : 'Relé desligado'"
            @update:model-value="comandar(modulo.serial, $event)"
          />
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
import { FetchError } from 'ofetch'
import type { ModuloIotRead, PontoLeitura, SerieLeitura } from '~/types/generated'

const props = defineProps<{ aquarioId: number, podeEditar: boolean }>()

const NOMES_TIPO: Record<number, string> = { 1: 'Distância', 2: 'Temperatura' }

// esp confirma em ~1s, o polling de 5s traz o estado novo
const ESPERA_CONFIRMACAO_MS = 15000

const api = useApi()
const toast = useToast()
const modulos = ref<ModuloIotRead[]>([])
const carregando = ref(true)
const agora = useNow({ interval: 1000 })

// serial -> estado pedido, sai qnd o esp confirma ou estoura o tempo
const pendentes = ref<Record<string, boolean>>({})

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

function mensagemErro(error: unknown, padrao: string): string {
  if (error instanceof FetchError && typeof error.data?.detail === 'string') {
    return error.data.detail
  }
  return padrao
}

// tira do pendente quem ja ta no estado pedido
function limparConfirmados() {
  for (const modulo of modulos.value) {
    if (pendentes.value[modulo.serial] === modulo.ligado) {
      delete pendentes.value[modulo.serial]
    }
  }
}

async function comandar(serial: string, ligar: boolean) {
  pendentes.value[serial] = ligar

  try {
    await api(`/aquarios/${props.aquarioId}/modulos/${serial}/comando`, {
      method: 'POST',
      body: { acao: ligar ? 'ativar' : 'desativar' },
    })
  }
  catch (error) {
    delete pendentes.value[serial]
    toast.add({ title: mensagemErro(error, 'Não foi possível enviar o comando'), color: 'error' })
    return
  }

  // sem confirmacao, volta pro estado real e avisa
  setTimeout(() => {
    if (pendentes.value[serial] === ligar) {
      delete pendentes.value[serial]
      toast.add({ title: 'O IoT não confirmou o comando', color: 'warning' })
    }
  }, ESPERA_CONFIRMACAO_MS)

  await carregar()
}

async function carregar() {
  try {
    modulos.value = await api(`/aquarios/${props.aquarioId}/modulos`)
    limparConfirmados()
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
