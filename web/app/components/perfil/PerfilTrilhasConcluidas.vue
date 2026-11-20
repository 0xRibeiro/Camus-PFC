<template>
  <UCard>
    <template #header>
      <h2 class="font-medium">
        Últimas trilhas concluídas
      </h2>
    </template>

    <div
      v-if="carregando"
      class="space-y-3"
    >
      <USkeleton
        v-for="indice in 3"
        :key="indice"
        class="h-10 w-full"
      />
    </div>

    <p
      v-else-if="!concluidas.length"
      class="text-sm text-muted"
    >
      Nenhuma trilha concluída ainda.
    </p>

    <ul
      v-else
      class="space-y-3"
    >
      <li
        v-for="trilha in concluidas.slice(0, 3)"
        :key="trilha.id"
      >
        <NuxtLink
          :to="`/trilhas/${trilha.id}`"
          class="group flex items-center gap-3"
        >
          <div class="flex size-10 shrink-0 items-center justify-center rounded-full bg-success/10 text-success">
            <UIcon
              name="i-lucide-check"
              class="size-5"
            />
          </div>
          <div class="min-w-0 flex-1">
            <p class="truncate text-sm font-medium text-highlighted group-hover:text-primary">
              {{ trilha.titulo }}
            </p>
            <p
              v-if="trilha.ultima_atividade_em"
              class="text-xs text-muted"
            >
              Concluída em {{ formatarData(trilha.ultima_atividade_em) }}
            </p>
          </div>
        </NuxtLink>
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

// a ultima conclusao de uma trilha completa é qnd ela terminou
const concluidas = computed(() => {
  const lista = []
  for (const trilha of props.trilhas) {
    if (trilha.total > 0 && !trilha.proximo_conteudo_id) lista.push(trilha)
  }
  return lista.sort((a, b) => (b.ultima_atividade_em ?? '').localeCompare(a.ultima_atividade_em ?? ''))
})

function formatarData(data: string) {
  return new Date(data).toLocaleDateString('pt-BR')
}
</script>
