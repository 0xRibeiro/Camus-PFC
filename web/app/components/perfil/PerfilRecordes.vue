<template>
  <UCard>
    <template #header>
      <div class="flex items-center justify-between gap-3">
        <h2 class="font-medium">
          Recordes nos minigames
        </h2>
        <UButton
          label="Jogar"
          to="/minigames"
          color="neutral"
          variant="link"
          trailing-icon="i-lucide-arrow-right"
          size="sm"
        />
      </div>
    </template>

    <div class="grid gap-3 sm:grid-cols-2">
      <template v-if="carregando">
        <USkeleton
          v-for="indice in 2"
          :key="indice"
          class="h-24 w-full"
        />
      </template>

      <NuxtLink
        v-for="item in recordes"
        v-else
        :key="item.jogo"
        :to="ROTAS[item.jogo] ?? '/minigames'"
        class="rounded-lg bg-elevated/50 p-3 transition hover:bg-elevated"
      >
        <p class="truncate text-sm font-medium text-highlighted">
          {{ item.titulo }}
        </p>
        <div class="mt-2 flex items-end justify-between gap-2">
          <div>
            <p class="flex items-center gap-1 text-2xl font-bold text-highlighted tabular-nums">
              <UIcon
                name="i-lucide-flame"
                class="size-5 text-warning"
              />
              {{ item.recorde }}
            </p>
            <p class="text-xs text-muted">
              maior sequência
            </p>
          </div>
          <div class="text-right text-xs text-muted">
            <p>{{ item.acertos }} acertos</p>
            <p v-if="item.respondidas">
              {{ Math.round(item.acertos * 100 / item.respondidas) }}% de acerto
            </p>
            <p v-else>
              nunca jogou
            </p>
          </div>
        </div>
      </NuxtLink>
    </div>
  </UCard>
</template>

<script setup lang="ts">
import type { RecordeRead } from '~/types/generated'

// o back manda o nome do jogo, a rota fica aqui
const ROTAS: Record<string, string> = {
  quem_e_esse_peixe: '/minigames/quem-e-esse-peixe',
  meio_peixe_meio_fotografo: '/minigames/meio-peixe-meio-fotografo',
}

const recordes = ref<RecordeRead[]>([])
const carregando = ref(true)

onMounted(async () => {
  try {
    recordes.value = await useApi()('/minigames/recordes')
  }
  catch {
    recordes.value = []
  }
  carregando.value = false
})
</script>
