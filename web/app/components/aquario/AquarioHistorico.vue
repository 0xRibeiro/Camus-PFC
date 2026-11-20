<template>
  <UModal
    v-model:open="open"
    title="Histórico dos sensores"
    description="Leituras guardadas dos últimos dias. Aqui não atualiza sozinho, só quando abre ou troca o período."
    fullscreen
  >
    <template #body>
      <div class="mx-auto max-w-6xl space-y-4">
        <UTabs
          v-model="minutos"
          :items="periodos"
          :content="false"
          class="w-fit"
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
            <!-- aquecedor n liga por aqui, so na tela de cima -->
            <AquarioTemperatura
              v-if="modulo.tipo === TIPO_TEMPERATURA"
              :modulo="modulo"
              :minutos="minutosCarregados"
              :pode-editar="false"
            />

            <AquarioNivel
              v-else-if="modulo.tipo === TIPO_DISTANCIA"
              :modulo="modulo"
              :minutos="minutosCarregados"
            />

            <AquarioQualidade
              v-else-if="modulo.tipo === TIPO_QUALIDADE_AGUA"
              :modulo="modulo"
              :minutos="minutosCarregados"
              class="lg:col-span-2"
            />
          </template>
        </div>
      </div>
    </template>
  </UModal>
</template>

<script setup lang="ts">
import type { ModuloIotRead } from '~/types/generated'

const props = defineProps<{ aquarioId: number }>()
const open = defineModel<boolean>('open', { required: true })

// igual ao TipoModulo do back
const TIPO_DISTANCIA = 1
const TIPO_TEMPERATURA = 2
const TIPO_QUALIDADE_AGUA = 3

const periodos = [
  { label: '7 dias', value: 10080 },
  { label: '30 dias', value: 43200 },
]

const api = useApi()
const modulos = ref<ModuloIotRead[]>([])
const carregando = ref(true)
const minutos = ref(10080)
const minutosCarregados = ref(minutos.value)

// busca uma vez, sem polling, periodo longo n muda de 5 em 5s
async function carregar() {
  const pedido = minutos.value
  carregando.value = true

  try {
    modulos.value = await api(`/aquarios/${props.aquarioId}/modulos`, { query: { minutos: pedido } })
    minutosCarregados.value = pedido
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
watch(minutos, carregar)
</script>
