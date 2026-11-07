import type { EditorSuggestionMenuItem, EditorCustomHandlers } from '@nuxt/ui'

export function useEditorSuggestions<T extends EditorCustomHandlers>() {
  const items = [[{
    type: 'label',
    label: 'Style',
  }, {
    kind: 'paragraph',
    label: 'Paragraph',
    icon: 'i-lucide-type',
  }, {
    kind: 'heading',
    level: 1,
    label: 'Heading 1',
    icon: 'i-lucide-heading-1',
  }, {
    kind: 'heading',
    level: 2,
    label: 'Heading 2',
    icon: 'i-lucide-heading-2',
  }, {
    kind: 'heading',
    level: 3,
    label: 'Heading 3',
    icon: 'i-lucide-heading-3',
  }, {
    kind: 'bulletList',
    label: 'Bullet List',
    icon: 'i-lucide-list',
  }, {
    kind: 'orderedList',
    label: 'Numbered List',
    icon: 'i-lucide-list-ordered',
  }, {
    kind: 'taskList',
    label: 'Task List',
    icon: 'i-lucide-list-check',
  }, {
    kind: 'blockquote',
    label: 'Blockquote',
    icon: 'i-lucide-text-quote',
  }, {
    kind: 'codeBlock',
    label: 'Code Block',
    icon: 'i-lucide-square-code',
  }], [{
    type: 'label',
    label: 'Insert',
  }, {
    kind: 'emoji',
    label: 'Emoji',
    icon: 'i-lucide-smile-plus',
  }, {
    kind: 'imageUpload',
    label: 'Image',
    icon: 'i-lucide-image',
  }, {
    kind: 'especieInat',
    label: 'Espécie (iNat)',
    icon: 'i-lucide-fish',
  }, {
    kind: 'table',
    label: 'Table',
    icon: 'i-lucide-table',
  }, {
    kind: 'horizontalRule',
    label: 'Horizontal Rule',
    icon: 'i-lucide-separator-horizontal',
  }]] satisfies EditorSuggestionMenuItem<T>[][]

  return {
    items,
  }
}
