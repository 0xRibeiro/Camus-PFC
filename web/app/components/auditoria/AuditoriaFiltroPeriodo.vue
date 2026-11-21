<template>
  <!-- versao simples do filtro da dashboard: so o calendario, sem atalhos -->
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
      <UCalendar
        v-model="periodo"
        range
        locale="pt-BR"
        :number-of-months="telaLarga ? 2 : 1"
        :max-value="hoje"
        class="p-2"
      />
    </template>
  </UPopover>
</template>

<script setup lang="ts">
import { getLocalTimeZone, today } from '@internationalized/date'
import type { CalendarDate } from '@internationalized/date'
import type { Periodo } from '~/composables/useDashboard'

const periodo = defineModel<Periodo>('periodo', { required: true })

const telaLarga = useMediaQuery('(min-width: 40rem)')
const hoje = today(getLocalTimeZone())

const formatoData = new Intl.DateTimeFormat('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric' })

function formatar(data: CalendarDate) {
  return formatoData.format(data.toDate(getLocalTimeZone()))
}

// "Hoje" quando e so o dia de hj, um dia so quando o fim e igual ou n tem
const textoPeriodo = computed(() => {
  const { start, end } = periodo.value
  if (!start) return 'Escolha um período'
  if (!end || start.compare(end) === 0) {
    if (start.compare(hoje) === 0) return 'Hoje'
    return formatar(start as CalendarDate)
  }
  return `${formatar(start as CalendarDate)} - ${formatar(end as CalendarDate)}`
})
</script>
