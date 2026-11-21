<template>
  <UCard :ui="{ body: 'p-0 sm:p-0' }">
    <template #header>
      <h2 class="font-medium">
        Funil dos conteúdos
      </h2>

      <p class="text-sm text-muted">
        Quantos dos alunos que começaram a trilha concluíram cada conteúdo. Clique num quiz pra ver o desempenho em detalhe.
      </p>
    </template>

    <ol
      v-if="funil.length"
      class="max-h-96 divide-y divide-default overflow-y-auto"
      tabindex="0"
      aria-label="Funil dos conteúdos"
    >
      <li
        v-for="(conteudo, posicao) in lista"
        :key="conteudo.id"
      >
        <!-- so o quiz tem dashboard, o resto fica sem link -->
        <component
          :is="conteudo.tipo === 'quiz' ? NuxtLink : 'div'"
          :to="conteudo.tipo === 'quiz' ? `${linkBase}/${conteudo.id}` : undefined"
          class="flex items-center gap-3 px-4 py-3 sm:px-6"
          :class="conteudo.tipo === 'quiz' && 'transition-colors hover:bg-elevated/50 focus-visible:bg-elevated/50 focus-visible:outline-none'"
        >
          <span class="w-5 shrink-0 text-right text-sm font-medium text-dimmed">
            {{ posicao + 1 }}
          </span>

          <div class="flex size-9 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary">
            <UIcon
              :name="icones[conteudo.tipo] ?? 'i-lucide-file'"
              class="size-4"
            />
          </div>

          <div class="min-w-0 flex-1 space-y-1.5">
            <div class="flex items-baseline justify-between gap-3">
              <div class="min-w-0">
                <p class="truncate font-medium text-highlighted">
                  {{ conteudo.titulo }}
                </p>

                <p class="truncate text-xs text-muted">
                  {{ conteudo.modulo }}
                </p>
              </div>

              <div class="flex shrink-0 items-center gap-2 text-sm">
                <!-- quanto caiu do conteudo anterior -->
                <span
                  v-if="conteudo.queda > 0"
                  class="text-xs text-error"
                >
                  −{{ conteudo.queda }}
                </span>

                <span class="font-semibold tabular-nums">
                  {{ formatarPorcentagem(conteudo.porcentagem) }}
                </span>

                <span class="text-muted">
                  · {{ conteudo.concluiram }}
                </span>
              </div>
            </div>

            <UProgress
              :model-value="conteudo.porcentagem"
              :max="1"
              size="sm"
            />
          </div>

          <UIcon
            name="i-lucide-chevron-right"
            class="size-4 shrink-0 text-dimmed"
          />
        </component>
      </li>
    </ol>

    <p
      v-else
      class="p-4 text-sm text-muted sm:p-6"
    >
      A trilha ainda não tem conteúdos.
    </p>
  </UCard>
</template>

<script setup lang="ts">
const NuxtLink = resolveComponent('NuxtLink')
import type { ConteudoFunilRead } from '~/types/generated'

const props = defineProps<{
  funil: ConteudoFunilRead[]
  iniciaram: number
  // rota da dash do conteudo sem o id
  linkBase: string
}>()

const icones: Record<string, string> = {
  video: 'i-lucide-play',
  artigo: 'i-lucide-book-open',
  quiz: 'i-lucide-list-checks',
}

const formatarPorcentagem = new Intl.NumberFormat('pt-BR', { style: 'percent', maximumFractionDigits: 1 }).format

const lista = computed(() => props.funil.map((conteudo, posicao) => {
  const anterior = props.funil[posicao - 1]
  return {
    ...conteudo,
    porcentagem: props.iniciaram ? conteudo.concluiram / props.iniciaram : 0,
    queda: anterior ? anterior.concluiram - conteudo.concluiram : 0,
  }
}))
</script>
