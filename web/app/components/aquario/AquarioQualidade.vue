<template>
  <UCard :ui="{ body: 'space-y-4' }">
    <div class="flex items-start justify-between gap-3">
      <div class="flex items-center gap-3">
        <div class="flex size-10 items-center justify-center rounded-full bg-emerald-500/10 text-emerald-500 ring ring-emerald-500/25 ring-inset">
          <UIcon
            name="i-lucide-droplets"
            class="size-5"
          />
        </div>

        <div>
          <h3 class="flex items-center gap-2 font-medium">
            Qualidade da água
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
        v-if="ultimaLeitura"
        class="text-xs text-muted"
      >
        {{ haQuanto(ultimaLeitura) }}
      </span>
    </div>

    <!-- 2 sensores no msm modulo, um do lado do outro -->
    <div class="grid gap-6 lg:grid-cols-2">
      <div
        v-for="medida in medidas"
        :key="medida.nome"
        class="space-y-3"
      >
        <div>
          <p class="text-sm font-medium text-muted">
            {{ medida.titulo }}
          </p>
          <p class="text-4xl font-semibold text-highlighted tabular-nums">
            {{ textoAtual(medida.serie, medida.formatar, fim === undefined) }}
          </p>
          <p class="text-sm text-muted">
            {{ medida.descricao }}
          </p>
        </div>

        <AquarioGrafico
          v-if="medida.serie"
          :serie="medida.serie"
          :rotulo="medida.titulo"
          :cor="medida.cor"
          :minutos="minutos"
          :fim="fim"
          :formatar="medida.formatar"
        />

        <p
          v-else
          class="text-sm text-muted"
        >
          Sem leituras nesse período.
        </p>
      </div>
    </div>
  </UCard>
</template>

<script setup lang="ts">
import type { ModuloIotRead } from '~/types/generated'

// fim do periodo no historico, sem ele e agora
const props = defineProps<{ modulo: ModuloIotRead, minutos: number, fim?: number }>()

const haQuanto = useHaQuanto()
const formatoTds = new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 0 })
const formatoTurbidez = new Intl.NumberFormat('pt-BR', { minimumFractionDigits: 1, maximumFractionDigits: 1 })

// nomes iguais ao catalogo do esp
const tds = computed(() => props.modulo.series.find(item => item.nome === 'tds'))
const turbidez = computed(() => props.modulo.series.find(item => item.nome === 'turbidez'))

const medidas = computed(() => [
  {
    nome: 'tds',
    titulo: 'Sólidos dissolvidos (TDS)',
    descricao: 'sais e minerais na água',
    cor: 'var(--color-emerald-500)',
    serie: tds.value,
    formatar: (valor: number) => `${formatoTds.format(valor)} ppm`,
  },
  {
    nome: 'turbidez',
    titulo: 'Turbidez',
    descricao: 'o quanto a água está turva',
    cor: 'var(--color-amber-500)',
    serie: turbidez.value,
    formatar: (valor: number) => `${formatoTurbidez.format(valor)} NTU`,
  },
])

// as 2 chegam juntas, pega a mais nova
const ultimaLeitura = computed(() => {
  const tempos: string[] = []
  for (const medida of medidas.value) {
    if (medida.serie?.atual) tempos.push(medida.serie.atual.tempo)
  }
  tempos.sort()
  return tempos.at(-1)
})
</script>
