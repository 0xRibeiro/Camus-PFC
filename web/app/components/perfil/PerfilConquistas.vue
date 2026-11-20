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
      class="space-y-3"
    >
      <li
        v-for="conquista in ultimas"
        :key="conquista.id"
        class="flex items-center gap-3"
      >
        <div class="flex size-11 shrink-0 items-center justify-center overflow-hidden rounded-xl bg-primary/10 text-primary">
          <img
            v-if="conquista.imagem_dir"
            :src="conquista.imagem_dir"
            :alt="conquista.titulo"
            class="size-full object-cover"
          >
          <UIcon
            v-else
            name="i-lucide-award"
            class="size-6"
          />
        </div>
        <div class="min-w-0 flex-1">
          <p class="truncate text-sm font-medium text-highlighted">
            {{ conquista.titulo }}
          </p>
          <p
            v-if="conquista.desbloqueada_em"
            class="text-xs text-muted"
          >
            {{ formatarData(conquista.desbloqueada_em) }}
          </p>
        </div>
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
