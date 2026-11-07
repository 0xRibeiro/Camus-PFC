<script setup lang="ts">
import type { LancamentoRead, TrilhaResumoRead, XpRead } from '~/types/generated'

const xp = ref(0)
const extrato = ref<LancamentoRead[]>([])
const trilhas = ref<TrilhaResumoRead[]>([])
const carregando = ref(true)
const erro = ref(false)

async function buscarPontuacao() {
  carregando.value = true
  erro.value = false
  try {
    const api = useApi()
    const [respostaXp, respostaExtrato, respostaTrilhas] = await Promise.all([
      api('/pontuacao/xp') as Promise<XpRead>,
      api('/pontuacao/extrato') as Promise<LancamentoRead[]>,
      api('/progresso/trilhas') as Promise<TrilhaResumoRead[]>,
    ])
    xp.value = respostaXp.xp_total
    extrato.value = respostaExtrato
    trilhas.value = respostaTrilhas
  }
  catch {
    erro.value = true
  }
  carregando.value = false
}

onMounted(buscarPontuacao)

function formatarData(data: string) {
  return new Date(data).toLocaleDateString('pt-BR')
}
</script>

<template>
  <section class="space-y-4">
    <UAlert
      v-if="erro"
      color="error"
      variant="subtle"
      icon="i-lucide-circle-alert"
      title="Não foi possível carregar a pontuação"
    />

    <div class="grid gap-4 sm:grid-cols-3">
      <!-- xp total -->
      <UCard>
        <p class="text-sm text-muted">
          XP total
        </p>
        <USkeleton
          v-if="carregando"
          class="mt-2 h-9 w-20"
        />
        <p
          v-else
          class="mt-2 text-3xl font-semibold text-primary"
        >
          {{ xp }}
        </p>
      </UCard>

      <!-- progresso por trilha -->
      <UCard class="sm:col-span-2">
        <p class="text-sm text-muted mb-3">
          Progresso nas trilhas
        </p>
        <p
          v-if="!carregando && !trilhas.length"
          class="text-sm text-muted"
        >
          Nenhuma trilha disponível.
        </p>
        <div class="space-y-3">
          <NuxtLink
            v-for="trilha in trilhas"
            :key="trilha.id"
            :to="`/trilhas/${trilha.id}`"
            class="block space-y-1 hover:text-primary"
          >
            <div class="flex justify-between text-sm">
              <span>{{ trilha.titulo }}</span>
              <span class="text-muted">{{ trilha.progresso }}%</span>
            </div>
            <UProgress
              :model-value="trilha.progresso"
              size="sm"
            />
          </NuxtLink>
        </div>
      </UCard>
    </div>

    <!-- extrato, o back ja manda do mais novo pro mais antigo -->
    <UCard v-if="extrato.length">
      <p class="text-sm text-muted mb-3">
        Últimos pontos ganhos
      </p>
      <ul class="divide-y divide-default">
        <li
          v-for="lancamento in extrato"
          :key="lancamento.id"
          class="flex items-center justify-between py-2 text-sm"
        >
          <span>
            {{ lancamento.titulo ?? 'Conteúdo removido' }}
            <span
              v-if="lancamento.versao > 1"
              class="text-muted"
            >· versão {{ lancamento.versao }}</span>
          </span>
          <span class="flex items-center gap-3">
            <span class="text-xs text-muted">{{ formatarData(lancamento.criado_em) }}</span>
            <span class="font-medium text-success">+{{ lancamento.pontos }} XP</span>
          </span>
        </li>
      </ul>
    </UCard>
  </section>
</template>
