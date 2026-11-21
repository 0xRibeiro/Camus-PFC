<template>
  <div class="flex-1">
    <!-- esse botão só aparece se estivermos em uma rota de grupo -->
    <UButton
      v-if="grupoId"
      label="Voltar ao grupo"
      icon="i-lucide-arrow-left"
      variant="link"
      color="neutral"
      class="mb-3 px-0"
      :to="`/grupos/${grupoId}`"
    />

    <!-- cabecalho: titulo + descricao curta + contador de trilhas -->
    <CamusBanner
      :titulo="grupoId ? 'Trilhas do grupo' : 'Gerenciar trilhas'"
      descricao="Cadastre uma trilha e clique nela para montar a jornada de módulos e conteúdos."
      :imagem="grupoId ? '/papeis-de-parede/laranja/trilhas.webp' : '/papeis-de-parede/vermelho/trilhas.webp'"
    >
      <template #acoes>
        <UBadge size="xl">
          {{ trilhas.length }} trilha{{ trilhas.length === 1 ? '' : 's' }}
        </UBadge>
        <UButton
          label="Nova trilha"
          icon="i-lucide-plus"
          size="lg"
          @click="abrirCriar()"
        />
      </template>
    </CamusBanner>

    <!-- filtros: busca, tag, status e agrupamento -->
    <div class="mb-6 space-y-3">
      <div class="flex flex-wrap items-center gap-3 sm:flex-nowrap">
        <UInput
          v-model="busca"
          icon="i-lucide-search"
          placeholder="Buscar trilha..."
          class="w-full min-w-0 sm:flex-1"
        />

        <USelect
          v-model="tagFiltro"
          :items="tagFiltroOptions"
          placeholder="Filtrar por tag"
          class="min-w-0 flex-1 sm:w-48 sm:flex-none"
        />

        <UButton
          v-if="filtrosAtivos"
          label="Limpar"
          icon="i-lucide-x"
          color="neutral"
          variant="ghost"
          @click="limparFiltros"
        />
      </div>

      <div class="flex flex-wrap items-center justify-between gap-3">
        <UTabs
          v-model="statusFiltro"
          :items="statusOptions"
          :content="false"
          size="sm"
        />

        <USwitch
          v-model="agruparPorTag"
          label="Agrupar por tag"
        />
      </div>
    </div>

    <!-- spinner enquanto busca as trilhas -->
    <div
      v-if="loading"
      class="flex justify-center py-12"
    >
      <UIcon
        name="i-lucide-loader-circle"
        class="size-6 animate-spin"
      />
    </div>

    <!-- nenhuma trilha cadastrada ainda -->
    <UCard
      v-else-if="!trilhas.length"
      class="text-center"
    >
      <UIcon
        name="i-lucide-route"
        class="size-10 text-primary"
      />
      <p class="mt-2 text-muted">
        Nenhuma trilha cadastrada ainda.
      </p>
      <UButton
        label="Cadastrar trilha"
        icon="i-lucide-plus"
        class="mt-4"
        @click="abrirCriar()"
      />
    </UCard>

    <!-- tem trilha mas o filtro n achou nada -->
    <UCard
      v-else-if="!trilhasFiltradas.length"
      class="text-center"
    >
      <UIcon
        name="i-lucide-search-x"
        class="size-10 text-muted"
      />
      <p class="mt-2 text-muted">
        Nenhuma trilha encontrada com esses filtros.
      </p>
      <UButton
        label="Limpar filtros"
        color="neutral"
        variant="outline"
        class="mt-4"
        @click="limparFiltros"
      />
    </UCard>

    <!--
      grid com 1 TrilhaCard por trilha, separado por tag ou tudo junto.

      :modulos-count e :conteudos-count sao props indo PRA DENTRO do componente
      (a pagina calculou essas contagens, o card so mostra).

      @edit e @delete sao o caminho contrario: eventos vindo DE DENTRO do componente
      pra fora. o TrilhaCard n sabe abrir modal nem chamar api - ele so avisa
      "cliquei em editar" ou "cliquei em excluir", e aqui na pagina a gente decide
      o que fazer com esse aviso (abrirEditar / abrirExcluir)
    -->
    <div
      v-else
      class="space-y-8"
    >
      <section
        v-for="secao in secoes"
        :key="secao.chave"
        class="space-y-3"
      >
        <div
          v-if="agruparPorTag"
          class="flex items-center gap-2"
        >
          <UBadge
            :label="rotuloSecao(secao.chave)"
            :color="corSecao(secao.chave)"
            variant="soft"
          />
          <span class="text-xs text-muted">
            {{ secao.trilhas.length }} trilha{{ secao.trilhas.length === 1 ? '' : 's' }}
          </span>
          <USeparator class="flex-1" />
        </div>

        <UPageGrid>
          <TrilhaCard
            v-for="trilha in secao.trilhas"
            :key="trilha.id"
            :trilha="trilha"
            :to="caminhoTrilha(trilha.id)"
            :dashboard="`${caminhoTrilha(trilha.id)}/dashboard`"
            :modulos-count="contarModulos(trilha.id)"
            :conteudos-count="contarConteudos(trilha.id)"
            @edit="abrirEditar(trilha)"
            @delete="abrirExcluir(trilha)"
          />
        </UPageGrid>
      </section>
    </div>

    <!--
      v-model:open="showModal" liga o estado "showModal" daqui com o defineModel('open')
      que existe dentro do TrilhaFormModal - os dois lados sempre ficam sincronizados,
      em qualquer direcao (a pagina fecha o modal fazendo showModal.value = false,
      e o modal tambem pode fechar sozinho por dentro, refletindo aqui fora).

      :trilha="editandoTrilha" e o que diz ao modal se e "criar" (null) ou "editar"
      (a trilha escolhida). @submit e o aviso que o modal manda quando o formulario
      ja foi validado e a pessoa quer salvar - so ai que a pagina chama a api de verdade
    -->
    <TrilhaFormModal
      v-model:open="showModal"
      :trilha="editandoTrilha"
      :saving="saving"
      @submit="onSubmitForm"
    />

    <UModal
      v-model:open="showDeleteModal"
      title="Excluir trilha"
      :description="descricaoExclusao"
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
// TrilhaRead vem do types.gen.ts, gerado a partir da resposta real da api (TrilhaRead
// no back, em python). n escrevemos esse tipo na mao - ele ja reflete exatamente os
// campos que a api devolve (id, titulo, descricao, foto, is_active), e se o back
// mudar um campo, esse tipo atualiza sozinho quando a gente roda o comando de gerar
import type { TrilhaRead } from '~/types/generated'

// Na rota global, a gestão exige author/admin. No grupo, exige o dono.
definePageMeta({ middleware: 'role', roles: ['author', 'admin'], key: route => route.path })

const grupoId = useRoute().params.grupoId
const api = useApi()
const toast = useToast()

const trilhas = ref<TrilhaRead[]>([])
const loading = ref(true)

const busca = ref('')

const tagFiltro = ref('')
const statusFiltro = ref<'todas' | 'ativas' | 'desativadas'>('todas')
const agruparPorTag = ref(true)

// trilha sem tag cai nessa chave
const SEM_TAG = 'sem-tag'

function rotuloSecao(chave: string) {
  if (chave === SEM_TAG) return 'Sem tag'
  return infoDaTagTrilha(chave).label
}

function corSecao(chave: string): CorTagTrilha {
  if (chave === SEM_TAG) return 'neutral'
  return infoDaTagTrilha(chave).color
}

// ordem alfabetica, com "outro" e "sem tag" sempre no fim
function pesoSecao(chave: string) {
  if (chave === SEM_TAG) return 2
  if (chave === 'outro') return 1
  return 0
}

function compararSecoes(a: string, b: string) {
  const diferenca = pesoSecao(a) - pesoSecao(b)
  if (diferenca !== 0) return diferenca
  return rotuloSecao(a).localeCompare(rotuloSecao(b), 'pt-BR')
}

const tagFiltroOptions: { label: string, value: string, chip: { color: CorTagTrilha } }[] = []
const chavesTags = [SEM_TAG]
for (const item of TRILHA_TAGS) chavesTags.push(item.value)
chavesTags.sort(compararSecoes)
for (const chave of chavesTags) {
  tagFiltroOptions.push({ label: rotuloSecao(chave), value: chave, chip: { color: corSecao(chave) } })
}

const totalAtivas = computed(() => {
  let total = 0
  for (const trilha of trilhas.value) {
    if (trilha.is_active) total++
  }
  return total
})

const statusOptions = computed(() => [
  { label: 'Todas', value: 'todas', badge: trilhas.value.length },
  { label: 'Ativas', value: 'ativas', badge: totalAtivas.value },
  { label: 'Desativadas', value: 'desativadas', badge: trilhas.value.length - totalAtivas.value },
])

const filtrosAtivos = computed(() => !!busca.value || !!tagFiltro.value || statusFiltro.value !== 'todas')

function limparFiltros() {
  busca.value = ''
  tagFiltro.value = ''
  statusFiltro.value = 'todas'
}

// ativa primeiro, depois pelo titulo
function compararTrilhas(a: TrilhaRead, b: TrilhaRead) {
  if (a.is_active !== b.is_active) return a.is_active ? -1 : 1
  return a.titulo.localeCompare(b.titulo, 'pt-BR')
}

// computed recalcula sozinho toda vez que "trilhas" ou algum filtro mudam
const trilhasFiltradas = computed(() => {
  const resultado: TrilhaRead[] = []
  const buscaLower = busca.value.toLowerCase()

  for (const trilha of trilhas.value) {
    let descricao = ''
    if (trilha.descricao) descricao = trilha.descricao

    let tag = SEM_TAG
    if (trilha.tag) tag = trilha.tag

    const bateBusca = trilha.titulo.toLowerCase().includes(buscaLower)
      || descricao.toLowerCase().includes(buscaLower)
    const bateTag = !tagFiltro.value || tag === tagFiltro.value

    let bateStatus = true
    if (statusFiltro.value === 'ativas') bateStatus = trilha.is_active
    if (statusFiltro.value === 'desativadas') bateStatus = !trilha.is_active

    if (bateBusca && bateTag && bateStatus) {
      resultado.push(trilha)
    }
  }
  resultado.sort(compararTrilhas)
  return resultado
})

// sem agrupar vira uma secao so
const secoes = computed(() => {
  if (!agruparPorTag.value) return [{ chave: 'todas', trilhas: trilhasFiltradas.value }]

  const porTag = new Map<string, TrilhaRead[]>()
  for (const trilha of trilhasFiltradas.value) {
    let chave = SEM_TAG
    if (trilha.tag) chave = trilha.tag

    let lista = porTag.get(chave)
    if (!lista) {
      lista = []
      porTag.set(chave, lista)
    }
    lista.push(trilha)
  }

  const chaves = Array.from(porTag.keys())
  chaves.sort(compararSecoes)

  const resultado: { chave: string, trilhas: TrilhaRead[] }[] = []
  for (const chave of chaves) {
    const lista = porTag.get(chave)
    if (lista) resultado.push({ chave, trilhas: lista })
  }
  return resultado
})

function caminhoTrilha(trilhaId: number) {
  if (grupoId) return `/grupos/${grupoId}/trilhas/${trilhaId}/editar`
  return `/author/trilhas/${trilhaId}`
}

// contagem de modulos/conteudos por trilha, pro rodape do card
const contagem = ref({
  modulos: new Map<number, number>(),
  conteudos: new Map<number, number>(),
})

// Map.get devolve undefined se a chave n existir - essas 2 funcoes so tratam
// esse caso e devolvem 0 no lugar, pra n espalhar esse "if" pelo template
function contarModulos(trilhaId: number) {
  const total = contagem.value.modulos.get(trilhaId)
  if (total === undefined) return 0
  return total
}

function contarConteudos(trilhaId: number) {
  const total = contagem.value.conteudos.get(trilhaId)
  if (total === undefined) return 0
  return total
}

async function fetchTrilhas() {
  loading.value = true
  const [trilhasRes, modulosRes, conteudosRes] = await Promise.all([
    api('/trilhas'),
    api('/modulos'),
    api('/conteudos'),
  ])
  trilhas.value = trilhasRes.data

  const modulosPorTrilha = new Map<number, number>()
  // guarda de qual trilha cada modulo e, pra depois somar o conteudo na trilha certa
  const trilhaDoModulo = new Map<number, number>()

  for (const modulo of modulosRes.data) {
    let totalModulos = modulosPorTrilha.get(modulo.trilha_id)
    if (totalModulos === undefined) totalModulos = 0
    modulosPorTrilha.set(modulo.trilha_id, totalModulos + 1)

    trilhaDoModulo.set(modulo.id, modulo.trilha_id)
  }

  const conteudosPorTrilha = new Map<number, number>()
  for (const conteudo of conteudosRes.data) {
    const trilhaId = trilhaDoModulo.get(conteudo.modulo_id)
    if (trilhaId === undefined) continue

    let totalConteudos = conteudosPorTrilha.get(trilhaId)
    if (totalConteudos === undefined) totalConteudos = 0
    conteudosPorTrilha.set(trilhaId, totalConteudos + 1)
  }

  contagem.value = { modulos: modulosPorTrilha, conteudos: conteudosPorTrilha }
  loading.value = false
}

// busca assim que a pagina abre
onMounted(fetchTrilhas)

const showDeleteModal = ref(false)
const excluindo = ref(false)
const trilhaParaExcluir = ref<TrilhaRead | null>(null)

const descricaoExclusao = computed(() => {
  if (!trilhaParaExcluir.value) return ''
  return `Excluir a trilha "${trilhaParaExcluir.value.titulo}"? Isso apaga todos os módulos e conteúdos dela também.`
})

function abrirExcluir(trilha: TrilhaRead) {
  trilhaParaExcluir.value = trilha
  showDeleteModal.value = true
}

async function confirmarExclusao() {
  if (!trilhaParaExcluir.value) return

  excluindo.value = true
  try {
    await api(`/trilhas/${trilhaParaExcluir.value.id}`, { method: 'DELETE' })

    // monta a lista de novo, sem a trilha excluida
    const restantes: TrilhaRead[] = []
    for (const t of trilhas.value) {
      if (t.id !== trilhaParaExcluir.value.id) restantes.push(t)
    }
    trilhas.value = restantes

    showDeleteModal.value = false
  }
  catch {
    toast.add({ title: 'Não foi possível excluir a trilha', color: 'error' })
  }
  finally {
    excluindo.value = false
  }
}

const showModal = ref(false)
const saving = ref(false)

// null = modo criar. preenchido = modo editar (repassado como prop pro TrilhaFormModal)
const editandoTrilha = ref<TrilhaRead | null>(null)

function abrirCriar() {
  editandoTrilha.value = null
  showModal.value = true
}

function abrirEditar(trilha: TrilhaRead) {
  editandoTrilha.value = trilha
  showModal.value = true
}

// isso aqui roda quando o TrilhaFormModal emite "submit" - o formulario ja foi
// validado la dentro do componente, aqui a gente so decide POST (criar) ou PATCH
// (editar) e atualiza a lista local, sem precisar buscar tudo do back de novo
async function onSubmitForm(dados: { titulo: string, descricao?: string | null, tag?: string | null, foto?: string | null, is_active: boolean }) {
  saving.value = true
  try {
    if (editandoTrilha.value) {
      // o PATCH do fastcrud n devolve o item atualizado (volta vazio), entao
      // atualiza a lista local com os dados que a gente ja tem, sem depender da resposta
      await api(`/trilhas/${editandoTrilha.value.id}`, {
        method: 'PATCH',
        body: dados,
      })

      let antiga: TrilhaRead | undefined
      for (const t of trilhas.value) {
        if (t.id === editandoTrilha.value.id) antiga = t
      }
      if (antiga) Object.assign(antiga, dados)
    }
    else {
      // is_active n existe no TrilhaCreate do back (toda trilha nasce inativa),
      // entao monta o corpo do POST so com o que ele aceita
      const dadosCriacao = { titulo: dados.titulo, descricao: dados.descricao, tag: dados.tag, foto: dados.foto }
      const nova = await api('/trilhas', { method: 'POST', body: dadosCriacao })
      trilhas.value.push(nova)
    }

    showModal.value = false
  }
  catch {
    toast.add({
      title: editandoTrilha.value ? 'Não foi possível salvar a trilha' : 'Não foi possível criar a trilha',
      color: 'error',
    })
  }
  finally {
    saving.value = false
  }
}
</script>
