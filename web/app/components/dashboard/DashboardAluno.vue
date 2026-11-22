<template>
  <div
    v-if="loading"
    class="flex justify-center py-8"
  >
    <UIcon
      name="i-lucide-loader-circle"
      class="size-6 animate-spin"
    />
  </div>

  <p
    v-else-if="erro || !aluno"
    class="text-sm text-muted"
  >
    {{ erro || 'Não foi possível carregar o aluno.' }}
  </p>

  <div
    v-else
    class="space-y-6"
  >
    <!-- cabecalho com o aluno e onde ele ta -->
    <div class="flex flex-wrap items-center gap-4">
      <UsuarioAvatar
        :avatar="aluno.avatar"
        :cor-fundo="aluno.cor_fundo"
        :tamanho="56"
      />

      <div class="min-w-0 flex-1">
        <p class="truncate text-lg font-semibold text-highlighted">
          {{ aluno.username }}
        </p>

        <p class="text-sm text-muted">
          {{ textoSituacao }}
        </p>
      </div>
    </div>

    <div class="grid grid-cols-1 gap-3 sm:grid-cols-[1fr_auto]">
      <!-- um pedaco da barra por conteudo, msm cor da linha do tempo -->
      <div class="space-y-2 rounded-lg bg-elevated/50 p-3">
        <div class="flex items-baseline justify-between gap-3">
          <p class="text-xs text-muted uppercase">
            Progresso
          </p>

          <p class="text-sm text-muted">
            <span class="text-xl font-semibold text-highlighted tabular-nums">{{ aluno.concluidos }}</span>
            de {{ aluno.total }} conteúdos
          </p>
        </div>

        <div
          class="flex gap-1"
          aria-hidden="true"
        >
          <span
            v-for="item in linhaDoTempo"
            :key="item.id"
            class="h-2.5 flex-1 rounded-full"
            :class="item.concluido_em ? 'bg-success' : item.proximo ? 'bg-warning' : 'bg-accented'"
          />
        </div>
      </div>

      <div class="rounded-lg bg-elevated/50 p-3 sm:min-w-40">
        <p class="text-xs text-muted uppercase">
          {{ terminou ? 'Concluiu em' : 'Tempo na trilha' }}
        </p>

        <p class="text-xl font-semibold text-highlighted tabular-nums">
          {{ tempoNaTrilha }}
        </p>
      </div>
    </div>

    <!-- linha do tempo dos conteudos na ordem da trilha -->
    <div>
      <h3 class="mb-3 font-medium">
        Conteúdos
      </h3>

      <ol>
        <li
          v-for="(item, indice) in linhaDoTempo"
          :key="item.id"
          class="relative flex gap-3 pb-4 last:pb-0"
        >
          <!-- traco ligando um ponto no outro -->
          <span
            v-if="indice < linhaDoTempo.length - 1"
            class="absolute top-7 bottom-0 left-3.5 w-px bg-(--ui-border)"
            aria-hidden="true"
          />

          <span
            class="relative flex size-7 shrink-0 items-center justify-center rounded-full ring ring-inset"
            :class="item.marcador.classe"
          >
            <UIcon
              :name="item.marcador.icone"
              class="size-3.5"
            />
          </span>

          <!-- quiz da versao atual abre as respostas dele -->
          <component
            :is="item.respostas.length ? 'button' : 'div'"
            :type="item.respostas.length ? 'button' : undefined"
            class="-mx-2 -my-1 min-w-0 flex-1 space-y-1 rounded-md px-2 py-1 text-left"
            :class="item.respostas.length && 'transition-colors hover:bg-elevated/50 focus-visible:bg-elevated/50 focus-visible:outline-none'"
            @click="item.respostas.length && abrirQuiz(item)"
          >
            <div class="flex flex-wrap items-baseline justify-between gap-x-3">
              <p
                class="font-medium"
                :class="item.concluido_em ? 'text-highlighted' : 'text-muted'"
              >
                {{ item.titulo }}
              </p>

              <span class="text-xs text-muted">
                {{ item.modulo }} · {{ rotuloTipo[item.tipo] ?? item.tipo }}
              </span>
            </div>

            <p
              v-if="item.concluido_em"
              class="text-xs text-muted"
            >
              Concluído em {{ formatarDataHora(item.concluido_em) }}
            </p>

            <p
              v-else-if="item.proximo"
              class="text-xs font-medium text-warning"
            >
              Próximo conteúdo
            </p>

            <!-- nota so no quiz -->
            <div
              v-if="item.acertos !== null && item.acertos !== undefined && item.questoes"
              class="flex flex-wrap items-center gap-2 pt-1"
            >
              <UBadge
                :color="corDaNota(item.acertos, item.questoes)"
                variant="subtle"
              >
                Nota {{ formatarNota(item.acertos, item.questoes) }}/10
              </UBadge>

              <span class="text-xs text-muted">
                {{ item.acertos }} de {{ item.questoes }} questões
              </span>

              <UBadge
                v-if="item.versao_antiga"
                color="neutral"
                variant="outline"
                size="sm"
              >
                fez uma versão antiga
              </UBadge>

              <span
                v-else-if="item.respostas.length"
                class="flex items-center gap-0.5 text-xs font-medium text-primary"
              >
                Ver respostas
                <UIcon
                  name="i-lucide-chevron-right"
                  class="size-3.5"
                />
              </span>
            </div>
          </component>
        </li>
      </ol>
    </div>

    <!-- abre por cima do modal do aluno -->
    <UModal
      v-model:open="showQuizModal"
      :title="quizAberto?.titulo ?? 'Quiz'"
      :description="`Respostas de ${aluno.username}`"
      :ui="{ content: 'sm:max-w-3xl' }"
    >
      <template #body>
        <DashboardAlunoQuiz
          v-if="quizAberto"
          :quiz="quizAberto"
        />
      </template>
    </UModal>
  </div>
</template>

<script setup lang="ts">
import DashboardAlunoQuiz from '~/components/dashboard/DashboardAlunoQuiz.vue'
import type { AlunoDetalheRead, ConteudoDoAlunoRead } from '~/types/generated'
import { formatarDataHora, formatarDuracao } from '~/utils/datas'
import { corDaNota, formatarNota } from '~/utils/notas'

const props = defineProps<{
  trilhaId: number
  usuarioId: number
}>()

const api = useApi()
const aluno = ref<AlunoDetalheRead | null>(null)
const loading = ref(true)
const erro = ref('')

async function buscarAluno() {
  loading.value = true
  erro.value = ''
  try {
    aluno.value = await api(`/trilhas/${props.trilhaId}/alunos/${props.usuarioId}`)
  }
  catch {
    aluno.value = null
    erro.value = 'Não foi possível carregar o aluno.'
  }
  loading.value = false
}

// trocar de aluno com o modal aberto busca de novo
watch(() => props.usuarioId, buscarAluno, { immediate: true })

const rotuloTipo: Record<string, string> = {
  artigo: 'Artigo',
  video: 'Vídeo',
  quiz: 'Quiz',
}

/* numeros do topo */

const terminou = computed(() => !!aluno.value && aluno.value.concluidos >= aluno.value.total)

// da 1a conclusao ate a ultima, igual o tempo da dashboard da trilha
const tempoNaTrilha = computed(() => {
  if (!aluno.value) return '—'
  let primeira: number | null = null
  let ultima: number | null = null
  for (const item of aluno.value.conteudos) {
    if (!item.concluido_em) continue
    const momento = new Date(item.concluido_em).getTime()
    if (primeira === null || momento < primeira) primeira = momento
    if (ultima === null || momento > ultima) ultima = momento
  }
  if (primeira === null || ultima === null || primeira === ultima) return '—'
  return formatarDuracao((ultima - primeira) / 3600000)
})

/* linha do tempo */

type ItemLinhaDoTempo = ConteudoDoAlunoRead & {
  respostas: NonNullable<ConteudoDoAlunoRead['respostas']>
  proximo: boolean
  marcador: { icone: string, classe: string }
}

const linhaDoTempo = computed(() => {
  const itens: ItemLinhaDoTempo[] = []
  if (!aluno.value) return itens

  let achouProximo = false
  for (const item of aluno.value.conteudos) {
    let proximo = false
    let marcador = { icone: 'i-lucide-circle', classe: 'bg-elevated ring-default text-dimmed' }

    if (item.concluido_em) {
      marcador = { icone: 'i-lucide-check', classe: 'bg-success/10 ring-success/25 text-success' }
    }
    else if (!achouProximo) {
      // o 1o q falta é onde ele ta agora
      achouProximo = true
      proximo = true
      marcador = { icone: 'i-lucide-map-pin', classe: 'bg-warning/10 ring-warning/25 text-warning' }
    }

    itens.push({ ...item, respostas: item.respostas ?? [], proximo, marcador })
  }
  return itens
})

const textoSituacao = computed(() => {
  if (!aluno.value) return ''
  if (!aluno.value.concluidos) return 'Ainda não começou a trilha'
  if (terminou.value) return 'Terminou a trilha'
  const proximo = linhaDoTempo.value.find(item => item.proximo)
  return proximo ? `Em andamento, parou em "${proximo.titulo}"` : 'Em andamento'
})

/* respostas do quiz */

const quizAberto = ref<ConteudoDoAlunoRead | null>(null)
const showQuizModal = ref(false)

function abrirQuiz(item: ConteudoDoAlunoRead) {
  quizAberto.value = item
  showQuizModal.value = true
}
</script>
