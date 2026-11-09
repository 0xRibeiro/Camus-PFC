<template>
  <div class="space-y-4">
    <template v-if="selecionado">
      <div class="flex flex-wrap items-center justify-between gap-3">
        <UButton
          label="Voltar aos módulos"
          variant="ghost"
          :disabled="busy"
          @click="selecionado = null"
        />
        <UCheckbox
          v-model="novaVersao"
          label="Alteração significativa" />
        <UButton
          v-if="selecionado.tipo === 'artigo'"
          label="Salvar artigo"
          :loading="busy"
          @click="salvarCorpo"
        />
      </div>
      <h1 class="text-xl font-semibold">
        {{ selecionado.titulo }}
      </h1>
      <EditorArtigo
        v-if="selecionado.tipo === 'artigo'"
        v-model="artigo"
      />
      <QuizMontador
        v-else
        :conteudo-id="selecionado.id"
        @alterou="salvarCorpo"
      />
    </template>

    <template v-else>
      <div class="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 class="text-xl font-semibold">
            {{ trilha.titulo }}
          </h1>
          <p class="text-sm text-muted">
            {{ trilha.is_active ? 'Ativa' : 'Rascunho. Ative a trilha quando estiver pronta.' }}
          </p>
        </div>
        <div class="flex flex-wrap gap-2">
          <UButton
            label="Editar trilha"
            variant="outline"
            @click="modalTrilha = true"
          />
          <UButton
            label="Novo módulo"
            :disabled="busy"
            @click="editarModulo()"
          />
          <UButton
            label="Excluir trilha"
            color="error"
            variant="ghost"
            @click="confirmarExclusao(`/trilhas/${trilha.id}`, true)"
          />
        </div>
      </div>

      <UCard
        v-for="modulo in modulos"
        :key="modulo.id"
      >
        <div class="mb-2 flex flex-wrap items-center justify-between gap-2">
          <h2 class="font-semibold">
            {{ modulo.titulo }}
          </h2>
          <div class="flex flex-wrap gap-1">
            <UButton
              label="Novo conteúdo"
              size="sm"
              :disabled="busy"
              @click="editarConteudo(modulo.id)"
            />
            <UButton
              label="Editar módulo"
              size="sm"
              variant="ghost"
              @click="editarModulo(modulo)"
            />
            <UButton
              label="Excluir módulo"
              size="sm"
              color="error"
              variant="ghost"
              @click="confirmarExclusao(`/modulos/${modulo.id}`)"
            />
          </div>
        </div>
        <div
          v-for="item in conteudosDoModulo(modulo.id)"
          :key="item.id"
          class="flex flex-wrap items-center justify-between gap-2 border-t border-default py-2"
        >
          <UButton
            :label="`${item.titulo} · ${item.pontos} XP`"
            variant="ghost"
            @click="abrir(item)"
          />
          <div class="flex gap-1">
            <UButton
              label="Configurar"
              size="sm"
              color="neutral"
              variant="ghost"
              @click="editarConteudo(modulo.id, item)"
            />
            <UButton
              label="Excluir"
              size="sm"
              color="error"
              variant="ghost"
              @click="confirmarExclusao(`/conteudos/${item.id}`)"
            />
          </div>
        </div>
      </UCard>
    </template>

    <TrilhaFormModal
      v-model:open="modalTrilha"
      :trilha="trilha"
      :saving="busy"
      @submit="salvarTrilha"
    />

    <UModal
      v-model:open="modalItem"
      :title="`${form.id === null ? 'Criar' : 'Editar'} ${form.moduloId === null ? 'módulo' : 'conteúdo'}`"
    >
      <template #body>
        <form
          class="space-y-3"
          @submit.prevent="salvarItem"
        >
          <UFormField label="Título">
            <UInput
              v-model="form.titulo"
              :maxlength="form.moduloId === null ? 50 : 100"
              class="w-full"
              required
            />
          </UFormField>
          <UFormField label="Ordem">
            <UInput
              v-model="form.ordem"
              type="number"
              :min="0"
              required
            />
          </UFormField>
          <UFormField
            v-if="form.moduloId !== null && form.id === null"
            label="Tipo"
          >
            <USelect
              v-model="form.tipo"
              :items="tipos"
            />
          </UFormField>
          <UFormField
            v-if="form.moduloId !== null"
            label="XP"
          >
            <UInput
              v-model="form.pontos"
              type="number"
              :min="0"
              required
            />
          </UFormField>
          <UButton
            type="submit"
            label="Salvar"
            :loading="busy"
          />
        </form>
      </template>
    </UModal>

    <UModal
      v-model:open="modalExcluir"
      title="Confirmar exclusão"
      description="O item e os conteúdos abaixo dele serão excluídos."
    >
      <template #footer="{ close }">
        <UButton
          label="Cancelar"
          color="neutral"
          variant="outline"
          @click="close"
        />
        <UButton
          label="Excluir"
          color="error"
          :loading="busy"
          @click="excluir"
        />
      </template>
    </UModal>
  </div>
</template>

<script setup lang="ts">
import type { JSONContent } from '@tiptap/core'
import type { ConteudoRead, ModuloRead, TrilhaRead } from '~/types/generated'

const trilha = defineModel<TrilhaRead>('trilha', { required: true })
const api = useApi()
const toast = useToast()
const grupoId = Number(useRoute().params.grupoId)
const modulos = ref<ModuloRead[]>([])
const conteudos = ref<ConteudoRead[]>([])
const selecionado = ref<ConteudoRead | null>(null)
const artigo = ref<JSONContent>()
const novaVersao = ref(false)
const busy = ref(false)
const modalTrilha = ref(false)
const modalItem = ref(false)
const modalExcluir = ref(false)
const exclusao = ref({ url: '', trilha: false })

const tipos: { label: string, value: 'artigo' | 'quiz' }[] = [
  { label: 'Artigo', value: 'artigo' },
  { label: 'Quiz', value: 'quiz' },
]
const form = reactive({
  id: null as number | null,
  moduloId: null as number | null,
  titulo: '',
  ordem: 0,
  pontos: 0,
  tipo: 'artigo' as 'artigo' | 'quiz',
})

function conteudosDoModulo(id: number) {
  return conteudos.value.filter(item => item.modulo_id === id)
}

async function carregar() {
  const resposta = await api('/modulos', {
    query: { trilha_id: trilha.value.id, sort: 'ordem,id' },
  })
  modulos.value = resposta.data
  const listas = await Promise.all(modulos.value.map(modulo =>
    api('/conteudos', { query: { modulo_id: modulo.id, sort: 'ordem,id' } }),
  ))
  conteudos.value = listas.flatMap(lista => lista.data)
}

async function executar(acao: () => Promise<void>) {
  busy.value = true
  try {
    await acao()
  }
  catch {
    toast.add({ title: 'Não foi possível completar a operação', color: 'error' })
  }
  finally {
    busy.value = false
  }
}

function editarModulo(modulo?: ModuloRead) {
  Object.assign(form, {
    id: modulo?.id ?? null,
    moduloId: null,
    titulo: modulo?.titulo ?? '',
    ordem: modulo?.ordem ?? Math.max(-1, ...modulos.value.map(item => item.ordem)) + 1,
  })
  modalItem.value = true
}

function editarConteudo(moduloId: number, conteudo?: ConteudoRead) {
  Object.assign(form, {
    id: conteudo?.id ?? null,
    moduloId,
    titulo: conteudo?.titulo ?? '',
    ordem: conteudo?.ordem ?? Math.max(-1, ...conteudosDoModulo(moduloId).map(item => item.ordem)) + 1,
    pontos: conteudo?.pontos ?? 0,
    tipo: conteudo?.tipo ?? 'artigo',
  })
  modalItem.value = true
}

function abrir(conteudo: ConteudoRead) {
  selecionado.value = conteudo
  artigo.value = (conteudo.artigo_conteudo ?? undefined) as JSONContent | undefined
  novaVersao.value = false
}

async function salvarItem() {
  if (!form.titulo.trim()) return
  await executar(async () => {
    const dados = { titulo: form.titulo.trim(), ordem: Number(form.ordem) }
    if (form.moduloId === null) {
      if (form.id === null) {
        await api('/modulos', { method: 'POST', body: { ...dados, trilha_id: trilha.value.id } })
      }
      else {
        await api(`/modulos/${form.id}`, { method: 'PATCH', body: dados })
      }
    }
    else if (form.id === null) {
      const novo = await api('/conteudos', {
        method: 'POST',
        body: { ...dados, modulo_id: form.moduloId, tipo: form.tipo, pontos: Number(form.pontos) },
      })
      abrir(novo)
    }
    else {
      await api(`/conteudos/${form.id}`, {
        method: 'PATCH',
        body: { ...dados, pontos: Number(form.pontos) },
      })
    }
    modalItem.value = false
    await carregar()
  })
}

async function salvarTrilha(dados: { titulo: string, descricao?: string | null, tag?: string | null, foto?: string | null, is_active: boolean }) {
  await executar(async () => {
    await api(`/trilhas/${trilha.value.id}`, { method: 'PATCH', body: dados })
    trilha.value = await api(`/trilhas/${trilha.value.id}`)
    modalTrilha.value = false
  })
}

async function salvarCorpo() {
  const item = selecionado.value
  if (!item || (item.tipo === 'quiz' && !novaVersao.value)) return
  await executar(async () => {
    const versao = item.versao + Number(novaVersao.value)
    const body = item.tipo === 'artigo' ? { versao, artigo_conteudo: artigo.value ?? null } : { versao }
    await api(`/conteudos/${item.id}`, { method: 'PATCH', body })
    novaVersao.value = false
    await carregar()
    selecionado.value = conteudos.value.find(conteudo => conteudo.id === item.id) ?? null
    toast.add({ title: 'Conteúdo salvo', color: 'success' })
  })
}

function confirmarExclusao(url: string, excluirTrilha = false) {
  exclusao.value = { url, trilha: excluirTrilha }
  modalExcluir.value = true
}

async function excluir() {
  await executar(async () => {
    await api(exclusao.value.url, { method: 'DELETE' })
    modalExcluir.value = false
    if (exclusao.value.trilha) await navigateTo(`/grupos/${grupoId}`)
    else await carregar()
  })
}

onMounted(() => executar(carregar))
</script>
