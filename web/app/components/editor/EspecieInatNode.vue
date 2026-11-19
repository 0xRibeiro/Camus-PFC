<script setup lang="ts">
import type { NodeViewProps } from '@tiptap/vue-3'
import { NodeViewWrapper } from '@tiptap/vue-3'
import type { TaxonInat } from '~/utils/inaturalista'

const props = defineProps<NodeViewProps>()

// mesmo formato q a colecao recebe da api do iNat
interface Peixe extends TaxonInat {
  observations_count?: number
  wikipedia_url?: string
}

interface RespostaTaxa {
  results?: Peixe[]
}

const inat = useInat()
const { fotos, carregar: carregarFotos, carregando: carregandoFoto } = useFotosLivres()
const busca = ref('')
const peixes = ref<Peixe[]>([])
const carregando = ref(false)
const erro = ref('')

// msm filtro da colecao: so peixes e so especie
async function buscarPeixes() {
  const termo = busca.value.trim()
  if (!termo) return

  carregando.value = true
  erro.value = ''
  try {
    const resposta = await inat<RespostaTaxa>('/taxa', {
      query: {
        q: termo,
        taxon_id: 47178,
        rank: 'species',
        per_page: 6,
        order: 'desc',
        order_by: 'observations_count',
      },
    })
    peixes.value = resposta.results ?? []
    carregarFotos(peixes.value)
    if (peixes.value.length === 0) erro.value = 'Nenhum peixe encontrado'
  }
  catch {
    erro.value = 'Não foi possível buscar no iNaturalist'
  }
  carregando.value = false
}

// grava a copia dos dados no node, dai em diante vira card
function escolherPeixe(peixe: Peixe) {
  props.updateAttributes({
    taxonId: peixe.id,
    nome: peixe.name,
    nomePopular: peixe.preferred_common_name ?? null,
    foto: fotos.value[peixe.id]?.medium_url ?? null,
    observacoes: peixe.observations_count ?? 0,
    wikipedia: peixe.wikipedia_url ?? null,
  })
}
</script>

<template>
  <NodeViewWrapper>
    <EditorEspecieInatCard
      v-if="node.attrs.taxonId"
      :nome="node.attrs.nome"
      :nome-popular="node.attrs.nomePopular"
      :foto="node.attrs.foto"
      :observacoes="node.attrs.observacoes"
      :wikipedia="node.attrs.wikipedia"
    />

    <!-- busca so aparece enquanto o author n escolheu a especie -->
    <div
      v-else-if="editor.isEditable"
      class="not-prose rounded-xl border border-dashed border-default p-4 my-4 space-y-3"
      contenteditable="false"
    >
      <div class="flex items-center gap-2 text-sm font-medium text-primary">
        <UIcon
          name="i-lucide-fish"
          class="size-4"
        />
        Espécie do iNaturalist
      </div>

      <div class="flex flex-wrap gap-2">
        <UInput
          v-model="busca"
          icon="i-lucide-search"
          placeholder="Nome popular ou científico do peixe"
          class="min-w-0 flex-1 basis-40"
          @keydown.enter.prevent="buscarPeixes"
        />
        <UButton
          label="Buscar"
          :loading="carregando"
          @click="buscarPeixes"
        />
      </div>

      <p
        v-if="erro"
        class="text-xs text-error"
      >
        {{ erro }}
      </p>

      <div
        v-if="peixes.length"
        class="grid gap-2 sm:grid-cols-2"
      >
        <button
          v-for="peixe in peixes"
          :key="peixe.id"
          type="button"
          class="flex items-center gap-3 rounded-lg border border-default p-2 text-left hover:bg-elevated disabled:cursor-wait"
          :disabled="carregandoFoto(peixe.id)"
          @click="escolherPeixe(peixe)"
        >
          <!-- espera a foto livre chegar pq ela vai salva no card -->
          <USkeleton
            v-if="carregandoFoto(peixe.id)"
            class="size-10 shrink-0 rounded"
          />
          <img
            v-else-if="fotos[peixe.id]"
            :src="fotos[peixe.id]?.medium_url"
            :alt="peixe.name"
            :title="fotos[peixe.id]?.attribution"
            class="size-10 shrink-0 rounded object-cover"
          >
          <div class="min-w-0">
            <p class="truncate text-sm font-medium">
              {{ peixe.preferred_common_name || peixe.name }}
            </p>
            <p class="truncate text-xs italic text-muted">
              {{ peixe.name }}
            </p>
          </div>
        </button>
      </div>
    </div>
  </NodeViewWrapper>
</template>
