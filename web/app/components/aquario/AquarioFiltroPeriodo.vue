<template>
  <div class="flex flex-wrap items-center gap-2">
    <UPopover :content="{ align: 'start' }">
      <UButton
        color="neutral"
        variant="ghost"
        icon="i-lucide-calendar"
        class="group data-[state=open]:bg-elevated"
      >
        <span class="truncate">{{ textoPeriodo }}</span>

        <template #trailing>
          <UIcon
            name="i-lucide-chevron-down"
            class="size-5 shrink-0 text-dimmed transition-transform duration-200 group-data-[state=open]:rotate-180"
          />
        </template>
      </UButton>

      <template #content>
        <div class="flex flex-col sm:flex-row sm:items-stretch sm:divide-x divide-default">
          <div class="flex flex-wrap justify-center border-b border-default sm:flex-col sm:flex-nowrap sm:border-b-0">
            <UButton
              v-for="atalho in atalhos"
              :key="atalho.label"
              :label="atalho.label"
              color="neutral"
              variant="ghost"
              class="rounded-none px-4"
              :class="atalhoAtivo(atalho) ? 'bg-elevated' : 'hover:bg-elevated/50'"
              @click="escolherAtalho(atalho)"
            />
          </div>

          <!-- antes disso o influx ja apagou -->
          <UCalendar
            v-model="periodo"
            range
            locale="pt-BR"
            :number-of-months="telaLarga ? 2 : 1"
            :min-value="primeiroDia"
            :max-value="hoje"
            class="p-2"
          />
        </div>
      </template>
    </UPopover>

    <USelect
      v-model="agrupamento"
      :items="agrupamentos"
      variant="ghost"
      class="w-36"
    />
  </div>
</template>

<script setup lang="ts">
import { getLocalTimeZone, today } from '@internationalized/date'
import type { CalendarDate } from '@internationalized/date'
import type { Periodo } from '~/composables/useDashboard'

// dias q o influx guarda, igual a retencao do bucket
const DIAS_GUARDADOS = 30

interface Atalho {
  label: string
  // quantos dias pra tras o periodo comeca e termina, 0 = hoje
  de: number
  ate: number
}

const periodo = defineModel<Periodo>('periodo', { required: true })
const agrupamento = defineModel<'auto' | 'hora' | 'dia'>('agrupamento', { required: true })

const telaLarga = useMediaQuery('(min-width: 40rem)')
const hoje = today(getLocalTimeZone())
const primeiroDia = hoje.subtract({ days: DIAS_GUARDADOS - 1 })

const atalhos: Atalho[] = [
  { label: 'Hoje', de: 0, ate: 0 },
  { label: 'Ontem', de: 1, ate: 1 },
  { label: 'Últimos 7 dias', de: 6, ate: 0 },
  { label: 'Últimos 14 dias', de: 13, ate: 0 },
  { label: 'Últimos 30 dias', de: DIAS_GUARDADOS - 1, ate: 0 },
]

// por dia num dia so daria 1 ponto, ai n tem grafico
const umDiaSo = computed(() => {
  const { start, end } = periodo.value
  return !start || !end || start.compare(end) === 0
})

const agrupamentos = computed(() => [
  { label: 'Automático', value: 'auto' },
  { label: 'Por hora', value: 'hora' },
  { label: 'Por dia', value: 'dia', disabled: umDiaSo.value },
])

// voltou pra um dia so com o por dia escolhido, troca pro automatico
watch(umDiaSo, (sim) => {
  if (sim && agrupamento.value === 'dia') agrupamento.value = 'auto'
})

function atalhoAtivo(atalho: Atalho) {
  const { start, end } = periodo.value
  if (!start || !end) return false
  return start.compare(hoje.subtract({ days: atalho.de })) === 0 && end.compare(hoje.subtract({ days: atalho.ate })) === 0
}

function escolherAtalho(atalho: Atalho) {
  periodo.value = { start: hoje.subtract({ days: atalho.de }), end: hoje.subtract({ days: atalho.ate }) }
}

const formatoData = new Intl.DateTimeFormat('pt-BR', { day: '2-digit', month: 'short', year: 'numeric' })

function formatar(data: CalendarDate) {
  return formatoData.format(data.toDate(getLocalTimeZone()))
}

// um dia so quando n tem fim ou e igual
const textoPeriodo = computed(() => {
  const { start, end } = periodo.value
  if (!start) return 'Escolha um período'
  if (!end || start.compare(end) === 0) return formatar(start)
  return `${formatar(start)} - ${formatar(end)}`
})
</script>
