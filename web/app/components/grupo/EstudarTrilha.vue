<template>
  <div class="space-y-4">
    <p
      v-if="loading"
      class="text-muted"
    >
      Carregando…
    </p>
    <UAlert
      v-else-if="erro"
      title="Trilha indisponível"
      color="error"
      variant="soft"
    />
    <template v-else-if="conteudo">
      <UButton
        label="Voltar à trilha"
        color="neutral"
        variant="ghost"
        @click="carregar"
      />
      <h1 class="text-xl font-semibold">
        {{ conteudo.titulo }}
      </h1>
      <EditorLeitura
        v-if="conteudo.tipo === 'artigo'"
        :conteudo="artigo"
      />
      <QuizResponder
        v-else-if="conteudo.tipo === 'quiz'"
        :key="conteudo.id"
        :conteudo-id="conteudo.id"
        :questoes="conteudo.questoes"
        @respondeu="marcarConcluido"
      />
      <div class="flex justify-end gap-2">
        <UButton
          v-if="conteudo.tipo === 'artigo' && (!conteudo.concluido || conteudo.atualizado)"
          label="Marcar como concluído"
          :loading="concluindo"
          @click="concluir"
        />
        <UButton
          v-if="conteudo.concluido && conteudo.proximo_conteudo_id"
          label="Próximo conteúdo"
          variant="outline"
          @click="abrir(conteudo.proximo_conteudo_id)"
        />
      </div>
    </template>

    <template v-else-if="trilha">
      <TrilhaImagem
        v-if="trilha.foto"
        :src="trilha.foto"
      />
      <h1 class="text-xl font-semibold">
        {{ trilha.titulo }}
      </h1>
      <p
        v-if="trilha.descricao"
        class="text-muted"
      >
        {{ trilha.descricao }}
      </p>
      <UProgress :model-value="trilha.progresso" />
      <p class="text-sm text-muted">
        {{ trilha.concluidos }} de {{ trilha.total }} concluídos
      </p>
      <p
        v-if="!trilha.total"
        class="text-muted"
      >
        Nenhum conteúdo disponível.
      </p>
      <UCard
        v-for="modulo in trilha.modulos"
        :key="modulo.id"
      >
        <h2 class="mb-2 font-semibold">
          {{ modulo.titulo }}
        </h2>
        <UButton
          v-for="item in modulo.conteudos"
          :key="item.id"
          :label="`${item.titulo} · ${item.pontos} XP`"
          :icon="item.atualizado ? 'i-lucide-refresh-cw' : item.concluido ? 'i-lucide-circle-check' : item.liberado ? 'i-lucide-book-open' : 'i-lucide-lock'"
          :disabled="!item.liberado"
          color="neutral"
          variant="ghost"
          class="w-full"
          @click="abrir(item.id)"
        />
      </UCard>
    </template>
  </div>
</template>

<script setup lang="ts">
import type { JSONContent } from '@tiptap/core'
import type { ConclusaoRead, ConteudoAlunoRead, TrilhaAlunoRead } from '~/types/generated'

const props = defineProps<{ trilhaId: number }>()
const api = useApi()
const toast = useToast()
const trilha = ref<TrilhaAlunoRead | null>(null)
const conteudo = ref<ConteudoAlunoRead | null>(null)
const loading = ref(true)
const concluindo = ref(false)
const erro = ref(false)
const artigo = computed(() => conteudo.value?.artigo_conteudo as JSONContent | null | undefined)

async function carregar() {
  loading.value = true
  erro.value = false
  conteudo.value = null
  try {
    trilha.value = await api(`/progresso/trilhas/${props.trilhaId}`)
  }
  catch {
    erro.value = true
  }
  finally {
    loading.value = false
  }
}

async function abrir(id: number) {
  loading.value = true
  try {
    conteudo.value = await api(`/progresso/conteudos/${id}`)
  }
  catch {
    toast.add({ title: 'Não foi possível abrir o conteúdo', color: 'error' })
  }
  finally {
    loading.value = false
  }
}

function marcarConcluido() {
  if (conteudo.value) {
    conteudo.value.concluido = true
    conteudo.value.atualizado = false
  }
}

async function concluir() {
  if (!conteudo.value) return
  concluindo.value = true
  try {
    const resultado: ConclusaoRead = await api(
      `/progresso/conteudos/${conteudo.value.id}/concluir`,
      { method: 'POST' },
    )
    marcarConcluido()
    toast.add({
      title: 'Artigo concluído',
      description: resultado.xp_ganho ? `+${resultado.xp_ganho} XP no grupo` : undefined,
      color: 'success',
    })
  }
  catch {
    toast.add({ title: 'Não foi possível concluir o artigo', color: 'error' })
  }
  finally {
    concluindo.value = false
  }
}

onMounted(carregar)
</script>
