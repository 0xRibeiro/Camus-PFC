<script setup lang="ts">
import type { JSONContent } from '@tiptap/core'
import type { DocumentoLegalHistorico, DocumentoLegalPublico, TipoDocumentoLegal } from '~/types/generated'

const props = defineProps<{
  tipo: TipoDocumentoLegal
  titulo: string
}>()

const route = useRoute()
const router = useRouter()
const api = useApi()

const documento = ref<DocumentoLegalPublico | null>(null)
const historico = ref<DocumentoLegalHistorico[]>([])
const loading = ref(true)
const naoPublicado = ref(false)

// sem ?versao e a atual
const versaoPedida = computed(() => {
  const valor = Number(route.query.versao)
  if (Number.isInteger(valor) && valor > 0) return valor
  return null
})

const versaoAtual = computed(() => historico.value[0]?.versao ?? null)
const vendoAntiga = computed(() => documento.value !== null && documento.value.versao !== versaoAtual.value)

function formatarData(data: string): string {
  return new Date(data).toLocaleDateString('pt-BR')
}

const opcoesVersao = computed(() => {
  const opcoes = []
  for (const item of historico.value) {
    let label = `Versão ${item.versao} — ${formatarData(item.publicado_em)}`
    if (item.versao === versaoAtual.value) label += ' (atual)'
    opcoes.push({ label, value: item.versao })
  }
  return opcoes
})

const versaoSelecionada = computed({
  get: () => documento.value?.versao,
  set: (versao) => {
    const query = { ...route.query }
    if (versao === versaoAtual.value) delete query.versao
    else query.versao = String(versao)
    router.replace({ query })
  },
})

async function fetchDocumento() {
  loading.value = true
  naoPublicado.value = false
  try {
    const url = versaoPedida.value
      ? `/documentos-legais/${props.tipo}/versoes/${versaoPedida.value}`
      : `/documentos-legais/${props.tipo}/atual`

    const [doc, lista] = await Promise.all([
      api(url),
      api(`/documentos-legais/${props.tipo}`),
    ])
    documento.value = doc
    historico.value = lista
  }
  catch {
    documento.value = null
    naoPublicado.value = true
  }
  loading.value = false
}

watch(versaoPedida, fetchDocumento)
onMounted(fetchDocumento)
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold mb-1">
      {{ titulo }} — Camus
    </h1>

    <div
      v-if="loading"
      class="flex justify-center py-12"
    >
      <UIcon
        name="i-lucide-loader-circle"
        class="size-6 animate-spin"
      />
    </div>

    <p
      v-else-if="naoPublicado"
      class="text-sm text-muted mt-4"
    >
      {{ versaoPedida ? 'Versão não encontrada.' : 'Este documento ainda não está disponível.' }}
    </p>

    <template v-else-if="documento">
      <div class="flex flex-wrap items-center justify-between gap-3 mb-6">
        <p class="text-sm text-muted">
          Última atualização: {{ formatarData(documento.publicado_em) }}
        </p>

        <USelect
          v-if="historico.length > 1"
          v-model="versaoSelecionada"
          :items="opcoesVersao"
          size="sm"
          class="w-64"
        />
      </div>

      <UAlert
        v-if="vendoAntiga"
        color="warning"
        variant="soft"
        icon="i-lucide-history"
        :title="`Você está vendo a versão ${documento.versao}, que não é mais a atual.`"
        :actions="[{ label: 'Ver a atual', color: 'warning', variant: 'outline', onClick: () => { versaoSelecionada = versaoAtual ?? undefined } }]"
        class="mb-6"
      />

      <EditorLeitura
        :conteudo="documento.conteudo as JSONContent"
        :ui="{ base: 'p-0 sm:px-0', content: '' }"
      />
    </template>
  </div>
</template>
