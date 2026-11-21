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

          <div class="flex flex-col">
            <UCalendar
              v-model="periodo"
              range
              locale="pt-BR"
              :number-of-months="telaLarga ? 2 : 1"
              :max-value="hoje"
              class="p-2"
            >
              <!-- anel no dia em q foi criado, antes dele fica apagado. so marca, n bloqueia -->
              <!-- selecionado o circulo todo fica da cor, se n some no meio da selecao -->
              <template #day="{ day }">
                <span
                  v-if="inicioTotal && day.compare(inicioTotal) === 0"
                  class="pointer-events-none absolute inset-0 rounded-full"
                  :class="selecionado(day) ? 'bg-info' : 'ring-2 ring-info ring-inset'"
                  aria-hidden="true"
                />
                <span
                  v-else-if="marcarVersao && versaoDesde && day.compare(versaoDesde) === 0"
                  class="pointer-events-none absolute inset-0 rounded-full"
                  :class="selecionado(day) ? 'bg-warning' : 'border-2 border-dashed border-warning'"
                  aria-hidden="true"
                />
                <span
                  v-else-if="day.compare(hoje) === 0"
                  class="pointer-events-none absolute inset-0 rounded-full"
                  :class="selecionado(day) ? 'bg-success' : 'ring-2 ring-success ring-inset'"
                  aria-hidden="true"
                />
                <span
                  class="relative"
                  :class="inicioTotal && day.compare(inicioTotal) < 0 && 'opacity-40'"
                >
                  {{ day.day }}
                </span>
              </template>
            </UCalendar>

            <div class="flex flex-wrap gap-x-4 gap-y-1 px-4 pb-3 text-xs text-muted">
              <p class="flex items-center gap-1.5">
                <span
                  class="size-3 shrink-0 rounded-full ring-2 ring-success ring-inset"
                  aria-hidden="true"
                />
                Hoje
              </p>

              <p
                v-if="inicioTotal"
                class="flex items-center gap-1.5"
              >
                <span
                  class="size-3 shrink-0 rounded-full ring-2 ring-info ring-inset"
                  aria-hidden="true"
                />
                Criado em {{ formatar(inicioTotal) }}
              </p>

              <p
                v-if="marcarVersao && versaoDesde"
                class="flex items-center gap-1.5"
              >
                <span
                  class="size-3 shrink-0 rounded-full border-2 border-dashed border-warning"
                  aria-hidden="true"
                />
                Versão atual desde {{ formatar(versaoDesde) }}
              </p>
            </div>
          </div>
        </div>
      </template>
    </UPopover>

    <!-- so aparece em quem tem grafico por tempo -->
    <USelect
      v-if="agrupamento"
      v-model="agrupamento"
      :items="agrupamentos"
      variant="ghost"
      class="w-32"
    />
  </div>
</template>

<script setup lang="ts">
import { getLocalTimeZone, today } from '@internationalized/date'
import type { CalendarDate, DateValue } from '@internationalized/date'
import type { Periodo } from '~/composables/useDashboard'

interface Atalho {
  label: string
  dias?: number
  meses?: number
  // vai do comeco (inicioTotal) ate hj
  todo?: boolean
}

const periodo = defineModel<Periodo>('periodo', { required: true })
const agrupamento = defineModel<'dia' | 'semana' | 'mes'>('agrupamento')

// dia q a coisa da dashboard comecou a existir, sem ele n tem o todo o periodo
const props = defineProps<{
  inicioTotal?: CalendarDate | null
  // so o quiz manda, quando a versao atual comecou. igual a criacao n marca de novo
  versaoDesde?: CalendarDate | null
}>()

const marcarVersao = computed(() => {
  if (!props.versaoDesde || !props.inicioTotal) return false
  return props.versaoDesde.compare(props.inicioTotal) !== 0
})

const telaLarga = useMediaQuery('(min-width: 40rem)')
const hoje = today(getLocalTimeZone())

const todosAtalhos: Atalho[] = [
  { label: 'Todo o período', todo: true },
  { label: 'Últimos 7 dias', dias: 7 },
  { label: 'Últimos 14 dias', dias: 14 },
  { label: 'Últimos 30 dias', dias: 30 },
  { label: 'Últimos 3 meses', meses: 3 },
  { label: 'Últimos 6 meses', meses: 6 },
  { label: 'Último ano', meses: 12 },
]

const atalhos = computed(() => {
  const lista = []
  for (const atalho of todosAtalhos) {
    if (!atalho.todo || props.inicioTotal) lista.push(atalho)
  }
  return lista
})

const agrupamentos = [
  { label: 'Diário', value: 'dia' },
  { label: 'Semanal', value: 'semana' },
  { label: 'Mensal', value: 'mes' },
]

// hoje conta como 1 dos dias
function inicioDoAtalho(atalho: Atalho) {
  if (atalho.todo && props.inicioTotal) return props.inicioTotal
  if (atalho.meses) return hoje.subtract({ months: atalho.meses }).add({ days: 1 })
  return hoje.subtract({ days: (atalho.dias ?? 1) - 1 })
}

// dentro do periodo escolhido, sem fim e um dia so
function selecionado(dia: DateValue) {
  const { start, end } = periodo.value
  if (!start) return false
  return dia.compare(start) >= 0 && dia.compare(end ?? start) <= 0
}

function atalhoAtivo(atalho: Atalho) {
  const { start, end } = periodo.value
  if (!start || !end) return false
  if (atalho.todo && !props.inicioTotal) return false
  return end.compare(hoje) === 0 && start.compare(inicioDoAtalho(atalho)) === 0
}

function escolherAtalho(atalho: Atalho) {
  periodo.value = { start: inicioDoAtalho(atalho), end: hoje }
}

// dd/mm/aaaa igual o resto da tela
const formatoData = new Intl.DateTimeFormat('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric' })

function formatar(data: CalendarDate) {
  return formatoData.format(data.toDate(getLocalTimeZone()))
}

// um dia so quando n tem fim ou e igual
const textoPeriodo = computed(() => {
  const { start, end } = periodo.value
  if (!start) return 'Escolha um período'
  if (atalhoAtivo(todosAtalhos[0]!)) return 'Todo o período'
  if (!end || start.compare(end) === 0) return formatar(start)
  return `${formatar(start)} - ${formatar(end)}`
})
</script>
