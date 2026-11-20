<template>
  <UCard :ui="{ body: 'space-y-4' }">
    <div class="flex items-start justify-between gap-3">
      <div class="flex items-center gap-3">
        <div class="flex size-10 items-center justify-center rounded-full bg-orange-500/10 text-orange-500 ring ring-orange-500/25 ring-inset">
          <UIcon
            name="i-lucide-thermometer"
            class="size-5"
          />
        </div>

        <div>
          <h3 class="font-medium">
            Temperatura da água
          </h3>
        </div>
      </div>

      <span
        v-if="serie?.atual"
        class="text-xs text-muted"
      >
        {{ haQuanto(serie.atual.tempo) }}
      </span>
    </div>

    <p class="text-4xl font-semibold text-highlighted tabular-nums">
      {{ textoAtual(serie, formatar, fim === undefined) }}
    </p>

    <AquarioGrafico
      v-if="serie"
      :serie="serie"
      rotulo="Temperatura"
      cor="var(--color-orange-500)"
      :minutos="minutos"
      :fim="fim"
      :formatar="formatar"
    />

    <p
      v-else
      class="text-sm text-muted"
    >
      Sem leituras nesse período.
    </p>

    <!-- rele do modulo de temperatura e o aquecedor -->
    <div
      v-if="modulo.ligado !== null && modulo.ligado !== undefined"
      class="flex flex-wrap items-center justify-between gap-3 rounded-xl p-4 ring ring-inset transition-colors"
      :class="ligadoNaTela ? 'bg-orange-500/10 ring-orange-500/40' : 'bg-elevated/50 ring-default'"
    >
      <div class="flex items-center gap-3">
        <div
          class="flex size-11 items-center justify-center rounded-full transition-colors"
          :class="ligadoNaTela ? 'bg-orange-500 text-white shadow-lg shadow-orange-500/40' : 'bg-elevated text-muted'"
        >
          <UIcon
            name="i-lucide-flame"
            class="size-6"
            :class="{ 'animate-pulse': ligadoNaTela && !aguardando }"
          />
        </div>

        <div>
          <p class="font-medium">
            Aquecedor
          </p>
          <p class="text-sm text-muted">
            {{ textoEstado }}
          </p>
        </div>
      </div>

      <UButton
        v-if="podeEditar"
        :label="ligadoNaTela ? 'Desligar' : 'Ligar'"
        :icon="ligadoNaTela ? 'i-lucide-power-off' : 'i-lucide-power'"
        :color="ligadoNaTela ? 'neutral' : 'warning'"
        :variant="ligadoNaTela ? 'outline' : 'solid'"
        :loading="aguardando"
        :disabled="aguardando"
        @click="emit('comandar', !ligadoNaTela)"
      />
    </div>
  </UCard>
</template>

<script setup lang="ts">
import type { ModuloIotRead } from '~/types/generated'

// sem o default o vue transforma o pendente q n foi passado em false, e o card ficava "desligando"
const props = withDefaults(defineProps<{
  modulo: ModuloIotRead
  minutos: number
  podeEditar: boolean
  // estado pedido enquanto o esp n confirma
  pendente?: boolean
  // fim do periodo no historico, sem ele e agora
  fim?: number
}>(), { pendente: undefined, fim: undefined })

const emit = defineEmits<{ comandar: [ligar: boolean] }>()

const haQuanto = useHaQuanto()
const formatoTemperatura = new Intl.NumberFormat('pt-BR', { minimumFractionDigits: 1, maximumFractionDigits: 1 })

const serie = computed(() => props.modulo.series.find(item => item.nome === 'temperatura') ?? props.modulo.series[0])
const aguardando = computed(() => props.pendente !== undefined)
const ligadoNaTela = computed(() => props.pendente ?? props.modulo.ligado ?? false)

const textoEstado = computed(() => {
  if (aguardando.value) return props.pendente ? 'Ligando, esperando o IoT…' : 'Desligando, esperando o IoT…'
  if (ligadoNaTela.value) return 'Ligado, aquecendo a água'
  return 'Desligado'
})

function formatar(valor: number) {
  return `${formatoTemperatura.format(valor)} °C`
}
</script>
