<template>
  <UCard :ui="{ body: 'p-0 sm:p-0' }">
    <template #header>
      <div class="flex flex-wrap items-start justify-between gap-3">
        <h2 class="font-medium">
          Alunos do grupo
        </h2>

        <div class="flex flex-wrap items-center gap-2">
          <UInput
            v-model="busca"
            icon="i-lucide-search"
            placeholder="Buscar aluno"
            size="sm"
            class="w-44"
          />

          <!-- clica e troca a ordem -->
          <UButton
            :icon="porProgresso ? 'i-lucide-trophy' : 'i-lucide-clock'"
            :label="porProgresso ? 'Mais avançados' : 'Atividade recente'"
            size="sm"
            color="neutral"
            variant="ghost"
            aria-label="Trocar a ordem dos alunos"
            @click="porProgresso = !porProgresso"
          />
        </div>
      </div>

      <!-- filtro por situacao, com quantos tem em cada -->
      <div class="mt-3 flex flex-wrap gap-1">
        <UButton
          v-for="opcao in situacoes"
          :key="opcao.value"
          :label="`${opcao.label} (${contagem[opcao.value]})`"
          size="xs"
          color="neutral"
          :variant="situacao === opcao.value ? 'soft' : 'ghost'"
          @click="situacao = opcao.value"
        />
      </div>
    </template>

    <div
      v-if="loading && !alunos.length"
      class="flex justify-center py-8"
    >
      <UIcon
        name="i-lucide-loader-circle"
        class="size-6 animate-spin"
      />
    </div>

    <p
      v-else-if="!lista.length"
      class="p-4 text-sm text-muted sm:p-6"
    >
      {{ alunos.length ? 'Nenhum aluno com esse filtro.' : 'O grupo ainda não tem membros.' }}
    </p>

    <ul
      v-else
      class="max-h-[32rem] divide-y divide-default overflow-y-auto"
      aria-label="Alunos do grupo"
    >
      <li
        v-for="aluno in lista"
        :key="aluno.id"
      >
        <button
          type="button"
          class="flex w-full items-center gap-3 px-4 py-3 text-left transition-colors hover:bg-elevated/50 focus-visible:bg-elevated/50 focus-visible:outline-none sm:px-6"
          @click="emit('abrir', aluno.id)"
        >
          <UsuarioAvatar
            :avatar="aluno.avatar"
            :cor-fundo="aluno.cor_fundo"
            :tamanho="36"
          />

          <div class="min-w-0 flex-1 space-y-1.5">
            <div class="flex flex-wrap items-center justify-between gap-x-3 gap-y-1">
              <p class="truncate font-medium text-highlighted">
                {{ aluno.username }}
              </p>

              <div class="flex items-center gap-2 text-xs">
                <span class="text-muted">
                  {{ aluno.ultima_atividade ? formatarRelativo(aluno.ultima_atividade) : 'sem atividade' }}
                </span>

                <UBadge
                  :color="situacaoDe(aluno).cor"
                  variant="subtle"
                  size="sm"
                >
                  {{ situacaoDe(aluno).label }}
                </UBadge>
              </div>
            </div>

            <div class="flex items-center gap-2">
              <div class="h-1.5 min-w-0 flex-1 overflow-hidden rounded-full bg-accented">
                <div
                  class="h-full rounded-full"
                  :class="situacaoDe(aluno).barra"
                  :style="{ width: `${aluno.total ? aluno.concluidos / aluno.total * 100 : 0}%` }"
                />
              </div>
              <span class="w-10 shrink-0 text-right text-xs text-muted tabular-nums">
                {{ aluno.concluidos }}/{{ aluno.total }}
              </span>
            </div>
          </div>

          <UIcon
            name="i-lucide-chevron-right"
            class="size-4 shrink-0 text-dimmed"
          />
        </button>
      </li>
    </ul>
  </UCard>
</template>

<script setup lang="ts">
import type { AlunoTrilhaRead } from '~/types/generated'
import { formatarRelativo } from '~/utils/datas'

const props = defineProps<{
  trilhaId: number
}>()

const emit = defineEmits<{
  abrir: [id: number]
}>()

const api = useApi()
const alunos = ref<AlunoTrilhaRead[]>([])
const loading = ref(true)

async function buscarAlunos() {
  loading.value = true
  try {
    alunos.value = await api(`/trilhas/${props.trilhaId}/alunos`)
  }
  catch {
    alunos.value = []
  }
  loading.value = false
}

onMounted(buscarAlunos)

/* situacao */

type Situacao = 'todos' | 'andamento' | 'terminou' | 'nao_comecou'

const situacoes: { label: string, value: Situacao }[] = [
  { label: 'Todos', value: 'todos' },
  { label: 'Em andamento', value: 'andamento' },
  { label: 'Terminaram', value: 'terminou' },
  { label: 'Não começaram', value: 'nao_comecou' },
]
const situacao = ref<Situacao>('todos')

function chaveSituacao(aluno: AlunoTrilhaRead): Situacao {
  if (!aluno.concluidos) return 'nao_comecou'
  if (aluno.concluidos >= aluno.total) return 'terminou'
  return 'andamento'
}

function situacaoDe(aluno: AlunoTrilhaRead) {
  const chave = chaveSituacao(aluno)
  if (chave === 'terminou') return { label: 'Terminou', cor: 'success' as const, barra: 'bg-success' }
  if (chave === 'andamento') return { label: 'Em andamento', cor: 'warning' as const, barra: 'bg-warning' }
  return { label: 'Não começou', cor: 'neutral' as const, barra: 'bg-inverted' }
}

const contagem = computed(() => {
  const total: Record<Situacao, number> = { todos: 0, andamento: 0, terminou: 0, nao_comecou: 0 }
  for (const aluno of alunos.value) {
    total.todos += 1
    total[chaveSituacao(aluno)] += 1
  }
  return total
})

/* busca e ordem */

const busca = ref('')

// comeca pela atividade recente
const porProgresso = ref(false)

// msm progresso: o mais recente fica na frente, sem atividade vai pelo nome
function desempatar(a: AlunoTrilhaRead, b: AlunoTrilhaRead) {
  if (a.ultima_atividade && b.ultima_atividade) {
    return new Date(b.ultima_atividade).getTime() - new Date(a.ultima_atividade).getTime()
  }
  return a.username.localeCompare(b.username)
}

// quem n tem atividade vai pro fim
function comparar(a: AlunoTrilhaRead, b: AlunoTrilhaRead) {
  if (porProgresso.value) return b.concluidos - a.concluidos || desempatar(a, b)
  if (!a.ultima_atividade) return b.ultima_atividade ? 1 : a.username.localeCompare(b.username)
  if (!b.ultima_atividade) return -1
  return new Date(b.ultima_atividade).getTime() - new Date(a.ultima_atividade).getTime()
}

const lista = computed(() => {
  const termo = busca.value.trim().toLowerCase()
  const filtrados = []
  for (const aluno of alunos.value) {
    if (termo && !aluno.username.toLowerCase().includes(termo)) continue
    if (situacao.value !== 'todos' && chaveSituacao(aluno) !== situacao.value) continue
    filtrados.push(aluno)
  }
  filtrados.sort(comparar)
  return filtrados
})
</script>
