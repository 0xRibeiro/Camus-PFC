<template>
  <div>
    <CamusBanner
      titulo="Dashboard"
      descricao="Indicadores gerais do Camus."
      imagem="/papeis-de-parede/azul/admin.webp"
    />

    <div class="mb-6 flex flex-wrap items-center justify-between gap-3">
      <DashboardFiltro
        v-model:periodo="periodo"
        v-model:agrupamento="agrupamento"
      />

      <UButton
        label="Atualizar"
        icon="i-lucide-refresh-cw"
        variant="outline"
        :loading="loading"
        @click="fetchDashboard"
      />
    </div>

    <div
      v-if="loading && !dados"
      class="flex justify-center py-12"
    >
      <UIcon
        name="i-lucide-loader-circle"
        class="size-6 animate-spin"
      />
    </div>

    <UCard v-else-if="erro">
      <div class="space-y-3">
        <p class="text-muted">
          {{ erro }}
        </p>

        <UButton
          label="Tentar novamente"
          color="neutral"
          variant="outline"
          :loading="loading"
          @click="fetchDashboard"
        />
      </div>
    </UCard>

    <div
      v-else-if="dados"
      class="space-y-6"
    >
      <DashboardEvolucao
        :evolucao="dados.evolucao"
        :agrupamento="agrupamentoCarregado"
        class="min-w-0"
      />

      <DashboardNumeros
        :totais="dados.totais"
        :anteriores="dados.totais_anteriores"
      />

      <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <DashboardTrilhas
          :globais="dados.total_trilhas_globais"
          :de-grupo="dados.total_trilhas_de_grupo"
          class="min-w-0"
        />

        <DashboardConquistas
          :conquistas="dados.conquistas_por_quantidade"
          class="min-w-0"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { getLocalTimeZone, today } from '@internationalized/date'
import { FetchError } from 'ofetch'
import type { Periodo } from '~/components/dashboard/DashboardFiltro.vue'
import type { DashboardRead } from '~/types/generated'

definePageMeta({ middleware: 'role', roles: ['admin'] })

const api = useApi()
const dados = ref<DashboardRead | null>(null)
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
    dados.value = await api('/admin/dashboard', {
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

// consulta novamente quando o período ou agrupamento mudar
watch([periodo, agrupamento], fetchDashboard)

// primeira consulta ao abrir a página
onMounted(fetchDashboard)
</script>
