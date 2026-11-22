<template>
  <div class="mx-auto w-full max-w-4xl space-y-8">
    <CamusBanner
      titulo="Ranking"
      descricao="Os 50 exploradores com mais XP no Camus."
      imagem="/papeis-de-parede/amarelo/conquistas.webp"
      headline="Comunidade"
      icone="i-lucide-medal"
    />

    <UAlert
      v-if="erro"
      color="error"
      variant="subtle"
      icon="i-lucide-circle-alert"
      title="Não foi possível carregar o ranking"
      :actions="[{ label: 'Tentar de novo', onClick: carregar }]"
    />

    <!-- carregando -->
    <div v-else-if="carregando" class="space-y-6">
      <div class="grid grid-cols-3 items-end gap-3">
        <USkeleton class="h-48 rounded-xl" />
        <USkeleton class="h-60 rounded-xl" />
        <USkeleton class="h-40 rounded-xl" />
      </div>
      <USkeleton v-for="i in 5" :key="i" class="h-14 rounded-xl" />
    </div>

    <UCard v-else-if="!ranking.length" class="text-center">
      <UIcon name="i-lucide-trophy" class="size-10 text-primary" />
      <p class="mt-2 text-muted">Ninguém ganhou XP ainda. Que tal ser o primeiro?</p>
    </UCard>

    <RankingLista v-else :ranking="ranking" />
  </div>
</template>

<script setup lang="ts">
import type { RankingItemRead } from '~/types/generated'

definePageMeta({ middleware: 'role' })

const api = useApi()

const ranking = ref<RankingItemRead[]>([])
const carregando = ref(true)
const erro = ref(false)

async function carregar() {
  carregando.value = true
  erro.value = false
  try {
    ranking.value = await api('/pontuacao/ranking')
  }
  catch {
    erro.value = true
  }
  carregando.value = false
}

onMounted(carregar)
</script>
