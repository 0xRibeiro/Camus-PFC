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

      <AquarioPeixes
        :aquario-id="aquario.id"
        :pode-editar="aquario.papel !== 'leitor'"
      />

      <div class="grid gap-4 md:grid-cols-2">
        <AquarioIot
          :aquario-id="aquario.id"
          :papel="aquario.papel ?? 'dono'"
          :dispositivo="aquario.dispositivo ?? null"
          @atualizado="atualizarDispositivo"
        />

        <AquarioMembros
          :aquario-id="aquario.id"
          :papel="aquario.papel ?? 'dono'"
        />
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import AquarioIot from '~/components/aquario/AquarioIot.vue'
import AquarioMembros from '~/components/aquario/AquarioMembros.vue'
import AquarioPeixes from '~/components/peixes/AquarioPeixes.vue'
import type { AquarioRead, DispositivoRead } from '~/types/generated'

definePageMeta({ middleware: 'role', key: route => route.path })

const route = useRoute()
const api = useApi()
const aquario = ref<AquarioRead | null>(null)
const carregando = ref(true)

function atualizarDispositivo(dispositivo: DispositivoRead | null) {
  if (aquario.value) {
    aquario.value.dispositivo = dispositivo
  }
}

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
