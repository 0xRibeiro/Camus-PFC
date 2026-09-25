<template>
  <div>
    <h1 class="text-xl font-semibold mb-4">
      Auditoria
    </h1>

    <div class="flex flex-wrap items-end gap-3 mb-4">
      <UFormField label="Entidade">
        <USelect v-model="entidade" :items="opcoesEntidade" class="w-40" />
      </UFormField>

      <UFormField label="Id do usuário">
        <UInput v-model.number="usuarioId" type="number" class="w-32" />
      </UFormField>
    </div>

    <AuditoriaTable :logs="logs" :loading="loading" />

    <div class="flex justify-end gap-2 mt-4">
      <UButton
        label="Anterior"
        variant="outline"
        :disabled="pagina === 1"
        @click="paginaAnterior"
      />
      <UButton
        label="Próxima"
        variant="outline"
        :disabled="logs.length < itensPorPagina"
        @click="proximaPagina"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import type { LogAuditoriaRead } from '~/types/generated'

definePageMeta({ middleware: 'role', roles: ['admin'] })

const logs = ref<LogAuditoriaRead[]>([])
const loading = ref(true)

const itensPorPagina = 10
const pagina = ref(1)
const entidade = ref<string | undefined>(undefined)
const usuarioId = ref<number | undefined>(undefined)

async function fetchLogs() {
  loading.value = true
  const api = useApi()
  const offset = (pagina.value - 1) * itensPorPagina

  logs.value = await api('/admin/auditoria', {
    query: {
      limite: itensPorPagina,
      offset,
      entidade: entidade.value,
      usuario_id: usuarioId.value,
    },
  })

  loading.value = false
}

onMounted(fetchLogs)

const opcoesEntidade = [
  { label: 'Todas', value: undefined },
  { label: 'usuarios', value: 'usuarios' },
  { label: 'trilhas', value: 'trilhas' },
  { label: 'modulos', value: 'modulos' },
  { label: 'conteudos', value: 'conteudos' },
  { label: 'questoes', value: 'questoes' },
  { label: 'alternativas', value: 'alternativas' },
  { label: 'conquistas', value: 'conquistas' },
]

// muda filtro -> volta pra pagina 1 e busca de novo
watch([entidade, usuarioId], () => {
  pagina.value = 1
  fetchLogs()
})

function paginaAnterior() {
  pagina.value -= 1
  fetchLogs()
}

function proximaPagina() {
  pagina.value += 1
  fetchLogs()
}
</script>
