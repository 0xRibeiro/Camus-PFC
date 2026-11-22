<template>
  <UCard>
    <NuxtLink :to="to" class="block">
      <TrilhaImagem :src="trilha.foto" :alt="trilha.titulo" />

      <div class="mt-3 space-y-1">
        <UBadge
          v-if="trilha.tag"
          :label="infoDaTagTrilha(trilha.tag).label"
          :color="infoDaTagTrilha(trilha.tag).color"
          variant="soft"
          size="sm"
          class="w-fit"
        />
        <p class="font-semibold">{{ trilha.titulo }}</p>
        <p v-if="trilha.descricao" class="text-sm text-muted line-clamp-2">
          {{ trilha.descricao }}
        </p>
      </div>
    </NuxtLink>

    <!-- progresso da trilha -->
    <template #footer>
      <div class="space-y-1">
        <div class="flex justify-between gap-2 text-xs text-muted">
          <span class="flex items-center gap-1">
            <UIcon
              name="i-lucide-layers"
              class="size-4 shrink-0"
            />
            {{ modulos }} módulo{{ modulos === 1 ? '' : 's' }}
            · {{ trilha.concluidos }}/{{ trilha.total }} conteúdos
          </span>
          <span>{{ trilha.progresso }}%</span>
        </div>
        <UProgress
          :model-value="trilha.progresso"
          :color="trilha.progresso === 100 ? 'success' : 'primary'"
          size="sm"
        />
      </div>
    </template>
  </UCard>
</template>

<script setup lang="ts">
import type { TrilhaResumoRead } from '~/types/generated'

const props = defineProps<{
  to: string
  trilha: TrilhaResumoRead
}>()

const modulos = computed(() => props.trilha.total_modulos ?? 0)
</script>
