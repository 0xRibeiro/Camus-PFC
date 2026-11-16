<template>
  <div>
    <h1 class="text-xl font-semibold mb-4">
      Termos e Política
    </h1>

    <div class="flex flex-wrap gap-3 mb-4">
      <UButton
        v-for="tipo in tipos"
        :key="tipo.value"
        :icon="rascunhoDe(tipo.value) ? 'i-lucide-pencil' : 'i-lucide-plus'"
        :label="rascunhoDe(tipo.value) ? `Continuar rascunho: ${tipo.label}` : `Nova versão: ${tipo.label}`"
        :loading="criando === tipo.value"
        :disabled="loading"
        @click="novaVersao(tipo.value)"
      />
    </div>

    <UTable
      :data="documentos"
      :columns="columns"
      :loading="loading"
      :ui="{ td: 'whitespace-normal wrap-anywhere' }"
    >
      <template #tipo-cell="{ row }">
        {{ rotuloTipo(row.original.tipo) }}
      </template>

      <template #versao-cell="{ row }">
        v{{ row.original.versao }}
      </template>

      <template #status-cell="{ row }">
        <UBadge
          :color="row.original.publicado_em ? 'success' : 'warning'"
          variant="soft"
        >
          {{ row.original.publicado_em ? 'Publicada' : 'Rascunho' }}
        </UBadge>
      </template>

      <template #publicado_em-cell="{ row }">
        {{ row.original.publicado_em ? formatarData(row.original.publicado_em) : '—' }}
      </template>

      <template #acoes-cell="{ row }">
        <UButton
          :label="row.original.publicado_em ? 'Ver' : 'Editar'"
          size="sm"
          color="neutral"
          variant="outline"
          :to="`/admin/documentos-legais/${row.original.id}`"
        />
      </template>
    </UTable>

    <p
      v-if="!loading && documentos.length === 0"
      class="text-sm text-muted mt-4"
    >
      Nenhuma versão criada ainda.
    </p>
  </div>
</template>

<script setup lang="ts">
import type { TableColumn } from '@nuxt/ui'
import { FetchError } from 'ofetch'
import type { DocumentoLegalRead, DocumentoLegalResumo, TipoDocumentoLegal } from '~/types/generated'

definePageMeta({ middleware: 'role', roles: ['admin'] })

const api = useApi()
const toast = useToast()

const documentos = ref<DocumentoLegalResumo[]>([])
const loading = ref(true)
const criando = ref<TipoDocumentoLegal | null>(null)

const tipos: { label: string, value: TipoDocumentoLegal }[] = [
  { label: 'Termos de Uso', value: 'termos_de_uso' },
  { label: 'Política de Privacidade', value: 'politica_de_privacidade' },
]

const columns: TableColumn<DocumentoLegalResumo>[] = [
  { accessorKey: 'tipo', header: 'Documento' },
  { accessorKey: 'versao', header: 'Versão' },
  { id: 'status', header: 'Status' },
  { accessorKey: 'autor', header: 'Autor' },
  { accessorKey: 'publicado_em', header: 'Publicado em' },
  { id: 'acoes', header: '' },
]

function rotuloTipo(tipo: TipoDocumentoLegal): string {
  for (const item of tipos) {
    if (item.value === tipo) return item.label
  }
  return tipo
}

function formatarData(data: string): string {
  return new Date(data).toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' })
}

function rascunhoDe(tipo: TipoDocumentoLegal): DocumentoLegalResumo | undefined {
  for (const documento of documentos.value) {
    if (documento.tipo === tipo && !documento.publicado_em) return documento
  }
  return undefined
}

// lista vem da mais nova
function atualPublicada(tipo: TipoDocumentoLegal): DocumentoLegalResumo | undefined {
  for (const documento of documentos.value) {
    if (documento.tipo === tipo && documento.publicado_em) return documento
  }
  return undefined
}

async function fetchDocumentos() {
  loading.value = true
  try {
    documentos.value = await api('/admin/documentos-legais')
  }
  catch {
    documentos.value = []
    toast.add({ title: 'Não foi possível carregar os documentos', color: 'error' })
  }
  finally {
    loading.value = false
  }
}

// rascunho nasce com o texto da atual
async function novaVersao(tipo: TipoDocumentoLegal) {
  const rascunho = rascunhoDe(tipo)
  if (rascunho) {
    return navigateTo(`/admin/documentos-legais/${rascunho.id}`)
  }

  criando.value = tipo
  try {
    let conteudo = { type: 'doc', content: [] } as Record<string, unknown>

    const atual = atualPublicada(tipo)
    if (atual) {
      const completo: DocumentoLegalRead = await api(`/admin/documentos-legais/${atual.id}`)
      conteudo = completo.conteudo
    }

    const criado: DocumentoLegalRead = await api('/admin/documentos-legais', {
      method: 'POST',
      body: { tipo, conteudo },
    })
    await navigateTo(`/admin/documentos-legais/${criado.id}`)
  }
  catch (error) {
    const detalhe = error instanceof FetchError && typeof error.data?.detail === 'string' ? error.data.detail : null
    toast.add({ title: detalhe ?? 'Não foi possível criar o rascunho', color: 'error' })
  }
  finally {
    criando.value = null
  }
}

onMounted(fetchDocumentos)
</script>
