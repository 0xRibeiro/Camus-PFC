// cor de cada tipo de conteudo, usada na tela de editar a trilha e no funil da dashboard.
// linha: faixa na esquerda + fundo leve, icone: bolinha do icone, selo: o tipo escrito, barra: preenchimento cheio
export const tiposInfo = {
  video: {
    label: 'Vídeo',
    icon: 'i-lucide-play-circle',
    linha: 'border-l-sky-500 bg-sky-500/5',
    icone: 'bg-sky-500/15 text-sky-500',
    selo: 'bg-sky-500/15 text-sky-600 ring-sky-500/30 dark:text-sky-300',
    barra: 'bg-sky-500',
  },
  artigo: {
    label: 'Artigo',
    icon: 'i-lucide-book-open',
    linha: 'border-l-emerald-500 bg-emerald-500/5',
    icone: 'bg-emerald-500/15 text-emerald-500',
    selo: 'bg-emerald-500/15 text-emerald-600 ring-emerald-500/30 dark:text-emerald-300',
    barra: 'bg-emerald-500',
  },
  quiz: {
    label: 'Quiz',
    icon: 'i-lucide-list-checks',
    linha: 'border-l-violet-500 bg-violet-500/5',
    icone: 'bg-violet-500/15 text-violet-500',
    selo: 'bg-violet-500/15 text-violet-600 ring-violet-500/30 dark:text-violet-300',
    barra: 'bg-violet-500',
  },
} as const

export type TipoConteudo = keyof typeof tiposInfo
