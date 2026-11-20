<template>
  <UCard>
    <template #header>
      <div class="flex items-center justify-between gap-3">
        <h2 class="font-medium">
          Progresso nas trilhas
        </h2>
        <UButton
          label="Ver trilhas"
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

    <p
      v-else-if="!trilhas.length"
      class="text-sm text-muted"
    >
      Nenhuma trilha disponível.
    </p>

    <ul
      v-else
      class="divide-y divide-default"
    >
      <li
        v-for="trilha in ordenadas"
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
            :color="trilha.progresso === 100 ? 'success' : 'primary'"
            size="sm"
          />
          <p
            v-if="trilha.proximo_conteudo_titulo && trilha.concluidos > 0"
            class="truncate text-xs text-muted"
          >
            Próximo: {{ trilha.proximo_conteudo_titulo }}
          </p>
        </div>

        <UBadge
          v-if="!trilha.proximo_conteudo_id && trilha.total > 0"
          label="Concluída"
          color="success"
          variant="subtle"
          icon="i-lucide-check"
        />
        <UButton
          v-else-if="trilha.proximo_conteudo_id"
          :label="trilha.concluidos > 0 ? 'Continuar' : 'Começar'"
          :to="`/trilhas/${trilha.id}/conteudos/${trilha.proximo_conteudo_id}`"
          :variant="trilha.concluidos > 0 ? 'solid' : 'outline'"
          trailing-icon="i-lucide-play"
          size="sm"
        />
      </li>
    </ul>
  </UCard>
</template>

<script setup lang="ts">
import type { TrilhaResumoRead } from '~/types/generated'

const trilhas = ref<TrilhaResumoRead[]>([])
const carregando = ref(true)

onMounted(async () => {
  try {
    trilhas.value = await useApi()('/progresso/trilhas')
  }
  catch {
    trilhas.value = []
  }
  carregando.value = false
})

// em andamento primeiro, dps as nao comecadas e as concluidas no fim
function peso(trilha: TrilhaResumoRead) {
  if (trilha.total > 0 && !trilha.proximo_conteudo_id) return 2
  if (trilha.concluidos > 0) return 0
  return 1
}

const ordenadas = computed(() => [...trilhas.value].sort((a, b) => peso(a) - peso(b)))
</script>
