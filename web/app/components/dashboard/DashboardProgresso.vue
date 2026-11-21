<template>
  <UCard>
    <template #header>
      <div class="flex flex-wrap items-center justify-between gap-3">
        <h2 class="font-medium">
          Progresso dos alunos
        </h2>

        <!-- msm botao do acerto por questao, troca os numeros da legenda e do funil juntos -->
        <UButton
          :icon="emPorcentagem ? 'i-lucide-percent' : 'i-lucide-hash'"
          :label="emPorcentagem ? 'Porcentagem' : 'Quantidade'"
          size="sm"
          color="neutral"
          variant="ghost"
          aria-label="Alternar entre porcentagem e quantidade"
          @click="emPorcentagem = !emPorcentagem"
        />
      </div>
    </template>

    <div class="space-y-8">
      <!-- uma barra so com a situacao de todo mundo -->
      <div class="space-y-3">
        <div
          class="flex h-4 overflow-hidden rounded-full bg-accented"
          role="img"
          :aria-label="textoSituacao"
        >
          <div
            v-for="parte in partes"
            :key="parte.titulo"
            class="h-full transition-[width] duration-500"
            :class="parte.barra"
            :style="{ width: `${parte.porcentagem * 100}%` }"
          />
        </div>

        <div class="flex flex-wrap gap-x-6 gap-y-2">
          <p
            v-for="parte in partes"
            :key="parte.titulo"
            class="flex items-center gap-2 text-sm"
          >
            <span
              class="size-2.5 shrink-0 rounded-full"
              :class="parte.barra"
              aria-hidden="true"
            />
            <span class="text-muted">{{ parte.titulo }}</span>
            <span class="font-semibold text-highlighted tabular-nums">
              {{ emPorcentagem ? formatarPorcentagem(parte.porcentagem) : parte.valor.toLocaleString('pt-BR') }}
            </span>
          </p>
        </div>
      </div>

      <!-- funil: cada conteudo com quantos dos q comecaram chegaram ali -->
      <div class="space-y-3">
        <h3 class="text-sm font-medium text-highlighted">
          Até onde chegaram
        </h3>

        <ol
          v-if="funil.length"
          class="space-y-1"
          aria-label="Funil dos conteúdos"
        >
          <li
            v-for="(conteudo, posicao) in lista"
            :key="conteudo.id"
          >
            <!-- so o quiz tem dashboard, abre no modal -->
            <component
              :is="conteudo.tipo === 'quiz' ? 'button' : 'div'"
              :type="conteudo.tipo === 'quiz' ? 'button' : undefined"
              class="grid w-full grid-cols-1 items-center gap-x-4 gap-y-1.5 rounded-md px-2 py-2 text-left sm:grid-cols-[14rem_1fr]"
              :class="conteudo.tipo === 'quiz' && 'group cursor-pointer ring-inset transition hover:bg-violet-500/10 hover:ring-1 hover:ring-violet-500/40 focus-visible:bg-violet-500/10 focus-visible:ring-1 focus-visible:ring-violet-500/40 focus-visible:outline-none'"
              @click="conteudo.tipo === 'quiz' && emit('abrirQuiz', conteudo)"
            >
              <div class="flex min-w-0 items-center gap-2">
                <span class="w-4 shrink-0 text-right text-xs font-medium text-dimmed">
                  {{ posicao + 1 }}
                </span>

                <!-- msm cor de cada tipo da tela de editar -->
                <span
                  class="flex size-7 shrink-0 items-center justify-center rounded-full"
                  :class="tipo(conteudo.tipo).icone"
                >
                  <UIcon
                    :name="tipo(conteudo.tipo).icon"
                    class="size-4"
                  />
                </span>

                <p class="truncate text-sm font-medium text-highlighted transition-colors group-hover:text-violet-600 dark:group-hover:text-violet-300">
                  {{ conteudo.titulo }}
                </p>

                <!-- icone de grafico: abre a dashboard do quiz -->
                <UIcon
                  v-if="conteudo.tipo === 'quiz'"
                  name="i-lucide-chart-column"
                  class="size-4 shrink-0 text-dimmed transition-colors group-hover:text-violet-500"
                />
              </div>

              <!-- o numero fica dentro da barra, se ela for curta vai pro lado -->
              <div class="flex h-7 items-center overflow-hidden rounded-md bg-elevated">
                <div
                  class="relative flex h-full items-center justify-end px-2 transition-[width] duration-500"
                  :style="{ width: `${conteudo.porcentagem * 100}%` }"
                >
                  <!-- quanto menos gente chegou mais fraca a cor, so o fundo apaga e o numero fica nitido -->
                  <span
                    class="absolute inset-0 rounded-md transition-opacity duration-500"
                    :class="tipo(conteudo.tipo).barra"
                    :style="{ opacity: conteudo.intensidade }"
                    aria-hidden="true"
                  />

                  <span
                    v-if="conteudo.porcentagem >= 0.15"
                    class="relative text-xs font-semibold tabular-nums"
                    :class="conteudo.intensidade >= 0.6 ? 'text-white' : 'text-highlighted'"
                  >
                    {{ conteudo.texto }}
                  </span>
                </div>

                <span
                  v-if="conteudo.porcentagem < 0.15"
                  class="px-2 text-xs font-semibold tabular-nums"
                >
                  {{ conteudo.texto }}
                </span>
              </div>
            </component>
          </li>
        </ol>

        <p
          v-else
          class="text-sm text-muted"
        >
          A trilha ainda não tem conteúdos.
        </p>
      </div>
    </div>
  </UCard>
</template>

<script setup lang="ts">
import type { ConteudoFunilRead, EngajamentoTrilhaRead } from '~/types/generated'
import { tiposInfo } from '~/utils/tiposConteudo'
import type { TipoConteudo } from '~/utils/tiposConteudo'

const props = defineProps<{
  engajamento: EngajamentoTrilhaRead
  funil: ConteudoFunilRead[]
  // so no grupo da pra saber quem ainda n comecou, na global a base é todo o sistema
  deGrupo?: boolean
}>()

const emPorcentagem = ref(false)

const emit = defineEmits<{
  abrirQuiz: [conteudo: ConteudoFunilRead]
}>()

// tipo q n tiver na lista cai no artigo
function tipo(nome: string) {
  if (nome in tiposInfo) return tiposInfo[nome as TipoConteudo]
  return tiposInfo.artigo
}

const formatarPorcentagem = new Intl.NumberFormat('pt-BR', { style: 'percent', maximumFractionDigits: 0 }).format

/* situacao de todo mundo */

// no grupo a base sao os membros, na global so quem comecou. base zerada fica 0
function sobreBase(valor: number) {
  const base = props.deGrupo ? props.engajamento.base : props.engajamento.iniciaram
  if (!base) return 0
  return valor / base
}

// msm cor da lista de alunos do grupo
const partes = computed(() => {
  const { base, iniciaram, concluiram } = props.engajamento
  const andamento = iniciaram - concluiram

  const lista = [
    { titulo: 'Terminaram', valor: concluiram, porcentagem: sobreBase(concluiram), barra: 'bg-success' },
    { titulo: 'Em andamento', valor: andamento, porcentagem: sobreBase(andamento), barra: 'bg-warning' },
  ]
  if (props.deGrupo) {
    let naoComecaram = base - iniciaram
    if (naoComecaram < 0) naoComecaram = 0
    lista.push({ titulo: 'Não começaram', valor: naoComecaram, porcentagem: sobreBase(naoComecaram), barra: 'bg-accented' })
  }
  return lista
})

const textoSituacao = computed(() => {
  const textos = []
  for (const parte of partes.value) textos.push(`${parte.titulo}: ${parte.valor}`)
  return textos.join(', ')
})

/* funil */

// a barra cheia fica com a cor toda e vai apagando ate 35%, nunca some
const lista = computed(() => {
  const itens = []
  for (const conteudo of props.funil) {
    const porcentagem = props.engajamento.iniciaram ? conteudo.concluiram / props.engajamento.iniciaram : 0
    itens.push({
      ...conteudo,
      porcentagem,
      intensidade: 0.35 + porcentagem * 0.65,
      texto: emPorcentagem.value ? formatarPorcentagem(porcentagem) : conteudo.concluiram.toLocaleString('pt-BR'),
    })
  }
  return itens
})
</script>
