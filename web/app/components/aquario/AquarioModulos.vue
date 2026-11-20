<template>
  <section class="space-y-4">
    <div class="flex flex-wrap items-center justify-between gap-3">
      <div class="flex items-center gap-2">
        <h2 class="text-lg font-semibold">
          Sensores
        </h2>

        <!-- so a ultima hora atualiza rapido -->
        <span
          v-if="minutos === 60"
          class="flex items-center gap-1.5 text-xs text-muted"
        >
          <span class="relative flex size-2">
            <span class="absolute inline-flex size-full animate-ping rounded-full bg-success opacity-75" />
            <span class="relative inline-flex size-2 rounded-full bg-success" />
          </span>
          ao vivo
        </span>
      </div>

      <div class="flex flex-wrap items-center gap-2">
        <UTabs
          v-model="minutos"
          :items="periodos"
          :content="false"
          size="sm"
        />

        <UButton
          label="Histórico"
          icon="i-lucide-history"
          color="neutral"
          variant="outline"
          @click="historicoAberto = true"
        />
      </div>
    </div>

    <AquarioHistorico
      v-model:open="historicoAberto"
      :aquario-id="aquarioId"
    />

    <div
      v-if="carregando"
      class="grid gap-4 lg:grid-cols-2"
    >
      <USkeleton class="h-96 w-full rounded-lg" />
      <USkeleton class="h-96 w-full rounded-lg" />
    </div>

    <UCard v-else-if="modulos.length === 0">
      <p class="text-sm text-muted">
        Nenhum módulo conectado no IoT.
      </p>
    </UCard>

    <div
      v-else
      class="grid gap-4 lg:grid-cols-2"
    >
      <template
        v-for="modulo in modulos"
        :key="modulo.serial"
      >
        <AquarioTemperatura
          v-if="modulo.tipo === TIPO_TEMPERATURA"
          :modulo="modulo"
          :minutos="minutosCarregados"
          :pode-editar="podeEditar"
          :pendente="pendentes[modulo.serial]"
          @comandar="comandar(modulo.serial, $event)"
        />

        <AquarioNivel
          v-else-if="modulo.tipo === TIPO_DISTANCIA"
          :modulo="modulo"
          :minutos="minutosCarregados"
        />

        <!-- 2 sensores, ocupa a linha toda -->
        <AquarioQualidade
          v-else-if="modulo.tipo === TIPO_QUALIDADE_AGUA"
          :modulo="modulo"
          :minutos="minutosCarregados"
          class="lg:col-span-2"
        />
      </template>
    </div>
  </section>
</template>

<script setup lang="ts">
import { FetchError } from 'ofetch'
import type { ModuloIotRead } from '~/types/generated'

const props = defineProps<{ aquarioId: number, podeEditar: boolean }>()

// igual ao TipoModulo do back
const TIPO_DISTANCIA = 1
const TIPO_TEMPERATURA = 2
const TIPO_QUALIDADE_AGUA = 3

// esp confirma em ~1s, o polling de 5s traz o estado novo
const ESPERA_CONFIRMACAO_MS = 15000

const periodos = [
  { label: '1 h', value: 60 },
  { label: '6 h', value: 360 },
  { label: '24 h', value: 1440 },
]

// 7 e 30 dias ficam no modal, buscam so qnd abre
const historicoAberto = ref(false)

const api = useApi()
const toast = useToast()
const modulos = ref<ModuloIotRead[]>([])
const carregando = ref(true)
const minutos = ref(60)

// rotulo do grafico so muda junto com os dados
const minutosCarregados = ref(minutos.value)

// serial -> estado pedido, sai qnd o esp confirma ou estoura o tempo
const pendentes = ref<Record<string, boolean>>({})

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
  const pedido = minutos.value

  try {
    modulos.value = await api(`/aquarios/${props.aquarioId}/modulos`, { query: { minutos: pedido } })
    minutosCarregados.value = pedido
    limparConfirmados()
  }
  catch {
    modulos.value = []
  }
  finally {
    carregando.value = false
  }
}

// estado do aquecedor sempre a cada 5s, periodo longo n muda tao rapido mas o rele precisa
useIntervalFn(carregar, 5000)
watch(minutos, carregar)
onMounted(carregar)
</script>
