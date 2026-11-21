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
      variant="outline"
      :ui="{
        container: 'gap-y-1.5',
        wrapper: 'items-start',
        leading: ['p-2.5 rounded-full ring ring-inset', cores[indicador.cor].fundo],
        leadingIcon: cores[indicador.cor].icone,
        title: 'font-normal text-muted text-xs uppercase',
      }"
    >
      <div class="space-y-1">
        <!-- a seta fica no numero de agora, a cor diz se foi bom ou ruim -->
        <div class="flex items-center gap-2">
          <span class="text-3xl font-semibold text-highlighted">
            {{ indicador.texto }}
          </span>

          <span
            v-if="indicador.antes !== null && periodoAnterior && indicador.comparacao.icone"
            class="flex size-6 items-center justify-center rounded-full"
            :class="indicador.comparacao.selo"
            :aria-label="indicador.comparacao.descricao"
          >
            <UIcon
              :name="indicador.comparacao.icone"
              class="size-4"
            />
          </span>
        </div>

        <!-- so informa o valor de antes -->
        <p
          v-if="indicador.antes !== null && periodoAnterior"
          class="text-xs text-muted"
        >
          Período anterior ({{ periodoAnterior }}):
          <span class="font-semibold tabular-nums">{{ indicador.antes }}</span>
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
  // null vira — (tempo sem ngm terminar, nota sem ngm fazer)
  valor: number | null
  // valor do periodo anterior, null ou 0 n mostra a comparacao
  anterior: number | null
  formatar?: (valor: number) => string
  // tempo por ex, cair é bom
  menorMelhor?: boolean
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

function formatarValor(indicador: Indicador, valor: number | null) {
  if (valor === null) return '—'
  if (indicador.formatar) return indicador.formatar(valor)
  return valor.toLocaleString('pt-BR')
}

// a seta segue o numero, a cor segue se foi bom ou ruim. sem valor agora n tem o q comparar
function comparar(atual: number | null, anterior: number, menorMelhor = false) {
  if (atual === null) return { selo: '', icone: '', descricao: '' }
  if (atual === anterior) return { selo: 'bg-elevated text-muted', icone: 'i-lucide-equal', descricao: 'Igual ao período anterior' }
  const subiu = atual > anterior
  const melhorou = subiu !== menorMelhor
  return {
    selo: melhorou ? 'bg-success/15 text-success' : 'bg-error/15 text-error',
    icone: subiu ? 'i-lucide-arrow-up' : 'i-lucide-arrow-down',
    descricao: subiu ? 'Subiu em relação ao período anterior' : 'Caiu em relação ao período anterior',
  }
}

const lista = computed(() => {
  const resultado = []
  for (const indicador of props.indicadores) {
    resultado.push({
      ...indicador,
      texto: formatarValor(indicador, indicador.valor),
      // antes zerado n compara nada
      antes: indicador.anterior ? formatarValor(indicador, indicador.anterior) : null,
      comparacao: comparar(indicador.valor, indicador.anterior ?? 0, indicador.menorMelhor),
    })
  }
  return resultado
})
</script>
