<template>
  <div>
    <h1 class="text-xl font-semibold mb-4">
      Denúncias
    </h1>

    <div class="flex flex-wrap items-end gap-3 mb-4">
      <UFormField label="Status">
        <USelect
          v-model="filtroStatus"
          :items="opcoesStatus"
          class="w-40"
        />
      </UFormField>
    </div>

    <UTable
      :data="denuncias"
      :columns="columns"
      :loading="loading"
    >
      <template #motivo-cell="{ row }">
        {{ rotuloMotivo(row.original.motivo) }}
      </template>

      <template #alvo-cell="{ row }">
        <p class="font-medium">
          {{ row.original.conteudo ?? 'Grupo inteiro' }}
        </p>
        <p
          v-if="row.original.descricao"
          class="text-sm text-muted max-w-xs break-words"
        >
          {{ row.original.descricao }}
        </p>
      </template>

      <template #criado_em-cell="{ row }">
        {{ formatarData(row.original.criado_em) }}
      </template>

      <template #status-cell="{ row }">
        <UBadge
          :color="corStatus(row.original.status)"
          variant="soft"
        >
          {{ row.original.status }}
        </UBadge>
      </template>

      <template #acoes-cell="{ row }">
        <!-- os botões só aparecem se a denúncia ainda estiver pendente -->
        <div
          v-if="row.original.status === 'pendente'"
          class="flex gap-2"
        >
          <UButton
            label="Resolver"
            size="sm"
            :loading="atualizando === row.original.id"
            @click="analisar(row.original, 'resolvida')"
          />
          <UButton
            label="Rejeitar"
            size="sm"
            color="neutral"
            variant="outline"
            :disabled="atualizando === row.original.id"
            @click="analisar(row.original, 'rejeitada')"
          />
        </div>
      </template>
    </UTable>

    <p
      v-if="!loading && denuncias.length === 0"
      class="text-sm text-muted mt-4"
    >
      Nenhuma denúncia encontrada.
    </p>
  </div>
</template>

<script setup lang="ts">
import type { TableColumn } from '@nuxt/ui'
import { FetchError } from 'ofetch'
import type { DenunciaAdminRead } from '~/types/generated/types.gen'

definePageMeta({ middleware: 'role', roles: ['admin'] })

const api = useApi()
const toast = useToast()

const denuncias = ref<DenunciaAdminRead[]>([])
const loading = ref(true)
const atualizando = ref<number | null>(null)

// "todas" não é enviado pro back, é só pra tirar o filtro
const filtroStatus = ref('pendente')

const opcoesStatus = [
  { label: 'Pendentes', value: 'pendente' },
  { label: 'Resolvidas', value: 'resolvida' },
  { label: 'Rejeitadas', value: 'rejeitada' },
  { label: 'Todas', value: 'todas' },
]

const motivos: Record<string, string> = {
  conteudo_improprio: 'Conteúdo impróprio',
  assedio: 'Assédio',
  spam: 'Spam',
  outro: 'Outro',
}

const columns: TableColumn<DenunciaAdminRead>[] = [
  { accessorKey: 'grupo', header: 'Grupo' },
  { accessorKey: 'dono', header: 'Dono' },
  { accessorKey: 'denunciante', header: 'Denunciante' },
  { accessorKey: 'motivo', header: 'Motivo' },
  { id: 'alvo', header: 'Alvo' },
  { accessorKey: 'criado_em', header: 'Data' },
  { accessorKey: 'status', header: 'Status' },
  { id: 'acoes', header: 'Ações' },
]

function rotuloMotivo(motivo: string): string {
  return motivos[motivo] ?? motivo
}

function formatarData(data: string): string {
  return new Date(data).toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' })
}

function corStatus(status: DenunciaAdminRead['status']) {
  if (status === 'pendente') return 'warning'
  if (status === 'resolvida') return 'success'
  return 'neutral'
}

async function fetchDenuncias() {
  loading.value = true
  try {
    denuncias.value = await api('/admin/denuncias', {
      query: { status: filtroStatus.value === 'todas' ? undefined : filtroStatus.value },
    })
  }
  catch {
    denuncias.value = []
    toast.add({ title: 'Não foi possível carregar as denúncias', color: 'error' })
  }
  finally {
    loading.value = false
  }
}

async function analisar(denuncia: DenunciaAdminRead, status: 'resolvida' | 'rejeitada') {
  atualizando.value = denuncia.id

  try {
    await api(`/admin/denuncias/${denuncia.id}`, { method: 'PATCH', body: { status } })
    toast.add({ title: status === 'resolvida' ? 'Denúncia resolvida' : 'Denúncia rejeitada', color: 'success' })
    await fetchDenuncias()
  }
  catch (error) {
    const detalhe = error instanceof FetchError && typeof error.data?.detail === 'string' ? error.data.detail : null
    toast.add({ title: detalhe ?? 'Não foi possível atualizar a denúncia', color: 'error' })
  }
  finally {
    atualizando.value = null
  }
}

watch(filtroStatus, fetchDenuncias)
onMounted(fetchDenuncias)
</script>
