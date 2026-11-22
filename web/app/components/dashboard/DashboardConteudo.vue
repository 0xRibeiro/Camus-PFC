<template>
  <div>
    <!-- so abre em modal, o titulo e a data ficam no cabecalho dele -->
    <!-- filtro gruda no topo do modal -->
    <div class="sticky top-0 z-10 mb-6 flex flex-wrap items-center justify-between gap-3 border-b border-default bg-default/90 py-3 backdrop-blur">
      <DashboardFiltro
        v-model:periodo="periodo"
        v-model:agrupamento="agrupamento"
        :inicio-total="inicioTotal"
        :versao-desde="versaoDesde"
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
        descricao="Quantos alunos fizeram o quiz, separados pela nota que tiraram."
        :agrupamento="agrupamentoCarregado"
        barras
        :eixo-x="tituloEixoX"
        eixo-y="Alunos"
        class="min-w-0"
      />

      <DashboardNumeros
        :indicadores="indicadores"
        :periodo-anterior="periodoAnterior"
      />

      <div class="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <DashboardNotas
          :notas="dados.notas"
          class="min-w-0"
        />

        <DashboardQuestoes
          :questoes="dados.questoes"
          class="min-w-0 lg:col-span-2"
        />
      </div>

      <!-- so no grupo o dono ve cada aluno, igual na dashboard da trilha -->
      <DashboardQuizAlunos
        v-if="comAlunos"
        :conteudo-id="conteudoId"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Indicador } from '~/components/dashboard/DashboardNumeros.vue'
import DashboardQuizAlunos from '~/components/dashboard/DashboardQuizAlunos.vue'
import type { DashboardConteudoRead } from '~/types/generated'
import { parseDate } from '@internationalized/date'

// modal da tela da trilha e da dashboard da trilha usam esse msm
const props = defineProps<{
  conteudoId: number
  // trilha de grupo mostra os alunos
  comAlunos?: boolean
}>()

const { dados, loading, erro, periodo, agrupamento, agrupamentoCarregado, periodoAnterior, inicioTotal, fetchDashboard } = useDashboard<DashboardConteudoRead>(`/conteudos/${props.conteudoId}/dashboard`)

// o titulo é do cabecalho do modal, entao manda a data pra ele mostrar
const emit = defineEmits<{
  criadoEm: [data: string]
}>()

watch(dados, (novos) => {
  if (novos) emit('criadoEm', novos.inicio_total)
})

const versaoDesde = computed(() => {
  if (!dados.value) return null
  return parseDate(dados.value.versao_desde)
})

const tituloEixoX = computed(() => {
  if (agrupamentoCarregado.value === 'semana') return 'Semana'
  if (agrupamentoCarregado.value === 'mes') return 'Mês'
  return 'Dia'
})

// msm corte e cor do selo de acerto de cada questao
const linhas = [
  { key: 'mal', label: 'Abaixo de 50%', color: 'error' },
  { key: 'medio', label: 'De 50% a 74%', color: 'warning' },
  { key: 'bem', label: '75% ou mais', color: 'success' },
]

const formatarPorcentagem = new Intl.NumberFormat('pt-BR', { style: 'percent', maximumFractionDigits: 1 }).format
const formatarNota = new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 1 }).format

// divisao por zero vira null
function dividir(valor: number, por: number) {
  if (!por) return null
  return valor / por
}

const indicadores = computed<Indicador[]>(() => {
  if (!dados.value) return []
  const { totais, totais_anteriores: anteriores } = dados.value

  // a nota é sempre de 0 a 10, independente de quantas questoes o quiz tem
  return [
    { titulo: 'Alunos que fizeram', icone: 'i-lucide-users', cor: 'quaternary', valor: totais.alunos, anterior: anteriores.alunos },
    {
      titulo: 'Nota média',
      icone: 'i-lucide-target',
      cor: 'primary',
      valor: totais.questoes ? (totais.acertos / totais.questoes) * 10 : null,
      anterior: anteriores.questoes ? (anteriores.acertos / anteriores.questoes) * 10 : null,
      formatar: valor => `${formatarNota(valor)}/10`,
    },
    {
      titulo: 'Gabaritaram',
      icone: 'i-lucide-trophy',
      cor: 'tertiary',
      valor: dividir(totais.gabaritaram, totais.alunos),
      anterior: dividir(anteriores.gabaritaram, anteriores.alunos),
      formatar: formatarPorcentagem,
    },
  ]
})
</script>
