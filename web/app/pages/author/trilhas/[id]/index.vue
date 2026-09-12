<template>
  <div>
    <!-- volta pra listagem. usa router.back() em vez de rota fixa pq n sabemos
    o path certo daqui - se recarregou a pagina sem historico, cai no fallback -->
    <UButton
      icon="i-lucide-arrow-left"
      label="Trilhas"
      color="neutral"
      variant="link"
      class="px-0 mb-3"
      @click="voltarParaTrilhas"
    />

    <div v-if="trilha" class="flex items-start justify-between mb-6">
      <div>
        <p class="text-xs font-medium text-muted uppercase tracking-wide">
          Jornada
        </p>
        <h1 class="text-xl font-semibold">
          {{ trilha.titulo }}
        </h1>
        <p class="text-sm text-muted">
          {{ trilha.descricao }}
        </p>
      </div>

      <div class="flex items-center gap-2">
        <UBadge color="neutral" variant="soft" size="lg">
          {{ modulos.length }} módulo{{ modulos.length === 1 ? '' : 's' }}
        </UBadge>
        <UBadge color="neutral" variant="soft" size="lg">
          {{ totalConteudos }} conteúdo{{ totalConteudos === 1 ? '' : 's' }}
        </UBadge>
        <UButton icon="i-lucide-plus" label="Módulo" color="primary" @click="abrirCriarModulo" />
      </div>
    </div>

    <div v-if="loading" class="flex justify-center py-12">
      <UIcon name="i-lucide-loader-circle" class="size-6 animate-spin" />
    </div>

    <!-- arrasta os MODULOS (nao os conteudos, isso ficou so no nivel modulo
    por enquanto). o handle=".modulo-drag-handle" trava o arrasto no icone de
    pontinhos, senao qualquer clique no card ia comecar a arrastar -->
    <VueDraggable
      v-else
      v-model="modulos"
      :animation="150"
      handle=".modulo-drag-handle"
      item-key="id"
      class="space-y-4"
      @end="onReordenarModulos"
    >
      <div
        v-for="(modulo, indiceModulo) in modulos"
        :key="modulo.id"
        class="bg-elevated/40 border border-default rounded-xl overflow-hidden"
      >
        <div class="flex items-center justify-between px-4 py-3">
          <div class="flex items-center gap-3">
            <UIcon
              name="i-lucide-grip-vertical"
              class="modulo-drag-handle size-4 text-muted cursor-grab active:cursor-grabbing"
            />
            <span class="rounded-full bg-slate-800 text-white text-xs font-semibold px-3 py-1.5 whitespace-nowrap">
              {{ modulo.titulo }}{{ indiceModulo === modulos.length - 1 ? ' - Final' : '' }}
            </span>
            <span class="text-xs text-muted">
              {{ contarConteudos(modulo.id) }} conteúdo{{ contarConteudos(modulo.id) === 1 ? '' : 's' }}
              · {{ somarPontos(modulo.id) }} pts
            </span>
          </div>

          <div class="flex items-center gap-1">
            <UButton
              icon="i-lucide-plus" size="xs" color="neutral" variant="ghost" label="Conteúdo"
              @click="abrirCriarConteudo(modulo)"
            />
            <UButton icon="i-lucide-trash-2" size="xs" color="error" variant="ghost" @click="onDeleteModulo(modulo)" />
          </div>
        </div>

        <div class="bg-default divide-y divide-default">
          <div
            v-for="conteudo in conteudosDoModulo(modulo.id)"
            :key="conteudo.id"
            class="flex items-center justify-between px-4 py-3"
          >
            <div class="flex items-center gap-3">
              <div class="flex items-center justify-center size-8 rounded-full bg-primary-50 shrink-0">
                <UIcon :name="tiposInfo[conteudo.tipo].icon" class="size-4 text-primary-600" />
              </div>
              <div>
                <p class="text-sm font-medium">
                  {{ conteudo.titulo }}
                </p>
                <p class="text-xs text-muted">
                  {{ conteudo.pontos }} pts
                  <span v-if="conteudo.tipo === 'video' && !conteudo.video_url" class="text-warning">
                    · sem link ainda
                  </span>
                </p>
              </div>
            </div>

            <div class="flex items-center gap-3">
              <!-- so mostra qual e o tipo, nao da pra trocar clicando -->
              <div class="hidden sm:flex items-center gap-1.5">
                <span
                  v-for="(info, tipo) in tiposInfo"
                  :key="tipo"
                  class="rounded-full text-xs px-2.5 py-1 font-medium"
                  :class="conteudo.tipo === tipo ? 'bg-slate-800 text-white' : 'bg-slate-100 text-slate-400'"
                >
                  {{ info.label }}
                </span>
              </div>

              <UButton icon="i-lucide-pencil" size="xs" color="neutral" variant="ghost" @click="abrirEditarConteudo(conteudo)" />
              <UButton
                v-if="conteudo.tipo === 'video'"
                :icon="conteudo.video_url ? 'i-lucide-play' : 'i-lucide-link'"
                size="xs" color="neutral" variant="ghost"
                @click="abrirLinkVideo(conteudo)"
              />
              <UButton icon="i-lucide-trash-2" size="xs" color="error" variant="ghost" @click="onDeleteConteudo(conteudo)" />
            </div>
          </div>
        </div>

        <p v-if="contarConteudos(modulo.id) === 0" class="px-4 py-6 text-sm text-muted text-center">
          Nenhum conteúdo neste módulo ainda.
        </p>
      </div>
    </VueDraggable>

    <p v-if="!loading && modulos.length === 0" class="text-sm text-muted text-center py-12">
      Nenhum módulo cadastrado. Clique em "Módulo" para começar a jornada.
    </p>

    <!-- criar modulo -->
    <UModal v-model:open="showModuloModal" title="Novo módulo">
      <template #body>
        <div class="space-y-4">
          <UFormField label="Título do módulo">
            <UInput v-model="formModulo.titulo" placeholder="Ex: Módulo 1" class="w-full" />
          </UFormField>
          <div class="flex justify-end gap-2">
            <UButton color="neutral" variant="ghost" label="Cancelar" @click="showModuloModal = false" />
            <UButton
              color="primary" label="Criar" :loading="savingModulo"
              :disabled="!formModulo.titulo.trim()" @click="onSubmitModulo"
            />
          </div>
        </div>
      </template>
    </UModal>

    <!-- criar ou editar conteudo, mesmo modal, so muda o titulo/botao e
    esconde o seletor de tipo quando ta editando (n da pra trocar o tipo depois) -->
    <UModal v-model:open="showConteudoModal" :title="modoConteudoModal === 'criar' ? 'Novo conteúdo' : 'Editar conteúdo'">
      <template #body>
        <div class="space-y-4">
          <UFormField v-if="modoConteudoModal === 'criar'" label="Tipo">
            <div class="flex gap-2">
              <UButton
                label="Vídeo"
                :color="formConteudo.tipo === 'video' ? 'primary' : 'neutral'"
                :variant="formConteudo.tipo === 'video' ? 'solid' : 'outline'"
                @click="formConteudo.tipo = 'video'"
              />
              <UButton label="Artigo" color="neutral" variant="outline" disabled title="Em breve" />
              <UButton label="Quiz" color="neutral" variant="outline" disabled title="Em breve" />
            </div>
          </UFormField>

          <UFormField label="Título">
            <UInput v-model="formConteudo.titulo" placeholder="Ex: Salinidade: o que é e como medir" class="w-full" />
          </UFormField>

          <UFormField label="Pontos">
            <UInputNumber v-model="formConteudo.pontos" :min="0" class="w-full" />
          </UFormField>

          <div class="flex justify-end gap-2">
            <UButton color="neutral" variant="ghost" label="Cancelar" @click="showConteudoModal = false" />
            <UButton
              color="primary"
              :label="modoConteudoModal === 'criar' ? 'Criar' : 'Salvar'"
              :loading="savingConteudo"
              :disabled="!formConteudo.titulo.trim()"
              @click="onSubmitConteudoModal"
            />
          </div>
        </div>
      </template>
    </UModal>

    <!-- colar e editar link do youtube -->
    <UModal v-model:open="showVideoModal" title="Link do vídeo">
      <template #body>
        <div class="space-y-4">
          <UFormField label="URL do YouTube">
            <UInput v-model="formVideoUrl" placeholder="https://www.youtube.com/watch?v=..." class="w-full" />
            <p v-if="formVideoUrl && !youtubeIdPreview" class="text-xs text-error mt-1">
              Não parece ser um link válido do YouTube.
            </p>
          </UFormField>

          <!-- se o link for valido, o video ja toca aqui antes de salvar -->
          <div v-if="youtubeIdPreview" class="aspect-video rounded-lg overflow-hidden border border-default">
            <iframe
              :src="`https://www.youtube.com/embed/${youtubeIdPreview}`"
              class="w-full h-full" frameborder="0"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowfullscreen
            />
          </div>

          <div class="flex justify-end gap-2">
            <UButton color="neutral" variant="ghost" label="Cancelar" @click="showVideoModal = false" />
            <UButton
              color="primary" label="Salvar" :loading="savingVideo"
              :disabled="!youtubeIdPreview" @click="onSubmitVideoUrl"
            />
          </div>
        </div>
      </template>
    </UModal>
  </div>
</template>

<script setup lang="ts">
import { VueDraggable } from 'vue-draggable-plus'
import type { Ref } from 'vue'
import type { ConteudoRead, ModuloRead, TrilhaRead } from '~/types/generated'

definePageMeta({ middleware: 'role', roles: ['author', 'admin'] })

const route = useRoute()
const router = useRouter()
const trilhaId = Number(route.params.id)
const toast = useToast()

function voltarParaTrilhas() {
  if (window.history.length > 1) router.back()
  else router.push('/author/trilha')
}

// pega o ID do video não importa o formato do link (normal, curto, embed, shorts)
function extrairYoutubeId(url: string): string | null {
  const match = url.match(/(?:youtube\.com\/(?:watch\?v=|embed\/|shorts\/)|youtu\.be\/)([\w-]{11})/)
  return match ? match[1] : null
}

// dois helpers pra n repetir try/catch/ em toda chamada de api:
// "comErro" so avisa se der ruim; "salvando" tambem liga/desliga um loading
async function comErro(mensagemErro: string, acao: () => Promise<void>) {
  try {
    await acao()
  }
  catch {
    toast.add({ title: mensagemErro, color: 'error' })
  }
}

async function salvando(saving: Ref<boolean>, mensagemErro: string, acao: () => Promise<void>) {
  saving.value = true
  await comErro(mensagemErro, acao)
  saving.value = false
}

// centraliza label + icone de cada tipo de conteudo num lugar so
const tiposInfo = {
  video: { label: 'Vídeo', icon: 'i-lucide-play-circle' },
  artigo: { label: 'Artigo', icon: 'i-lucide-book-open' },
  quiz: { label: 'Quiz', icon: 'i-lucide-list-checks' },
} as const
type TipoConteudo = keyof typeof tiposInfo

const trilha = ref<TrilhaRead | null>(null)
const modulos = ref<ModuloRead[]>([])
const conteudos = ref<ConteudoRead[]>([])
const loading = ref(true)

// conteudo agrupado por modulo, so pra contar/somar/listar mais facil
const conteudosPorModulo = reactive<Record<number, ConteudoRead[]>>({})

const totalConteudos = computed(() => conteudos.value.length)

function conteudosDoModulo(moduloId: number) {
  return conteudosPorModulo[moduloId] ?? []
}
function contarConteudos(moduloId: number) {
  return conteudosDoModulo(moduloId).length
}
function somarPontos(moduloId: number) {
  return conteudosDoModulo(moduloId).reduce((total, c) => total + c.pontos, 0)
}

function popularConteudosPorModulo() {
  // eslint-disable-next-line @typescript-eslint/no-dynamic-delete
  for (const chave of Object.keys(conteudosPorModulo)) delete conteudosPorModulo[Number(chave)]
  for (const modulo of modulos.value) {
    conteudosPorModulo[modulo.id] = conteudos.value
      .filter(c => c.modulo_id === modulo.id)
      .sort((a, b) => a.ordem - b.ordem)
  }
}

async function fetchTudo() {
  loading.value = true
  const api = useApi()

  const [trilhaRes, modulosRes, conteudosRes] = await Promise.all([
    api(`/trilhas/${trilhaId}`),
    api('/modulos', { query: { trilha_id: trilhaId } }),
    api('/conteudos'),
  ])

  trilha.value = trilhaRes
  modulos.value = modulosRes.data.sort((a: ModuloRead, b: ModuloRead) => a.ordem - b.ordem)

  const idsDosModulos = new Set(modulos.value.map(m => m.id))
  conteudos.value = conteudosRes.data.filter((c: ConteudoRead) => idsDosModulos.has(c.modulo_id))
  popularConteudosPorModulo()

  loading.value = false
}

onMounted(fetchTudo)

/* modulo */

async function onReordenarModulos() {
  const api = useApi()
  await comErro('Não foi possível salvar a nova ordem dos módulos', async () => {
    await Promise.all(modulos.value.map((modulo, indice) => {
      modulo.ordem = indice
      return api(`/modulos/${modulo.id}`, { method: 'PATCH', body: { ordem: indice } })
    }))
  })
}

const showModuloModal = ref(false)
const savingModulo = ref(false)
const formModulo = reactive({ titulo: '' })

function abrirCriarModulo() {
  formModulo.titulo = ''
  showModuloModal.value = true
}

async function onSubmitModulo() {
  await salvando(savingModulo, 'Não foi possível criar o módulo', async () => {
    const api = useApi()
    const novoModulo = await api('/modulos', {
      method: 'POST',
      body: { trilha_id: trilhaId, titulo: formModulo.titulo, ordem: modulos.value.length },
    })
    modulos.value.push(novoModulo)
    conteudosPorModulo[novoModulo.id] = []
    showModuloModal.value = false
  })
}

async function onDeleteModulo(modulo: ModuloRead) {
  if (!confirm(`Excluir o módulo "${modulo.titulo}"? Isso apaga os conteúdos dele também.`)) return
  await comErro('Não foi possível excluir o módulo', async () => {
    const api = useApi()
    await api(`/modulos/${modulo.id}`, { method: 'DELETE' })
    modulos.value = modulos.value.filter(m => m.id !== modulo.id)
    conteudos.value = conteudos.value.filter(c => c.modulo_id !== modulo.id)
    // eslint-disable-next-line @typescript-eslint/no-dynamic-delete
    delete conteudosPorModulo[modulo.id]
  })
}

/* conteudo criar + editar no mesmo modal */

const showConteudoModal = ref(false)
const savingConteudo = ref(false)
const modoConteudoModal = ref<'criar' | 'editar'>('criar')
const moduloAlvo = ref<ModuloRead | null>(null) // usado so no modo criar
const conteudoEditando = ref<ConteudoRead | null>(null) // usado so no modo editar
const formConteudo = reactive({ tipo: 'video' as TipoConteudo, titulo: '', pontos: 10 })

function abrirCriarConteudo(modulo: ModuloRead) {
  modoConteudoModal.value = 'criar'
  moduloAlvo.value = modulo
  Object.assign(formConteudo, { tipo: 'video', titulo: '', pontos: 10 })
  showConteudoModal.value = true
}

function abrirEditarConteudo(conteudo: ConteudoRead) {
  modoConteudoModal.value = 'editar'
  conteudoEditando.value = conteudo
  Object.assign(formConteudo, { tipo: conteudo.tipo, titulo: conteudo.titulo, pontos: conteudo.pontos })
  showConteudoModal.value = true
}

async function onSubmitConteudoModal() {
  await salvando(savingConteudo, 'Não foi possível salvar o conteúdo', async () => {
    const api = useApi()

    if (modoConteudoModal.value === 'criar' && moduloAlvo.value) {
      const novo = await api('/conteudos', {
        method: 'POST',
        body: {
          modulo_id: moduloAlvo.value.id,
          titulo: formConteudo.titulo,
          tipo: formConteudo.tipo,
          ordem: contarConteudos(moduloAlvo.value.id),
          pontos: formConteudo.pontos,
        },
      })
      conteudos.value.push(novo)
      conteudosPorModulo[moduloAlvo.value.id] ??= []
      conteudosPorModulo[moduloAlvo.value.id].push(novo)
    }
    else if (conteudoEditando.value) {
      const id = conteudoEditando.value.id
      await api(`/conteudos/${id}`, {
        method: 'PATCH',
        body: { titulo: formConteudo.titulo, pontos: formConteudo.pontos },
      })
      // PATCH do fastcrud n devolve o item, entao atualiza local com o que ja temos
      for (const lista of [conteudos.value, conteudosPorModulo[conteudoEditando.value.modulo_id] ?? []]) {
        const alvo = lista.find(c => c.id === id)
        if (alvo) Object.assign(alvo, { titulo: formConteudo.titulo, pontos: formConteudo.pontos })
      }
    }
    showConteudoModal.value = false
  })
}

async function onDeleteConteudo(conteudo: ConteudoRead) {
  if (!confirm(`Excluir o conteúdo "${conteudo.titulo}"?`)) return
  await comErro('Não foi possível excluir o conteúdo', async () => {
    const api = useApi()
    await api(`/conteudos/${conteudo.id}`, { method: 'DELETE' })
    conteudos.value = conteudos.value.filter(c => c.id !== conteudo.id)
    const lista = conteudosPorModulo[conteudo.modulo_id]
    if (lista) conteudosPorModulo[conteudo.modulo_id] = lista.filter(c => c.id !== conteudo.id)
  })
}

/* inserir link do video */

const showVideoModal = ref(false)
const savingVideo = ref(false)
const conteudoAlvo = ref<ConteudoRead | null>(null)
const formVideoUrl = ref('')
const youtubeIdPreview = computed(() => extrairYoutubeId(formVideoUrl.value))

function abrirLinkVideo(conteudo: ConteudoRead) {
  conteudoAlvo.value = conteudo
  formVideoUrl.value = conteudo.video_url ?? ''
  showVideoModal.value = true
}

async function onSubmitVideoUrl() {
  if (!conteudoAlvo.value) return
  const id = conteudoAlvo.value.id
  const moduloId = conteudoAlvo.value.modulo_id

  await salvando(savingVideo, 'Não foi possível salvar o link do vídeo', async () => {
    const api = useApi()
    await api(`/conteudos/${id}`, { method: 'PATCH', body: { video_url: formVideoUrl.value } })

    for (const lista of [conteudos.value, conteudosPorModulo[moduloId] ?? []]) {
      const alvo = lista.find(c => c.id === id)
      if (alvo) alvo.video_url = formVideoUrl.value
    }
    showVideoModal.value = false
  })
}
</script>
