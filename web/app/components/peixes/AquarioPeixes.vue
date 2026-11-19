<template>
  <UCard :ui="{ body: 'space-y-4' }">
    <template #header>
      <div class="flex items-center gap-3">
        <div class="flex size-10 items-center justify-center rounded-full bg-sky-500/10 text-sky-500 ring ring-sky-500/25 ring-inset">
          <UIcon
            name="i-lucide-fish"
            class="size-5"
          />
        </div>

        <div>
          <h2 class="font-medium">
            Peixes
          </h2>
          <p
            v-if="peixes"
            class="text-xs text-muted"
          >
            {{ totalPeixes }} {{ totalPeixes === 1 ? 'peixe' : 'peixes' }} no aquário
          </p>
        </div>

        <UButton
          v-if="podeEditar && peixes"
          label="Adicionar peixe"
          icon="i-lucide-plus"
          class="ml-auto"
          @click="abrirCadastro"
        />
      </div>
    </template>

    <USkeleton
      v-if="carregando"
      class="h-40 w-full rounded-xl"
    />

    <div
      v-else-if="peixes === null"
      class="space-y-2"
    >
      <UAlert
        color="error"
        title="Não foi possível carregar os peixes"
      />

      <UButton
        label="Tentar novamente"
        variant="outline"
        @click="carregarPeixes"
      />
    </div>

    <template v-else>
      <!-- agua com degrade -->
      <div class="relative flex min-h-40 items-center justify-center overflow-hidden rounded-xl bg-linear-to-b from-sky-400/15 via-sky-500/15 to-blue-700/30 p-6 ring ring-sky-500/30 ring-inset">
        <p
          v-if="!peixes.length"
          class="text-sm text-muted"
        >
          Seu aquário ainda está vazio.
        </p>

        <ul
          v-else
          class="flex w-full flex-wrap justify-center gap-x-6 gap-y-5"
        >
          <li
            v-for="peixe in peixes"
            :key="peixe.id"
            class="w-28"
          >
            <component
              :is="podeEditar ? 'button' : 'div'"
              :type="podeEditar ? 'button' : undefined"
              class="group flex w-full flex-col items-center rounded-xl p-1 text-center outline-primary focus-visible:outline-2"
              :class="podeEditar && 'cursor-pointer'"
              @click="podeEditar && abrirEdicao(peixe)"
            >
              <span class="relative block">
                <img
                  v-if="peixe.foto_url"
                  :src="peixe.foto_url"
                  :alt="peixe.nome_popular"
                  :title="peixe.foto_credito ?? undefined"
                  loading="lazy"
                  class="size-20 rounded-2xl object-cover shadow-sm ring-2 ring-white/70 transition group-hover:scale-105"
                >

                <span
                  v-else
                  class="flex size-20 items-center justify-center rounded-2xl bg-sky-500/15 text-sky-500 ring-2 ring-white/70"
                >
                  <UIcon
                    name="i-lucide-fish"
                    class="size-8"
                  />
                </span>

                <UBadge
                  v-if="peixe.quantidade > 1"
                  :label="`×${peixe.quantidade}`"
                  color="info"
                  size="lg"
                  class="absolute -top-2 -right-2 rounded-full"
                />
              </span>

              <!-- com 1 e nome mostra o nome do pet em cima -->
              <template v-if="peixe.quantidade === 1 && peixe.apelido">
                <p class="mt-2 w-full break-words font-medium">
                  {{ peixe.apelido }}
                </p>
                <p class="w-full break-words text-xs text-muted">
                  {{ peixe.nome_popular }}
                </p>
              </template>

              <p
                v-else
                class="mt-2 w-full break-words text-sm font-medium"
              >
                {{ peixe.nome_popular }}
              </p>
            </component>
          </li>
        </ul>
      </div>

    </template>

    <UModal
      v-model:open="cadastroAberto"
      title="Adicionar peixe"
      :description="especie ? 'Diga quantos você tem' : 'Busque a espécie no iNaturalist'"
      :dismissible="!cadastrando"
      :ui="{ content: 'sm:max-w-3xl' }"
    >
      <template #body>
        <!-- passo 1: busca -->
        <div
          v-if="!especie"
          class="space-y-4"
        >
          <UInput
            v-model="termo"
            placeholder="Ex. palhaço, neon, betta..."
            icon="i-lucide-search"
            size="xl"
            :loading="buscando"
            autofocus
            class="w-full"
          />

          <div class="h-[50vh] overflow-y-auto">
            <p
              v-if="termo.trim().length < 2"
              class="py-16 text-center text-sm text-muted"
            >
              Digite o nome do peixe pra buscar.
            </p>

            <p
              v-else-if="!buscando && !resultados.length"
              class="py-16 text-center text-sm text-muted"
            >
              Nenhuma espécie encontrada.
            </p>

            <ul
              v-else
              class="grid grid-cols-2 gap-3 sm:grid-cols-4"
            >
              <li
                v-for="opcao in resultados"
                :key="opcao.id"
              >
                <button
                  type="button"
                  class="w-full cursor-pointer overflow-hidden rounded-xl text-left ring ring-default transition hover:ring-2 hover:ring-primary"
                  @click="especie = opcao"
                >
                  <USkeleton
                    v-if="carregandoFoto(opcao.id)"
                    class="aspect-square w-full rounded-none"
                  />

                  <img
                    v-else-if="fotos[opcao.id]"
                    :src="fotos[opcao.id]?.medium_url"
                    :alt="opcao.nome"
                    :title="fotos[opcao.id]?.attribution"
                    loading="lazy"
                    class="aspect-square w-full object-cover"
                  >

                  <span
                    v-else
                    class="flex aspect-square w-full items-center justify-center bg-sky-500/10 text-sky-500"
                  >
                    <UIcon
                      name="i-lucide-fish"
                      class="size-10"
                    />
                  </span>

                  <span class="block p-2">
                    <span class="block truncate text-sm font-medium">{{ opcao.nome }}</span>
                    <span class="block truncate text-xs text-muted italic">{{ opcao.nome_cientifico }}</span>
                  </span>
                </button>
              </li>
            </ul>
          </div>
        </div>

        <!-- passo 2: quantidade e nome -->
        <form
          v-else
          class="grid gap-6 sm:grid-cols-[16rem_1fr]"
          @submit.prevent="cadastrarPeixe"
        >
          <div class="overflow-hidden rounded-xl ring ring-default">
            <USkeleton
              v-if="carregandoFoto(especie.id)"
              class="aspect-square w-full rounded-none"
            />

            <img
              v-else-if="fotos[especie.id]"
              :src="fotos[especie.id]?.medium_url"
              :alt="especie.nome"
              :title="fotos[especie.id]?.attribution"
              class="aspect-square w-full object-cover"
            >

            <span
              v-else
              class="flex aspect-square w-full items-center justify-center bg-sky-500/10 text-sky-500"
            >
              <UIcon
                name="i-lucide-fish"
                class="size-12"
              />
            </span>
          </div>

          <div class="flex flex-col gap-4">
            <div>
              <p class="text-lg font-medium">
                {{ especie.nome }}
              </p>
              <p class="text-sm text-muted italic">
                {{ especie.nome_cientifico }}
              </p>
            </div>

            <UFormField
              label="Quantidade"
              required
            >
              <UInputNumber
                v-model="quantidade"
                :min="1"
                :max="999"
                class="w-40"
              />
            </UFormField>

            <!-- com mais de 1 fica travado, n some -->
            <UFormField
              label="Nome do pet"
              :description="quantidade === 1 ? 'Opcional' : 'Só dá pra dar nome quando é 1 peixe'"
            >
              <UInput
                v-model="apelido"
                placeholder="Ex. Nemo"
                maxlength="50"
                :disabled="quantidade !== 1"
                class="w-full"
              />
            </UFormField>

            <div class="mt-auto flex flex-wrap justify-between gap-2">
              <UButton
                label="Trocar espécie"
                icon="i-lucide-arrow-left"
                variant="ghost"
                color="neutral"
                :disabled="cadastrando"
                @click="especie = undefined"
              />

              <UButton
                type="submit"
                label="Adicionar"
                icon="i-lucide-plus"
                :loading="cadastrando"
                :disabled="!quantidade"
              />
            </div>
          </div>
        </form>
      </template>
    </UModal>

    <UModal
      v-model:open="edicaoAberta"
      title="Editar peixe"
      :dismissible="!salvando && !removendo"
      :ui="{ content: 'sm:max-w-3xl' }"
    >
      <template #body>
        <!-- msm layout do passo 2 do cadastro -->
        <form
          v-if="editando"
          class="grid gap-6 sm:grid-cols-[16rem_1fr]"
          @submit.prevent="salvarEdicao"
        >
          <div class="overflow-hidden rounded-xl ring ring-default">
            <img
              v-if="editando.foto_url"
              :src="editando.foto_url"
              :alt="editando.nome_popular"
              :title="editando.foto_credito ?? undefined"
              class="aspect-square w-full object-cover"
            >

            <span
              v-else
              class="flex aspect-square w-full items-center justify-center bg-sky-500/10 text-sky-500"
            >
              <UIcon
                name="i-lucide-fish"
                class="size-12"
              />
            </span>
          </div>

          <div class="flex flex-col gap-4">
            <div>
              <p class="text-lg font-medium">
                {{ editando.nome_popular }}
              </p>
              <p class="text-sm text-muted italic">
                {{ editando.nome_cientifico }}
              </p>
            </div>

            <UFormField
              label="Quantidade"
              required
            >
              <UInputNumber
                v-model="quantidadeEdicao"
                :min="1"
                :max="999"
                class="w-40"
              />
            </UFormField>

            <UFormField
              label="Nome do pet"
              :description="quantidadeEdicao === 1 ? 'Opcional' : 'Só dá pra dar nome quando é 1 peixe'"
            >
              <UInput
                v-model="apelidoEdicao"
                placeholder="Ex. Nemo"
                maxlength="50"
                :disabled="quantidadeEdicao !== 1"
                class="w-full"
              />
            </UFormField>

            <div class="mt-auto flex flex-wrap justify-between gap-2">
              <UButton
                label="Remover do aquário"
                icon="i-lucide-trash-2"
                color="error"
                variant="ghost"
                :loading="removendo"
                :disabled="salvando"
                @click="removerPeixe"
              />

              <UButton
                type="submit"
                label="Salvar"
                :loading="salvando"
                :disabled="removendo || !quantidadeEdicao"
              />
            </div>
          </div>
        </form>
      </template>
    </UModal>
  </UCard>
</template>

<script setup lang="ts">
import type { PeixeRead, PeixeUpdate } from '~/types/generated'
import type { TaxonInat } from '~/utils/inaturalista'
import { TAXONS_COLECAO } from '~/utils/inaturalista'

const props = withDefaults(defineProps<{ aquarioId: number, podeEditar?: boolean }>(), { podeEditar: true })

interface OpcaoEspecie {
  id: number
  nome: string
  nome_cientifico: string
}

const api = useApi()
const inat = useInat()
const toast = useToast()
const { fotos, carregar: carregarFotos, carregando: carregandoFoto } = useFotosLivres()

const carregando = ref(true)
const cadastrando = ref(false)
const peixes = ref<PeixeRead[] | null>(null)

const cadastroAberto = ref(false)
const termo = ref('')
const buscando = ref(false)
const resultados = ref<OpcaoEspecie[]>([])
const especie = ref<OpcaoEspecie>()
const quantidade = ref<number | null>(1)
const apelido = ref('')

const editando = ref<PeixeRead | null>(null)
const edicaoAberta = ref(false)
const apelidoEdicao = ref('')
const quantidadeEdicao = ref<number | null>(null)
const salvando = ref(false)
const removendo = ref(false)

const totalPeixes = computed(() => {
  let total = 0
  for (const peixe of peixes.value ?? []) total += peixe.quantidade
  return total
})

async function carregarPeixes() {
  carregando.value = true

  try {
    peixes.value = await api(`/aquarios/${props.aquarioId}/peixes`)
  }
  catch {
    peixes.value = null
  }
  finally {
    carregando.value = false
  }
}

// msm grupos da colecao, nome popular em pt
async function buscarEspecies() {
  const busca = termo.value.trim()
  if (busca.length < 2) {
    resultados.value = []
    return
  }

  buscando.value = true
  try {
    const resposta = await inat<{ results?: TaxonInat[] }>('/taxa/autocomplete', {
      query: { q: busca, taxon_id: TAXONS_COLECAO, locale: 'pt-BR', is_active: true, per_page: 12 },
    })

    const opcoes: OpcaoEspecie[] = []
    for (const taxon of resposta.results ?? []) {
      const nome = taxon.preferred_common_name ?? taxon.name
      opcoes.push({
        id: taxon.id,
        nome: nome.charAt(0).toUpperCase() + nome.slice(1),
        nome_cientifico: taxon.name,
      })
    }
    resultados.value = opcoes
    // n espera, os cards ficam no skeleton ate a foto chegar
    carregarFotos(resposta.results ?? [])
  }
  catch {
    toast.add({ title: 'Não foi possível buscar no iNaturalist', color: 'error' })
  }
  finally {
    buscando.value = false
  }
}

// espera parar de digitar pra n estourar o limite do iNat
watchDebounced(termo, buscarEspecies, { debounce: 350 })

// sempre abre limpo no passo da busca
function abrirCadastro() {
  especie.value = undefined
  termo.value = ''
  resultados.value = []
  quantidade.value = 1
  apelido.value = ''
  cadastroAberto.value = true
}

async function cadastrarPeixe() {
  if (cadastrando.value || peixes.value === null || !especie.value || !quantidade.value) return

  cadastrando.value = true

  try {
    const peixe: PeixeRead = await api(`/aquarios/${props.aquarioId}/peixes`, {
      method: 'POST',
      body: {
        taxon_id: especie.value.id,
        quantidade: quantidade.value,
        apelido: quantidade.value === 1 && apelido.value.trim() ? apelido.value.trim() : null,
      },
    })

    peixes.value.push(peixe)
    cadastroAberto.value = false
    toast.add({ title: 'Peixe adicionado', color: 'success' })
  }
  catch {
    toast.add({ title: 'Não foi possível adicionar o peixe', color: 'error' })
  }
  finally {
    cadastrando.value = false
  }
}

function abrirEdicao(peixe: PeixeRead) {
  editando.value = peixe
  apelidoEdicao.value = peixe.apelido ?? ''
  quantidadeEdicao.value = peixe.quantidade
  edicaoAberta.value = true
}

function trocarNaLista(peixe: PeixeRead) {
  if (!peixes.value) return

  const indice = peixes.value.findIndex(item => item.id === peixe.id)
  if (indice !== -1) peixes.value[indice] = peixe
}

async function salvarEdicao() {
  if (!editando.value || salvando.value || !quantidadeEdicao.value) return

  // com mais de 1 o back apaga o nome
  const body: PeixeUpdate = {
    quantidade: quantidadeEdicao.value,
    apelido: quantidadeEdicao.value === 1 ? apelidoEdicao.value.trim() || null : null,
  }

  salvando.value = true

  try {
    const peixe: PeixeRead = await api(`/aquarios/${props.aquarioId}/peixes/${editando.value.id}`, { method: 'PATCH', body })
    trocarNaLista(peixe)
    edicaoAberta.value = false
    toast.add({ title: 'Peixe atualizado', color: 'success' })
  }
  catch {
    toast.add({ title: 'Não foi possível atualizar o peixe', color: 'error' })
  }
  finally {
    salvando.value = false
  }
}

async function removerPeixe() {
  if (!editando.value || removendo.value) return

  const id = editando.value.id
  removendo.value = true

  try {
    await api(`/aquarios/${props.aquarioId}/peixes/${id}`, { method: 'DELETE' })
    if (peixes.value) peixes.value = peixes.value.filter(peixe => peixe.id !== id)
    edicaoAberta.value = false
    toast.add({ title: 'Peixe removido', color: 'success' })
  }
  catch {
    toast.add({ title: 'Não foi possível remover o peixe', color: 'error' })
  }
  finally {
    removendo.value = false
  }
}

onMounted(carregarPeixes)
</script>
