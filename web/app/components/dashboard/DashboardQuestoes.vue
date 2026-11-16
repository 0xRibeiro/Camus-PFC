<template>
  <UCard :ui="{ body: 'p-0 sm:p-0' }">
    <template #header>
      <h2 class="font-medium">
        Acerto por questão
      </h2>

      <p class="text-sm text-muted">
        Das mais erradas pras mais acertadas, contando só a versão atual de cada quiz.
      </p>
    </template>

    <ul
      v-if="questoes.length"
      class="max-h-96 divide-y divide-default overflow-y-auto"
      tabindex="0"
      aria-label="Acerto por questão"
    >
      <li
        v-for="questao in lista"
        :key="questao.id"
        class="space-y-2 px-4 py-3 sm:px-6"
      >
        <div class="flex items-start justify-between gap-3">
          <div class="min-w-0">
            <p class="line-clamp-2 font-medium text-highlighted">
              {{ questao.enunciado }}
            </p>

            <p class="text-xs text-muted">
              {{ questao.quiz }} · {{ questao.respostas }} {{ questao.respostas === 1 ? 'resposta' : 'respostas' }}
            </p>
          </div>

          <span class="shrink-0 text-sm font-semibold tabular-nums">
            {{ questao.taxa === null ? '—' : formatarPorcentagem(questao.taxa) }}
          </span>
        </div>

        <UProgress
          v-if="questao.taxa !== null"
          :model-value="questao.taxa"
          :max="1"
          :color="cor(questao.taxa)"
          size="sm"
        />
      </li>
    </ul>

    <p
      v-else
      class="p-4 text-sm text-muted sm:p-6"
    >
      A trilha ainda não tem quizzes.
    </p>
  </UCard>
</template>

<script setup lang="ts">
import type { QuestaoAcertoRead } from '~/types/generated'

const props = defineProps<{
  questoes: QuestaoAcertoRead[]
}>()

const formatarPorcentagem = new Intl.NumberFormat('pt-BR', { style: 'percent', maximumFractionDigits: 1 }).format

// abaixo da metade e vermelho
function cor(taxa: number) {
  if (taxa < 0.5) return 'error'
  if (taxa < 0.75) return 'warning'
  return 'success'
}

// sem resposta vai pro fim
const lista = computed(() => {
  const comTaxa = props.questoes.map(questao => ({
    ...questao,
    taxa: questao.respostas ? questao.acertos / questao.respostas : null,
  }))

  return comTaxa.sort((a, b) => {
    if (a.taxa === null) return 1
    if (b.taxa === null) return -1
    return a.taxa - b.taxa
  })
})
</script>
