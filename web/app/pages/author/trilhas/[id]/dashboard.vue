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

      <!-- data de criacao do lado do nome -->
      <div class="flex flex-wrap items-baseline gap-x-3">
        <h1 class="text-xl font-semibold">
          {{ trilha?.titulo }}
        </h1>

        <span
          v-if="dados"
          class="text-sm text-muted"
        >
          {{ formatarData(dados.inicio_total) }}
        </span>
      </div>
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
        :linhas="colunas"
        descricao="Alunos ativos em cada ponto, separados pelo que fizeram nele. Quem começou e terminou no mesmo ponto conta como terminou."
        :agrupamento="agrupamentoCarregado"
        barras
        :eixo-x="tituloEixoX"
        eixo-y="Alunos"
        class="min-w-0"
      />

      <!-- os cards sao do periodo, o progresso é de sempre -->
      <DashboardNumeros
        :indicadores="indicadores"
        :periodo-anterior="periodoAnterior"
      />

      <DashboardProgresso
        :engajamento="dados.engajamento"
        :funil="dados.funil"
        :de-grupo="!!grupoId"
        @abrir-quiz="abrirQuiz"
        class="min-w-0"
      />

      <!-- so no grupo o dono ve cada aluno, na global fica so o geral -->
      <DashboardMembros
        v-if="grupoId"
        :trilha-id="trilhaId"
        @abrir="abrirAluno"
      />
    </div>

    <UModal
      v-model:open="showAlunoModal"
      title="Aluno na trilha"
      :ui="{ content: 'sm:max-w-3xl' }"
    >
      <template #body>
        <DashboardAluno
          v-if="alunoAberto"
          :trilha-id="trilhaId"
          :usuario-id="alunoAberto"
        />
      </template>
    </UModal>

    <!-- dashboard do quiz, igual a da tela de editar a trilha -->
    <UModal
      v-model:open="showQuizModal"
      :ui="{ content: 'sm:max-w-5xl' }"
    >
      <template #title>
        <span class="flex flex-wrap items-baseline gap-x-3">
          {{ quizAberto ? `Desempenho: ${quizAberto.titulo}` : 'Desempenho' }}
          <span
            v-if="quizCriadoEm"
            class="text-sm font-normal text-muted"
          >
            {{ formatarData(quizCriadoEm) }}
          </span>
        </span>
      </template>

      <template #body>
        <DashboardConteudo
          v-if="quizAberto"
          :conteudo-id="quizAberto.id"
          @criado-em="quizCriadoEm = $event"
        />
      </template>
    </UModal>
  </div>
</template>

<script setup lang="ts">
import type { Indicador } from '~/components/dashboard/DashboardNumeros.vue'
import DashboardAluno from '~/components/dashboard/DashboardAluno.vue'
import DashboardMembros from '~/components/dashboard/DashboardMembros.vue'
import DashboardProgresso from '~/components/dashboard/DashboardProgresso.vue'
import type { ConteudoFunilRead, DashboardTrilhaRead, TrilhaRead } from '~/types/generated'
import { formatarData, formatarDuracao } from '~/utils/datas'

definePageMeta({ middleware: 'role', roles: ['author', 'admin'], key: route => route.path })

const route = useRoute()
const api = useApi()
const grupoId = route.params.grupoId
const trilhaId = Number(route.params.id)
const caminhoTrilha = grupoId ? `/grupos/${grupoId}/trilhas/${trilhaId}/editar` : `/author/trilhas/${trilhaId}`

const trilha = ref<TrilhaRead | null>(null)
const { dados, loading, erro, periodo, agrupamento, agrupamentoCarregado, periodoAnterior, inicioTotal, fetchDashboard } = useDashboard<DashboardTrilhaRead>(`/trilhas/${trilhaId}/dashboard`)

const tituloEixoX = computed(() => {
  if (agrupamentoCarregado.value === 'semana') return 'Semana'
  if (agrupamentoCarregado.value === 'mes') return 'Mês'
  return 'Dia'
})

// msm cor dos cards de comecaram, ativos e terminaram
const colunas = [
  { key: 'comecaram', label: 'Começaram', color: 'secondary' },
  { key: 'andamento', label: 'Em andamento', color: 'quaternary' },
  { key: 'terminaram', label: 'Terminaram', color: 'tertiary' },
]

// so pro titulo, o erro de acesso aparece pela dash
onMounted(async () => {
  trilha.value = await api(`/trilhas/${trilhaId}`).catch(() => null)
})

const indicadores = computed<Indicador[]>(() => {
  if (!dados.value) return []
  const { totais, totais_anteriores: anteriores } = dados.value

  return [
    { titulo: 'Começaram', icone: 'i-lucide-user-plus', cor: 'secondary', valor: totais.novos, anterior: anteriores.novos },
    { titulo: 'Terminaram', icone: 'i-lucide-flag', cor: 'tertiary', valor: totais.terminaram, anterior: anteriores.terminaram },
    { titulo: 'Em andamento', icone: 'i-lucide-hourglass', cor: 'quaternary', valor: totais.em_andamento, anterior: anteriores.em_andamento },
    {
      // mediana, da 1a ate a ultima conclusao de quem terminou no periodo
      titulo: 'Tempo mediano até terminar',
      icone: 'i-lucide-timer',
      cor: 'primary',
      valor: totais.tempo_mediano ?? null,
      anterior: anteriores.tempo_mediano ?? null,
      formatar: formatarDuracao,
      menorMelhor: true,
    },
  ]
})

// so na trilha de grupo
const alunoAberto = ref<number | null>(null)
const showAlunoModal = ref(false)

function abrirAluno(id: number) {
  alunoAberto.value = id
  showAlunoModal.value = true
}

// quiz clicado no funil
const quizAberto = ref<ConteudoFunilRead | null>(null)
const quizCriadoEm = ref('')
const showQuizModal = ref(false)

function abrirQuiz(conteudo: ConteudoFunilRead) {
  quizAberto.value = conteudo
  quizCriadoEm.value = ''
  showQuizModal.value = true
}
</script>
