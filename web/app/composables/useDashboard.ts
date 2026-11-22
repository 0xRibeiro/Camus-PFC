import { getLocalTimeZone, parseDate, today } from '@internationalized/date'
import type { CalendarDate } from '@internationalized/date'
import { FetchError } from 'ofetch'
import type { UnwrapRef } from 'vue'

// sem end e um dia so
export interface Periodo {
  start: CalendarDate | undefined
  end: CalendarDate | undefined
}

// a data sai do ref sem o campo privado da classe
type DiaDoFiltro = UnwrapRef<CalendarDate>

// filtro e carga das dashboards, cada pagina so passa a rota
// toda dashboard manda o dia q comecou a existir, é o comeco do todo o periodo
export function useDashboard<T extends { inicio_total: string }>(caminho: string) {
  const api = useApi()
  const dados = ref<T | null>(null) as Ref<T | null>
  const loading = ref(true)
  const erro = ref('')

  // comeca nos ultimos 30 dias
  const hoje = today(getLocalTimeZone())
  const periodo = ref<Periodo>({ start: hoje.subtract({ days: 29 }), end: hoje })
  const agrupamento = ref<'dia' | 'semana' | 'mes'>('dia')

  // rotulo do grafico so muda junto com os dados
  const agrupamentoCarregado = ref(agrupamento.value)

  const inicioTotal = computed(() => {
    if (!dados.value) return null
    return parseDate(dados.value.inicio_total)
  })

  // texto do periodo q os numeros comparam, msm conta do back: o msm tamanho logo antes.
  // vazio quando o periodo ja comeca antes de existir, ai n tem com o q comparar
  const periodoAnterior = ref('')

  function formatarDia(dia: DiaDoFiltro) {
    return `${String(dia.day).padStart(2, '0')}/${String(dia.month).padStart(2, '0')}`
  }

  function descreverPeriodoAnterior(inicio: DiaDoFiltro, fim: DiaDoFiltro) {
    const dias = fim.compare(inicio) + 1
    const inicioAnterior = inicio.subtract({ days: dias })
    const fimAnterior = inicio.subtract({ days: 1 })
    if (dias === 1) return formatarDia(fimAnterior)
    return `${formatarDia(inicioAnterior)} a ${formatarDia(fimAnterior)}`
  }

  async function fetchDashboard() {
    const { start, end } = periodo.value
    if (!start) return

    loading.value = true
    erro.value = ''

    try {
      // sem fim e um dia so
      dados.value = await api(caminho, {
        query: {
          inicio: start.toString(),
          fim: (end ?? start).toString(),
          agrupamento: agrupamento.value,
        },
      })
      agrupamentoCarregado.value = agrupamento.value
      periodoAnterior.value = ''
      if (inicioTotal.value && start.compare(inicioTotal.value) > 0) {
        periodoAnterior.value = descreverPeriodoAnterior(start, end ?? start)
      }
    }
    catch (error) {
      erro.value = 'Não foi possível carregar a dashboard'

      if (error instanceof FetchError && typeof error.data?.detail === 'string') {
        erro.value = error.data.detail
      }
    }
    finally {
      loading.value = false
    }
  }

  watch([periodo, agrupamento], fetchDashboard)
  onMounted(fetchDashboard)

  return { dados, loading, erro, periodo, agrupamento, agrupamentoCarregado, periodoAnterior, inicioTotal, fetchDashboard }
}
