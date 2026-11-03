<script setup lang="ts">
import type { NodeViewProps } from '@tiptap/vue-3'
import { NodeViewWrapper } from '@tiptap/vue-3'

const props = defineProps<NodeViewProps>()

const error = ref<string | null>(null)
const loading = ref(false)

const { enviarImagem, mensagemDeErro } = useUploadImagem()

// envia e troca o bloco de upload pela imagem com a url q voltou
async function onFileChange(arquivo: File | null | undefined) {
  if (!arquivo) {
    return
  }

  loading.value = true
  error.value = null

  try {
    const url = await enviarImagem(arquivo)

    const pos = props.getPos()
    if (typeof pos !== 'number') {
      return
    }

    props.editor
      .chain()
      .focus()
      .deleteRange({ from: pos, to: pos + 1 })
      .setImage({ src: url })
      .run()
  }
  catch (e) {
    error.value = mensagemDeErro(e)
  }
  finally {
    loading.value = false
  }
}
</script>

<template>
  <NodeViewWrapper>
    <UFileUpload
      accept="image/png,image/jpeg,image/webp,image/gif"
      label="Enviar uma imagem"
      :description="error || 'PNG, JPG, WEBP ou GIF (máx. 10 MB)'"
      :preview="false"
      class="min-h-48"
      :ui="{ description: error ? 'text-error' : '' }"
      @update:model-value="onFileChange"
    >
      <template #leading>
        <UAvatar
          :icon="error ? 'i-lucide-alert-circle' : loading ? 'i-lucide-loader-circle' : 'i-lucide-image'"
          size="xl"
          :ui="{ icon: [loading && 'animate-spin', error && 'text-error'] }"
        />
      </template>
    </UFileUpload>
  </NodeViewWrapper>
</template>
