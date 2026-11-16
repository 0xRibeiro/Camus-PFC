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

          <UCalendar
            v-model="periodo"
            range
            locale="pt-BR"
            :number-of-months="telaLarga ? 2 : 1"
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
      class="w-32"
    />
  </div>
</template>

<script setup lang="ts">
import { CalendarDate, getLocalTimeZone, today } from '@internationalized/date'

export interface Periodo {
  start: CalendarDate | undefined
  end: CalendarDate | undefined
}

interface Atalho {
  label: string
  dias?: number
  meses?: number
}

const periodo = defineModel<Periodo>('periodo', { required: true })
const agrupamento = defineModel<'dia' | 'semana' | 'mes'>('agrupamento', { required: true })

const telaLarga = useMediaQuery('(min-width: 40rem)')
const hoje = today(getLocalTimeZone())

const atalhos: Atalho[] = [
  { label: 'Últimos 7 dias', dias: 7 },
  { label: 'Últimos 14 dias', dias: 14 },
  { label: 'Últimos 30 dias', dias: 30 },
  { label: 'Últimos 3 meses', meses: 3 },
  { label: 'Últimos 6 meses', meses: 6 },
  { label: 'Último ano', meses: 12 },
]

const agrupamentos = [
  { label: 'Diário', value: 'dia' },
  { label: 'Semanal', value: 'semana' },
  { label: 'Mensal', value: 'mes' },
]

// hoje conta como 1 dos dias
function inicioDoAtalho(atalho: Atalho) {
  if (atalho.meses) return hoje.subtract({ months: atalho.meses }).add({ days: 1 })
  return hoje.subtract({ days: (atalho.dias ?? 1) - 1 })
}

function atalhoAtivo(atalho: Atalho) {
  const { start, end } = periodo.value
  if (!start || !end) return false
  return end.compare(hoje) === 0 && start.compare(inicioDoAtalho(atalho)) === 0
}

function escolherAtalho(atalho: Atalho) {
  periodo.value = { start: inicioDoAtalho(atalho), end: hoje }
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
