import { Node, mergeAttributes } from '@tiptap/core'
import type { NodeViewRenderer } from '@tiptap/core'
import { VueNodeViewRenderer } from '@tiptap/vue-3'
import EspecieInatNodeComponent from './EspecieInatNode.vue'

declare module '@tiptap/core' {
  interface Commands<ReturnType> {
    especieInat: {
      insertEspecieInat: () => ReturnType
    }
  }
}

// bloco de especie do iNat, guarda o taxon_id e uma copia dos dados do card no JSON do artigo
export const EspecieInat = Node.create({
  name: 'especieInat',
  group: 'block',
  atom: true,
  draggable: true,
  addAttributes() {
    return {
      taxonId: { default: null },
      nome: { default: null },
      nomePopular: { default: null },
      foto: { default: null },
      observacoes: { default: null },
      wikipedia: { default: null },
    }
  },
  parseHTML() {
    return [{
      tag: 'div[data-type="especie-inat"]',
    }]
  },
  renderHTML({ HTMLAttributes }) {
    return ['div', mergeAttributes(HTMLAttributes, { 'data-type': 'especie-inat' })]
  },
  addNodeView(): NodeViewRenderer {
    return VueNodeViewRenderer(EspecieInatNodeComponent)
  },
  addCommands() {
    return {
      insertEspecieInat: () => ({ commands }) => {
        return commands.insertContent({ type: this.name })
      },
    }
  },
})

export default EspecieInat
