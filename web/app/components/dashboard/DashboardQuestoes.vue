<template>
  <UCard :ui="{ body: 'p-0 sm:p-0' }">
    <template #header>
      <div class="flex flex-wrap items-start justify-between gap-3">
        <div class="min-w-0">
          <h2 class="font-medium">
            Acerto por questão
          </h2>

          <p class="text-sm text-muted">
            Quanto cada alternativa foi marcada no período, na versão atual.
          </p>
        </div>

        <div class="flex flex-wrap items-center gap-1">
          <UButton
            :icon="emPorcentagem ? 'i-lucide-percent' : 'i-lucide-hash'"
            :label="emPorcentagem ? 'Porcentagem' : 'Quantidade'"
            size="sm"
            color="neutral"
            variant="ghost"
            aria-label="Alternar entre porcentagem e quantidade"
            @click="emPorcentagem = !emPorcentagem"
          />

          <UButton
          :icon="dificeisPrimeiro ? 'i-lucide-arrow-down-wide-narrow' : 'i-lucide-arrow-up-narrow-wide'"
          :label="dificeisPrimeiro ? 'Menos acertadas' : 'Mais acertadas'"
          size="sm"
          color="neutral"
          variant="ghost"
          aria-label="Inverter a ordem das questões"
          @click="dificeisPrimeiro = !dificeisPrimeiro"
          />
        </div>
      </div>
    </template>

    <ul
      v-if="questoes.length"
      class="max-h-[32rem] divide-y divide-default overflow-y-auto"
      tabindex="0"
      aria-label="Acerto por questão"
    >
      <li
        v-for="questao in lista"
        :key="questao.id"
        class="space-y-3 px-4 py-4 sm:px-6"
      >
        <div class="flex items-start justify-between gap-3">
          <div class="min-w-0">
            <p class="font-medium text-highlighted">
              {{ questao.enunciado }}
            </p>

            <p class="text-xs text-muted">
              {{ questao.respostas }} {{ questao.respostas === 1 ? 'resposta' : 'respostas' }}
            </p>
          </div>

          <UBadge
            v-if="questao.taxa !== null"
            :color="cor(questao.taxa)"
            variant="subtle"
            class="shrink-0 tabular-nums"
          >
            <template v-if="emPorcentagem">
              {{ formatarPorcentagem(questao.taxa) }} de acerto
            </template>
            <template v-else>
              {{ questao.acertos }} de {{ questao.respostas }} acertaram
            </template>
          </UBadge>
        </div>

        <ul class="space-y-2">
          <li
            v-for="alternativa in questao.alternativas"
            :key="alternativa.id"
            class="space-y-1"
          >
            <div class="flex items-center justify-between gap-3 text-sm">
              <p class="flex min-w-0 items-center gap-2">
                <UIcon
                  :name="alternativa.correta ? 'i-lucide-circle-check' : 'i-lucide-circle-x'"
                  class="size-4 shrink-0"
                  :class="alternativa.correta ? 'text-success' : 'text-dimmed'"
                  :aria-label="alternativa.correta ? 'Correta' : 'Errada'"
                />
                <span class="truncate">{{ alternativa.texto }}</span>
              </p>

              <span class="shrink-0 text-muted tabular-nums">
                {{ emPorcentagem ? formatarPorcentagem(questao.respostas ? alternativa.escolhas / questao.respostas : 0) : alternativa.escolhas }}
              </span>
            </div>

            <UProgress
              :model-value="questao.respostas ? alternativa.escolhas / questao.respostas : 0"
              :max="1"
              :color="alternativa.correta ? 'success' : 'error'"
              :ui="{ indicator: !alternativa.correta && alternativa.id !== questao.pegadinha ? 'opacity-45' : '' }"
              size="xs"
            />
          </li>
        </ul>
      </li>
    </ul>

    <p
      v-else
      class="p-4 text-sm text-muted sm:p-6"
    >
      O quiz ainda não tem questões.
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

// errada com mais escolha, se ninguem errou n tem
function pegadinha(questao: QuestaoAcertoRead) {
  let maisMarcada: { id: number, escolhas: number } | null = null
  for (const alternativa of questao.alternativas) {
    if (alternativa.correta || !alternativa.escolhas) continue
    if (!maisMarcada || alternativa.escolhas > maisMarcada.escolhas) maisMarcada = alternativa
  }
  return maisMarcada?.id ?? null
}

const dificeisPrimeiro = ref(true)
// muda o numero da questao e das alternativas juntos
const emPorcentagem = ref(true)

// sem resposta vai pro fim nas duas ordens
const lista = computed(() => {
  const comTaxa = props.questoes.map(questao => ({
    ...questao,
    taxa: questao.respostas ? questao.acertos / questao.respostas : null,
    pegadinha: pegadinha(questao),
  }))

  return comTaxa.sort((a, b) => {
    if (a.taxa === null) return 1
    if (b.taxa === null) return -1
    if (!dificeisPrimeiro.value) return b.taxa - a.taxa
    return a.taxa - b.taxa
  })
})
</script>
