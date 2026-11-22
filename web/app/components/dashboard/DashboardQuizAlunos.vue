<template>
  <UCard :ui="{ body: 'p-0 sm:p-0' }">
    <template #header>
      <div class="flex flex-wrap items-start justify-between gap-3">
        <h2 class="font-medium">
          Alunos que fizeram
          <span
            v-if="alunos.length"
            class="font-normal text-muted"
          >({{ alunos.length }})</span>
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
            :icon="porNota ? 'i-lucide-trophy' : 'i-lucide-clock'"
            :label="porNota ? 'Maiores notas' : 'Feito recente'"
            size="sm"
            color="neutral"
            variant="ghost"
            aria-label="Trocar a ordem dos alunos"
            @click="porNota = !porNota"
          />
        </div>
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
      {{ alunos.length ? 'Nenhum aluno com esse nome.' : 'Nenhum aluno fez esse quiz ainda.' }}
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
        <!-- so abre quem fez a versao atual, a antiga n tem as questoes -->
        <component
          :is="aluno.respostas?.length ? 'button' : 'div'"
          :type="aluno.respostas?.length ? 'button' : undefined"
          class="flex w-full items-center gap-3 px-4 py-3 text-left sm:px-6"
          :class="aluno.respostas?.length && 'transition-colors hover:bg-elevated/50 focus-visible:bg-elevated/50 focus-visible:outline-none'"
          @click="aluno.respostas?.length && abrir(aluno)"
        >
          <UsuarioAvatar
            :avatar="aluno.avatar"
            :cor-fundo="aluno.cor_fundo"
            :tamanho="36"
          />

          <p class="min-w-0 flex-1 truncate font-medium text-highlighted">
            {{ aluno.username }}
          </p>

          <!-- quando fez fica colado na nota, igual a lista de alunos da trilha -->
          <div class="flex shrink-0 items-center gap-2">
            <span class="text-xs text-muted">
              {{ formatarRelativo(aluno.concluido_em) }}
            </span>
            <UBadge
              v-if="aluno.versao_antiga"
              color="neutral"
              variant="outline"
              size="sm"
            >
              versão antiga
            </UBadge>

            <UBadge
              :color="corDaNota(aluno.acertos, aluno.questoes)"
              variant="subtle"
              class="tabular-nums"
            >
              {{ formatarNota(aluno.acertos, aluno.questoes) }}/10
            </UBadge>
          </div>

          <UIcon
            v-if="aluno.respostas?.length"
            name="i-lucide-chevron-right"
            class="size-4 shrink-0 text-dimmed"
          />
        </component>
      </li>
    </ul>

    <!-- abre por cima do modal do quiz -->
    <UModal
      v-model:open="showRespostas"
      :title="alunoAberto?.username ?? 'Aluno'"
      description="Respostas desse aluno no quiz"
      :ui="{ content: 'sm:max-w-3xl' }"
    >
      <template #body>
        <DashboardAlunoQuiz
          v-if="alunoAberto"
          :quiz="alunoAberto"
        />
      </template>
    </UModal>
  </UCard>
</template>

<script setup lang="ts">
import DashboardAlunoQuiz from '~/components/dashboard/DashboardAlunoQuiz.vue'
import type { AlunoQuizRead } from '~/types/generated'
import { formatarRelativo } from '~/utils/datas'
import { corDaNota, formatarNota } from '~/utils/notas'

const props = defineProps<{
  conteudoId: number
}>()

const api = useApi()
const alunos = ref<AlunoQuizRead[]>([])
const loading = ref(true)

async function buscarAlunos() {
  loading.value = true
  try {
    alunos.value = await api(`/conteudos/${props.conteudoId}/alunos`)
  }
  catch {
    alunos.value = []
  }
  loading.value = false
}

onMounted(buscarAlunos)

/* busca e ordem */

const busca = ref('')
// comeca por quem fez mais recente
const porNota = ref(false)

function nota(aluno: AlunoQuizRead) {
  return aluno.questoes ? aluno.acertos / aluno.questoes : 0
}

function momento(aluno: AlunoQuizRead) {
  return new Date(aluno.concluido_em).getTime()
}

// empate na nota vai pelo mais recente e dps pelo nome
function comparar(a: AlunoQuizRead, b: AlunoQuizRead) {
  if (porNota.value && nota(a) !== nota(b)) return nota(b) - nota(a)
  return momento(b) - momento(a) || a.username.localeCompare(b.username)
}

const lista = computed(() => {
  const termo = busca.value.trim().toLowerCase()
  const filtrados = []
  for (const aluno of alunos.value) {
    if (termo && !aluno.username.toLowerCase().includes(termo)) continue
    filtrados.push(aluno)
  }
  filtrados.sort(comparar)
  return filtrados
})

/* respostas */

const alunoAberto = ref<AlunoQuizRead | null>(null)
const showRespostas = ref(false)

function abrir(aluno: AlunoQuizRead) {
  alunoAberto.value = aluno
  showRespostas.value = true
}
</script>
