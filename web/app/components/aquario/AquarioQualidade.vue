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
          <h3 class="font-medium">
            Qualidade da água
          </h3>
          <p class="text-xs text-muted">
            Módulo {{ modulo.serial }}
          </p>
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
            {{ medida.serie?.atual ? medida.formatar(medida.serie.atual.valor) : '—' }}
          </p>
          <p class="text-sm text-muted">
            {{ medida.descricao }}
          </p>
        </div>

        <AquarioGrafico
          v-if="medida.serie"
          :pontos="medida.serie.pontos"
          :rotulo="medida.titulo"
          :cor="medida.cor"
          :minutos="minutos"
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

const props = defineProps<{ modulo: ModuloIotRead, minutos: number }>()

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
