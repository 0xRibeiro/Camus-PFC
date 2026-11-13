<script setup lang="ts">
import type { JSONContent } from '@tiptap/core'
import type { ConteudoRead } from '~/types/generated'

definePageMeta({ middleware: 'role', roles: ['author', 'admin'], key: route => route.path })

const route = useRoute()
const api = useApi()
const grupoId = route.params.grupoId
const toast = useToast()
const trilhaId = Number(route.params.id)
const trilhaPath = grupoId ? `/grupos/${grupoId}/trilhas/${trilhaId}/editar` : `/author/trilhas/${trilhaId}`
const conteudoId = Number(route.params.conteudoId)

const conteudo = ref<ConteudoRead | null>(null)
const artigo = ref<JSONContent>()
const loading = ref(true)
const salvandoArtigo = ref(false)
const alteracaoSignificativa = ref(false)

async function fetchConteudo() {
  loading.value = true
  try {
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

/* quiz salva pergunta por pergunta */

// o montador avisa qnd salvou ou excluiu algo, se ta marcado sobe a versao 1 vez
async function onQuizAlterou() {
  if (!conteudo.value || !alteracaoSignificativa.value) return

  try {
    const versao = conteudo.value.versao + 1
    await api(`/conteudos/${conteudoId}`, { method: 'PATCH', body: { versao } })
    conteudo.value.versao = versao
    alteracaoSignificativa.value = false
    toast.add({ title: 'Versão do quiz atualizada', color: 'success' })
  }
  catch {
    toast.add({ title: 'Não foi possível atualizar a versão do quiz', color: 'error' })
  }
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
        :to="trilhaPath"
      />

      <div
        v-if="conteudo"
        class="flex items-center gap-4"
      >
        <!-- no quiz vale pro proximo salvar ou excluir de pergunta -->
        <UCheckbox
          v-model="alteracaoSignificativa"
          label="Alteração significativa"
        />
        <UButton
          v-if="conteudo.tipo === 'artigo'"
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
        @alterou="onQuizAlterou"
      />
    </template>
  </div>
</template>
