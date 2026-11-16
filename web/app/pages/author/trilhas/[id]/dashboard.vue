<template>
  <div class="flex-1">
    <UButton
      icon="i-lucide-arrow-left"
      label="Voltar para a trilha"
      color="neutral"
      variant="link"
      class="mb-3 px-0"
      :to="caminhoTrilha"
    />

    <div class="mb-6 min-w-0 wrap-anywhere">
      <p class="text-xs font-medium tracking-wide text-muted uppercase">
        Dashboard da trilha
      </p>

      <h1 class="text-xl font-semibold">
        {{ trilha?.titulo }}
      </h1>
    </div>

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
        :linhas="linhas"
        descricao="Conteúdos concluídos e tentativas de quiz feitas pelos alunos."
        :agrupamento="agrupamentoCarregado"
        class="min-w-0"
      />

      <DashboardNumeros :indicadores="indicadores" />
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Indicador } from '~/components/dashboard/DashboardNumeros.vue'
import type { DashboardTrilhaRead, TotaisTrilhaRead, TrilhaRead } from '~/types/generated'

definePageMeta({ middleware: 'role', roles: ['author', 'admin'], key: route => route.path })

const route = useRoute()
const api = useApi()
const grupoId = route.params.grupoId
const trilhaId = Number(route.params.id)
const caminhoTrilha = grupoId ? `/grupos/${grupoId}/trilhas/${trilhaId}/editar` : `/author/trilhas/${trilhaId}`

const trilha = ref<TrilhaRead | null>(null)
const { dados, loading, erro, periodo, agrupamento, agrupamentoCarregado, fetchDashboard } = useDashboard<DashboardTrilhaRead>(`/trilhas/${trilhaId}/dashboard`)

// so pro titulo, o erro de acesso aparece pela dash
onMounted(async () => {
  trilha.value = await api(`/trilhas/${trilhaId}`).catch(() => null)
})

const linhas = [
  { key: 'conclusoes', label: 'Conteúdos concluídos', color: 'primary' },
  { key: 'tentativas', label: 'Tentativas de quiz', color: 'secondary' },
]

const formatarPorcentagem = new Intl.NumberFormat('pt-BR', { style: 'percent', maximumFractionDigits: 1 }).format

// sem questao respondida n tem taxa
function taxaAcerto(totais: TotaisTrilhaRead) {
  if (!totais.questoes) return null
  return totais.acertos / totais.questoes
}

const indicadores = computed<Indicador[]>(() => {
  if (!dados.value) return []
  const { totais, totais_anteriores: anteriores } = dados.value

  return [
    { titulo: 'Alunos ativos', icone: 'i-lucide-users', cor: 'quaternary', valor: totais.alunos_ativos, anterior: anteriores.alunos_ativos },
    { titulo: 'Conteúdos concluídos', icone: 'i-lucide-circle-check', cor: 'primary', valor: totais.conclusoes, anterior: anteriores.conclusoes },
    { titulo: 'Tentativas de quiz', icone: 'i-lucide-list-checks', cor: 'secondary', valor: totais.tentativas, anterior: anteriores.tentativas },
    {
      titulo: 'Taxa de acerto',
      icone: 'i-lucide-target',
      cor: 'tertiary',
      valor: taxaAcerto(totais) ?? 0,
      anterior: taxaAcerto(anteriores),
      formatar: valor => totais.questoes ? formatarPorcentagem(valor) : '—',
    },
  ]
})
</script>
