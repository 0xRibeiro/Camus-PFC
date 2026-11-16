<script setup lang="ts">
import type { JSONContent } from '@tiptap/core'
import { FetchError } from 'ofetch'
import type { DocumentoLegalRead } from '~/types/generated'

definePageMeta({ middleware: 'role', roles: ['admin'], key: route => route.path })

const route = useRoute()
const api = useApi()
const toast = useToast()
const documentoId = Number(route.params.id)

const documento = ref<DocumentoLegalRead | null>(null)
const conteudo = ref<JSONContent>()
const loading = ref(true)
const salvando = ref(false)
const publicando = ref(false)
const descartando = ref(false)
const showPublicarModal = ref(false)
const showDescartarModal = ref(false)

const rascunho = computed(() => documento.value !== null && !documento.value.publicado_em)

const titulo = computed(() => {
  if (!documento.value) return ''
  const nome = documento.value.tipo === 'termos_de_uso' ? 'Termos de Uso' : 'Política de Privacidade'
  return `${nome} — v${documento.value.versao}`
})

function erroDetalhe(error: unknown): string | null {
  if (error instanceof FetchError && typeof error.data?.detail === 'string') return error.data.detail
  return null
}

async function fetchDocumento() {
  loading.value = true
  try {
    documento.value = await api(`/admin/documentos-legais/${documentoId}`)
    conteudo.value = documento.value?.conteudo as JSONContent
  }
  catch {
    toast.add({ title: 'Não foi possível carregar o documento', color: 'error' })
  }
  loading.value = false
}

async function salvar() {
  await api(`/admin/documentos-legais/${documentoId}`, {
    method: 'PATCH',
    body: { conteudo: conteudo.value },
  })
}

async function onSalvar() {
  salvando.value = true
  try {
    await salvar()
    toast.add({ title: 'Rascunho salvo', color: 'success' })
  }
  catch (error) {
    toast.add({ title: erroDetalhe(error) ?? 'Não foi possível salvar o rascunho', color: 'error' })
  }
  salvando.value = false
}

// salva antes de publicar
async function onPublicar() {
  publicando.value = true
  try {
    await salvar()
    documento.value = await api(`/admin/documentos-legais/${documentoId}/publicar`, { method: 'POST' })
    showPublicarModal.value = false
    toast.add({ title: 'Versão publicada', color: 'success' })
  }
  catch (error) {
    toast.add({ title: erroDetalhe(error) ?? 'Não foi possível publicar', color: 'error' })
  }
  publicando.value = false
}

async function onDescartar() {
  descartando.value = true
  try {
    await api(`/admin/documentos-legais/${documentoId}`, { method: 'DELETE' })
    toast.add({ title: 'Rascunho descartado', color: 'success' })
    await navigateTo('/admin/documentos-legais')
  }
  catch (error) {
    toast.add({ title: erroDetalhe(error) ?? 'Não foi possível descartar', color: 'error' })
  }
  descartando.value = false
}

onMounted(fetchDocumento)
</script>

<template>
  <div>
    <div class="flex flex-wrap items-center justify-between gap-3 mb-3">
      <UButton
        icon="i-lucide-arrow-left"
        label="Termos e Política"
        color="neutral"
        variant="link"
        class="px-0"
        to="/admin/documentos-legais"
      />

      <div
        v-if="rascunho"
        class="flex flex-wrap items-center gap-2"
      >
        <UButton
          icon="i-lucide-trash-2"
          label="Descartar"
          color="error"
          variant="outline"
          @click="showDescartarModal = true"
        />
        <UButton
          icon="i-lucide-save"
          label="Salvar"
          color="neutral"
          variant="outline"
          :loading="salvando"
          @click="onSalvar"
        />
        <UButton
          icon="i-lucide-send"
          label="Publicar"
          @click="showPublicarModal = true"
        />
      </div>
    </div>

    <div
      v-if="loading"
      class="flex justify-center py-12"
    >
      <UIcon
        name="i-lucide-loader-circle"
        class="size-6 animate-spin"
      />
    </div>

    <template v-else-if="documento">
      <div class="mb-4 flex flex-wrap items-center gap-2">
        <h1 class="text-xl font-semibold">
          {{ titulo }}
        </h1>
        <UBadge
          :color="rascunho ? 'warning' : 'success'"
          variant="soft"
        >
          {{ rascunho ? 'Rascunho' : 'Publicada' }}
        </UBadge>
      </div>

      <EditorArtigo
        v-if="rascunho"
        v-model="conteudo"
      />

      <template v-else>
        <p class="text-sm text-muted mb-4">
          Publicada em {{ new Date(documento.publicado_em!).toLocaleString('pt-BR') }}.
          Versões publicadas não podem ser alteradas, crie uma nova versão.
        </p>
        <EditorLeitura :conteudo="documento.conteudo" />
      </template>
    </template>

    <UModal
      v-model:open="showPublicarModal"
      title="Publicar versão"
      description="Depois de publicada ela não pode mais ser alterada, e todos os usuários vão precisar aceitar de novo."
      :ui="{ footer: 'justify-end' }"
    >
      <template #footer="{ close }">
        <UButton
          label="Cancelar"
          color="neutral"
          variant="outline"
          @click="close"
        />
        <UButton
          label="Publicar"
          :loading="publicando"
          @click="onPublicar"
        />
      </template>
    </UModal>

    <UModal
      v-model:open="showDescartarModal"
      title="Descartar rascunho"
      description="O rascunho vai ser apagado. Essa ação não pode ser desfeita."
      :ui="{ footer: 'justify-end' }"
    >
      <template #footer="{ close }">
        <UButton
          label="Cancelar"
          color="neutral"
          variant="outline"
          @click="close"
        />
        <UButton
          label="Descartar"
          color="error"
          :loading="descartando"
          @click="onDescartar"
        />
      </template>
    </UModal>
  </div>
</template>
