<script setup lang="ts">
import type { TrilhaResumoRead } from '~/types/generated'

definePageMeta({ middleware: 'role', key: route => route.path })

const grupoId = useRoute().params.grupoId
const api = useApi()

const toast = useToast()

const trilhas = ref<TrilhaResumoRead[]>([])
const loading = ref(true)

async function fetchTrilhas() {
  loading.value = true
  try {
    trilhas.value = await api('/progresso/trilhas')
  }
  catch {
    toast.add({ title: 'Não foi possível carregar as trilhas', color: 'error' })
  }
  loading.value = false
}

onMounted(fetchTrilhas)
</script>

<template>
  <div class="grid flex-1 auto-rows-min grid-cols-[minmax(0,1fr)_auto] items-start gap-4 xl:grid-cols-[minmax(0,1fr)_clamp(12rem,18vw,17rem)] xl:gap-x-5">
    <div class="contents xl:block xl:min-w-0">
      <div class="min-w-0">
        <UButton
          v-if="grupoId"
          label="Voltar ao grupo"
          icon="i-lucide-arrow-left"
          variant="link"
          color="neutral"
          class="mb-3 px-0"
          :to="`/grupos/${grupoId}`"
        />

        <div class="xl:mb-4">
          <h1 class="text-xl font-semibold">
            {{ grupoId ? 'Trilhas do grupo' : 'Trilhas' }}
          </h1>
          <p class="text-sm text-muted">
            Escolha uma trilha e siga os conteúdos na ordem.
          </p>
        </div>
      </div>

      <div class="col-span-2 row-start-2 min-w-0">
        <div v-if="loading" class="flex justify-center py-12">
          <UIcon name="i-lucide-loader-circle" class="size-6 animate-spin" />
        </div>

        <p v-else-if="!trilhas.length" class="text-sm text-muted text-center py-12">
          Nenhuma trilha disponível ainda.
        </p>

        <UPageGrid v-else>
          <UCard v-for="trilha in trilhas" :key="trilha.id">
            <NuxtLink
              :to="grupoId ? `/grupos/${grupoId}/trilhas/${trilha.id}` : `/trilhas/${trilha.id}`"
              class="block"
            >
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
                <div class="flex justify-between text-xs text-muted">
                  <span>{{ trilha.concluidos }}/{{ trilha.total }} conteúdos</span>
                  <span>{{ trilha.progresso }}%</span>
                </div>
                <UProgress :model-value="trilha.progresso" size="sm" />
              </div>
            </template>
          </UCard>
        </UPageGrid>
      </div>
    </div>

    <CamusImagem
      :src="grupoId
        ? '/papeis-de-parede/laranja/trilha-vertical.webp'
        : '/papeis-de-parede/vermelho/trilha-vertical.webp'"
      media="(width < 1280px)"
      class="col-start-2 row-start-1 w-24 sm:w-32 xl:w-full"
      img-class="h-auto w-full rounded-xl"
    />
  </div>
</template>
