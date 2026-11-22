<template>
  <UCard>
    <template #header>
      <h2 class="font-medium">
        Distribuição das notas
      </h2>
    </template>

    <div
      v-if="total"
      class="flex flex-col items-center gap-4"
    >
      <UChart
        type="donut"
        :data="fatias"
        index="nota"
        :categories="[{ key: 'quantidade', label: 'Alunos' }]"
        :colors="cores"
        :aspect-ratio="1"
        :thickness="40"
        :legend="false"
        :format="formatarNumero"
        :aria-label="`Distribuição das notas de ${total} alunos`"
        class="mx-auto w-full max-w-56"
      >
        <template #center>
          <div
            class="flex flex-col items-center"
            aria-hidden="true"
          >
            <span class="text-3xl font-semibold text-highlighted">
              {{ formatarNumero(total) }}
            </span>
            <span class="text-xs text-muted">
              {{ total === 1 ? 'aluno' : 'alunos' }}
            </span>
          </div>
        </template>
      </UChart>

      <!-- da nota com mais aluno pra menos -->
      <ul class="w-full space-y-2.5">
        <li
          v-for="fatia in legenda"
          :key="fatia.nota"
          class="space-y-1"
        >
          <div class="flex items-center justify-between gap-3 text-sm">
            <span
              class="font-semibold tabular-nums"
              :style="{ color: corDaNota(fatia.acertos) }"
            >
              {{ fatia.nota }}
            </span>

            <span class="text-muted tabular-nums">
              <span class="font-semibold text-highlighted">{{ formatarNumero(fatia.quantidade) }}</span>
              {{ fatia.quantidade === 1 ? 'aluno' : 'alunos' }} · {{ formatarPorcentagem(fatia.quantidade / total) }}
            </span>
          </div>

          <div class="h-1.5 overflow-hidden rounded-full bg-elevated">
            <div
              class="h-full rounded-full"
              :style="{ width: `${(fatia.quantidade / total) * 100}%`, background: corDaNota(fatia.acertos) }"
            />
          </div>
        </li>
      </ul>
    </div>

    <p
      v-else
      class="text-sm text-muted"
    >
      Ninguém fez a versão atual do quiz nesse período.
    </p>
  </UCard>
</template>

<script setup lang="ts">
import type { NotaQuizRead } from '~/types/generated'

const props = defineProps<{
  notas: NotaQuizRead[]
}>()

const formatarNumero = new Intl.NumberFormat('pt-BR').format
const formatarPorcentagem = new Intl.NumberFormat('pt-BR', { style: 'percent', maximumFractionDigits: 1 }).format

// ultima nota e o total de questoes
const totalQuestoes = computed(() => props.notas.length - 1)

// nota sem ninguem n vira fatia
const fatias = computed(() => {
  const lista = []
  for (const nota of props.notas) {
    if (nota.quantidade) lista.push({ nota: `${nota.acertos}/${totalQuestoes.value}`, acertos: nota.acertos, quantidade: nota.quantidade })
  }
  return lista
})

// no grafico fica na ordem da nota pro degrade, na legenda pela quantidade. empate fica a maior nota em cima
const legenda = computed(() => {
  const lista = [...fatias.value]
  lista.sort((a, b) => b.quantidade - a.quantidade || b.acertos - a.acertos)
  return lista
})

// vai do vermelho (zerou) ao verde (gabaritou) passando pelo amarelo
function corDaNota(acertos: number) {
  const fracao = totalQuestoes.value ? acertos / totalQuestoes.value : 0
  if (fracao <= 0.5) return `color-mix(in oklch, var(--ui-warning) ${Math.round(fracao * 200)}%, var(--ui-error))`
  return `color-mix(in oklch, var(--ui-success) ${Math.round((fracao - 0.5) * 200)}%, var(--ui-warning))`
}

const cores = computed(() => {
  const lista = []
  for (const fatia of fatias.value) lista.push(corDaNota(fatia.acertos))
  return lista
})

const total = computed(() => {
  let soma = 0
  for (const nota of props.notas) soma += nota.quantidade
  return soma
})
</script>
