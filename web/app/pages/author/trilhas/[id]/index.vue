<template>
  <div class="flex-1">
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

    <div
      v-if="trilha"
      class="mb-6 flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between"
    >
      <div class="min-w-0 wrap-anywhere">
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

      <div class="flex flex-wrap items-center gap-2 sm:justify-end">
        <!-- botao novo teste para o dono ver a trilha igual os alunos veriam -->
        <UButton
          v-if="trilhaGrupo && trilha.is_active"
          label="Estudar trilha"
          color="neutral"
          variant="outline"
          :to="trilhaGrupo"
        />
        <UButton
          label="Dashboard"
          icon="i-lucide-chart-spline"
          color="neutral"
          variant="outline"
          :to="trilhaGrupo ? `${trilhaGrupo}/editar/dashboard` : `/author/trilhas/${trilhaId}/dashboard`"
        />
        <UBadge
          color="neutral"
          variant="soft"
          size="lg"
        >
          {{ modulos.length }} módulo{{ modulos.length === 1 ? '' : 's' }}
        </UBadge>
        <UBadge
          color="neutral"
          variant="soft"
          size="lg"
        >
          {{ totalConteudos }} conteúdo{{ totalConteudos === 1 ? '' : 's' }}
        </UBadge>
        <UButton
          icon="i-lucide-plus"
          label="Módulo"
          color="primary"
          @click="abrirCriarModulo"
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

    <!-- arrasta os MODULOS, os conteudos tem o draggable deles mais embaixo.
    o handle=".modulo-drag-handle" trava o arrasto no icone de
    pontinhos, senao qualquer clique no card ia comecar a arrastar -->
    <VueDraggable
      v-else-if="trilha"
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
        <div class="flex flex-wrap items-center justify-between gap-3 px-4 py-3">
          <div class="flex min-w-0 flex-wrap items-center gap-2">
            <UIcon
              name="i-lucide-grip-vertical"
              class="modulo-drag-handle size-4 shrink-0 text-muted cursor-grab active:cursor-grabbing"
            />
            <span class="min-w-0 rounded-full bg-slate-800 px-3 py-1.5 text-xs font-semibold wrap-anywhere text-white">
              {{ modulo.titulo }}{{ indiceModulo === modulos.length - 1 ? ' - Final' : '' }}
            </span>
            <span class="text-xs text-muted">
              {{ contarConteudos(modulo.id) }} conteúdo{{ contarConteudos(modulo.id) === 1 ? '' : 's' }}
              · {{ somarPontos(modulo.id) }} pts
            </span>
          </div>

          <div class="flex shrink-0 items-center gap-1">
            <UButton
              icon="i-lucide-plus"
              size="xs"
              color="neutral"
              variant="ghost"
              label="Conteúdo"
              @click="abrirCriarConteudo(modulo)"
            />
            <UButton
              icon="i-lucide-pencil"
              size="xs"
              color="neutral"
              variant="ghost"
              aria-label="Editar módulo"
              @click="abrirEditarModulo(modulo)"
            />
            <UButton
              icon="i-lucide-trash-2"
              size="xs"
              color="error"
              variant="ghost"
              @click="onDeleteModulo(modulo)"
            />
          </div>
        </div>

        <!-- todas as listas no msm group, da pra arrastar o conteudo pra outro modulo.
        vazia ganha altura pra ter onde soltar, e o aviso fica por cima sem bloquear -->
        <div class="relative">
          <p
            v-if="contarConteudos(modulo.id) === 0"
            class="pointer-events-none absolute inset-0 flex items-center justify-center text-sm text-muted"
          >
            Nenhum conteúdo neste módulo ainda.
          </p>

          <VueDraggable
            :model-value="conteudosDoModulo(modulo.id)"
            :animation="150"
            group="conteudos"
            handle=".conteudo-drag-handle"
            class="bg-default divide-y divide-default"
            :class="contarConteudos(modulo.id) === 0 ? 'min-h-17 bg-transparent' : ''"
            @update:model-value="(lista: ConteudoRead[]) => conteudosPorModulo[modulo.id] = lista"
            @end="onReordenarConteudos"
          >
          <div
            v-for="conteudo in conteudosDoModulo(modulo.id)"
            :key="conteudo.id"
            class="flex items-start justify-between gap-2 border-l-4 px-4 py-3 sm:items-center"
            :class="tiposInfo[conteudo.tipo].linha"
          >
            <div class="flex min-w-0 flex-1 items-start gap-2 sm:items-center sm:gap-3">
              <UIcon
                name="i-lucide-grip-vertical"
                class="conteudo-drag-handle size-4 shrink-0 self-center text-muted cursor-grab active:cursor-grabbing"
              />
              <div
                class="flex items-center justify-center size-8 rounded-full shrink-0"
                :class="tiposInfo[conteudo.tipo].icone"
              >
                <UIcon
                  :name="tiposInfo[conteudo.tipo].icon"
                  class="size-4"
                />
              </div>
              <div class="min-w-0 wrap-anywhere">
                <!-- lapis do lado do nome, ele so edita nome e pontos -->
                <p class="flex items-center gap-1 text-sm font-medium">
                  {{ conteudo.titulo }}
                  <UButton
                    icon="i-lucide-pencil"
                    size="xs"
                    color="neutral"
                    variant="ghost"
                    aria-label="Editar nome e pontos"
                    class="shrink-0"
                    @click="abrirEditarConteudo(conteudo)"
                  />
                </p>
                <p class="text-xs text-muted">
                  {{ conteudo.pontos }} pts
                  <span
                    v-if="conteudo.tipo === 'video' && !conteudo.video_url"
                    class="text-warning"
                  >
                    · sem link ainda
                  </span>
                  <span
                    v-if="conteudo.tipo === 'artigo' && !conteudo.artigo_conteudo"
                    class="text-warning"
                  >
                    · sem texto ainda
                  </span>
                  <span
                    v-if="conteudo.tipo === 'quiz'"
                    class="text-warning"
                  >
                    · {{ textoPerguntas(conteudo.id) }}
                  </span>
                </p>
              </div>
            </div>

            <div class="flex shrink-0 items-center gap-1 sm:gap-2">
              <!-- so o quiz tem desempenho, de sempre. clicando abre o dashboard completo no modal -->
              <button
                v-if="conteudo.tipo === 'quiz'"
                type="button"
                class="flex items-center gap-3 rounded-lg px-2 py-1 text-sm text-muted ring ring-default transition hover:bg-elevated hover:text-highlighted"
                aria-label="Ver desempenho do quiz"
                @click="abrirDesempenho(conteudo)"
              >
                <span class="flex items-center gap-1.5 font-medium">
                  <UIcon
                    name="i-lucide-chart-no-axes-column"
                    class="size-4 shrink-0"
                  />
                  <span class="hidden sm:inline">Desempenho</span>
                </span>
                <span
                  v-if="resumoPorConteudo[conteudo.id]"
                  class="hidden items-center gap-3 text-xs tabular-nums md:flex"
                >
                  <UTooltip text="Nota média (versão atual)">
                    <span class="flex items-center gap-1">
                      <UIcon
                        name="i-lucide-target"
                        class="size-3.5"
                      />
                      {{ formatarAcerto(resumoPorConteudo[conteudo.id]!.acerto) }}
                    </span>
                  </UTooltip>
                  <UTooltip text="Concluíram">
                    <span class="flex items-center gap-1">
                      <UIcon
                        name="i-lucide-users"
                        class="size-3.5"
                      />
                      {{ resumoPorConteudo[conteudo.id]!.concluiram }}
                    </span>
                  </UTooltip>
                </span>
              </button>

              <!-- o selo do tipo ja e o botao de editar: video abre o modal do link,
              artigo e quiz vao pro editor deles. no celular fica so o icone -->
              <NuxtLink
                v-if="conteudo.tipo !== 'video'"
                :to="`${trilhaPath}/conteudos/${conteudo.id}`"
                class="flex items-center justify-center gap-1.5 rounded-full px-2.5 py-1 text-sm font-semibold ring transition hover:brightness-110 sm:w-30 sm:px-3"
                :class="tiposInfo[conteudo.tipo].selo"
                :aria-label="conteudo.tipo === 'artigo' ? 'Editar artigo' : 'Editar quiz'"
              >
                <UIcon
                  :name="tiposInfo[conteudo.tipo].icon"
                  class="size-4"
                />
                <span class="hidden sm:inline">{{ tiposInfo[conteudo.tipo].label }}</span>
                <UIcon
                  name="i-lucide-arrow-up-right"
                  class="size-3.5 opacity-70"
                />
              </NuxtLink>
              <button
                v-else
                type="button"
                class="flex items-center justify-center gap-1.5 rounded-full px-2.5 py-1 text-sm font-semibold ring transition hover:brightness-110 sm:w-30 sm:px-3"
                :class="tiposInfo[conteudo.tipo].selo"
                :aria-label="conteudo.video_url ? 'Editar link do vídeo' : 'Adicionar link do vídeo'"
                @click="abrirLinkVideo(conteudo)"
              >
                <UIcon
                  :name="tiposInfo[conteudo.tipo].icon"
                  class="size-4"
                />
                <span class="hidden sm:inline">{{ tiposInfo[conteudo.tipo].label }}</span>
                <UIcon
                  name="i-lucide-link"
                  class="size-3.5 opacity-70"
                />
              </button>

              <UButton
                icon="i-lucide-trash-2"
                size="xs"
                color="error"
                variant="ghost"
                aria-label="Excluir conteúdo"
                @click="onDeleteConteudo(conteudo)"
              />
            </div>
          </div>
          </VueDraggable>
        </div>
      </div>
    </VueDraggable>

    <p
      v-if="!loading && trilha && modulos.length === 0"
      class="text-sm text-muted text-center py-12"
    >
      Nenhum módulo cadastrado. Clique em "Módulo" para começar a jornada.
    </p>

    <!-- criar ou editar modulo -->
    <UModal
      v-model:open="showModuloModal"
      :title="moduloEditando ? 'Editar módulo' : 'Novo módulo'"
    >
      <template #body>
        <div class="space-y-4">
          <UFormField label="Título do módulo">
            <UInput
              v-model="formModulo.titulo"
              placeholder="Ex: Módulo 1"
              class="w-full"
            />
          </UFormField>
          <div class="flex justify-end gap-2">
            <UButton
              color="neutral"
              variant="ghost"
              label="Cancelar"
              @click="showModuloModal = false"
            />
            <UButton
              color="primary"
              :label="moduloEditando ? 'Salvar' : 'Criar'"
              :loading="savingModulo"
              :disabled="!formModulo.titulo.trim()"
              @click="onSubmitModulo"
            />
          </div>
        </div>
      </template>
    </UModal>

    <!-- criar ou editar conteudo, mesmo modal, so muda o titulo/botao e
    esconde o seletor de tipo quando ta editando (n da pra trocar o tipo depois) -->
    <UModal
      v-model:open="showConteudoModal"
      :title="modoConteudoModal === 'criar' ? 'Novo conteúdo' : 'Editar conteúdo'"
    >
      <template #body>
        <div class="space-y-4">
          <UFormField
            v-if="modoConteudoModal === 'criar'"
            label="Tipo"
          >
            <div class="flex flex-wrap gap-2">
              <UButton
                label="Vídeo"
                :color="formConteudo.tipo === 'video' ? 'primary' : 'neutral'"
                :variant="formConteudo.tipo === 'video' ? 'solid' : 'outline'"
                @click="formConteudo.tipo = 'video'"
              />
              <UButton
                label="Artigo"
                :color="formConteudo.tipo === 'artigo' ? 'primary' : 'neutral'"
                :variant="formConteudo.tipo === 'artigo' ? 'solid' : 'outline'"
                @click="formConteudo.tipo = 'artigo'"
              />
              <UButton
                label="Quiz"
                :color="formConteudo.tipo === 'quiz' ? 'primary' : 'neutral'"
                :variant="formConteudo.tipo === 'quiz' ? 'solid' : 'outline'"
                @click="formConteudo.tipo = 'quiz'"
              />
            </div>
          </UFormField>

          <UFormField label="Título">
            <UInput
              v-model="formConteudo.titulo"
              placeholder="Ex: Salinidade: o que é e como medir"
              class="w-full"
            />
          </UFormField>

          <UFormField label="Pontos">
            <UInputNumber
              v-model="formConteudo.pontos"
              :min="0"
              class="w-full"
            />
          </UFormField>

          <div class="flex justify-end gap-2">
            <UButton
              color="neutral"
              variant="ghost"
              label="Cancelar"
              @click="showConteudoModal = false"
            />
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
    <UModal
      v-model:open="showVideoModal"
      title="Link do vídeo"
    >
      <template #body>
        <div class="space-y-4">
          <UFormField label="URL do YouTube">
            <UInput
              v-model="formVideoUrl"
              placeholder="https://www.youtube.com/watch?v=..."
              class="w-full"
            />
            <p
              v-if="formVideoUrl && !youtubeIdPreview"
              class="text-xs text-error mt-1"
            >
              Não parece ser um link válido do YouTube.
            </p>
          </UFormField>

          <!-- se o link for valido, o video ja toca aqui antes de salvar -->
          <div
            v-if="youtubeIdPreview"
            class="aspect-video rounded-lg overflow-hidden border border-default"
          >
            <iframe
              :src="`https://www.youtube.com/embed/${youtubeIdPreview}`"
              class="w-full h-full"
              frameborder="0"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowfullscreen
            />
          </div>

          <!-- so aparece trocando um link q ja existia, o 1 link n e alteracao -->
          <UCheckbox
            v-if="conteudoAlvo?.video_url"
            v-model="alteracaoVideo"
            label="Alteração significativa"
            description="Avisa quem já concluiu que o vídeo mudou."
          />

          <div class="flex justify-end gap-2">
            <UButton
              color="neutral"
              variant="ghost"
              label="Cancelar"
              @click="showVideoModal = false"
            />
            <UButton
              color="primary"
              label="Salvar"
              :loading="savingVideo"
              :disabled="!youtubeIdPreview"
              @click="onSubmitVideoUrl"
            />
          </div>
        </div>
      </template>
    </UModal>

    <!-- dashboard do conteudo sem sair da tela, busca os dados toda vez q abre -->
    <UModal
      v-model:open="showDesempenhoModal"
      :title="conteudoDesempenho ? `Desempenho: ${conteudoDesempenho.titulo}` : 'Desempenho'"
      :ui="{ content: 'sm:max-w-5xl' }"
    >
      <template #body>
        <DashboardConteudo
          v-if="conteudoDesempenho"
          :conteudo-id="conteudoDesempenho.id"
          :com-titulo="false"
        />
      </template>
    </UModal>

    <UModal
      v-model:open="showDeleteModal"
      :title="exclusao?.titulo"
      :description="exclusao?.descricao"
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
          label="Excluir"
          color="error"
          :loading="excluindo"
          @click="confirmarExclusao"
        />
      </template>
    </UModal>
  </div>
</template>

<script setup lang="ts">
import { VueDraggable } from 'vue-draggable-plus'
import type { Ref } from 'vue'
import type { ConteudoRead, ModuloRead, ResumoConteudoRead, TrilhaRead } from '~/types/generated'

definePageMeta({ middleware: 'role', roles: ['author', 'admin'], key: route => route.path })

const route = useRoute()
const api = useApi()
const grupoId = route.params.grupoId
const router = useRouter()
const trilhaId = Number(route.params.id)
const trilhaGrupo = grupoId ? `/grupos/${grupoId}/trilhas/${trilhaId}` : null
const trilhaPath = trilhaGrupo ? `${trilhaGrupo}/editar` : `/author/trilhas/${trilhaId}`
const toast = useToast()

function voltarParaTrilhas() {
  if (grupoId) return router.push(`/grupos/${grupoId}/trilhas/gerenciar`)
  if (window.history.length > 1) router.back()
  else return router.push('/author/trilhas')
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
// classes inteiras pq o tailwind n acha classe montada com variavel
// linha: faixa na esquerda + fundo leve, icone: bolinha do icone, selo: o tipo escrito
const tiposInfo = {
  video: {
    label: 'Vídeo',
    icon: 'i-lucide-play-circle',
    linha: 'border-l-sky-500 bg-sky-500/5',
    icone: 'bg-sky-500/15 text-sky-500',
    selo: 'bg-sky-500/15 text-sky-600 ring-sky-500/30 dark:text-sky-300',
  },
  artigo: {
    label: 'Artigo',
    icon: 'i-lucide-book-open',
    linha: 'border-l-emerald-500 bg-emerald-500/5',
    icone: 'bg-emerald-500/15 text-emerald-500',
    selo: 'bg-emerald-500/15 text-emerald-600 ring-emerald-500/30 dark:text-emerald-300',
  },
  quiz: {
    label: 'Quiz',
    icon: 'i-lucide-list-checks',
    linha: 'border-l-violet-500 bg-violet-500/5',
    icone: 'bg-violet-500/15 text-violet-500',
    selo: 'bg-violet-500/15 text-violet-600 ring-violet-500/30 dark:text-violet-300',
  },
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
      .sort((a, b) => a.ordem - b.ordem || a.id - b.id)
  }
}

// quantas perguntas cada quiz tem, o conteudo n traz isso entao busca as questoes de cada um
const perguntasPorQuiz = reactive<Record<number, number>>({})

async function contarPerguntas() {
  const quizzes = []
  for (const conteudo of conteudos.value) {
    if (conteudo.tipo === 'quiz') quizzes.push(conteudo.id)
  }
  const respostas = await Promise.all(quizzes.map(id => api('/questoes', { query: { conteudo_id: id } })))
  let indice = 0
  for (const id of quizzes) {
    perguntasPorQuiz[id] = respostas[indice]!.data.length
    indice += 1
  }
}

function textoPerguntas(conteudoId: number) {
  const quantidade = perguntasPorQuiz[conteudoId]
  if (quantidade === undefined) return '...'
  if (quantidade === 0) return 'sem perguntas ainda'
  return `${quantidade} pergunta${quantidade === 1 ? '' : 's'}`
}

async function fetchTudo() {
  loading.value = true

  await comErro('Não foi possível carregar a trilha', async () => {
    const [dadosTrilha, modulosRes] = await Promise.all([
      api(`/trilhas/${trilhaId}`),
      api('/modulos', { query: { trilha_id: trilhaId, sort: 'ordem,id' } }),
    ])

    modulos.value = modulosRes.data
    const listas = await Promise.all(modulos.value.map(modulo =>
      api('/conteudos', { query: { modulo_id: modulo.id, sort: 'ordem,id' } }),
    ))
    conteudos.value = listas.flatMap(lista => lista.data)
    popularConteudosPorModulo()
    await Promise.all([contarPerguntas(), buscarResumo()])
    trilha.value = dadosTrilha
  })

  loading.value = false
}

onMounted(fetchTudo)

/* modulo */

async function onReordenarModulos() {
  await comErro('Não foi possível salvar a nova ordem dos módulos', async () => {
    await Promise.all(modulos.value.map((modulo, indice) => {
      modulo.ordem = indice
      return api(`/modulos/${modulo.id}`, { method: 'PATCH', body: { ordem: indice } })
    }))
  })
}

/* conteudo */

// as listas ja chegam na ordem nova. passa por todos os modulos pq o arrasto pode ter
// mexido em dois (o de onde saiu e o q recebeu), e so manda pro back quem mudou
async function onReordenarConteudos() {
  await comErro('Não foi possível salvar a nova ordem dos conteúdos', async () => {
    const pedidos = []
    for (const modulo of modulos.value) {
      let indice = 0
      for (const conteudo of conteudosDoModulo(modulo.id)) {
        if (conteudo.ordem !== indice || conteudo.modulo_id !== modulo.id) {
          conteudo.ordem = indice
          conteudo.modulo_id = modulo.id
          pedidos.push(api(`/conteudos/${conteudo.id}`, { method: 'PATCH', body: { ordem: indice, modulo_id: modulo.id } }))
        }
        indice += 1
      }
    }
    await Promise.all(pedidos)
  })
}

const showModuloModal = ref(false)
const savingModulo = ref(false)
const moduloEditando = ref<ModuloRead | null>(null)
const formModulo = reactive({ titulo: '' })

function abrirCriarModulo() {
  moduloEditando.value = null
  formModulo.titulo = ''
  showModuloModal.value = true
}

function abrirEditarModulo(modulo: ModuloRead) {
  moduloEditando.value = modulo
  formModulo.titulo = modulo.titulo
  showModuloModal.value = true
}

async function onSubmitModulo() {
  await salvando(savingModulo, 'Não foi possível salvar o módulo', async () => {
    const titulo = formModulo.titulo
    if (moduloEditando.value) {
      await api(`/modulos/${moduloEditando.value.id}`, { method: 'PATCH', body: { titulo } })
      moduloEditando.value.titulo = titulo
    }
    else {
      const novoModulo = await api('/modulos', {
        method: 'POST',
        body: { trilha_id: trilhaId, titulo, ordem: modulos.value.length },
      })
      modulos.value.push(novoModulo)
      conteudosPorModulo[novoModulo.id] = []
    }
    showModuloModal.value = false
  })
}

function onDeleteModulo(modulo: ModuloRead) {
  pedirExclusao(
    'Excluir módulo',
    `Excluir o módulo "${modulo.titulo}"? Isso apaga os conteúdos dele também.`,
    'Não foi possível excluir o módulo',
    async () => {
      await api(`/modulos/${modulo.id}`, { method: 'DELETE' })
      modulos.value = modulos.value.filter(m => m.id !== modulo.id)
      conteudos.value = conteudos.value.filter(c => c.modulo_id !== modulo.id)
      // eslint-disable-next-line @typescript-eslint/no-dynamic-delete
      delete conteudosPorModulo[modulo.id]
    },
  )
}

/* conteudo criar + editar no mesmo modal */

const showConteudoModal = ref(false)
const savingConteudo = ref(false)
const modoConteudoModal = ref<'criar' | 'editar'>('criar')
const moduloAlvo = ref<ModuloRead | null>(null) // usado so no modo criar
const conteudoEditando = ref<ConteudoRead | null>(null) // usado so no modo editar
// a ordem agora e pelo draggable, o modal so mexe no nome e nos pontos
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
    if (modoConteudoModal.value === 'criar' && moduloAlvo.value) {
      // conteudo novo vai pro fim do modulo
      const ordem = Math.max(-1, ...conteudosDoModulo(moduloAlvo.value.id).map(c => c.ordem)) + 1
      const novo = await api('/conteudos', {
        method: 'POST',
        body: {
          modulo_id: moduloAlvo.value.id,
          titulo: formConteudo.titulo,
          tipo: formConteudo.tipo,
          ordem,
          pontos: formConteudo.pontos,
        },
      })
      conteudos.value.push(novo)
      popularConteudosPorModulo()

      // artigo e quiz ja abrem direto a tela de edicao depois de criar
      if (novo.tipo !== 'video') {
        showConteudoModal.value = false
        await router.push(`${trilhaPath}/conteudos/${novo.id}`)
        return
      }
    }
    else if (conteudoEditando.value) {
      const id = conteudoEditando.value.id

      // so mudar os pontos sobe a versao, trocar o nome n precisa
      let versao = conteudoEditando.value.versao
      if (formConteudo.pontos !== conteudoEditando.value.pontos) {
        versao += 1
      }

      const { titulo, pontos } = formConteudo
      const dados = { titulo, pontos, versao }
      await api(`/conteudos/${id}`, { method: 'PATCH', body: dados })
      // PATCH do fastcrud n devolve o item, entao atualiza local com o que ja temos
      Object.assign(conteudoEditando.value, dados)
      popularConteudosPorModulo()
    }
    showConteudoModal.value = false
  })
}

function onDeleteConteudo(conteudo: ConteudoRead) {
  pedirExclusao(
    'Excluir conteúdo',
    `Excluir o conteúdo "${conteudo.titulo}"?`,
    'Não foi possível excluir o conteúdo',
    async () => {
      await api(`/conteudos/${conteudo.id}`, { method: 'DELETE' })
      conteudos.value = conteudos.value.filter(c => c.id !== conteudo.id)
      const lista = conteudosPorModulo[conteudo.modulo_id]
      if (lista) conteudosPorModulo[conteudo.modulo_id] = lista.filter(c => c.id !== conteudo.id)
    },
  )
}

/* desempenho do conteudo no modal */

// concluiram e acerto de cada quiz, vem tudo numa chamada so
const resumoPorConteudo = reactive<Record<number, ResumoConteudoRead>>({})

async function buscarResumo() {
  const lista: ResumoConteudoRead[] = await api(`/trilhas/${trilhaId}/resumo-conteudos`)
  for (const item of lista) resumoPorConteudo[item.id] = item
}

const formatarNota = new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 1 }).format

// nota de 0 a 10 igual a dashboard do quiz
function formatarAcerto(acerto: number | null | undefined) {
  if (acerto === null || acerto === undefined) return '—'
  return `${formatarNota(acerto * 10)}/10`
}

const showDesempenhoModal = ref(false)
const conteudoDesempenho = ref<ConteudoRead | null>(null)

function abrirDesempenho(conteudo: ConteudoRead) {
  conteudoDesempenho.value = conteudo
  showDesempenhoModal.value = true
}

/* modal de excluir, serve pra modulo e conteudo */

const showDeleteModal = ref(false)
const excluindo = ref(false)
// guarda o texto e oq fazer qnd confirmar
const exclusao = ref<{ titulo: string, descricao: string, erro: string, excluir: () => Promise<void> } | null>(null)

function pedirExclusao(titulo: string, descricao: string, erro: string, excluir: () => Promise<void>) {
  exclusao.value = { titulo, descricao, erro, excluir }
  showDeleteModal.value = true
}

async function confirmarExclusao() {
  if (!exclusao.value) return
  await salvando(excluindo, exclusao.value.erro, exclusao.value.excluir)
  showDeleteModal.value = false
}

/* inserir link do video */

const showVideoModal = ref(false)
const savingVideo = ref(false)
const conteudoAlvo = ref<ConteudoRead | null>(null)
const formVideoUrl = ref('')
const alteracaoVideo = ref(false)
const youtubeIdPreview = computed(() => extrairYoutubeId(formVideoUrl.value))

function abrirLinkVideo(conteudo: ConteudoRead) {
  conteudoAlvo.value = conteudo
  formVideoUrl.value = conteudo.video_url ?? ''
  alteracaoVideo.value = false
  showVideoModal.value = true
}

async function onSubmitVideoUrl() {
  if (!conteudoAlvo.value) return
  const id = conteudoAlvo.value.id
  const moduloId = conteudoAlvo.value.modulo_id

  let versao = conteudoAlvo.value.versao
  if (alteracaoVideo.value) versao += 1

  await salvando(savingVideo, 'Não foi possível salvar o link do vídeo', async () => {
    await api(`/conteudos/${id}`, { method: 'PATCH', body: { video_url: formVideoUrl.value, versao } })

    for (const lista of [conteudos.value, conteudosPorModulo[moduloId] ?? []]) {
      const alvo = lista.find(c => c.id === id)
      if (alvo) Object.assign(alvo, { video_url: formVideoUrl.value, versao })
    }
    showVideoModal.value = false
  })
}
</script>
