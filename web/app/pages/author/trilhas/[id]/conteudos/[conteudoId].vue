<script setup lang="ts">
import type { JSONContent } from '@tiptap/core'
import type { ConteudoRead } from '~/types/generated'

definePageMeta({ middleware: 'role', roles: ['author', 'admin'] })

const route = useRoute()
const toast = useToast()
const trilhaId = Number(route.params.id)
const conteudoId = Number(route.params.conteudoId)

const conteudo = ref<ConteudoRead | null>(null)
const artigo = ref<JSONContent>()
const loading = ref(true)
const salvandoArtigo = ref(false)
const alteracaoSignificativa = ref(false)

async function fetchConteudo() {
  loading.value = true
  try {
    const api = useApi()
    conteudo.value = await api(`/conteudos/${conteudoId}`)
    artigo.value = (conteudo.value?.artigo_conteudo ?? undefined) as JSONContent | undefined
  }
  catch {
    toast.add({ title: 'Não foi possível carregar o conteúdo', color: 'error' })
  }
  loading.value = false
}

onMounted(fetchConteudo)

/* salvar artigo */

async function onSalvarArtigo() {
  if (!conteudo.value) return

  salvandoArtigo.value = true
  try {
    // marcou alteracao significativa entao sobe a versao
    let versao = conteudo.value.versao
    if (alteracaoSignificativa.value) versao += 1

    const api = useApi()
    await api(`/conteudos/${conteudoId}`, {
      method: 'PATCH',
      body: { artigo_conteudo: artigo.value ?? null, versao },
    })
    conteudo.value.versao = versao
    alteracaoSignificativa.value = false
    toast.add({ title: 'Artigo salvo', color: 'success' })
  }
  catch {
    toast.add({ title: 'Não foi possível salvar o artigo', color: 'error' })
  }
  salvandoArtigo.value = false
}
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-3">
      <UButton
        icon="i-lucide-arrow-left"
        label="Trilha"
        color="neutral"
        variant="link"
        class="px-0"
        :to="`/author/trilhas/${trilhaId}`"
      />

      <div
        v-if="conteudo?.tipo === 'artigo'"
        class="flex items-center gap-4"
      >
        <UCheckbox
          v-model="alteracaoSignificativa"
          label="Alteração significativa"
        />
        <UButton
          icon="i-lucide-save"
          label="Salvar"
          color="primary"
          :loading="salvandoArtigo"
          @click="onSalvarArtigo"
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

    <template v-else-if="conteudo">
      <div class="mb-4">
        <p class="text-xs font-medium text-muted uppercase tracking-wide">
          {{ conteudo.tipo === 'artigo' ? 'Artigo' : 'Quiz' }}
        </p>
        <h1 class="text-xl font-semibold">
          {{ conteudo.titulo }}
        </h1>
      </div>

      <!-- cada tipo tem sua tela de edicao -->
      <EditorArtigo
        v-if="conteudo.tipo === 'artigo'"
        v-model="artigo"
      />

      <QuizMontador
        v-else-if="conteudo.tipo === 'quiz'"
        :conteudo-id="conteudo.id"
      />
    </template>
  </div>
</template>
