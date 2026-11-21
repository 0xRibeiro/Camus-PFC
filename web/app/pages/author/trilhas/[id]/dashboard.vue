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

    <!-- filtro acompanha a rolagem -->
    <div class="sticky top-0 z-10 mb-6 flex flex-wrap items-center justify-between gap-3 border-b border-default bg-default/90 py-3 backdrop-blur">
      <DashboardFiltro
        v-model:periodo="periodo"
        v-model:agrupamento="agrupamento"
        :inicio-total="inicioTotal"
      />

      <UButton
        label="Atualizar"
        icon="i-lucide-refresh-cw"
        variant="outline"
        :loading="loading"
        @click="fetchDashboard"
      />

      <!-- so avisa, da pra escolher antes disso msm assim -->
      <p
        v-if="dados"
        class="w-full text-xs text-muted"
      >
        Trilha criada em {{ formatarData(dados.inicio_total) }}
      </p>
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
        descricao="Conteúdos concluídos, alunos que começaram e alunos que terminaram a trilha."
        :agrupamento="agrupamentoCarregado"
        class="min-w-0"
      />

      <DashboardNumeros
        :indicadores="indicadores"
        :periodo-anterior="periodoAnterior"
      />

      <div class="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <DashboardEngajamento
          :engajamento="dados.engajamento"
          :rotulo-base="grupoId ? 'membros do grupo' : 'alunos'"
          class="min-w-0"
        />

        <DashboardFunil
          :funil="dados.funil"
          :iniciaram="dados.engajamento.iniciaram"
          :link-base="`${caminhoTrilha}/dashboard-conteudo`"
          class="min-w-0 lg:col-span-2"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Indicador } from '~/components/dashboard/DashboardNumeros.vue'
import type { DashboardTrilhaRead, TrilhaRead } from '~/types/generated'
import { formatarData } from '~/utils/datas'

definePageMeta({ middleware: 'role', roles: ['author', 'admin'], key: route => route.path })

const route = useRoute()
const api = useApi()
const grupoId = route.params.grupoId
const trilhaId = Number(route.params.id)
const caminhoTrilha = grupoId ? `/grupos/${grupoId}/trilhas/${trilhaId}/editar` : `/author/trilhas/${trilhaId}`

const trilha = ref<TrilhaRead | null>(null)
const { dados, loading, erro, periodo, agrupamento, agrupamentoCarregado, periodoAnterior, inicioTotal, fetchDashboard } = useDashboard<DashboardTrilhaRead>(`/trilhas/${trilhaId}/dashboard`)

// so pro titulo, o erro de acesso aparece pela dash
onMounted(async () => {
  trilha.value = await api(`/trilhas/${trilhaId}`).catch(() => null)
})

// msm cor nas linhas e nos cards
const linhas = [
  { key: 'conclusoes', label: 'Conteúdos concluídos', color: 'primary' },
  { key: 'novos', label: 'Novos na trilha', color: 'secondary' },
  { key: 'terminaram', label: 'Terminaram a trilha', color: 'tertiary' },
]

const indicadores = computed<Indicador[]>(() => {
  if (!dados.value) return []
  const { totais, totais_anteriores: anteriores } = dados.value

  return [
    { titulo: 'Alunos ativos', icone: 'i-lucide-users', cor: 'quaternary', valor: totais.alunos_ativos, anterior: anteriores.alunos_ativos },
    { titulo: 'Novos na trilha', icone: 'i-lucide-user-plus', cor: 'secondary', valor: totais.novos, anterior: anteriores.novos },
    { titulo: 'Conteúdos concluídos', icone: 'i-lucide-circle-check', cor: 'primary', valor: totais.conclusoes, anterior: anteriores.conclusoes },
    { titulo: 'Terminaram a trilha', icone: 'i-lucide-flag', cor: 'tertiary', valor: totais.terminaram, anterior: anteriores.terminaram },
  ]
})
</script>
