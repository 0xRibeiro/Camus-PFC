import type { BadgeProps } from '@nuxt/ui'

export type CorTagTrilha = NonNullable<BadgeProps['color']>

type TagTrilha = { label: string, value: string, color: CorTagTrilha }

export const TRILHA_TAGS: TagTrilha[] = [
  { label: 'IoT', value: 'iot', color: 'secondary' },
  { label: 'Limnologia', value: 'limnologia', color: 'primary' },
  { label: 'Biologia', value: 'biologia', color: 'quaternary' },
  { label: 'Oceanografia', value: 'oceanografia', color: 'tertiary' },
  { label: 'Aquarismo', value: 'aquarismo', color: 'error' },
  { label: 'Outro', value: 'outro', color: 'neutral' },
]

export function infoDaTagTrilha(tag: string | null | undefined): TagTrilha {
  for (const item of TRILHA_TAGS) {
    if (item.value === tag) return item
  }

  if (!tag) return { label: '', value: '', color: 'neutral' }

  return { label: tag, value: tag, color: 'neutral' }
}
