<script setup lang="ts">
import type { AlternativaAlunoRead, QuestaoAlunoRead, ResultadoQuizRead } from '~/types/generated'

const props = defineProps<{
  conteudoId: number
  questoes: QuestaoAlunoRead[]
}>()

const emit = defineEmits<{
  respondeu: [resultado: ResultadoQuizRead]
}>()

const toast = useToast()

// troca a ordem das alternativas, cada vez q abre ou refaz fica diferente
function embaralhar(alternativas: AlternativaAlunoRead[]) {
  const copia = alternativas.slice()
  for (let i = copia.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    const temp = copia[i]!
    copia[i] = copia[j]!
    copia[j] = temp
  }
  return copia
}

function montarQuestoes() {
  const lista = []
  for (const questao of props.questoes) {
    lista.push({ ...questao, alternativas: embaralhar(questao.alternativas) })
  }
  return lista
}

const questoesEmbaralhadas = ref(montarQuestoes())
const respostas = ref<Record<number, number>>({})
const resultado = ref<ResultadoQuizRead | null>(null)
const enviando = ref(false)

const todasRespondidas = computed(() => {
  for (const questao of props.questoes) {
    if (!respostas.value[questao.id]) return false
  }
  return true
})

async function onEnviar() {
  enviando.value = true
  try {
    const api = useApi()
    const resposta: ResultadoQuizRead = await api(`/progresso/conteudos/${props.conteudoId}/responder`, {
      method: 'POST',
      body: { respostas: respostas.value },
    })
    resultado.value = resposta
    emit('respondeu', resposta)
  }
  catch {
    toast.add({ title: 'Não foi possível enviar as respostas', color: 'error' })
  }
  enviando.value = false
}

function onRefazer() {
  respostas.value = {}
  resultado.value = null
  questoesEmbaralhadas.value = montarQuestoes()
}

/* correcao */

function correcaoDa(questaoId: number) {
  if (!resultado.value) return null
  for (const item of resultado.value.correcao) {
    if (item.questao_id === questaoId) return item
  }
  return null
}

// verde na certa, vermelho na q o aluno marcou errado
function corDaAlternativa(questaoId: number, alternativaId: number) {
  const correcao = correcaoDa(questaoId)
  if (!correcao) return ''
  if (correcao.alternativa_correta_id === alternativaId) return 'border-success bg-success/10'
  if (correcao.alternativa_escolhida_id === alternativaId) return 'border-error bg-error/10'
  return 'border-default opacity-60'
}
</script>

<template>
  <div class="space-y-4">
    <!-- nota final -->
    <UAlert
      v-if="resultado"
      :color="resultado.acertos === resultado.total ? 'success' : 'warning'"
      variant="soft"
      icon="i-lucide-award"
      :title="`Você acertou ${resultado.acertos} de ${resultado.total}`"
      :description="resultado.xp_ganho > 0 ? `+${resultado.xp_ganho} XP` : 'Nenhum XP novo nesta tentativa'"
    />

    <UCard
      v-for="(questao, index) in questoesEmbaralhadas"
      :key="questao.id"
    >
      <p class="font-medium mb-3">
        {{ index + 1 }}. {{ questao.enunciado }}
      </p>

      <div class="space-y-2">
        <button
          v-for="alternativa in questao.alternativas"
          :key="alternativa.id"
          type="button"
          class="w-full flex items-center gap-2 text-left text-sm rounded-md border px-3 py-2 transition"
          :class="resultado
            ? corDaAlternativa(questao.id, alternativa.id)
            : respostas[questao.id] === alternativa.id ? 'border-primary bg-primary/10' : 'border-default hover:bg-elevated'"
          :disabled="!!resultado"
          @click="respostas[questao.id] = alternativa.id"
        >
          <UIcon
            :name="respostas[questao.id] === alternativa.id ? 'i-lucide-circle-dot' : 'i-lucide-circle'"
            class="size-4 shrink-0"
          />
          {{ alternativa.texto }}
        </button>
      </div>
    </UCard>

    <div class="flex justify-end">
      <UButton
        v-if="resultado"
        icon="i-lucide-rotate-ccw"
        label="Refazer"
        color="neutral"
        variant="outline"
        @click="onRefazer"
      />
      <UButton
        v-else
        icon="i-lucide-send"
        label="Enviar respostas"
        :disabled="!todasRespondidas"
        :loading="enviando"
        @click="onEnviar"
      />
    </div>
  </div>
</template>
