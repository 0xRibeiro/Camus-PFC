<template>
  <UCard :class="card">
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
          class="h-28 w-full rounded-xl"
        />
      </template>

      <NuxtLink
        v-for="item in recordes"
        v-else
        :key="item.jogo"
        :to="ROTAS[item.jogo] ?? '/minigames'"
        class="group relative overflow-hidden rounded-xl p-4 ring transition hover:-translate-y-0.5"
        :class="item.recorde
          ? 'bg-gradient-to-br from-amber-400/20 via-orange-500/15 to-red-500/20 ring-orange-500/30 hover:shadow-lg hover:shadow-orange-500/20'
          : 'bg-elevated/50 ring-default'"
      >
        <!-- brilho de fundo atras do fogo -->
        <div
          v-if="item.recorde"
          class="pointer-events-none absolute -top-8 -right-8 size-28 rounded-full bg-orange-500/30 blur-2xl"
        />

        <p class="relative truncate text-sm font-medium text-highlighted">
          {{ item.titulo }}
        </p>

        <div class="relative mt-3 flex items-center gap-3">
          <div
            class="flex size-12 shrink-0 items-center justify-center rounded-full"
            :class="item.recorde
              ? 'bg-gradient-to-t from-red-500 via-orange-500 to-amber-400 shadow-lg shadow-orange-500/40'
              : 'bg-accented'"
          >
            <UIcon
              name="i-lucide-flame"
              class="size-7 transition group-hover:scale-110"
              :class="item.recorde ? 'text-white' : 'text-dimmed'"
            />
          </div>

          <div>
            <p
              class="text-3xl leading-none font-extrabold tabular-nums"
              :class="item.recorde ? 'bg-gradient-to-t from-red-500 to-amber-400 bg-clip-text text-transparent' : 'text-muted'"
            >
              {{ item.recorde }}
            </p>
            <p class="mt-1 text-xs text-muted">
              {{ item.recorde ? 'acertos seguidos' : 'jogue para acender' }}
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

const { card } = usePerfilVisual()

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
