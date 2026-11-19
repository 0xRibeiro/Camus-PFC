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

      <form
        v-if="podeEditar"
        class="flex flex-col gap-3 sm:flex-row sm:items-end"
        @submit.prevent="cadastrarPeixe"
      >
        <UFormField
          label="Espécie"
          required
          class="flex-1"
        >
          <UInputMenu
            v-model="especie"
            v-model:search-term="termo"
            :items="resultados"
            :loading="buscando"
            ignore-filter
            placeholder="Busque no iNaturalist, ex. palhaço"
            icon="i-lucide-search"
            class="w-full"
          >
            <template #empty>
              {{ termo.trim().length < 2 ? 'Digite pelo menos 2 letras' : 'Nenhuma espécie encontrada' }}
            </template>
          </UInputMenu>
        </UFormField>

        <UFormField
          label="Quantidade"
          required
          class="sm:w-32"
        >
          <UInputNumber
            v-model="quantidade"
            :min="1"
            :max="999"
            class="w-full"
          />
        </UFormField>

        <UFormField
          v-if="quantidade === 1"
          label="Nome do pet"
          class="flex-1"
        >
          <UInput
            v-model="apelido"
            placeholder="Ex. Nemo (opcional)"
            maxlength="50"
            class="w-full"
          />
        </UFormField>

        <UButton
          type="submit"
          label="Adicionar"
          icon="i-lucide-plus"
          :loading="cadastrando"
          :disabled="!especie || !quantidade"
          class="justify-center"
        />
      </form>
    </template>

    <UModal
      v-model:open="edicaoAberta"
      :title="editando?.apelido ?? editando?.nome_popular"
      :description="editando?.nome_cientifico"
      :dismissible="!salvando && !removendo"
    >
      <template #body>
        <form
          v-if="editando"
          class="space-y-4"
          @submit.prevent="salvarEdicao"
        >
          <!-- com 1 so muda o nome, com mais so a quantidade -->
          <UFormField
            v-if="editando.quantidade === 1"
            label="Nome do pet"
          >
            <UInput
              v-model="apelidoEdicao"
              placeholder="Sem nome"
              maxlength="50"
              class="w-full"
            />
          </UFormField>

          <UFormField
            v-else
            label="Quantidade"
          >
            <UInputNumber
              v-model="quantidadeEdicao"
              :min="1"
              :max="999"
              class="w-full"
            />
          </UFormField>

          <div class="flex flex-wrap justify-between gap-2">
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
              :disabled="removendo || (editando.quantidade > 1 && !quantidadeEdicao)"
            />
          </div>
        </form>
      </template>
    </UModal>
  </UCard>
</template>

<script setup lang="ts">
import type { InputMenuItem } from '@nuxt/ui'
import type { PeixeRead, PeixeUpdate } from '~/types/generated'
import { TAXONS_COLECAO } from '~/utils/inaturalista'

const props = withDefaults(defineProps<{ aquarioId: number, podeEditar?: boolean }>(), { podeEditar: true })

// so o q a gente usa do /taxa/autocomplete
interface TaxonInat {
  id: number
  name: string
  preferred_common_name?: string
  default_photo?: { square_url?: string }
}

type OpcaoEspecie = InputMenuItem & { id: number, label: string }

const api = useApi()
const inat = useInat()
const toast = useToast()

const carregando = ref(true)
const cadastrando = ref(false)
const peixes = ref<PeixeRead[] | null>(null)

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
  // qnd escolhe um item o termo vira o label, n precisa buscar dnv
  if (busca.length < 2 || busca === especie.value?.label) return

  buscando.value = true
  try {
    const resposta = await inat<{ results?: TaxonInat[] }>('/taxa/autocomplete', {
      query: { q: busca, taxon_id: TAXONS_COLECAO, locale: 'pt-BR', is_active: true, per_page: 8 },
    })

    const opcoes: OpcaoEspecie[] = []
    for (const taxon of resposta.results ?? []) {
      const nome = taxon.preferred_common_name ?? taxon.name
      opcoes.push({
        id: taxon.id,
        label: nome.charAt(0).toUpperCase() + nome.slice(1),
        description: taxon.name,
        avatar: taxon.default_photo?.square_url ? { src: taxon.default_photo.square_url, alt: nome } : undefined,
      })
    }
    resultados.value = opcoes
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
    especie.value = undefined
    termo.value = ''
    resultados.value = []
    quantidade.value = 1
    apelido.value = ''
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
  if (!editando.value || salvando.value) return

  let body: PeixeUpdate
  if (editando.value.quantidade === 1) {
    body = { apelido: apelidoEdicao.value.trim() || null }
  }
  else {
    if (!quantidadeEdicao.value) return
    body = { quantidade: quantidadeEdicao.value }
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
