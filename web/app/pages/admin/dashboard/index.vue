<template>
  <div>
    <div class="flex flex-wrap items-end justify-between gap-4 mb-6">
      <div>
        <h1 class="text-xl font-semibold">
          Dashboard
        </h1>

        <p class="text-sm text-muted">
          Indicadores gerais do Camus.
        </p>
      </div>

      <div class="flex flex-wrap items-end gap-3">
        <UFormField label="Período dos cadastros">
          <USelect
            v-model="dias"
            :items="periodos"
            :disabled="loading"
            class="w-44"
          />
        </UFormField>

        <UButton
          label="Atualizar"
          icon="i-lucide-refresh-cw"
          color="neutral"
          variant="outline"
          :loading="loading"
          @click="fetchDashboard"
        />
      </div>
    </div>

    <div
      v-if="loading && !dados"
      class="flex justify-center py-12"
    >
      <UIcon
        name="i-lucide-loader-circle"
        class="size-6 animate-spin"
      />
    </div>

    <UCard v-else-if="erro">
      <div class="space-y-3">
        <p class="text-muted">
          {{ erro }}
        </p>

        <UButton
          label="Tentar novamente"
          color="neutral"
          variant="outline"
          :loading="loading"
          @click="fetchDashboard"
        />
      </div>
    </UCard>

    <div
      v-else-if="dados"
      class="space-y-6"
    >
      <DashboardNumeros :dados="dados" />

      <div class="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <DashboardCadastros
          :cadastros="dados.cadastros_por_dia"
          class="xl:col-span-2"
        />
        <DashboardConquistas :conquistas="dados.conquistas_por_quantidade" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { FetchError } from 'ofetch'
import type { DashboardRead } from '~/types/generated'

definePageMeta({ middleware: 'role', roles: ['admin'] })

const api = useApi()
const dados = ref<DashboardRead | null>(null)
const loading = ref(true)
const erro = ref('')

const dias = ref(30)

const periodos = [
  { label: 'Últimos 7 dias', value: 7 },
  { label: 'Últimos 30 dias', value: 30 },
  { label: 'Últimos 90 dias', value: 90 },
]

async function fetchDashboard() {
  loading.value = true
  erro.value = ''

  try {
    dados.value = await api('/admin/dashboard', { query: { dias: dias.value } })
  }
  catch (error) {
    erro.value = 'Não foi possível carregar a dashboard'

    if (error instanceof FetchError && typeof error.data?.detail === 'string') {
      erro.value = error.data.detail
    }
  }
  finally {
    loading.value = false
  }
}

// consulta novamente quando o período selecionado mudar
watch(dias, fetchDashboard)

// primeira consulta ao abrir a página
onMounted(fetchDashboard)
</script>
