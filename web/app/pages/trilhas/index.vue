<script setup lang="ts">
import type { TrilhaResumoRead } from '~/types/generated'

definePageMeta({ middleware: 'role', key: route => route.path })

const grupoId = useRoute().params.grupoId
const api = useApi()

const toast = useToast()

const trilhas = ref<TrilhaResumoRead[]>([])
const loading = ref(true)

const base = grupoId ? `/grupos/${grupoId}/trilhas` : '/trilhas'

async function fetchTrilhas() {
  loading.value = true
  try {
    trilhas.value = await api('/progresso/trilhas')
  }
  catch {
    toast.add({ title: 'Não foi possível carregar as trilhas', color: 'error' })
  }
  loading.value = false
}

onMounted(fetchTrilhas)

// ------- status de cada trilha pro aluno
type Status = 'nao-iniciadas' | 'andamento' | 'concluidas'

function statusDa(trilha: TrilhaResumoRead): Status {
  if (trilha.total > 0 && trilha.concluidos === trilha.total) return 'concluidas'
  if (trilha.concluidos > 0) return 'andamento'
  return 'nao-iniciadas'
}

// mais recente primeiro, quem nunca mexeu vai pro fim
function compararAtividade(a: TrilhaResumoRead, b: TrilhaResumoRead) {
  const dataA = a.ultima_atividade_em ? new Date(a.ultima_atividade_em).getTime() : 0
  const dataB = b.ultima_atividade_em ? new Date(b.ultima_atividade_em).getTime() : 0
  return dataB - dataA
}

function listarPorStatus(status: Status) {
  const lista: TrilhaResumoRead[] = []
  for (const trilha of trilhas.value) {
    if (statusDa(trilha) === status) lista.push(trilha)
  }
  return lista
}

const emAndamento = computed(() => listarPorStatus('andamento').sort(compararAtividade))
const concluidas = computed(() => listarPorStatus('concluidas').sort(compararAtividade))

function tempoDoUltimoConteudo(trilha: TrilhaResumoRead) {
  if (!trilha.ultimo_conteudo_em) return 0
  return new Date(trilha.ultimo_conteudo_em).getTime()
}

// as q receberam conteudo por ultimo, so uma linha
const novidades = computed(() => {
  const lista: TrilhaResumoRead[] = []
  for (const trilha of trilhas.value) {
    if (trilha.ultimo_conteudo_em) lista.push(trilha)
  }
  lista.sort((a, b) => {
    const diferenca = tempoDoUltimoConteudo(b) - tempoDoUltimoConteudo(a)
    if (diferenca !== 0) return diferenca
    return a.titulo.localeCompare(b.titulo, 'pt-BR')
  })
  return lista.slice(0, 3)
})

// ------- filtros
const busca = ref('')
const tagFiltro = ref('')
const ordem = ref<'titulo' | 'novas' | 'curtas'>('titulo')
const soNaoIniciadas = ref(false)

const tagFiltroOptions = opcoesFiltroTagTrilha()

// clicar na tag q ja ta marcada desmarca
function alternarTag(valor: string) {
  tagFiltro.value = tagFiltro.value === valor ? '' : valor
}

const ordemOptions = [
  { label: 'Nome (A–Z)', value: 'titulo', icon: 'i-lucide-arrow-down-a-z' },
  { label: 'Conteúdo mais novo', value: 'novas', icon: 'i-lucide-sparkles' },
  { label: 'Mais curtas', value: 'curtas', icon: 'i-lucide-timer' },
] as const

// cada clique no botao passa pra proxima ordem
const ordemAtual = computed(() => {
  for (const opcao of ordemOptions) {
    if (opcao.value === ordem.value) return opcao
  }
  return ordemOptions[0]
})

function trocarOrdem() {
  let indice = 0
  for (let i = 0; i < ordemOptions.length; i++) {
    if (ordemOptions[i]?.value === ordem.value) indice = i
  }
  const proxima = ordemOptions[(indice + 1) % ordemOptions.length]
  if (proxima) ordem.value = proxima.value
}

const filtrosAtivos = computed(() => !!busca.value || !!tagFiltro.value || soNaoIniciadas.value)

function limparFiltros() {
  busca.value = ''
  tagFiltro.value = ''
  soNaoIniciadas.value = false
}

function compararOrdem(a: TrilhaResumoRead, b: TrilhaResumoRead) {
  // a q recebeu conteudo por ultimo primeiro
  if (ordem.value === 'novas') {
    const diferenca = tempoDoUltimoConteudo(b) - tempoDoUltimoConteudo(a)
    if (diferenca !== 0) return diferenca
  }
  // menos conteudo primeiro
  if (ordem.value === 'curtas' && a.total !== b.total) {
    return a.total - b.total
  }
  return a.titulo.localeCompare(b.titulo, 'pt-BR')
}

const trilhasFiltradas = computed(() => {
  const resultado: TrilhaResumoRead[] = []
  const buscaLower = busca.value.toLowerCase()

  for (const trilha of trilhas.value) {
    let descricao = ''
    if (trilha.descricao) descricao = trilha.descricao

    const bateBusca = trilha.titulo.toLowerCase().includes(buscaLower)
      || descricao.toLowerCase().includes(buscaLower)
    const bateTag = !tagFiltro.value || chaveDaTagTrilha(trilha.tag) === tagFiltro.value
    const bateStatus = !soNaoIniciadas.value || statusDa(trilha) === 'nao-iniciadas'

    if (bateBusca && bateTag && bateStatus) resultado.push(trilha)
  }
  resultado.sort(compararOrdem)
  return resultado
})

// ------- paginacao
const POR_PAGINA = 12
const pagina = ref(1)

watch([busca, tagFiltro, ordem, soNaoIniciadas], () => {
  pagina.value = 1
})

const trilhasDaPagina = computed(() => {
  const inicio = (pagina.value - 1) * POR_PAGINA
  return trilhasFiltradas.value.slice(inicio, inicio + POR_PAGINA)
})
</script>

<template>
  <div class="flex-1">
    <UButton
      v-if="grupoId"
      label="Voltar ao grupo"
      icon="i-lucide-arrow-left"
      variant="link"
      color="neutral"
      class="mb-3 px-0"
      :to="`/grupos/${grupoId}`"
    />

    <CamusBanner
      :titulo="grupoId ? 'Trilhas do grupo' : 'Trilhas'"
      descricao="Escolha uma trilha e siga os conteúdos na ordem."
      :imagem="grupoId ? '/papeis-de-parede/laranja/trilhas.webp' : '/papeis-de-parede/vermelho/trilhas.webp'"
    >
      <template
        v-if="!loading && trilhas.length"
        #acoes
      >
        <UBadge
          size="xl"
          icon="i-lucide-circle-check"
        >
          {{ concluidas.length }}/{{ trilhas.length }} concluídas
        </UBadge>
      </template>
    </CamusBanner>

    <!-- carregando -->
    <div
      v-if="loading"
      class="space-y-6"
    >
      <div class="grid gap-4 md:grid-cols-3">
        <USkeleton
          v-for="i in 3"
          :key="i"
          class="h-32 rounded-xl"
        />
      </div>
      <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <USkeleton
          v-for="i in 6"
          :key="i"
          class="h-64 rounded-xl"
        />
      </div>
    </div>

    <UCard
      v-else-if="!trilhas.length"
      class="text-center"
    >
      <UIcon
        name="i-lucide-route"
        class="size-10 text-primary"
      />
      <p class="mt-2 text-muted">
        Nenhuma trilha disponível ainda.
      </p>
    </UCard>

    <div
      v-else
      class="space-y-10"
    >
      <!-- fixo no topo, todas as que a pessoa ta fazendo, sem filtro e sem pagina -->
      <section
        v-if="emAndamento.length"
        class="space-y-3"
      >
        <h2 class="flex items-center gap-2 text-lg font-semibold text-highlighted">
          <UIcon
            name="i-lucide-play"
            class="size-5 text-primary"
          />
          Continuar de onde parou
        </h2>

        <UPageGrid>
          <TrilhaProgressoCard
            v-for="trilha in emAndamento"
            :key="trilha.id"
            :trilha="trilha"
            :to="`${base}/${trilha.id}`"
          />
        </UPageGrid>
      </section>

      <section
        v-if="novidades.length"
        class="space-y-3"
      >
        <h2 class="flex items-center gap-2 text-lg font-semibold text-highlighted">
          <UIcon
            name="i-lucide-sparkles"
            class="size-5 text-primary"
          />
          Conteúdo novo
        </h2>

        <UPageGrid>
          <TrilhaProgressoCard
            v-for="trilha in novidades"
            :key="trilha.id"
            :trilha="trilha"
            :to="`${base}/${trilha.id}`"
          />
        </UPageGrid>
      </section>

      <!-- todas as trilhas com filtro -->
      <section class="space-y-4">
        <h2 class="flex items-center gap-2 text-lg font-semibold text-highlighted">
          <UIcon
            name="i-lucide-compass"
            class="size-5 text-primary"
          />
          Todas as trilhas
        </h2>

        <div class="space-y-3">
          <div class="flex flex-wrap items-center gap-3 sm:flex-nowrap">
            <UInput
              v-model="busca"
              icon="i-lucide-search"
              placeholder="Buscar trilha..."
              class="w-full min-w-0 sm:flex-1"
            />

            <UButton
              :label="ordemAtual.label"
              :icon="ordemAtual.icon"
              :aria-label="`Ordenar por ${ordemAtual.label}, clique pra trocar`"
              color="neutral"
              variant="outline"
              class="shrink-0"
              @click="trocarOrdem"
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

          <!-- tags em botoes, com a cor de cada uma -->
          <div class="flex flex-wrap items-center gap-2">
            <UButton
              label="Todas as tags"
              size="sm"
              color="neutral"
              :variant="tagFiltro ? 'outline' : 'solid'"
              @click="tagFiltro = ''"
            />
            <UButton
              v-for="tag in tagFiltroOptions"
              :key="tag.value"
              :label="tag.label"
              size="sm"
              :color="tag.chip.color"
              :variant="tagFiltro === tag.value ? 'solid' : 'soft'"
              @click="alternarTag(tag.value)"
            />

            <USwitch
              v-model="soNaoIniciadas"
              label="Só as que ainda não comecei"
              class="sm:ms-auto"
            />
          </div>
        </div>

        <UCard
          v-if="!trilhasFiltradas.length"
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

        <template v-else>
          <UPageGrid>
            <TrilhaProgressoCard
              v-for="trilha in trilhasDaPagina"
              :key="trilha.id"
              :trilha="trilha"
              :to="`${base}/${trilha.id}`"
            />
          </UPageGrid>

          <div
            v-if="trilhasFiltradas.length > POR_PAGINA"
            class="flex justify-center pt-2"
          >
            <UPagination
              v-model:page="pagina"
              :total="trilhasFiltradas.length"
              :items-per-page="POR_PAGINA"
            />
          </div>
        </template>
      </section>
    </div>
  </div>
</template>
