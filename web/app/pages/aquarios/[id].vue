<template>
  <div class="mx-auto w-full max-w-4xl space-y-6 p-4">
    <UButton
      to="/aquarios"
      label="Voltar aos aquários"
      icon="i-lucide-arrow-left"
      variant="ghost"
    />

    <USkeleton
      v-if="carregando"
      class="h-24 w-full rounded-lg"
    />

    <UAlert
      v-else-if="!aquario"
      color="error"
      title="Não foi possível abrir o aquário"
    />

    <template v-else>
      <UPageHeader
        :title="aquario.nome"
        :description="aquario.litros === null ? 'Volume não informado' : `${aquario.litros} L`"
      />

      <AquarioPeixes :aquario-id="aquario.id" />
    </template>
  </div>
</template>

<script setup lang="ts">
import AquarioPeixes from '~/components/peixes/AquarioPeixes.vue'

definePageMeta({ middleware: 'role', key: route => route.path })

type Aquario = {
  id: number
  nome: string
  litros: number | null
}

const route = useRoute()
const api = useApi()
const aquario = ref<Aquario | null>(null)
const carregando = ref(true)

onMounted(async () => {
  try {
    aquario.value = await api(`/aquarios/${route.params.id}`)
  }
  catch {
    aquario.value = null
  }
  finally {
    carregando.value = false
  }
})
</script>
