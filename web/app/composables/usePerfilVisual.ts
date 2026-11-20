// troca aqui pra comparar os dois jeitos do transparente
const ESTILO_TRANSPARENTE: 'xadrez' | 'vidro' = 'vidro'

// vidro branco: fundo quase nada, desfoque do q ta atras, borda clara e reflexo na diagonal
const CARD_VIDRO = 'bg-white/15 bg-linear-to-br from-white/50 via-white/5 to-white/10 backdrop-blur-xl ring-white/60 divide-white/40 shadow-lg shadow-black/5 dark:bg-white/5 dark:from-white/15 dark:via-white/0 dark:to-white/5 dark:ring-white/15 dark:divide-white/10 dark:shadow-black/30'

// opaco, so puxando um pouco do primary (q no perfil é a cor_fundo do usuario)
const CARD_TINGIDO = 'bg-default bg-linear-to-br from-primary/15 via-primary/0 to-primary/5 ring-primary/25 divide-primary/15 shadow-lg shadow-primary/10'

// msm xadrez do seletor do perfil, mas seguindo o tema claro/escuro
export const XADREZ = 'repeating-conic-gradient(var(--ui-border-accented) 0 25%, var(--ui-bg) 0 50%) 0 0 / 8px 8px'

// visual dos cards do perfil, todos usam pra ficar igual
export function usePerfilVisual() {
  const auth = useAuthStore()

  // easter egg: 100% transparente troca o visual dos cards e do grafico
  const transparente = computed(() => {
    const salva = auth.user?.cor_fundo ?? ''
    return salva.length === 9 && salva.slice(7) === '00'
  })

  const estilo = computed(() => transparente.value ? ESTILO_TRANSPARENTE : undefined)

  // vai no style de quem envolve os cards, troca o primary so ali dentro
  const tema = computed(() => {
    if (transparente.value) return { '--ui-primary': 'var(--ui-text-highlighted)' }
    return { '--ui-primary': (auth.user?.cor_fundo ?? '#0EA5E9').slice(0, 7) }
  })

  const card = computed(() => {
    if (estilo.value === 'vidro') return CARD_VIDRO
    if (estilo.value === 'xadrez') return ''
    return CARD_TINGIDO
  })

  return { transparente, estilo, tema, card }
}
