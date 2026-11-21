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
          <h3 class="flex items-center gap-2 font-medium">
            Nível da água
            <UBadge
              v-if="modulo.removido"
              label="Removido"
              color="neutral"
              variant="subtle"
              size="sm"
            />
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

    <div>
      <p class="text-4xl font-semibold text-highlighted tabular-nums">
        {{ textoAtual(serie, formatar, fim === undefined) }}
      </p>
      <p class="text-sm text-muted">
        do sensor até a água
      </p>
    </div>

    <AquarioGrafico
      v-if="serie"
      :serie="serie"
      rotulo="Distância até a água"
      cor="var(--color-sky-500)"
      :minutos="minutos"
      :fim="fim"
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
  </UCard>
</template>

<script setup lang="ts">
import type { ModuloIotRead } from '~/types/generated'

const props = defineProps<{
  modulo: ModuloIotRead
  minutos: number
  // fim do periodo no historico, sem ele e agora
  fim?: number
}>()

const haQuanto = useHaQuanto()
const formatoDistancia = new Intl.NumberFormat('pt-BR', { minimumFractionDigits: 1, maximumFractionDigits: 1 })

const serie = computed(() => props.modulo.series.find(item => item.nome === 'distancia') ?? props.modulo.series[0])

function formatar(valor: number) {
  return `${formatoDistancia.format(valor)} cm`
}
</script>
