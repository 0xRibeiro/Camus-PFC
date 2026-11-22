<template>
  <div class="space-y-5">
    <div class="flex flex-wrap items-center gap-2">
      <UBadge
        v-if="quiz.acertos !== null && quiz.acertos !== undefined && quiz.questoes"
        :color="corDaNota(quiz.acertos, quiz.questoes)"
        variant="subtle"
        size="lg"
      >
        Nota {{ formatarNota(quiz.acertos, quiz.questoes) }}/10
      </UBadge>

      <span class="text-sm text-muted">
        Acertou {{ quiz.acertos }} de {{ quiz.questoes }} questões
        <template v-if="quiz.concluido_em">
          · {{ formatarDataHora(quiz.concluido_em) }}
        </template>
      </span>
    </div>

    <!-- msm cara do acerto por questao, so q com o q ele marcou -->
    <!-- fundo leve verde ou vermelho pelo acerto -->
    <ul class="divide-y divide-default overflow-hidden rounded-lg border border-default">
      <li
        v-for="(resposta, posicao) in quiz.respostas"
        :key="resposta.id"
        class="space-y-3 p-4"
        :class="resposta.acertou ? 'bg-success/[0.04]' : 'bg-error/[0.04]'"
      >
        <p class="font-medium text-highlighted wrap-anywhere">
          {{ posicao + 1 }}. {{ resposta.enunciado }}
        </p>

        <ul class="space-y-1.5">
          <li
            v-for="alternativa in resposta.alternativas"
            :key="alternativa.id"
            class="flex items-center gap-2 rounded-md px-2 py-1.5 text-sm"
            :class="estilo(alternativa).linha"
          >
            <UIcon
              :name="estilo(alternativa).icone"
              class="size-4 shrink-0"
              :class="estilo(alternativa).cor"
            />

            <span class="min-w-0 flex-1 wrap-anywhere">{{ alternativa.texto }}</span>

            <span
              v-if="estilo(alternativa).rotulo"
              class="shrink-0 text-xs font-medium"
              :class="estilo(alternativa).cor"
            >
              {{ estilo(alternativa).rotulo }}
            </span>
          </li>
        </ul>

        <p
          v-if="!resposta.acertou && !marcouAlguma(resposta)"
          class="text-xs text-muted"
        >
          Não respondeu essa questão.
        </p>
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import type { AlternativaDoAlunoRead, RespostaDoAlunoRead } from '~/types/generated'
import { formatarDataHora } from '~/utils/datas'
import { corDaNota, formatarNota } from '~/utils/notas'

// vem do modal do aluno (conteudo dele) ou do card de alunos do quiz, os dois tem esses campos
defineProps<{
  quiz: {
    acertos?: number | null
    questoes?: number | null
    concluido_em?: string | null
    respostas?: RespostaDoAlunoRead[]
  }
}>()

// o q ele marcou fica forte (verde se acertou, vermelho se errou).
// a correta q ele n marcou so ganha um contorno tracejado, pra n competir com a resposta dele
function estilo(alternativa: AlternativaDoAlunoRead) {
  if (alternativa.escolhida && alternativa.correta) {
    return { icone: 'i-lucide-circle-check-big', cor: 'text-success font-semibold', linha: 'bg-success/20 ring-2 ring-success ring-inset font-medium', rotulo: 'Marcou' }
  }
  if (alternativa.escolhida) {
    return { icone: 'i-lucide-circle-x', cor: 'text-error font-semibold', linha: 'bg-error/20 ring-2 ring-error ring-inset font-medium', rotulo: 'Marcou' }
  }
  if (alternativa.correta) {
    return { icone: 'i-lucide-circle-check', cor: 'text-success', linha: 'border border-dashed border-success', rotulo: 'Correta' }
  }
  return { icone: 'i-lucide-circle', cor: 'text-dimmed', linha: 'ring ring-default ring-inset', rotulo: '' }
}

function marcouAlguma(resposta: RespostaDoAlunoRead) {
  for (const alternativa of resposta.alternativas) {
    if (alternativa.escolhida) return true
  }
  return false
}
</script>
