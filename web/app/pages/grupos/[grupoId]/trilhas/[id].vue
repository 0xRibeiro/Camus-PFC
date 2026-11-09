<template>
  <section class="space-y-4">
    <div class="flex flex-wrap items-center justify-between gap-3">
      <UButton
        label="Voltar ao grupo"
        icon="i-lucide-arrow-left"
        :to="`/grupos/${grupoId}`"
        color="neutral"
        variant="ghost"
      />
      <UButton
        v-if="trilha?.is_active && !erro"
        :label="gerenciando ? 'Estudar trilha' : 'Gerenciar trilha'"
        color="neutral"
        variant="outline"
        @click="gerenciando = !gerenciando"
      />
    </div>

    <p
      v-if="loading"
      class="text-muted"
    >
      Carregando trilha…
    </p>
    <UAlert
      v-else-if="erro"
      title="Trilha indisponível"
      color="error"
      variant="soft"
    />
    <GrupoEditarTrilha
      v-else-if="gerenciando && trilha"
      v-model:trilha="trilha"
    />
    <GrupoEstudarTrilha
      v-else
      :trilha-id="trilhaId"
    />
  </section>
</template>

<script setup lang="ts">
import type { GrupoRead, TrilhaRead } from '~/types/generated'

definePageMeta({ middleware: 'role', key: route => route.path })

const route = useRoute()
const api = useApi()
const auth = useAuthStore()
const grupoId = Number(route.params.grupoId)
const trilhaId = Number(route.params.id)
const grupo = ref<GrupoRead | null>(null)
const trilha = ref<TrilhaRead | null>(null)
const loading = ref(true)
const erro = ref(false)
const gerenciando = ref(false)

async function carregar() {
  loading.value = true
  erro.value = false
  try {
    grupo.value = await api(`/grupos/${grupoId}`)
    if (grupo.value?.id_dono === auth.user?.id) {
      trilha.value = await api(`/trilhas/${trilhaId}`)
      gerenciando.value = true
    }
  }
  catch {
    erro.value = true
  }
  finally {
    loading.value = false
  }
}

onMounted(carregar)
</script>
