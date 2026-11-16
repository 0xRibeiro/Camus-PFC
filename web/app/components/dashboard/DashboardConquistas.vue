<template>
  <UCard :ui="{ body: 'p-0 sm:p-0' }">
    <template #header>
      <div class="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 class="font-medium">
            {{ mostrarMais ? 'Conquistas mais obtidas' : 'Conquistas menos obtidas' }}
          </h2>

          <p class="text-sm text-muted">
            Porcentagem dos alunos que já desbloquearam.
          </p>
        </div>

        <UFieldGroup size="sm">
          <UButton
            label="Mais"
            icon="i-lucide-trending-up"
            color="neutral"
            :variant="mostrarMais ? 'solid' : 'outline'"
            @click="mostrarMais = true"
          />

          <UButton
            label="Menos"
            icon="i-lucide-trending-down"
            color="neutral"
            :variant="mostrarMais ? 'outline' : 'solid'"
            @click="mostrarMais = false"
          />
        </UFieldGroup>
      </div>
    </template>

    <ol
      v-if="conquistas.length"
      class="max-h-80 divide-y divide-default overflow-y-auto"
      tabindex="0"
      aria-label="Lista de Conquistas"
    >
      <li
        v-for="(conquista, posicao) in lista"
        :key="conquista.id"
        class="flex items-center gap-3 px-4 py-3 sm:px-6"
      >
        <span class="w-5 shrink-0 text-right text-sm font-medium text-dimmed">
          {{ posicao + 1 }}
        </span>

        <div class="flex size-10 shrink-0 items-center justify-center overflow-hidden rounded-lg bg-secondary/10 text-secondary">
          <img
            v-if="conquista.imagem_dir"
            :src="conquista.imagem_dir"
            alt=""
            class="size-full object-cover"
          >
          <UIcon
            v-else
            name="i-lucide-trophy"
            class="size-5"
          />
        </div>

        <div class="min-w-0 flex-1 space-y-1.5">
          <div class="flex items-baseline justify-between gap-3">
            <p class="truncate font-medium text-highlighted">
              {{ conquista.titulo }}
            </p>

            <span class="shrink-0 text-sm font-semibold tabular-nums">
              {{ formatarPorcentagem(conquista.porcentagem) }}
            </span>
          </div>

          <UProgress
            :model-value="conquista.porcentagem"
            :max="1"
            color="secondary"
            size="sm"
          />
        </div>
      </li>
    </ol>

    <p
      v-else
      class="p-4 text-sm text-muted sm:p-6"
    >
      Nenhuma conquista cadastrada.
    </p>
  </UCard>
</template>

<script setup lang="ts">
import type { ConquistaResumoRead } from '~/types/generated'

const props = defineProps<{
  conquistas: ConquistaResumoRead[]
  totalAlunos: number
}>()

const mostrarMais = ref(true)

const formatarPorcentagem = new Intl.NumberFormat('pt-BR', { style: 'percent', maximumFractionDigits: 1 }).format

// ja vem ordenada da api, menos so inverte
const lista = computed(() => {
  const comPorcentagem = props.conquistas.map(conquista => ({
    ...conquista,
    porcentagem: props.totalAlunos ? conquista.quantidade / props.totalAlunos : 0,
  }))

  if (mostrarMais.value) return comPorcentagem
  return comPorcentagem.reverse()
})
</script>
