<template>
  <UTable
    :data="logs"
    :columns="columns"
    :loading="loading"
    :ui="{ base: 'table-fixed' }"
    class="cursor-pointer"
    @select="abrirDetalhe"
  >
    <template #entidade-cell="{ row }">
      <span
        class="inline-flex max-w-full truncate rounded-md px-2 py-0.5 text-xs font-medium"
        :class="entidadeAuditoria(row.original.entidade).classe"
      >
        {{ entidadeAuditoria(row.original.entidade).label }}
      </span>
    </template>

    <template #usuario_id-cell="{ row }">
      {{ row.original.usuario_id === null ? '-' : `${row.original.usuario_id} - ${row.original.usuario_nome ?? '?'}` }}
    </template>

    <template #acao-cell="{ row }">
      <UBadge
        :label="row.original.acao"
        :color="corDaAcao(row.original.acao)"
        variant="soft"
      />
    </template>

    <template #criado_em-cell="{ row }">
      {{ formatarData(row.original.criado_em) }}
    </template>
  </UTable>

  <AuditoriaDetalheModal
    v-model:open="modalAberto"
    :log="logSelecionado"
  />
</template>

<script setup lang="ts">
import type { TableColumn } from '@nuxt/ui'
import type { LogAuditoriaRead } from '~/types/generated'

// o nome de quem fez ja vem no log (usuario_nome), n precisa da lista de usuarios
defineProps<{
  logs: LogAuditoriaRead[]
  loading: boolean
}>()

// largura fixa pra tabela n mudar de tamanho de uma pagina pra outra
const columns: TableColumn<LogAuditoriaRead>[] = [
  { accessorKey: 'criado_em', header: 'Quando', meta: { class: { th: 'w-[20%]' } } },
  { accessorKey: 'usuario_id', header: 'Usuário', meta: { class: { th: 'w-[30%]', td: 'truncate' } } },
  { accessorKey: 'acao', header: 'Ação', meta: { class: { th: 'w-[13%]' } } },
  { accessorKey: 'entidade', header: 'Entidade', meta: { class: { th: 'w-[25%]' } } },
  { accessorKey: 'entidade_id', header: 'Id', meta: { class: { th: 'w-[12%]' } } },
]

function corDaAcao(acao: string) {
  if (acao === 'create') return 'success'
  if (acao === 'update') return 'warning'
  if (acao === 'delete') return 'error'
  if (acao === 'view') return 'info'
  return 'neutral'
}

function formatarData(valor: string) {
  return new Date(valor).toLocaleString('pt-BR')
}

const modalAberto = ref(false)
const logSelecionado = ref<LogAuditoriaRead | null>(null)

function abrirDetalhe(_event: Event, row: { original: LogAuditoriaRead }) {
  logSelecionado.value = row.original
  modalAberto.value = true
}
</script>
