<script setup lang="ts">
import { VueDraggable } from 'vue-draggable-plus'
import type { AlternativaRead, QuestaoRead } from '~/types/generated'

const props = defineProps<{
  conteudoId: number
}>()

// avisa a pagina q o quiz mudou no banco, ela decide se sobe a versao
const emit = defineEmits<{
  alterou: []
}>()

const toast = useToast()

// estado local de cada pergunta, id null = ainda n foi pro banco
interface AlternativaLocal {
  id: number | null
  texto: string
  correta: boolean
}

interface QuestaoLocal {
  chave: string
  id: number | null
  enunciado: string
  alternativas: AlternativaLocal[]
  removidas: number[]
  alterada: boolean
  salvando: boolean
}

const questoes = ref<QuestaoLocal[]>([])
const loading = ref(true)
let contadorChave = 0

function novaChave() {
  contadorChave += 1
  return `q${contadorChave}`
}

/* carregar */

async function fetchQuiz() {
  loading.value = true
  try {
    const api = useApi()
    const questoesRes = await api('/questoes', { query: { conteudo_id: props.conteudoId } })
    const ordenadas = questoesRes.data.sort((a: QuestaoRead, b: QuestaoRead) => a.ordem - b.ordem)

    const lista: QuestaoLocal[] = []
    for (const questao of ordenadas as QuestaoRead[]) {
      const alternativasRes = await api('/alternativas', { query: { questao_id: questao.id } })

      const alternativas: AlternativaLocal[] = []
      for (const alternativa of alternativasRes.data as AlternativaRead[]) {
        alternativas.push({ id: alternativa.id, texto: alternativa.texto, correta: alternativa.correta })
      }

      lista.push({
        chave: novaChave(),
        id: questao.id,
        enunciado: questao.enunciado,
        alternativas,
        removidas: [],
        alterada: false,
        salvando: false,
      })
    }
    questoes.value = lista
  }
  catch {
    toast.add({ title: 'Não foi possível carregar o quiz', color: 'error' })
  }
  loading.value = false
}

onMounted(fetchQuiz)

/* editar local */

function adicionarPergunta() {
  questoes.value.push({
    chave: novaChave(),
    id: null,
    enunciado: '',
    alternativas: [
      { id: null, texto: '', correta: true },
      { id: null, texto: '', correta: false },
    ],
    removidas: [],
    alterada: true,
    salvando: false,
  })
}

function adicionarAlternativa(questao: QuestaoLocal) {
  questao.alternativas.push({ id: null, texto: '', correta: false })
  questao.alterada = true
}

function removerAlternativa(questao: QuestaoLocal, indice: number) {
  const alternativa = questao.alternativas[indice]
  if (!alternativa) return
  if (alternativa.id !== null) questao.removidas.push(alternativa.id)
  questao.alternativas.splice(indice, 1)
  questao.alterada = true
}

// so uma correta por pergunta, marcar uma desmarca as outras
function marcarCorreta(questao: QuestaoLocal, indice: number) {
  for (let i = 0; i < questao.alternativas.length; i++) {
    const alternativa = questao.alternativas[i]
    if (alternativa) alternativa.correta = i === indice
  }
  questao.alterada = true
}

/* regras do quiz, so no front */

function erroDaPergunta(questao: QuestaoLocal): string | null {
  if (!questao.enunciado.trim()) return 'Escreva o enunciado da pergunta'
  if (questao.alternativas.length < 2) return 'A pergunta precisa de pelo menos 2 alternativas'

  let corretas = 0
  for (const alternativa of questao.alternativas) {
    if (!alternativa.texto.trim()) return 'Preencha o texto de todas as alternativas'
    if (alternativa.texto.length > 200) return 'Alternativa com mais de 200 caracteres'
    if (alternativa.correta) corretas += 1
  }
  if (corretas !== 1) return 'Marque exatamente 1 alternativa correta'

  return null
}

const totalSalvas = computed(() => {
  let total = 0
  for (const questao of questoes.value) {
    if (questao.id !== null) total += 1
  }
  return total
})

/* salvar no banco, uma requisicao por item */

async function salvarPergunta(questao: QuestaoLocal, indice: number) {
  const erro = erroDaPergunta(questao)
  if (erro) {
    toast.add({ title: erro, color: 'warning' })
    return
  }

  questao.salvando = true
  try {
    const api = useApi()

    if (questao.id === null) {
      const nova = await api('/questoes', {
        method: 'POST',
        body: { conteudo_id: props.conteudoId, ordem: indice, enunciado: questao.enunciado },
      })
      questao.id = nova.id
    }
    else {
      await api(`/questoes/${questao.id}`, { method: 'PATCH', body: { enunciado: questao.enunciado } })
    }

    for (const id of questao.removidas) {
      await api(`/alternativas/${id}`, { method: 'DELETE' })
    }
    questao.removidas = []

    for (const alternativa of questao.alternativas) {
      if (alternativa.id === null) {
        const nova = await api('/alternativas', {
          method: 'POST',
          body: { questao_id: questao.id, texto: alternativa.texto, correta: alternativa.correta },
        })
        alternativa.id = nova.id
      }
      else {
        await api(`/alternativas/${alternativa.id}`, {
          method: 'PATCH',
          body: { texto: alternativa.texto, correta: alternativa.correta },
        })
      }
    }

    questao.alterada = false
    toast.add({ title: 'Pergunta salva', color: 'success' })
    emit('alterou')
  }
  catch {
    toast.add({ title: 'Não foi possível salvar a pergunta', color: 'error' })
  }
  questao.salvando = false
}

/* excluir pergunta com modal de confirmacao */

const showDeleteModal = ref(false)
const excluindo = ref(false)
const questaoParaExcluir = ref<QuestaoLocal | null>(null)

function pedirExclusao(questao: QuestaoLocal) {
  questaoParaExcluir.value = questao
  showDeleteModal.value = true
}

async function excluirPergunta() {
  const questao = questaoParaExcluir.value
  if (!questao) return

  excluindo.value = true
  try {
    if (questao.id !== null) {
      const api = useApi()
      await api(`/questoes/${questao.id}`, { method: 'DELETE' })
    }
    questoes.value = questoes.value.filter(q => q.chave !== questao.chave)
    await salvarOrdem()
    if (questao.id !== null) emit('alterou')
    showDeleteModal.value = false
  }
  catch {
    toast.add({ title: 'Não foi possível excluir a pergunta', color: 'error' })
  }
  excluindo.value = false
}

// depois de arrastar ou excluir, regrava a ordem das q ja tao no banco
async function salvarOrdem() {
  try {
    const api = useApi()
    for (let indice = 0; indice < questoes.value.length; indice++) {
      const questao = questoes.value[indice]
      if (questao && questao.id !== null) {
        await api(`/questoes/${questao.id}`, { method: 'PATCH', body: { ordem: indice } })
      }
    }
  }
  catch {
    toast.add({ title: 'Não foi possível salvar a nova ordem', color: 'error' })
  }
}
</script>

<template>
  <div class="max-w-3xl mx-auto space-y-4">
    <div class="flex items-center justify-between">
      <p class="text-sm text-muted">
        {{ totalSalvas }} pergunta{{ totalSalvas === 1 ? '' : 's' }} salva{{ totalSalvas === 1 ? '' : 's' }}
      </p>
      <UButton
        icon="i-lucide-plus"
        label="Pergunta"
        color="primary"
        @click="adicionarPergunta"
      />
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

    <template v-else>
      <UAlert
        v-if="totalSalvas === 0"
        color="warning"
        variant="subtle"
        icon="i-lucide-triangle-alert"
        title="O quiz precisa de pelo menos 1 pergunta salva"
      />

      <!-- arrasta pelo icone de pontinhos pra mudar a ordem -->
      <VueDraggable
        v-model="questoes"
        :animation="150"
        handle=".questao-drag-handle"
        class="space-y-4"
        @end="salvarOrdem"
      >
        <div
          v-for="(questao, indice) in questoes"
          :key="questao.chave"
          class="bg-elevated/40 border border-default rounded-xl p-4 space-y-3"
        >
          <div class="flex items-center justify-between gap-2">
            <div class="flex items-center gap-2">
              <UIcon
                name="i-lucide-grip-vertical"
                class="questao-drag-handle size-4 text-muted cursor-grab active:cursor-grabbing"
              />
              <span class="text-sm font-semibold">Pergunta {{ indice + 1 }}</span>
              <UBadge
                v-if="questao.alterada"
                color="warning"
                variant="soft"
                size="sm"
              >
                não salva
              </UBadge>
            </div>
            <UButton
              icon="i-lucide-trash-2"
              size="xs"
              color="error"
              variant="ghost"
              @click="pedirExclusao(questao)"
            />
          </div>

          <UTextarea
            v-model="questao.enunciado"
            placeholder="Enunciado da pergunta"
            autoresize
            class="w-full"
            @update:model-value="questao.alterada = true"
          />

          <!-- clicar no circulo marca a correta -->
          <div class="space-y-2">
            <div
              v-for="(alternativa, indiceAlt) in questao.alternativas"
              :key="indiceAlt"
              class="flex items-center gap-2"
            >
              <UButton
                :icon="alternativa.correta ? 'i-lucide-circle-check' : 'i-lucide-circle'"
                :color="alternativa.correta ? 'success' : 'neutral'"
                variant="ghost"
                size="sm"
                :title="alternativa.correta ? 'Alternativa correta' : 'Marcar como correta'"
                @click="marcarCorreta(questao, indiceAlt)"
              />
              <UInput
                v-model="alternativa.texto"
                :placeholder="`Alternativa ${indiceAlt + 1}`"
                :maxlength="200"
                class="flex-1"
                @update:model-value="questao.alterada = true"
              />
              <UButton
                icon="i-lucide-x"
                color="neutral"
                variant="ghost"
                size="sm"
                :disabled="questao.alternativas.length <= 2"
                @click="removerAlternativa(questao, indiceAlt)"
              />
            </div>
          </div>

          <div class="flex items-center justify-between">
            <UButton
              icon="i-lucide-plus"
              label="Alternativa"
              color="neutral"
              variant="ghost"
              size="xs"
              @click="adicionarAlternativa(questao)"
            />
            <UButton
              icon="i-lucide-save"
              label="Salvar pergunta"
              size="sm"
              :loading="questao.salvando"
              @click="salvarPergunta(questao, indice)"
            />
          </div>
        </div>
      </VueDraggable>
    </template>

    <UModal
      v-model:open="showDeleteModal"
      title="Excluir pergunta"
      description="Excluir essa pergunta e as alternativas dela?"
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
          @click="excluirPergunta"
        />
      </template>
    </UModal>
  </div>
</template>
