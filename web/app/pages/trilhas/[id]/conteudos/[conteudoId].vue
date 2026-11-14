<script setup lang="ts">
import type { JSONContent } from '@tiptap/core'
import { FetchError } from 'ofetch'
import type { ConclusaoRead, ConteudoAlunoRead } from '~/types/generated'

definePageMeta({ middleware: 'role', key: route => route.path })

const route = useRoute()
const api = useApi()
const grupoId = route.params.grupoId
const toast = useToast()
const trilhaId = Number(route.params.id)
const trilhaPath = grupoId ? `/grupos/${grupoId}/trilhas/${trilhaId}` : `/trilhas/${trilhaId}`
const conteudoId = Number(route.params.conteudoId)

const conteudo = ref<ConteudoAlunoRead | null>(null)
const loading = ref(true)
const concluindo = ref(false)

async function fetchConteudo() {
  loading.value = true
  try {
    conteudo.value = await api(`/progresso/conteudos/${conteudoId}`)
  }
  catch (error) {
    // Se o conteúdo ainda não foi liberado, volta para a trilha.
    if (error instanceof FetchError && error.status === 403 && error.data?.detail === 'Conclua os conteúdos anteriores primeiro') {
      toast.add({ title: 'Conclua os conteúdos anteriores primeiro', color: 'warning' })
      await navigateTo(trilhaPath)
      return
    }
    toast.add({ title: 'Não foi possível carregar o conteúdo', color: 'error' })
  }
  loading.value = false
}

onMounted(fetchConteudo)

const youtubeId = computed(() => {
  if (!conteudo.value?.video_url) return null
  return extrairYoutubeId(conteudo.value.video_url)
})

const artigo = computed(() => conteudo.value?.artigo_conteudo as JSONContent | null | undefined)

/* concluir artigo e video */

async function onConcluir() {
  if (!conteudo.value) return

  concluindo.value = true
  try {
    const resposta: ConclusaoRead = await api(`/progresso/conteudos/${conteudoId}/concluir`, { method: 'POST' })
    conteudo.value.concluido = true
    conteudo.value.atualizado = false
    toast.add({
      title: 'Conteúdo concluído',
      description: resposta.xp_ganho > 0 ? `+${resposta.xp_ganho} XP${grupoId ? ' no grupo' : ''}` : undefined,
      color: 'success',
    })
  }
  catch {
    toast.add({ title: 'Não foi possível concluir o conteúdo', color: 'error' })
  }
  concluindo.value = false
}

// quiz conclui sozinho qnd responde
function onRespondeu() {
  if (!conteudo.value) return
  conteudo.value.concluido = true
  conteudo.value.atualizado = false
}

const precisaConcluir = computed(() => {
  if (!conteudo.value) return false
  return !conteudo.value.concluido || conteudo.value.atualizado
})
</script>

<template>
  <div>
    <UButton
      icon="i-lucide-arrow-left"
      label="Trilha"
      color="neutral"
      variant="link"
      class="px-0 mb-3"
      :to="trilhaPath"
    />

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
      <div class="mb-4 flex items-start justify-between gap-3">
        <div>
          <p class="text-xs font-medium text-muted uppercase tracking-wide">
            {{ conteudo.tipo }} · {{ conteudo.pontos }} XP
          </p>
          <h1 class="text-xl font-semibold">
            {{ conteudo.titulo }}
          </h1>
        </div>
        <UBadge
          v-if="conteudo.atualizado"
          label="Atualizado"
          color="warning"
          variant="soft"
        />
        <UBadge
          v-else-if="conteudo.concluido"
          label="Concluído"
          color="success"
          variant="soft"
          icon="i-lucide-circle-check"
        />
      </div>

      <!-- cada tipo tem seu jeito de mostrar -->
      <EditorLeitura
        v-if="conteudo.tipo === 'artigo'"
        :conteudo="artigo"
      />

      <template v-else-if="conteudo.tipo === 'video'">
        <div
          v-if="youtubeId"
          class="aspect-video w-full max-w-4xl mx-auto"
        >
          <iframe
            :src="`https://www.youtube.com/embed/${youtubeId}`"
            class="w-full h-full rounded-md"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowfullscreen
          />
        </div>
        <p
          v-else
          class="text-sm text-muted"
        >
          Vídeo indisponível.
        </p>
      </template>

      <QuizResponder
        v-else-if="conteudo.tipo === 'quiz'"
        :conteudo-id="conteudo.id"
        :questoes="conteudo.questoes"
        @respondeu="onRespondeu"
      />

      <div class="mt-6 flex justify-end gap-2">
        <UButton
          v-if="conteudo.tipo !== 'quiz' && precisaConcluir"
          icon="i-lucide-check"
          label="Marcar como concluído"
          :loading="concluindo"
          @click="onConcluir"
        />
        <!-- proximo so aparece dps de concluir, senao ia dar 403 -->
        <UButton
          v-if="conteudo.proximo_conteudo_id && conteudo.concluido"
          icon="i-lucide-arrow-right"
          trailing
          label="Próximo"
          color="neutral"
          variant="outline"
          :to="`${trilhaPath}/conteudos/${conteudo.proximo_conteudo_id}`"
        />
      </div>
    </template>
  </div>
</template>
