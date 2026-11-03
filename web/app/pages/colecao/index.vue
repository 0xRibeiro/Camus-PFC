<template>
  <div class="mx-auto max-w-5xl space-y-6">
    <UPageHeader
      title="Coleção de peixes"
      description="Procure uma espécie no iNaturalist."
    >
      <template #headline>
        <div class="flex items-center gap-2 text-sm font-medium text-primary">
          <UIcon
            name="i-lucide-fish"
            class="size-4"
          />
          Coleção
        </div>
      </template>
    </UPageHeader>

    <UCard>
      <div class="flex flex-col gap-3 sm:flex-row">
        <UInput
          v-model="busca"
          icon="i-lucide-search"
          placeholder="Digite um nome de peixe"
          class="w-full"
          :disabled="carregando"
          @keyup.enter="buscarPeixes"
        />

        <UButton
          label="Buscar"
          icon="i-lucide-search"
          :loading="carregando"
          class="sm:shrink-0"
          @click="buscarPeixes"
        />
      </div>
    </UCard>

    <UAlert
      v-if="mensagemDeErro"
      color="error"
      variant="subtle"
      icon="i-lucide-circle-alert"
      title="Ocorreu um erro"
      :description="mensagemDeErro"
    />

    <div
      v-if="carregando"
      class="grid gap-4 sm:grid-cols-2"
    >
      <UCard
        v-for="indice in 6"
        :key="indice"
      >
        <USkeleton class="aspect-video w-full rounded-lg" />

        <div class="mt-4 space-y-2">
          <USkeleton class="h-5 w-2/3" />
          <USkeleton class="h-4 w-1/2" />
        </div>
      </UCard>
    </div>

    <UEmpty
      v-else-if="!peixes.length && !mensagemDeErro"
      icon="i-lucide-fish"
      title="Nada encontrado"
      description="Tente o nome comum do peixe ou o nome científico."
    />

    <section
      v-else-if="peixes.length && !mensagemDeErro"
      class="grid gap-6 lg:grid-cols-[minmax(0,1fr)_minmax(18rem,24rem)]"
    >
      <div>
        <p class="mb-3 text-sm text-muted">
          Exibindo {{ inicioResultado }} a {{ fimResultado }}
          de {{ totalResultados.toLocaleString('pt-BR') }}
          {{ totalResultados === 1 ? 'espécie' : 'espécies' }}
          para “{{ termoPesquisado }}”
        </p>

        <div class="grid gap-4 sm:grid-cols-2">
          <UCard
            v-for="peixe in peixes"
            :key="peixe.id"
            class="cursor-pointer"
            :class="peixeSelecionado?.id === peixe.id ? 'border-primary ring-1 ring-primary' : ''"
            :aria-label="`Selecionar ${peixe.preferred_common_name || peixe.name}`"
            @click="selecionarPeixe(peixe)"
          >
            <img
              v-if="peixe.default_photo?.medium_url"
              :src="peixe.default_photo.medium_url"
              :alt="`Imagem de ${peixe.preferred_common_name || peixe.name}`"
              class="aspect-video w-full rounded-lg object-cover"
            >

            <div
              v-else
              class="flex aspect-video items-center justify-center rounded-lg bg-elevated text-muted"
            >
              <UIcon
                name="i-lucide-image-off"
                class="size-8"
              />
            </div>

            <div class="mt-4 min-w-0">
              <h2 class="truncate font-semibold text-highlighted">
                {{ peixe.preferred_common_name || peixe.name }}
              </h2>

              <p class="mt-1 truncate text-sm italic text-muted">
                {{ peixe.name }}
              </p>
            </div>
          </UCard>
        </div>
      </div>

      <UCard>
        <template #header>
          <div class="flex items-center justify-between gap-3">
            <h2 class="font-semibold text-highlighted">
              Peixe Selecionado
            </h2>

            <UIcon
              name="i-lucide-eye"
              class="size-5 text-primary"
            />
          </div>
        </template>

        <template v-if="peixeSelecionado">
          <img
            v-if="peixeSelecionado.default_photo?.square_url"
            :src="peixeSelecionado.default_photo.square_url"
            :alt="`Imagem de ${peixeSelecionado.preferred_common_name || peixeSelecionado.name}`"
            class="aspect-square w-full rounded-lg object-cover"
          >

          <div
            v-else
            class="flex aspect-square items-center justify-center rounded-lg bg-elevated text-muted"
          >
            <UIcon
              name="i-lucide-fish"
              class="size-12"
            />
          </div>

          <div class="mt-4 space-y-3">
            <div>
              <p class="text-lg font-semibold text-highlighted">
                {{ peixeSelecionado.preferred_common_name || peixeSelecionado.name }}
              </p>

              <p class="text-sm italic text-muted">
                {{ peixeSelecionado.name }}
              </p>
            </div>

            <div class="flex flex-wrap gap-2">
              <UBadge
                color="neutral"
                variant="subtle"
              >
                {{ new Intl.NumberFormat('pt-BR').format(peixeSelecionado.observations_count ?? 0) }}
                observações
              </UBadge>

              <UBadge
                v-if="peixeSelecionado.rank"
                color="primary"
                variant="subtle"
              >
                {{ peixeSelecionado.rank }}
              </UBadge>
            </div>

            <UButton
              v-if="peixeSelecionado.wikipedia_url"
              label="Ver mais informações"
              icon="i-lucide-external-link"
              variant="outline"
              block
              :to="peixeSelecionado.wikipedia_url"
              target="_blank"
            />
          </div>
        </template>

        <UEmpty
          v-else
          icon="i-lucide-mouse-pointer-click"
          title="Escolha um peixe"
          description="Clique em um dos resultados para ver mais detalhes."
        />
      </UCard>
    </section>

    <div
      v-if="totalResultados > itensPorPagina && !mensagemDeErro"
      class="flex flex-wrap items-center justify-between gap-3"
    >
      <p class="text-sm text-muted">
        Página {{ pagina }} de {{ totalPaginas }}
      </p>

      <UPagination
        :page="pagina"
        :items-per-page="itensPorPagina"
        :total="totalResultados"
        :disabled="carregando"
        @update:page="mudarPagina"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { useConquistasStore } from '~/stores/conquistas'

definePageMeta({ middleware: 'role' })

interface FotosPeixe {
  medium_url?: string
  square_url?: string
}

interface Peixe {
  id: number
  name: string
  preferred_common_name?: string
  rank?: string
  observations_count?: number
  wikipedia_url?: string
  default_photo?: FotosPeixe
}

interface RespostaTaxa {
  total_results: number
  page?: number
  results?: Peixe[]
}

const inat = useInat()
const conquistas = useConquistasStore()

const busca = ref('')
const termoPesquisado = ref('')
const peixes = ref<Peixe[]>([])
const peixeSelecionado = ref<Peixe | null>(null)
const carregando = ref(false)
const mensagemDeErro = ref('')

const pagina = ref(1)
const itensPorPagina = 20
const totalResultados = ref(0)

const totalPaginas = computed(() => Math.ceil(totalResultados.value / itensPorPagina))
const inicioResultado = computed(() => peixes.value.length ? (pagina.value - 1) * itensPorPagina + 1 : 0)
const fimResultado = computed(() => peixes.value.length ? inicioResultado.value + peixes.value.length - 1 : 0)

// uma nova pesquisa sempre começa na primeira página
async function buscarPeixes() {
  const termo = busca.value.trim()
  if (!termo || carregando.value) return

  termoPesquisado.value = termo
  pagina.value = 1
  totalResultados.value = 0

  await carregarPagina(1)
}

async function mudarPagina(novaPagina: number) {
  if (novaPagina === pagina.value) return

  await carregarPagina(novaPagina)
}

async function carregarPagina(paginaSolicitada: number) {
  if (carregando.value || !termoPesquisado.value) return

  carregando.value = true
  mensagemDeErro.value = ''
  peixeSelecionado.value = null

  try {
    const resposta = await inat<RespostaTaxa>('/taxa', {
      query: {
        q: termoPesquisado.value,
        taxon_id: 47178,
        rank: 'species',
        page: paginaSolicitada,
        per_page: itensPorPagina,
        order: 'desc',
        order_by: 'observations_count',
      },
    })

    peixes.value = resposta.results ?? []
    totalResultados.value = resposta.total_results ?? peixes.value.length
    pagina.value = resposta.page ?? paginaSolicitada
  }
  catch {
    peixes.value = []
    totalResultados.value = 0
    mensagemDeErro.value = 'Não foi possível carregar os peixes. Tente novamente.'
  }
  finally {
    carregando.value = false
  }

  // mantém a conquista da pesquisa com resultados
  if (peixes.value.length > 0) {
    await conquistas.desbloquearConquista(6).catch(() => {})
  }
}

async function selecionarPeixe(peixe: Peixe) {
  peixeSelecionado.value = peixe

  await conquistas.desbloquearConquista(7).catch(() => {})
}
</script>
