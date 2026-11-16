import { getLocalTimeZone, today } from '@internationalized/date'
import type { CalendarDate } from '@internationalized/date'
import { FetchError } from 'ofetch'

// sem end e um dia so
export interface Periodo {
  start: CalendarDate | undefined
  end: CalendarDate | undefined
}

// filtro e carga das dashboards, cada pagina so passa a rota
export function useDashboard<T>(caminho: string) {
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

  return { dados, loading, erro, periodo, agrupamento, agrupamentoCarregado, fetchDashboard }
}
