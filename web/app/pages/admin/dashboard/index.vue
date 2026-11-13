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

      <div class="space-y-6 xl:col-span-2">
        <DashboardCadastros :cadastros="dados.cadastros_por_dia" />

        <UCard>
          <template #header>
            <h2 class="font-medium">
              Trilhas por escopo
            </h2>
            <p class="text-sm text-muted">
              Todas as trilhas cadastradas, incluindo rascunhos.
            </p>
          </template>

          <UChart
            v-if="dados.total_trilhas > 0"
            type="donut"
            :data="trilhasPorEscopo"
            index="escopo"
            :categories="[{ key: 'quantidade', label: 'Trilhas' }]"
            :height="208"
            :colors="['primary', 'quaternary']"
            :legend="false"
            :format="formatarNumero"
            :aria-label="`Trilhas por escopo. Globais: ${dados.total_trilhas_globais}. De grupo: ${dados.total_trilhas_de_grupo}.`"
          >
            <template #center>
              <span class="text-2xl font-semibold text-highlighted" aria-hidden="true">
                {{ formatarNumero(dados.total_trilhas) }}
              </span>
            </template>
          </UChart>
          <p v-else class="text-sm text-muted">
            Nenhuma trilha cadastrada.
          </p>

          <ul
            v-if="dados.total_trilhas > 0"
            class="mt-3 flex flex-wrap justify-center gap-x-6 gap-y-2 text-sm text-muted"
          >
            <li
              v-for="trilha in trilhasPorEscopo"
              :key="trilha.escopo"
              class="flex items-center gap-2"
            >
              <span
                class="size-2 rounded-full"
                :class="trilha.escopo === 'Globais' ? 'bg-primary' : 'bg-quaternary'"
                aria-hidden="true"
              />
              {{ trilha.escopo }}
              <span class="font-medium text-highlighted">
                {{ formatarNumero(trilha.quantidade) }}
              </span>
            </li>
          </ul>
        </UCard>
      </div>
      <DashboardConquistas :conquistas="dados.conquistas_por_quantidade" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { FetchError } from 'ofetch'
import type { DashboardRead } from '~/types/generated'

definePageMeta({ middleware: 'role', roles: ['admin'] })

const api = useApi()
const dados = ref<DashboardRead | null>(null)
const formatarNumero = new Intl.NumberFormat('pt-BR').format
const trilhasPorEscopo = computed(() => [
  { escopo: 'Globais', quantidade: dados.value?.total_trilhas_globais ?? 0 },
  { escopo: 'De grupo', quantidade: dados.value?.total_trilhas_de_grupo ?? 0 },
])
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
