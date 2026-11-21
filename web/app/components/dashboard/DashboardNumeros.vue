<template>
  <!-- uma coluna por card, sem sobrar espaço do lado -->
  <UPageGrid
    class="gap-4 sm:grid-cols-2"
    :class="indicadores.length === 3 ? 'lg:grid-cols-3' : 'lg:grid-cols-4'"
  >
    <UPageCard
      v-for="indicador in lista"
      :key="indicador.titulo"
      :icon="indicador.icone"
      :title="indicador.titulo"
      variant="subtle"
      :ui="{
        container: 'gap-y-1.5',
        wrapper: 'items-start',
        leading: ['p-2.5 rounded-full ring ring-inset', cores[indicador.cor].fundo],
        leadingIcon: cores[indicador.cor].icone,
        title: 'font-normal text-muted text-xs uppercase',
      }"
    >
      <div class="space-y-1">
        <span class="text-3xl font-semibold text-highlighted">
          {{ indicador.texto }}
        </span>

        <!-- valor de antes numa linha so, a cor diz se subiu ou desceu -->
        <p
          v-if="indicador.antes !== null && periodoAnterior"
          class="flex flex-wrap items-center gap-x-1 text-xs"
          :class="indicador.comparacao.texto"
        >
          <span>Período anterior ({{ periodoAnterior }}):</span>
          <span class="flex items-center gap-0.5 font-semibold tabular-nums">
            <UIcon
              :name="indicador.comparacao.icone"
              class="size-3.5"
            />
            {{ indicador.antes }}
          </span>
        </p>
      </div>
    </UPageCard>
  </UPageGrid>
</template>

<script setup lang="ts">
type Cor = 'primary' | 'secondary' | 'tertiary' | 'quaternary'

export interface Indicador {
  titulo: string
  icone: string
  cor: Cor
  valor: number
  // valor do periodo anterior, null ou 0 n mostra a comparacao
  anterior: number | null
  formatar?: (valor: number) => string
}

const props = defineProps<{
  indicadores: Indicador[]
  // vazio n mostra a comparacao
  periodoAnterior: string
}>()

// classes inteiras pro tailwind achar
const cores: Record<Cor, { fundo: string, icone: string }> = {
  primary: { fundo: 'bg-primary/10 ring-primary/25', icone: 'text-primary' },
  secondary: { fundo: 'bg-secondary/10 ring-secondary/25', icone: 'text-secondary' },
  tertiary: { fundo: 'bg-tertiary/10 ring-tertiary/25', icone: 'text-tertiary' },
  quaternary: { fundo: 'bg-quaternary/10 ring-quaternary/25', icone: 'text-quaternary' },
}

function formatarValor(indicador: Indicador, valor: number) {
  if (indicador.formatar) return indicador.formatar(valor)
  return valor.toLocaleString('pt-BR')
}

// em todos os cards subir e bom
function comparar(atual: number, anterior: number) {
  if (atual > anterior) return { texto: 'text-success', icone: 'i-lucide-arrow-up' }
  if (atual < anterior) return { texto: 'text-error', icone: 'i-lucide-arrow-down' }
  return { texto: 'text-muted', icone: 'i-lucide-equal' }
}

const lista = computed(() => {
  const resultado = []
  for (const indicador of props.indicadores) {
    resultado.push({
      ...indicador,
      texto: formatarValor(indicador, indicador.valor),
      // antes zerado n compara nada
      antes: indicador.anterior ? formatarValor(indicador, indicador.anterior) : null,
      comparacao: comparar(indicador.valor, indicador.anterior ?? indicador.valor),
    })
  }
  return resultado
})
</script>
