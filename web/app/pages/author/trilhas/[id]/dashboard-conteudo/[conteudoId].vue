<template>
  <div class="flex-1">
    <UButton
      icon="i-lucide-arrow-left"
      label="Dashboard da trilha"
      color="neutral"
      variant="link"
      class="mb-3 px-0"
      :to="`${caminhoTrilha}/dashboard`"
    />

    <div class="mb-6 flex flex-wrap items-start justify-between gap-3">
      <div class="min-w-0 wrap-anywhere">
        <p class="text-xs font-medium tracking-wide text-muted uppercase">
          Dashboard do conteúdo
        </p>

        <h1 class="flex flex-wrap items-center gap-2 text-xl font-semibold">
          {{ dados?.titulo }}

          <UBadge
            v-if="dados"
            color="neutral"
            variant="soft"
          >
            {{ tipos[dados.tipo] ?? dados.tipo }}
          </UBadge>
        </h1>
      </div>

      <UButton
        label="Editar conteúdo"
        icon="i-lucide-pencil"
        color="neutral"
        variant="outline"
        :to="`${caminhoTrilha}/conteudos/${conteudoId}`"
      />
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
        :descricao="ehQuiz ? 'Conclusões e tentativas do quiz.' : 'Conclusões do conteúdo.'"
        :agrupamento="agrupamentoCarregado"
        class="min-w-0"
      />

      <DashboardNumeros :indicadores="indicadores" />

      <div
        v-if="ehQuiz"
        class="grid grid-cols-1 gap-6 lg:grid-cols-3"
      >
        <DashboardNotas
          :notas="dados.notas"
          class="min-w-0"
        />

        <DashboardQuestoes
          :questoes="dados.questoes"
          class="min-w-0 lg:col-span-2"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Indicador } from '~/components/dashboard/DashboardNumeros.vue'
import type { DashboardConteudoRead } from '~/types/generated'

definePageMeta({ middleware: 'role', roles: ['author', 'admin'], key: route => route.path })

const route = useRoute()
const grupoId = route.params.grupoId
const trilhaId = Number(route.params.id)
const conteudoId = Number(route.params.conteudoId)
const caminhoTrilha = grupoId ? `/grupos/${grupoId}/trilhas/${trilhaId}/editar` : `/author/trilhas/${trilhaId}`

const { dados, loading, erro, periodo, agrupamento, agrupamentoCarregado, fetchDashboard } = useDashboard<DashboardConteudoRead>(`/conteudos/${conteudoId}/dashboard`)

const tipos: Record<string, string> = { video: 'Vídeo', artigo: 'Artigo', quiz: 'Quiz' }
const ehQuiz = computed(() => dados.value?.tipo === 'quiz')

// tentativa so existe no quiz
const linhas = computed(() => {
  const lista = [{ key: 'conclusoes', label: 'Conclusões', color: 'primary' }]
  if (ehQuiz.value) lista.push({ key: 'tentativas', label: 'Tentativas', color: 'secondary' })
  return lista
})

const formatarPorcentagem = new Intl.NumberFormat('pt-BR', { style: 'percent', maximumFractionDigits: 1 }).format
const formatarMedia = new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 1 }).format

// divisao por zero vira null
function dividir(valor: number, por: number) {
  if (!por) return null
  return valor / por
}

const indicadores = computed<Indicador[]>(() => {
  if (!dados.value) return []
  const { totais, totais_anteriores: anteriores } = dados.value

  // de sempre, sem %
  const concluiram: Indicador = {
    titulo: 'Concluíram (dos que começaram a trilha)',
    icone: 'i-lucide-flag',
    cor: 'tertiary',
    valor: dividir(dados.value.concluiram, dados.value.iniciaram_trilha) ?? 0,
    anterior: null,
    formatar: valor => dados.value?.iniciaram_trilha ? formatarPorcentagem(valor) : '—',
  }

  if (!ehQuiz.value) {
    return [
      { titulo: 'Conclusões no período', icone: 'i-lucide-circle-check', cor: 'primary', valor: totais.conclusoes, anterior: anteriores.conclusoes },
      concluiram,
    ]
  }

  return [
    { titulo: 'Alunos que fizeram', icone: 'i-lucide-users', cor: 'quaternary', valor: totais.alunos_quiz, anterior: anteriores.alunos_quiz },
    {
      titulo: 'Tentativas por aluno',
      icone: 'i-lucide-repeat',
      cor: 'secondary',
      valor: dividir(totais.tentativas, totais.alunos_quiz) ?? 0,
      anterior: dividir(anteriores.tentativas, anteriores.alunos_quiz),
      formatar: valor => totais.alunos_quiz ? formatarMedia(valor) : '—',
    },
    {
      titulo: 'Taxa de acerto (versão atual)',
      icone: 'i-lucide-target',
      cor: 'primary',
      valor: dividir(totais.acertos, totais.questoes) ?? 0,
      anterior: dividir(anteriores.acertos, anteriores.questoes),
      formatar: valor => totais.questoes ? formatarPorcentagem(valor) : '—',
    },
    concluiram,
  ]
})
</script>
