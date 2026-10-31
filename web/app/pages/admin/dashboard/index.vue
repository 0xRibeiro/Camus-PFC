<template>
  <div>
    <div class="flex flex-wrap items-center justify-between gap-3 mb-6">
      <div>
        <h1 class="text-xl font-semibold">
          Dashboard
        </h1>

        <p class="text-sm text-muted">
          Indicadores gerais do Camus.
        </p>
      </div>

      <UButton
        label="Atualizar"
        icon="i-lucide-refresh-cw"
        color="neutral"
        variant="outline"
        :loading="loading"
        @click="fetchDashboard"
      />
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
      <DashboardCadastros :cadastros="dados.cadastros_por_dia" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { FetchError } from 'ofetch'
import type { DashboardRead } from '~/types/generated'

// permite o acesso à página apenas para administradores
definePageMeta({ middleware: 'role', roles: ['admin'] })

const api = useApi()
const dados = ref<DashboardRead | null>(null)
const loading = ref(true)
const erro = ref('')

async function fetchDashboard() {
  loading.value = true
  erro.value = ''

  try {
    dados.value = await api('/admin/dashboard')
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

onMounted(fetchDashboard)
</script>
