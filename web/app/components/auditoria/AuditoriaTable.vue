<template>
  <UTable :data="logs" :columns="columns" :loading="loading">
    <template #acao-cell="{ row }">
      <UBadge :label="row.original.acao" :color="corDaAcao(row.original.acao)" variant="soft" />
    </template>

    <template #criado_em-cell="{ row }">
      {{ formatarData(row.original.criado_em) }}
    </template>
  </UTable>
</template>

<script setup lang="ts">
import type { TableColumn } from '@nuxt/ui'
import type { LogAuditoriaRead } from '~/types/generated'

defineProps<{
  logs: LogAuditoriaRead[]
  loading: boolean
}>()

const columns: TableColumn<LogAuditoriaRead>[] = [
  { accessorKey: 'criado_em', header: 'Quando' },
  { accessorKey: 'usuario_id', header: 'Usuário' },
  { accessorKey: 'acao', header: 'Ação' },
  { accessorKey: 'entidade', header: 'Entidade' },
  { accessorKey: 'entidade_id', header: 'Id' },
]

function corDaAcao(acao: string) {
  if (acao === 'create') return 'success'
  if (acao === 'update') return 'warning'
  if (acao === 'delete') return 'error'
  return 'neutral'
}

function formatarData(valor: string) {
  return new Date(valor).toLocaleString('pt-BR')
}
</script>
