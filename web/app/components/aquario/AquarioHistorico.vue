<template>
  <UModal
    v-model:open="open"
    title="Histórico dos sensores"
    description="Leituras guardadas dos últimos 30 dias. Aqui não atualiza sozinho, só quando abre ou troca o período."
    fullscreen
  >
    <template #body>
      <div class="mx-auto max-w-6xl space-y-4">
        <AquarioFiltroPeriodo
          v-model:periodo="periodo"
          v-model:agrupamento="agrupamento"
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
            :key="modulo.serial ?? `removido-${modulo.tipo}`"
          >
            <!-- aquecedor n liga por aqui, so na tela de cima -->
            <AquarioTemperatura
              v-if="modulo.tipo === TIPO_TEMPERATURA"
              :modulo="modulo"
              :minutos="carregado.minutos"
              :fim="carregado.fim"
              :pode-editar="false"
            />

            <AquarioNivel
              v-else-if="modulo.tipo === TIPO_DISTANCIA"
              :modulo="modulo"
              :minutos="carregado.minutos"
              :fim="carregado.fim"
            />

            <AquarioQualidade
              v-else-if="modulo.tipo === TIPO_QUALIDADE_AGUA"
              :modulo="modulo"
              :minutos="carregado.minutos"
              :fim="carregado.fim"
              class="lg:col-span-2"
            />
          </template>
        </div>
      </div>
    </template>
  </UModal>
</template>

<script setup lang="ts">
import { getLocalTimeZone, today } from '@internationalized/date'
import type { Periodo } from '~/composables/useDashboard'
import type { ModuloIotRead } from '~/types/generated'

const props = defineProps<{ aquarioId: number }>()
const open = defineModel<boolean>('open', { required: true })

// igual ao TipoModulo do back
const TIPO_DISTANCIA = 1
const TIPO_TEMPERATURA = 2
const TIPO_QUALIDADE_AGUA = 3

const fuso = getLocalTimeZone()
const hoje = today(fuso)

const api = useApi()
const modulos = ref<ModuloIotRead[]>([])
const carregando = ref(true)
const periodo = ref<Periodo>({ start: hoje.subtract({ days: 6 }), end: hoje })
const agrupamento = ref<'auto' | 'hora' | 'dia'>('auto')

// grafico so muda junto com os dados
const carregado = ref({ minutos: 10080, fim: Date.now() })

// do comeco do primeiro dia ate o fim do ultimo, ou ate agora se o ultimo e hoje
function intervalo() {
  const { start, end } = periodo.value
  if (!start) return null

  const ultimo = end ?? start
  const inicio = start.toDate(fuso).getTime()
  const fim = ultimo.compare(hoje) === 0 ? Date.now() : ultimo.add({ days: 1 }).toDate(fuso).getTime()
  return { inicio, fim }
}

// busca uma vez, sem polling, historico n muda de 5 em 5s
async function carregar() {
  const pedido = intervalo()
  if (!pedido) return
  carregando.value = true

  try {
    modulos.value = await api(`/aquarios/${props.aquarioId}/modulos`, {
      query: {
        inicio: new Date(pedido.inicio).toISOString(),
        fim: new Date(pedido.fim).toISOString(),
        agrupamento: agrupamento.value,
      },
    })
    carregado.value = { minutos: (pedido.fim - pedido.inicio) / 60000, fim: pedido.fim }
  }
  catch {
    modulos.value = []
  }
  finally {
    carregando.value = false
  }
}

watch(open, (aberto) => {
  if (aberto) carregar()
})

// no meio da escolha do calendario so tem o comeco, espera o fim
watch([periodo, agrupamento], () => {
  if (periodo.value.end) carregar()
})
</script>
