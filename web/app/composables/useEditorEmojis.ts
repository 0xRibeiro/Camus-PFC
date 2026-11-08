import type { EditorEmojiMenuItem } from '@nuxt/ui'
import { Emoji, gitHubEmojis, shortcodeToEmoji } from '@tiptap/extension-emoji'

export function useEditorEmojis() {
  const items: EditorEmojiMenuItem[] = gitHubEmojis.filter(
    emoji => !emoji.name.startsWith('regional_indicator_'),
  )

  const extension = Emoji.extend({
    markdownTokenName: 'emoji',
    markdownTokenizer: {
      name: 'emoji',
      level: 'inline',
      start: ':',
      tokenize(src) {
        const match = src.match(/^:([a-zA-Z0-9_+-]+):/)
        if (!match?.[1]) return undefined
        if (!shortcodeToEmoji(match[1], gitHubEmojis)) return undefined
        return { type: 'emoji', raw: match[0], name: match[1] }
      },
    },
    parseMarkdown(token, { createNode }) {
      return createNode('emoji', { name: token.name })
    },
    renderMarkdown(node) {
      if (!node.attrs?.name) return ''
      const emojiItem = shortcodeToEmoji(node.attrs.name, gitHubEmojis)
      return emojiItem?.emoji || `:${node.attrs.name}:`
    },
  })

  return {
    items,
    extension,
  }
}
