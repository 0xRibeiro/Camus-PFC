import type { BadgeProps } from '@nuxt/ui'

export type CorTagTrilha = NonNullable<BadgeProps['color']>

type TagTrilha = { label: string, value: string, color: CorTagTrilha }

export const TRILHA_TAGS: TagTrilha[] = [
  { label: 'IoT', value: 'iot', color: 'secondary' },
  { label: 'Limnologia', value: 'limnologia', color: 'quinary' },
  { label: 'Biologia', value: 'biologia', color: 'quaternary' },
  { label: 'Oceanografia', value: 'oceanografia', color: 'tertiary' },
  { label: 'Aquarismo', value: 'aquarismo', color: 'senary' },
  { label: 'Outro', value: 'outro', color: 'neutral' },
]

export function infoDaTagTrilha(tag: string | null | undefined): TagTrilha {
  for (const item of TRILHA_TAGS) {
    if (item.value === tag) return item
  }

  if (!tag) return { label: '', value: '', color: 'neutral' }

  return { label: tag, value: tag, color: 'neutral' }
}

// trilha sem tag cai nessa chave nos filtros e nas secoes
export const SEM_TAG_TRILHA = 'sem-tag'

export function chaveDaTagTrilha(tag: string | null | undefined) {
  if (!tag) return SEM_TAG_TRILHA
  return tag
}

export function rotuloDaSecaoTrilha(chave: string) {
  if (chave === SEM_TAG_TRILHA) return 'Sem tag'
  return infoDaTagTrilha(chave).label
}

export function corDaSecaoTrilha(chave: string): CorTagTrilha {
  if (chave === SEM_TAG_TRILHA) return 'neutral'
  return infoDaTagTrilha(chave).color
}

// ordem alfabetica, com "outro" e "sem tag" sempre no fim
function pesoDaSecaoTrilha(chave: string) {
  if (chave === SEM_TAG_TRILHA) return 2
  if (chave === 'outro') return 1
  return 0
}

export function compararSecoesTrilha(a: string, b: string) {
  const diferenca = pesoDaSecaoTrilha(a) - pesoDaSecaoTrilha(b)
  if (diferenca !== 0) return diferenca
  return rotuloDaSecaoTrilha(a).localeCompare(rotuloDaSecaoTrilha(b), 'pt-BR')
}

// opcoes do filtro, ja na ordem das secoes. "sem tag" fica de fora, toda trilha nova tem tag
export function opcoesFiltroTagTrilha() {
  const chaves: string[] = []
  for (const item of TRILHA_TAGS) chaves.push(item.value)
  chaves.sort(compararSecoesTrilha)

  const opcoes: { label: string, value: string, chip: { color: CorTagTrilha } }[] = []
  for (const chave of chaves) {
    opcoes.push({ label: rotuloDaSecaoTrilha(chave), value: chave, chip: { color: corDaSecaoTrilha(chave) } })
  }
  return opcoes
}
