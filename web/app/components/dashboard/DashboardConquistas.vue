<template>
  <UCard>
    <template #header>
      <div>
        <h2 class="font-medium">
          Conquistas mais e menos obtidas
        </h2>

        <p class="text-sm text-muted">
          Ordenadas pela quantidade de usuários que as obtiveram.
        </p>
      </div>
    </template>

    <div
      v-if="conquistas.length"
      class="space-y-5"
    >
      <div
        v-for="conquista in conquistas"
        :key="conquista.id"
        class="space-y-2"
      >
        <div class="flex items-center justify-between gap-3">
          <p class="min-w-0 break-words font-medium">
            {{ conquista.titulo }}
          </p>

          <span class="shrink-0 text-sm text-muted">
            {{ conquista.quantidade.toLocaleString('pt-BR') }}
            {{ conquista.quantidade === 1 ? 'usuário' : 'usuários' }}
          </span>
        </div>

        <div
          class="h-2 overflow-hidden rounded-full bg-elevated"
          aria-hidden="true"
        >
          <div
            class="h-full rounded-full bg-primary"
            :style="{ width: `${conquista.quantidade / maiorQuantidade * 100}%` }"
          />
        </div>
      </div>
    </div>

    <p
      v-else
      class="text-sm text-muted"
    >
      Nenhuma conquista cadastrada.
    </p>
  </UCard>
</template>

<script setup lang="ts">
import type { ConquistaResumoRead } from '~/types/generated'

const props = defineProps<{
  conquistas: ConquistaResumoRead[]
}>()

// o mínimo de 1 evita divisão por zero quando nenhuma conquista foi obtida
const maiorQuantidade = computed(() => Math.max(1, ...props.conquistas.map(conquista => conquista.quantidade)))
</script>
