<template>
  <!-- versao simples do filtro da dashboard: atalhos do lado e o calendario -->
  <UPopover :content="{ align: 'start' }">
    <UButton
      color="neutral"
      variant="outline"
      icon="i-lucide-calendar"
      class="group w-full justify-start data-[state=open]:bg-elevated"
    >
      <span class="truncate">{{ textoPeriodo }}</span>

      <template #trailing>
        <UIcon
          name="i-lucide-chevron-down"
          class="ms-auto size-5 shrink-0 text-dimmed transition-transform duration-200 group-data-[state=open]:rotate-180"
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

        <!-- antes disso a limpeza do back ja apagou -->
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
</template>

<script setup lang="ts">
import { getLocalTimeZone, today } from '@internationalized/date'
import type { CalendarDate } from '@internationalized/date'
import type { Periodo } from '~/composables/useDashboard'

// dias q o back guarda os logs, igual ao DIAS_GUARDADOS da limpeza
const DIAS_GUARDADOS = 60

interface Atalho {
  label: string
  // quantos dias pra tras o periodo comeca, sempre termina hoje
  dias: number
}

const periodo = defineModel<Periodo>('periodo', { required: true })

const telaLarga = useMediaQuery('(min-width: 40rem)')
const hoje = today(getLocalTimeZone())
const primeiroDia = hoje.subtract({ days: DIAS_GUARDADOS - 1 })

const atalhos: Atalho[] = [
  { label: 'Hoje', dias: 0 },
  { label: 'Últimos 3 dias', dias: 2 },
  { label: 'Últimos 7 dias', dias: 6 },
  { label: 'Últimos 14 dias', dias: 13 },
]

function atalhoAtivo(atalho: Atalho) {
  const { start, end } = periodo.value
  if (!start || !end) return false
  return start.compare(hoje.subtract({ days: atalho.dias })) === 0 && end.compare(hoje) === 0
}

function escolherAtalho(atalho: Atalho) {
  periodo.value = { start: hoje.subtract({ days: atalho.dias }), end: hoje }
}

const formatoData = new Intl.DateTimeFormat('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric' })

function formatar(data: CalendarDate) {
  return formatoData.format(data.toDate(getLocalTimeZone()))
}

// nome do atalho qnd bate com um, se n um dia so ou o intervalo
const textoPeriodo = computed(() => {
  const { start, end } = periodo.value
  if (!start) return 'Escolha um período'
  for (const atalho of atalhos) {
    if (atalhoAtivo(atalho)) return atalho.label
  }
  if (!end || start.compare(end) === 0) return formatar(start as CalendarDate)
  return `${formatar(start as CalendarDate)} - ${formatar(end as CalendarDate)}`
})
</script>
