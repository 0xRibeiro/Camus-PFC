<template>
  <UCard>
    <template #header>
      <h2 class="font-medium">
        Trilhas por escopo
      </h2>
      <p class="text-sm text-muted">
        Todas as trilhas cadastradas, incluindo rascunhos.
      </p>
    </template>

    <div
      v-if="total > 0"
      class="@container"
    >
      <div class="grid items-center gap-x-4 gap-y-1 @min-[24rem]:grid-cols-[minmax(0,1fr)_auto]">
        <UChart
          type="donut"
          :data="trilhasPorEscopo"
          index="escopo"
          :categories="[{ key: 'quantidade', label: 'Trilhas' }]"
          :aspect-ratio="1"
          :thickness="56"
          :colors="['primary', 'quaternary']"
          :legend="false"
          :format="formatarNumero"
          :aria-label="`Trilhas por escopo. Globais: ${globais}. De grupo: ${deGrupo}.`"
          class="mx-auto w-full max-w-60 @min-[24rem]:max-w-64"
        >
          <template #center>
            <span
              class="text-3xl font-semibold text-highlighted"
              aria-hidden="true"
            >
              {{ formatarNumero(total) }}
            </span>
          </template>
        </UChart>

        <ul class="flex flex-wrap justify-center gap-x-4 gap-y-1 text-xs text-muted @min-[24rem]:flex-col">
          <li
            v-for="trilha in trilhasPorEscopo"
            :key="trilha.escopo"
            class="flex items-center gap-2"
          >
            <span
              class="size-2 shrink-0 rounded-full"
              :class="trilha.escopo === 'Globais' ? 'bg-primary' : 'bg-quaternary'"
              aria-hidden="true"
            />
            {{ trilha.escopo }}
            <span class="font-medium text-highlighted">
              {{ formatarNumero(trilha.quantidade) }}
            </span>
          </li>
        </ul>
      </div>
    </div>

    <p
      v-else
      class="text-sm text-muted"
    >
      Nenhuma trilha cadastrada.
    </p>
  </UCard>
</template>

<script setup lang="ts">
const props = defineProps<{
  globais: number
  deGrupo: number
}>()

const formatarNumero = new Intl.NumberFormat('pt-BR').format
const total = computed(() => props.globais + props.deGrupo)

const trilhasPorEscopo = computed(() => [
  { escopo: 'Globais', quantidade: props.globais },
  { escopo: 'De grupo', quantidade: props.deGrupo },
])
</script>
