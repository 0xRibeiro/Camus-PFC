<template>
  <div class="flex-1">
    <div class="mx-auto w-full max-w-6xl space-y-6 p-4">
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
        <div class="space-y-3 border-b border-default pb-6">
          <h1 class="text-3xl font-bold text-highlighted wrap-anywhere">
            {{ aquario.nome }}
          </h1>

          <div class="flex flex-wrap gap-2">
            <UBadge
              icon="i-lucide-droplets"
              :label="aquario.litros === null ? 'Volume não informado' : `${aquario.litros} litros`"
              color="info"
              variant="subtle"
              size="lg"
            />

            <UBadge
              :icon="aquario.dispositivo ? 'i-lucide-wifi' : 'i-lucide-wifi-off'"
              :label="textoIot"
              :color="aquario.dispositivo?.estado === 'online' ? 'success' : 'neutral'"
              variant="subtle"
              size="lg"
            />

            <UBadge
              :icon="papeis[aquario.papel ?? 'dono'].icone"
              :label="`Você é ${papeis[aquario.papel ?? 'dono'].nome}`"
              color="neutral"
              variant="subtle"
              size="lg"
            />
          </div>
        </div>

        <AquarioModulos
          v-if="aquario.dispositivo"
          :aquario-id="aquario.id"
          :pode-editar="aquario.papel !== 'leitor'"
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
  </div>
</template>

<script setup lang="ts">
import AquarioIot from '~/components/aquario/AquarioIot.vue'
import AquarioMembros from '~/components/aquario/AquarioMembros.vue'
import AquarioModulos from '~/components/aquario/AquarioModulos.vue'
import AquarioPeixes from '~/components/peixes/AquarioPeixes.vue'
import type { AquarioRead, DispositivoRead, PapelAquario } from '~/types/generated'

definePageMeta({ middleware: 'role', key: route => route.path })

const route = useRoute()
const api = useApi()
const aquario = ref<AquarioRead | null>(null)
const carregando = ref(true)

const papeis: Record<PapelAquario, { nome: string, icone: string }> = {
  dono: { nome: 'dono', icone: 'i-lucide-crown' },
  operador: { nome: 'operador', icone: 'i-lucide-wrench' },
  leitor: { nome: 'leitor', icone: 'i-lucide-eye' },
}

const textoIot = computed(() => {
  if (!aquario.value?.dispositivo) return 'Sem IoT'
  return aquario.value.dispositivo.estado === 'online' ? 'IoT online' : 'IoT offline'
})

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
