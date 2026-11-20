<template>
  <UCard :ui="{ body: 'space-y-4' }">
    <div class="flex items-start justify-between gap-3">
      <div class="flex items-center gap-3">
        <div class="flex size-10 items-center justify-center rounded-full bg-sky-500/10 text-sky-500 ring ring-sky-500/25 ring-inset">
          <UIcon
            name="i-lucide-waves"
            class="size-5"
          />
        </div>

        <div>
          <h3 class="font-medium">
            Nível da água
          </h3>
          <p class="text-xs text-muted">
            Módulo {{ modulo.serial }}
          </p>
        </div>
      </div>

      <span
        v-if="serie?.atual"
        class="text-xs text-muted"
      >
        {{ haQuanto(serie.atual.tempo) }}
      </span>
    </div>

    <div class="flex flex-wrap items-end justify-between gap-2">
      <div>
        <p class="text-4xl font-semibold text-highlighted tabular-nums">
          {{ textoAtual(serie, formatar) }}
        </p>
        <p class="text-sm text-muted">
          do sensor até a água
        </p>
      </div>

      <!-- distancia menor e agua mais alta -->
      <UBadge
        v-if="variacao !== null"
        :color="Math.abs(variacao) < 0.5 ? 'neutral' : variacao > 0 ? 'info' : 'warning'"
        variant="subtle"
        :icon="Math.abs(variacao) < 0.5 ? 'i-lucide-minus' : variacao > 0 ? 'i-lucide-arrow-up' : 'i-lucide-arrow-down'"
      >
        {{ textoVariacao }}
      </UBadge>
    </div>

    <AquarioGrafico
      v-if="serie"
      :serie="serie"
      rotulo="Distância até a água"
      cor="var(--color-sky-500)"
      :minutos="minutos"
      :formatar="formatar"
      :titulos-estatisticas="['Mais cheio', 'Média', 'Mais vazio']"
      invertido
    />

    <p
      v-else
      class="text-sm text-muted"
    >
      Sem leituras nesse período.
    </p>

    <p class="flex items-start gap-2 text-xs text-muted">
      <UIcon
        name="i-lucide-info"
        class="mt-0.5 size-3.5 shrink-0"
      />
      O sensor fica em cima do aquário e mede até a superfície. Quanto menor a distância, mais cheio. No gráfico, a linha sobe quando a água sobe.
    </p>
  </UCard>
</template>

<script setup lang="ts">
import type { ModuloIotRead } from '~/types/generated'

const props = defineProps<{
  modulo: ModuloIotRead
  minutos: number
}>()

const haQuanto = useHaQuanto()
const formatoDistancia = new Intl.NumberFormat('pt-BR', { minimumFractionDigits: 1, maximumFractionDigits: 1 })

const serie = computed(() => props.modulo.series.find(item => item.nome === 'distancia') ?? props.modulo.series[0])

function formatar(valor: number) {
  return `${formatoDistancia.format(valor)} cm`
}

// positivo e agua subindo no periodo
const variacao = computed(() => {
  const pontos = serie.value?.pontos ?? []
  const primeiro = pontos[0]
  const ultimo = pontos.at(-1)
  if (!primeiro || !ultimo || pontos.length < 2) return null
  return primeiro.valor - ultimo.valor
})

const textoVariacao = computed(() => {
  if (variacao.value === null) return ''
  if (Math.abs(variacao.value) < 0.5) return 'Nível estável'
  const quanto = formatar(Math.abs(variacao.value))
  return variacao.value > 0 ? `Subiu ${quanto}` : `Baixou ${quanto}`
})
</script>
