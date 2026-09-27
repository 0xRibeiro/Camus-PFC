<template>
  <UTable :data="logs" :columns="columns" :loading="loading" class="cursor-pointer" @select="abrirDetalhe">
    <template #usuario_id-cell="{ row }">
      {{ nomeDoUsuario(row.original.usuario_id) }}
    </template>

    <template #acao-cell="{ row }">
      <UBadge :label="row.original.acao" :color="corDaAcao(row.original.acao)" variant="soft" />
    </template>

    <template #criado_em-cell="{ row }">
      {{ formatarData(row.original.criado_em) }}
    </template>
  </UTable>

  <AuditoriaDetalheModal v-model:open="modalAberto" :log="logSelecionado" />
</template>

<script setup lang="ts">
import type { TableColumn } from '@nuxt/ui'
import type { LogAuditoriaRead, UsuarioRead } from '~/types/generated'

const props = defineProps<{
  logs: LogAuditoriaRead[]
  loading: boolean
  usuarios: UsuarioRead[]
}>()

function nomeDoUsuario(usuarioId: number | null) {
  if (usuarioId === null) return '-'

  let username: string | undefined
  for (const usuario of props.usuarios) {
    if (usuario.id === usuarioId) {
      username = usuario.username
      break
    }
  }

  return `${usuarioId} - ${username ?? '?'}`
}

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

const modalAberto = ref(false)
const logSelecionado = ref<LogAuditoriaRead | null>(null)

function abrirDetalhe(_event: Event, row: { original: LogAuditoriaRead }) {
  logSelecionado.value = row.original
  modalAberto.value = true
}
</script>
