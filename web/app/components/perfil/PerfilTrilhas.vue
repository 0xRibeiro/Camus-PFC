<template>
  <UCard>
    <template #header>
      <div class="flex items-center justify-between gap-3">
        <h2 class="font-medium">
          Trilhas em andamento
        </h2>
        <UButton
          v-if="emAndamento.length > LIMITE"
          label="Mostrar todas"
          to="/trilhas"
          color="neutral"
          variant="link"
          trailing-icon="i-lucide-arrow-right"
          size="sm"
        />
      </div>
    </template>

    <div
      v-if="carregando"
      class="space-y-4"
    >
      <USkeleton
        v-for="indice in 3"
        :key="indice"
        class="h-10 w-full"
      />
    </div>

    <div
      v-else-if="!emAndamento.length"
      class="flex flex-col items-start gap-2"
    >
      <p class="text-sm text-muted">
        Nenhuma trilha em andamento.
      </p>
      <UButton
        label="Escolher uma trilha"
        to="/trilhas"
        variant="outline"
        size="sm"
        trailing-icon="i-lucide-arrow-right"
      />
    </div>

    <ul
      v-else
      class="divide-y divide-default"
    >
      <li
        v-for="trilha in emAndamento.slice(0, LIMITE)"
        :key="trilha.id"
        class="flex items-center gap-4 py-3 first:pt-0 last:pb-0"
      >
        <div class="min-w-0 flex-1 space-y-1.5">
          <div class="flex items-center justify-between gap-2 text-sm">
            <NuxtLink
              :to="`/trilhas/${trilha.id}`"
              class="truncate font-medium text-highlighted hover:text-primary"
            >
              {{ trilha.titulo }}
            </NuxtLink>
            <span class="shrink-0 text-xs text-muted tabular-nums">
              {{ trilha.concluidos }}/{{ trilha.total }}
            </span>
          </div>
          <UProgress
            :model-value="trilha.progresso"
            size="sm"
          />
          <p
            v-if="trilha.proximo_conteudo_titulo"
            class="truncate text-xs text-muted"
          >
            Próximo: {{ trilha.proximo_conteudo_titulo }}
          </p>
        </div>

        <UButton
          label="Continuar"
          :to="`/trilhas/${trilha.id}/conteudos/${trilha.proximo_conteudo_id}`"
          trailing-icon="i-lucide-play"
          size="sm"
        />
      </li>
    </ul>
  </UCard>
</template>

<script setup lang="ts">
import type { TrilhaResumoRead } from '~/types/generated'

const props = defineProps<{
  trilhas: TrilhaResumoRead[]
  carregando: boolean
}>()

const LIMITE = 5

// comecou e n terminou, a q mexeu por ultimo fica no topo
const emAndamento = computed(() => {
  const lista = []
  for (const trilha of props.trilhas) {
    if (trilha.concluidos > 0 && trilha.proximo_conteudo_id) lista.push(trilha)
  }
  return lista.sort((a, b) => (b.ultima_atividade_em ?? '').localeCompare(a.ultima_atividade_em ?? ''))
})
</script>
