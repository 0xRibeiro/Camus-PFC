<template>
  <UCard>
    <template #header>
      <div class="flex items-center justify-between gap-3">
        <h2 class="font-medium">
          Últimas conquistas
        </h2>
        <UButton
          label="Ver todas"
          to="/conquistas"
          color="neutral"
          variant="link"
          trailing-icon="i-lucide-arrow-right"
          size="sm"
        />
      </div>
    </template>

    <p
      v-if="!ultimas.length"
      class="text-sm text-muted"
    >
      Nenhuma conquista ainda. Explore a plataforma para desbloquear.
    </p>

    <ul
      v-else
      class="space-y-2"
    >
      <li
        v-for="conquista in ultimas"
        :key="conquista.id"
        class="relative flex items-center gap-3 overflow-hidden rounded-xl bg-gradient-to-r from-yellow-400/20 via-amber-300/10 to-transparent p-2 ring ring-amber-400/30"
      >
        <!-- medalha dourada com brilho -->
        <div class="flex size-11 shrink-0 items-center justify-center overflow-hidden rounded-full bg-gradient-to-br from-yellow-300 via-amber-400 to-yellow-600 text-white shadow-md shadow-amber-500/40 ring-2 ring-yellow-200/60">
          <img
            v-if="conquista.imagem_dir"
            :src="conquista.imagem_dir"
            :alt="conquista.titulo"
            class="size-full object-cover"
          >
          <UIcon
            v-else
            name="i-lucide-trophy"
            class="size-5 drop-shadow"
          />
        </div>
        <div class="min-w-0 flex-1">
          <p class="truncate text-sm font-semibold text-highlighted">
            {{ conquista.titulo }}
          </p>
          <p
            v-if="conquista.desbloqueada_em"
            class="text-xs text-amber-700 dark:text-amber-300"
          >
            {{ formatarData(conquista.desbloqueada_em) }}
          </p>
        </div>
        <UIcon
          name="i-lucide-sparkles"
          class="size-4 shrink-0 text-amber-500"
        />
      </li>
    </ul>
  </UCard>
</template>

<script setup lang="ts">
import type { ConquistaUsuarioRead } from '~/types/generated'

// o back ja manda da mais nova pra mais velha
const props = defineProps<{
  conquistas: ConquistaUsuarioRead[]
}>()

const ultimas = computed(() => props.conquistas.slice(0, 3))

function formatarData(data: string) {
  return new Date(data).toLocaleDateString('pt-BR', { day: '2-digit', month: 'long', year: 'numeric' })
}
</script>
