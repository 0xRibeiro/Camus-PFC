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
        :linhas="linhas"
        descricao="Novos cadastros de alunos, dispositivos IoT, trilhas e grupos."
        :agrupamento="agrupamentoCarregado"
        class="min-w-0"
      />

      <DashboardNumeros :indicadores="indicadores" />

      <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <DashboardTrilhas
          :globais="dados.total_trilhas_globais"
          :de-grupo="dados.total_trilhas_de_grupo"
          class="min-w-0"
        />

        <DashboardConquistas
          :conquistas="dados.conquistas_por_quantidade"
          :total-alunos="dados.total_alunos"
          class="min-w-0"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Indicador } from '~/components/dashboard/DashboardNumeros.vue'
import type { DashboardRead } from '~/types/generated'

definePageMeta({ middleware: 'role', roles: ['admin'] })

const { dados, loading, erro, periodo, agrupamento, agrupamentoCarregado, fetchDashboard } = useDashboard<DashboardRead>('/admin/dashboard')

// msm cor nas linhas e nos cards
const linhas = [
  { key: 'alunos', label: 'Alunos', color: 'primary' },
  { key: 'dispositivos', label: 'Dispositivos IoT', color: 'secondary' },
  { key: 'trilhas', label: 'Trilhas', color: 'tertiary' },
  { key: 'grupos', label: 'Grupos', color: 'quaternary' },
]

const indicadores = computed<Indicador[]>(() => {
  if (!dados.value) return []
  const { totais, totais_anteriores: anteriores } = dados.value

  return [
    { titulo: 'Alunos novos', icone: 'i-lucide-users', cor: 'primary', valor: totais.alunos, anterior: anteriores.alunos },
    { titulo: 'Dispositivos IoT novos', icone: 'i-lucide-cpu', cor: 'secondary', valor: totais.dispositivos, anterior: anteriores.dispositivos },
    { titulo: 'Trilhas novas', icone: 'i-lucide-route', cor: 'tertiary', valor: totais.trilhas, anterior: anteriores.trilhas },
    { titulo: 'Grupos novos', icone: 'i-lucide-users-round', cor: 'quaternary', valor: totais.grupos, anterior: anteriores.grupos },
  ]
})
</script>
